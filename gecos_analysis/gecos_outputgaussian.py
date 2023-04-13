import cclib
import glob
import os
from collections import defaultdict
from openbabel import openbabel as ob
import pandas as pd
import rmsd
import copy
import numpy as np
import datetime
import MDAnalysis
from utils.internal_coordinates import dihedral_py
try:
    from gecos_analysis.gecos_closecontacts import CloseContacts
except ModuleNotFoundError:
    from gecos_closecontacts import CloseContacts


class GaussianGecos:

    # =========================================================================
    def __init__(self, pathlogfiles, ext="log", logger=None):

        """
        Initialize the instance

        :param pathlogfiles: Path to the output files from Gaussian16
        :param ext: Extension of the output files
        :param logger: Logger to write results
        """

        # Logger to write results
        self._logger = logger
        # Path where the log iles are located
        self._logfiles = sorted(glob.glob(os.path.join(pathlogfiles, "*." + ext)))
        self._optscfenergies = defaultdict()
        self._freenergies = defaultdict()
        self._optgeometry = defaultdict(list)
        self._rotconsts = defaultdict(list)
        self._vibfreqs = defaultdict()
        self._vibirs = defaultdict()
        self._temperature = defaultdict()
        self._xyzlist = []
        self._internalcoords = defaultdict(dict)
        self._minscfenergy_ha = None

        if len(self._logfiles) == 0:
            m = "\n\t\t ERROR. No G16 log files in the folder\n"
            m += "\t\t {}".format(pathlogfiles)
            print(m) if self._logger is None else self._logger.error(m)
            exit()

        # DataFrame
        self._df = pd.DataFrame({'ID': [],
                                 'OptEnergy(Ha)': [],
                                 'DeltaEnergy(kcal/mol)': [],
                                 'Path': [],
                                 'RMSDwithHs': [],
                                 'RMSDwithoutHs': [],
                                 'RotConstA(Ghz)': [],
                                 'RotConstB(Ghz)': [],
                                 'RotConstC(Ghz)': [],
                                 'AngleMainPrincipalAxes(deg)': [],
                                 'NHbonds': [],
                                 'NvdwContacts_Intermol': [],
                                 'NvdwContacts_Intramol': [],
                                 'Delta_G(kcal/mol)': [],
                                 'Delta_-TS(kcal/mol)': [],
                                 'Delta_H(kcal/mol)': []})

    # =========================================================================
    def getlogfiles(self):

        return self._logfiles

    # =========================================================================
    def getvibfreqs(self):

        return self._vibfreqs

    # =========================================================================
    def getvibirs(self):

        return self._vibirs

    # =========================================================================
    def gettemperature(self):

        return self._temperature

    # =========================================================================
    def getdeltag(self):

        dd = defaultdict()
        ll = list(self._df['Delta_G(kcal/mol)'])
        for i, item in enumerate(list(self._df['ID'])):
            dd[item] = ll[i]

        return dd

    # =========================================================================
    def getoptxyz_coordinates(self):

        return self._xyzlist

    # =========================================================================
    def extract_vibrational_ir(self):

        # ==================== THERMOCHEMISTRY ============================
        # Parse data from gaussian logs
        entropy_list = defaultdict()
        temperature_list = defaultdict()
        enthalpy_list = defaultdict()
        scf_list = defaultdict()
        vibfreqs_list = defaultdict()
        vibirs_list = defaultdict()
        for ipath in self._logfiles:
            ifile = os.path.splitext(os.path.split(ipath)[-1])[0]
            parser = cclib.io.ccopen(ipath)
            data = parser.parse()
            self._freenergies[ifile] = data.freeenergy
            entropy_list[ifile] = data.entropy
            enthalpy_list[ifile] = data.enthalpy
            temperature_list[ifile] = data.temperature
            scf_list[ifile] = data.scfenergies[-1]
            vibfreqs_list[ifile] = data.vibfreqs
            vibirs_list[ifile] = data.vibirs

        # Ordering the structures by free energy
        self._freenergies = dict(sorted(self._freenergies.items(), key=lambda v: v[1]))
        pathlist = [i for i in self._freenergies.keys()]
        idlist = [os.path.splitext(os.path.split(i)[-1])[0] for i in self._freenergies.keys()]
        freeenergylist = [i for key, i in self._freenergies.items()]
        minfreeenergy = freeenergylist[0]

        deltafreeenergylist = [cclib.parser.utils.convertor(i - minfreeenergy, 'hartree', 'kcal/mol')
                               for i in freeenergylist]

        # Get all values of thermochemistry
        iref = list(self._freenergies.items())[0][0]
        self._df['ID'] = idlist
        self._df['Delta_G(kcal/mol)'] = deltafreeenergylist
        self._df['Path'] = pathlist
        delta_tentropy_list = []
        delta_enthalpy_list = []
        delta_scf_list = []
        for ikey, ivalue in self._freenergies.items():
            delta_tentropy = entropy_list[ikey] - entropy_list[iref]
            delta_tentropy = cclib.parser.utils.convertor(delta_tentropy, 'hartree', 'kcal/mol')\
                             * temperature_list[iref] * (-1)
            delta_tentropy_list.append(delta_tentropy)

            delta_enthalpy = enthalpy_list[ikey] - enthalpy_list[iref]
            delta_enthalpy = cclib.parser.utils.convertor(delta_enthalpy, 'hartree', 'kcal/mol')
            delta_enthalpy_list.append(delta_enthalpy)

            delta_scf = scf_list[ikey] - scf_list[iref]
            delta_scf = cclib.parser.utils.convertor(delta_scf, 'eV', 'kcal/mol')
            delta_scf_list.append(delta_scf)

            self._vibfreqs[ikey] = vibfreqs_list[ikey]
            self._vibirs[ikey] = vibirs_list[ikey]
            self._temperature[ikey] = temperature_list[ikey]

        self._df['Delta_-TS(kcal/mol)'] = delta_tentropy_list
        self._df['Delta_H(kcal/mol)'] = delta_enthalpy_list
        self._df['Delta_E(kcal/mol)'] = delta_scf_list

    # =========================================================================
    def extract_energy(self):

        # Extracting energy of the optimized structure from the logfiles
        tmp_optgeometry = defaultdict(list)
        nl = len(self._logfiles)
        for idx, ifile in enumerate(self._logfiles):
            if idx % int(nl*0.1) == 0:
                now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                m = "\t\t\tParsing {} log files out of {} ({})".format(idx, nl, now)
                print(m) if self._logger is None else self._logger.info(m)
            parser = cclib.io.ccopen(ifile)
            data = parser.parse()
            self._optscfenergies[ifile] = data.scfenergies[-1]  # in eV,
            tmp_optgeometry[ifile].append(data.atomnos)
            tmp_optgeometry[ifile].append(data.atomcoords[-1])
            self._rotconsts[ifile].append(data.rotconsts[-1])

        # Creating the dataframe
        self._optscfenergies = dict(sorted(self._optscfenergies.items(), key=lambda v: v[1]))
        pathlist = [i for i in self._optscfenergies.keys()]
        idlist = [os.path.splitext(os.path.split(i)[-1])[0] for i in self._optscfenergies.keys()]
        energylist = [cclib.parser.utils.convertor(i, 'eV', 'hartree') for key, i in self._optscfenergies.items()]
        minenergy = energylist[0]
        self._minscfenergy_ha = minenergy
        deltaenergylist = [cclib.parser.utils.convertor(i - minenergy, 'hartree', 'kcal/mol') for i in energylist]

        rotconstlist_a = []
        rotconstlist_b = []
        rotconstlist_c = []

        for ikey, ivalue in self._optscfenergies.items():
            rotconstlist_a.append(self._rotconsts[ikey][0][0])
            rotconstlist_b.append(self._rotconsts[ikey][0][1])
            rotconstlist_c.append(self._rotconsts[ikey][0][2])
            self._optgeometry[ikey] = tmp_optgeometry[ikey]

        self._df['ID'] = idlist
        self._df['OptEnergy(Ha)'] = energylist
        self._df['DeltaEnergy(kcal/mol)'] = deltaenergylist
        self._df['Path'] = pathlist
        self._df['RotConstA(Ghz)'] = rotconstlist_a
        self._df['RotConstB(Ghz)'] = rotconstlist_b
        self._df['RotConstC(Ghz)'] = rotconstlist_c

    # =========================================================================
    def extract_rmsd(self):

        """
        Calculate the rmsd between all molecules and the lowest energy molecule
        as reference

        """

        rmsd_all_list = []
        rmsd_noh_list = []
        idxfile = 0
        for ifile, values in self._optgeometry.items():
            localdir, basename = os.path.split(ifile)
            basename = os.path.splitext(basename)[0]
            natoms = len(values[0])
            xyzstring = "{0:<s}\n{1:<s}\n".format(str(natoms), basename)
            for idx in range(len(values[0])):
                element = ob.GetSymbol(int(values[0][idx]))
                xyzstring += "{0:<s}  {1:10.4f}  {2:10.4f}  {3:10.4f}\n".format \
                    (element, values[1][idx][0], values[1][idx][1], values[1][idx][2])
            self._xyzlist.append(xyzstring)
            # xyzlist[0] = "3\nCarb\nC 1.54 0.0 0.0\nC 0.0 1.54 0.0\nC 0.0 0.0 1.54"
            if idxfile == 0:
                molref = ob.OBMol()
                obref = ob.OBConversion()
                obref.SetInAndOutFormats('xyz', 'xyz')
                obref.ReadString(molref, self._xyzlist[0])
                namefileref = os.path.join(localdir, "reference_allign.xyz")
                obref.WriteFile(molref, namefileref)
                atoms_ref, coord_ref = rmsd.get_coordinates_xyz(namefileref)
                atoms_ref_noh = np.where(atoms_ref != 'H')
                coord_ref_noh = copy.deepcopy(coord_ref[atoms_ref_noh])
                rmsd_all_list.append(0.0)
                rmsd_noh_list.append(0.0)
                os.remove(namefileref)
            else:
                obtarget = ob.OBConversion()
                obtarget.SetInAndOutFormats('xyz', 'xyz')
                moltarget = ob.OBMol()
                obtarget.ReadString(moltarget, self._xyzlist[idxfile])
                a = ob.OBAlign(False, False)
                a.SetRefMol(molref)
                a.SetTargetMol(moltarget)
                a.Align()
                a.UpdateCoords(moltarget)
                namefile = os.path.join(localdir, "target_{}_allign.xyz".format(idxfile))
                obref.WriteFile(moltarget, namefile)
                atoms_target, coord_target = rmsd.get_coordinates_xyz(namefile)
                atoms_target_noh = np.where(atoms_target != 'H')
                coord_target_noh = copy.deepcopy(coord_target[atoms_target_noh])
                rmsd_noh_list.append(rmsd.rmsd(coord_target_noh, coord_ref_noh))
                rmsd_all_list.append(rmsd.rmsd(coord_target, coord_ref))
                os.remove(namefile)
            idxfile += 1

        self._df["RMSDwithHs"] = rmsd_all_list
        self._df["RMSDwithoutHs"] = rmsd_noh_list

    # =========================================================================
    def extract_internalcoords(self, args):

        """
         The ndx file must contiain labels [ distances ], [ angles ] and/or [ dihedral ].
         Following the label a line for each the internal coordinate must be listed.
         The internal coodinate must to be present in the log file otherwise is not considered.
         Example:
              [ distances ]
              1 2
              2 3
              [ dihedrals ]
              4 3 2 1
              5 4 3 1
         This file extracts the values of two distances (1-2 and 2-3) and two dihedrals (4-3-2-1 and 5-4-3-1)
         The numbering starts at 1 in th file internally the numbering starts at 0.
        """

        distances_list = []
        angles_list = []
        dihedrals_list = []

        with open(args.indxfile, 'r') as fout:
            lines = fout.readlines()
            for iline in lines:
                if iline.count("[") != 0:
                    continue
                else:
                    tokens = iline.split()
                    if len(tokens) == 2:
                        # Distance
                        try:
                            distances_list.append([int(i) for i in tokens])
                        except (Exception, ):
                            m = "\t\t ERROR in {} file. Distances".format(args.indxfile)
                            print(m) if self._logger is None else self._logger.info(m)
                            exit()
                    elif len(tokens) == 3:
                        # Angles
                        try:
                            angles_list.append([int(i) for i in tokens])
                        except (Exception, ):
                            m = "\t\t ERROR in {} file. Angles".format(args.indxfile)
                            print(m) if self._logger is None else self._logger.info(m)
                            exit()
                    elif len(tokens) == 4:
                        # Dihedrals
                        try:
                            dihedrals_list.append([int(i) for i in tokens])
                        except (Exception, ):
                            m = "\t\t ERROR in {} file. Distances".format(args.indxfile)
                            print(m) if self._logger is None else self._logger.info(m)
                            exit()

        for key, values in self._optgeometry.items():
            for idist in distances_list:
                m = "\t\t ERROR in {} file. " \
                    "Distances are not yet implemented in gecos_outputgaussian.py".format(args.indxfile)
                print(m) if self._logger is None else self._logger.info(m)
                exit()
            for iangle in angles_list:
                m = "\t\t ERROR in {} file. " \
                    "Angles are not yet implemented in gecos_outputgaussian.py".format(args.indxfile)
                print(m) if self._logger is None else self._logger.info(m)
                exit()
            for idih in dihedrals_list:
                at1, at2, at3, at4 = idih[0:4]
                c1 = values[1][at1-1]
                c2 = values[1][at2-1]
                c3 = values[1][at3-1]
                c4 = values[1][at4-1]
                dih_angle = dihedral_py(c1, c2, c3, c4, units="degree")
                if at4 < at1:
                    label = "{}-{}-{}-{}".format(at4, at3, at2, at1)
                else:
                    label = "{}-{}-{}-{}".format(at1, at2, at3, at4)
                self._internalcoords[key][label] = dih_angle

        m = "\n\t\tInternal coordinates have been written in distances.dat, angles.dat and/or dihedral.dat files.\n"
        print(m) if self._logger is None else self._logger.info(m)

        with open("dihedral.dat", 'w') as fdih:
            for ikey, ivalues in self._internalcoords.items():
                line = key
                for jkey, jvalues in ivalues.items():
                    line += " {0:.1f} ".format(jvalues)
                ecurr = cclib.parser.utils.convertor(self._optscfenergies[ikey], 'eV', 'hartree')
                de = ecurr - self._minscfenergy_ha
                de_kcalmol = cclib.parser.utils.convertor(de, 'hartree', 'kcal/mol')
                line += "{0:.2f} ".format(de_kcalmol)
                fdih.writelines(line+"\n")

    # =========================================================================
    def write_to_log(self, logfolder, generate_data_gnuplot=True):

        df = self._df

        # Files
        m = "\t\tLocaldir                      : {}\n".format(os.getcwd())
        m += "\t\tDirectory with Log files      : {}\n".format(logfolder)
        print(m) if self._logger is None else self._logger.info(m)

        # Write table
        m = "\n\t\t{0:1s} {1:^30s} {2:^19s} {3:^8s} {4:^17s} " \
            "{5:^16s} {6:^16s} {7:^16s} {8:^28s} {9:^8s} " \
            "{10:^17s} {11:^17s}\n".format('#', 'ID', 'DeltaEnergy(kcal/mol)',
                                           'RMSDwithHs(A)', 'RMSDwithoutHs(A)',
                                           'RotConstA(Ghz)', 'RotConstB(Ghz)',
                                           'RotConstC(Ghz)', 'AngleMainPrincipalAxes(deg)',
                                           'NHbonds', 'NvdwCont_Intermol', 'NvdwCont_Intramol')

        lenm = len(m)
        m += "\t\t# " + len(m) * "=" + "\n"
        for ind in df.index:
            line = "\t\t{0:^30s} {1:>14.2f} {2:>20.3f} {3:>14.3f} {4:>17.6f}  " \
                   "{5:>14.6f}   {6:>14.6f}  {7:>20.1f}  {8:14d}  {9:14d}  {10:14d}\n" \
                .format(df['ID'][ind],
                        df['DeltaEnergy(kcal/mol)'][ind],
                        df['RMSDwithHs'][ind],
                        df['RMSDwithoutHs'][ind],
                        df['RotConstA(Ghz)'][ind],
                        df['RotConstB(Ghz)'][ind],
                        df['RotConstC(Ghz)'][ind],
                        df['AngleMainPrincipalAxes(deg)'][ind],
                        df['NHbonds'][ind],
                        df['NvdwContacts_Intermol'][ind],
                        df['NvdwContacts_Intramol'][ind], )
            m += line
        print(m) if self._logger is None else self._logger.info(m)

        # Job Time
        m1 = "\t\t# " + lenm * "=" + "\n"
        print(m1) if self._logger is None else self._logger.info(m1)
        end = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m1 = "\t\t Job Finnished: {}\n".format(end)
        print(m1) if self._logger is None else self._logger.info(m1)

        # Generate data to draw in gnuplot
        if generate_data_gnuplot:
            if self._logger is not None:
                folder, basename = os.path.split(self._logger.handlers[0].baseFilename)
                basename = os.path.splitext(basename)[0]
            else:
                basename = "gecos_energy_analysis.dat"
            with open(os.path.join(folder, basename + ".dat"), 'w') as fdata:
                fdata.writelines(m)

    # =========================================================================
    def write_vib_to_log(self, logfolder, generate_data_gnuplot=True):

        df = self._df

        # Files
        m = "\t\tLocaldir                      : {}\n".format(os.getcwd())
        m += "\t\tDirectory with Log files      : {}\n".format(logfolder)
        print(m) if self._logger is None else self._logger.info(m)

        # Write table
        m = "\n\t\t{0:1s} {1:^40s} {2:^19s} {3:^19s} {4:^17s} " \
            "{5:^16s} \n".format('#', 'ID', 'DeltaG(kcal/mol)',
                                 'Delta_-TS(kcal/mol)', 'DeltaH(kcal/mol)',
                                 'DeltaEscf(kcal/mol)')

        lenm = len(m)
        m += "\t\t# " + len(m) * "=" + "\n"
        for ind in df.index:
            line = "\t\t{0:^40s} {1:^18.2f} {2:>18.2f} {3:>18.2f} {4:>18.2f}\n" \
                .format(df['ID'][ind],
                        df['Delta_G(kcal/mol)'][ind],
                        df['Delta_-TS(kcal/mol)'][ind],
                        df['Delta_H(kcal/mol)'][ind],
                        df['Delta_E(kcal/mol)'][ind])
            m += line
        print(m) if self._logger is None else self._logger.info(m)

        # Job Time
        m1 = "\t\t# " + lenm * "=" + "\n"
        print(m1) if self._logger is None else self._logger.info(m1)
        end = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m1 = "\t\t Job Finnished: {}\n".format(end)
        print(m1) if self._logger is None else self._logger.info(m1)

        # Generate data to draw in gnuplot
        if generate_data_gnuplot:
            if self._logger is not None:
                folder, basename = os.path.split(self._logger.handlers[0].baseFilename)
                basename = os.path.splitext(basename)[0]
            else:
                basename = "gecos_thermo_analysis.dat"
            with open(os.path.join(folder, basename + ".dat"), 'w') as fdata:
                fdata.writelines(m)

    # =========================================================================
    def close_contacts(self, args):

        if len(self._xyzlist) == 0:
            m1 = "\t\t No XYZ coordinates are found.!!!!!!\n"
            m2 = "\t\t Close Contacts cannot be calculated.!!!!!!"
            m3 = "\n\t\t" + len(m2) * "*" + "\n"
            print(m3 + m1 + m2 + m3) if self._logger is None else self._logger.warn(m3 + m1 + m2 + m3)
            return False

        # Initialize instance Contacts
        contacts = CloseContacts(self._logger)

        # For each molecule in the class search for close_contacts
        nhbonds_list = []
        nvdwcontacts_inter = []
        nvdwcontacts_intra = []
        for idx, ixyzmol in enumerate(self._xyzlist):
            molob = ob.OBMol()
            obmol = ob.OBConversion()
            obmol.SetInAndOutFormats('xyz', 'xyz')
            obmol.ReadString(molob, self._xyzlist[idx])

            # Number of fragments. Getting info from fragments
            numfrag = molob.Separate()
            if len(numfrag) != 2 and len(numfrag) != 1:
                m = "\t\tERROR. Two fragments are expected ({} fragments found)".format(len(numfrag))
                print(m) if self._logger is None else self._logger.error(m)
                exit()

            # For each fragment get the necessary info in idatoms_info_frag dictionary
            idatoms_info_frag = defaultdict(list)
            list_nb_pairs = defaultdict(list)
            for idx_ifrag, ifrag_ob in enumerate(numfrag):
                for pair in ob.OBMolPairIter(ifrag_ob):
                    (first, second) = pair
                    begin = ifrag_ob.GetAtom(first).GetId()
                    end = ifrag_ob.GetAtom(second).GetId()
                    list_nb_pairs[idx_ifrag].append({begin, end})
                for iat in ob.OBMolAtomIter(ifrag_ob):
                    symbol = ob.GetSymbol(iat.GetAtomicNum())
                    idatoms_info_frag[idx_ifrag].append([iat.GetId(),
                                                         symbol,
                                                         [iat.GetX(), iat.GetY(), iat.GetZ()]])
            if hasattr(args, "vdw") and args.vdw is not None:
                contacts.vanderwaals(self._df['ID'][idx],
                                     idatoms_info_frag,
                                     list_nb_pairs,
                                     delta=args.vdw,
                                     noignore_hs=args.noignoreh)

            if hasattr(args, "hbonds") and args.hbonds is not None:

                # HD means H atom bonded to Donor atom (D), A=acceptor
                hd_atom_idx_list = []
                acc_atom_idx_list = []
                hd_d_idx_dict = {}
                coords = []
                for iatom in ob.OBMolAtomIter(molob):
                    coords.append([iatom.GetX(), iatom.GetY(), iatom.GetZ()])
                coords = np.array(coords)

                for iatom in ob.OBMolAtomIter(molob):
                    idx_atom = iatom.GetId()
                    if iatom.GetAtomicNum() == 1:
                        for neighbor in ob.OBAtomAtomIter(iatom):
                            if neighbor.IsHbondDonor():
                                hd_atom_idx_list.append(idx_atom)  # list of H atoms
                                hd_d_idx_dict[idx_atom] = neighbor.GetId()  # dictionary of H
                    if iatom.IsHbondAcceptor():
                        acc_atom_idx_list.append(idx_atom)

                contacts.hbonds(self._df['ID'][idx],
                                idatoms_info_frag,
                                coords,
                                hd_atom_idx_list,
                                hd_d_idx_dict,
                                acc_atom_idx_list,
                                args.hbonds[0],
                                args.hbonds[1])

            nhbonds_list.append(len(contacts._hbond_list[self._df['ID'][idx]]))
            nvdwcontacts_inter.append(len(contacts._vdwcontacts_intermol[self._df['ID'][idx]]))
            nvdwcontacts_intra.append(len(contacts._vdwcontacts_intermol[self._df['ID'][idx]]))

        self._df['NHbonds'] = nhbonds_list
        self._df['NvdwContacts_Intermol'] = nvdwcontacts_inter
        self._df['NvdwContacts_Intramol'] = nvdwcontacts_intra

        if hasattr(args, "hbonds") and args.hbonds is not None:
            with open("hydrogen_bonds_info.dat", 'w') as fhbond:
                line = "#        Name        Donor     H     Acceptor    Distance(A)    Angle(degree)\n"
                fhbond.writelines(line)
                for idmol in self._df["ID"]:
                    line = "#{0:30s}\n".format(idmol)
                    fhbond.writelines(line)
                    for ihbond in contacts._hbond_list[idmol]:
                        line = "{0:10d} {1:10d} {2:10d} {3:10.3f} {4:10.1f}\n".format(ihbond[0], ihbond[1],
                                                                                      ihbond[2], ihbond[3], ihbond[4])
                        fhbond.writelines(line)

        return True

    # =========================================================================
    def moment_of_inertia(self):

        """
        Calculate the angle between the principal axis of the moment of inertia

        :return:
        """

        # For each molecule in the class search for close_contacts
        localdir = os.getcwd()
        angle_list = []
        for idxmol, ixyzmol in enumerate(self._xyzlist):
            nmols_array = defaultdict(list)
            molob = ob.OBMol()
            obmol = ob.OBConversion()
            obmol.SetInAndOutFormats('xyz', 'pdb')
            obmol.ReadString(molob, self._xyzlist[idxmol])
            namefileref = os.path.join(localdir, "tmp.pdb")
            obmol.WriteFile(molob, namefileref)

            universe = MDAnalysis.Universe("tmp.pdb")
            vects = defaultdict()
            for idxfrg, frg in enumerate(universe.atoms.fragments):
                nmols_array[idxfrg] = list(frg.indices)
                seltxt = "index "
                for iat in nmols_array[idxfrg]:
                    seltxt += "{0:d} ".format(iat)
                g = universe.select_atoms(seltxt)
                utransp = g.principal_axes()
                u = utransp.T
                vects[idxfrg] = u[:, 0]  # main axis of the principal axes

            if len(vects) == 2:
                angle_list.append(np.arccos(np.dot(vects[0], vects[1])) * 180. / np.pi)
        try:
            self._df["AngleMainPrincipalAxes(deg)"] = angle_list
        except ValueError:
            pass
