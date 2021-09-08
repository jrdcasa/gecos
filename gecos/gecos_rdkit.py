import os
import utils
import datetime
import rdkit
import rdkit.Chem.rdDistGeom
import rdkit.Chem.AllChem
import rdkit.Chem.Draw
import rdkit.ML.Cluster.Butina
from rdkit import RDLogger
from collections import defaultdict


class GecosRdkit:

    """
    This class is used to generate conformers using the RDKit package in python
    https://www.rdkit.org/

    """

    # =========================================================================
    def __init__(self, filename=None, total_charge=0,
                 bond_perception=False, logger=None):

        """
        Initialize a GecosRdkit object

        Args:
            filename (str) : Name of the file containing the molecule.
            total_charge (int) : Total charge of the molecule.
            bond_perception (bool): If True the bonds are calculated using the ``indigo-bondorders`` software
                (located in thirdparty/indigo-bondorder).
            logger (logger): Logger to send the outputs.

        """

        self._logger = logger
        self._charge = total_charge
        self._bond_list = None  # List [{1,2}, {2,3}, ...]
        self._elements = None
        self._atom_formal_charges = []
        self._isheader_print = False

        if filename is not None and os.path.splitext(filename)[-1] == ".pdb":
            self.mol_rdkit = rdkit.Chem.rdmolfiles.MolFromPDBFile(filename, removeHs=False)
            self._edmol = rdkit.Chem.EditableMol(self.mol_rdkit)
            self.set_elements()
            self.set_bonds()
            self.set_get_formal_charge(filename)
            if bond_perception:
                self.bond_perception()
            else:
                m = "\tBond_perception is FALSE for PDB file\n"
                m += "\t\tPDB file does not contain info for bond orders.\n"
                print(m) if self._logger is None else self._logger.warning(m)
        elif filename is not None and os.path.splitext(filename)[-1] == ".mol2":
            self.mol_rdkit = rdkit.Chem.rdmolfiles.MolFromMol2File(filename, removeHs=False)
            if self.mol_rdkit is not None:
                self._edmol = rdkit.Chem.EditableMol(self.mol_rdkit)
                self.set_elements()
                self.set_bonds()
                if bond_perception:
                    self.bond_perception()
                else:
                    # Assign bond property --> '_MolFileBondType'
                    try:
                        for ibond in self.mol_rdkit.GetBonds():
                            t = int(ibond.GetBondTypeAsDouble())
                            ibond.SetIntProp('_MolFileBondType', t)
                    except AttributeError:
                        pass
        elif filename is not None and os.path.splitext(filename)[-1] == ".sdf":
            suppl = rdkit.Chem.ForwardSDMolSupplier(filename, removeHs=False)
            for imol in suppl:
                self.mol_rdkit = imol
        else:
            self.mol_rdkit = None

        # Gasteiger Charges
        if self.mol_rdkit is not None:
            self.mol_rdkit.ComputeGasteigerCharges()

        # Report
        if not self._isheader_print:
            utils.print_header(self._logger)
            self._isheader_print = True

        m = "\t\t******** CREATION OF THE GECOS RDKIT OBJECT ********\n\n"
        m += "\t\tConformers will be generated with RdKit library " \
             "(https://www.rdkit.org/docs/GettingStartedInPython.html)\n"
        m += "\n"

        if self.mol_rdkit is not None:
            m += "\t\tMolecular file seed  : {}\n".format(filename)
            m += "\t\tBond Perception: {}\n".format(bond_perception)
            if not bond_perception and os.path.splitext(filename)[-1] == ".pdb":
                m += "\t\t\t WARNING!!!! Bond perception should be TRUE in PDB files"
                m += "\t\t\t WARNING!!!! otherwise conformers can be incorrect."
            if os.path.splitext(filename)[-1] == ".pdb":
                m += "\n"
                m += ""
        else:
            m += "\t\t\t WARNING!!!! Molecule might not be correctly setup.\n"
            m += "\t\t\t WARNING!!!! RdKit molecule seems to be empty (self.mol_rdkit is None).\n"
            m += "\t\t\t WARNING!!!! conformers cannot be generated.\n"
            m += "\t\t\t WARNING!!!! Revise both input parameters and/or {} inputfile .\n".format(filename)

        m += "\t\t******** CREATION OF THE GECOS RDKIT OBJECT ********\n\n"
        print(m) if self._logger is None else self._logger.info(m)

    # =========================================================================
    def __align_conformers(self, clust_ids):

        """
        Alignment of conformations. The first conformation in `clust_ids` is used as reference.

        Args:
            clust_ids (tuple): Indices of the conformers of the current cluster

        Returns:
            A list containing the rmsd of each conformer respect to the first conformer in the `clust_ids` tuple

        """

        rmsdlist = []
        rdkit.Chem.AllChem.AlignMolConformers(self.mol_rdkit, confIds=clust_ids, RMSlist=rmsdlist)
        return rmsdlist

    # =========================================================================
    def bond_perception(self):

        """
        This function assigns bond orders to the bonds according to [#]_.
        The function uses the external software ``indigo-bondorders`` (located in thirdparty/indigo-bondorder).
        This code must be compiled and installed in thirdparty/indigox

        The ``self._mol_rdkit`` attribute is modified in this function.

        .. warning::
            The structure to assign bonds needs to have all hydrogen bonds correctly placed.
            United atom models do not work with this function.

        .. [#] Welsh I.D. et al. "Automated simultaneous assignment of bond orders and formal charges",
            J. Cheminform (2019) 11:18, https://doi.org/10.1186/s13321-019-0340-0

        """

        import indigox as ix

        # Periodic Table data from indigox
        PT = ix.PeriodicTable()

        # Build a molecule in the indigox framework
        mol = ix.Molecule()
        mol.SetTotalCharge(self._charge)

        # Add all atoms in a dictionary and get the bonds in the
        # framework of indigox program
        all_atoms = dict()

        for i, j in self._bond_list:
            if i not in all_atoms:
                # Element of i
                e = self._elements[i]
                all_atoms[i] = mol.NewAtom(PT[e])
                index = all_atoms[i].SetIndex(i)
                name = e + str(index)
                all_atoms[i].SetName(name)

            if j not in all_atoms:
                # Element of j
                e = self._elements[j]
                all_atoms[j] = mol.NewAtom(PT[e])
                index = all_atoms[j].SetIndex(j)
                name = e+str(index)
                all_atoms[j].SetName(name)

            if all_atoms[i].GetIndex() < all_atoms[j].GetIndex():
                mol.NewBond(all_atoms[i], all_atoms[j])
            else:
                mol.NewBond(all_atoms[j], all_atoms[i])

        # Set formal charges
        for iatom in mol.GetAtoms():
            idx = iatom.GetIndex()
            try:
                iatom.SetFormalCharge(self._atom_formal_charges[idx])
            except IndexError:
                iatom.SetFormalCharge(iatom.GetFormalCharge())

        # Setup to use the FPT algorithm with single electrons without preplacing
        # to calculate bond orders and formal charges
        opts = ix.Options.AssignElectrons
        opts.ALGORITHM = opts.Algorithm.FPT
        opts.FPT.ADD_EDGES_TO_TD = False
        opts.FPT.MINIMUM_PROPAGATION_DEPTH = 1
        opts.USE_ELECTRON_PAIRS = False

        # Calculate bond orders and formal charges.
        # Count have the ttotal number of resonance structures
        nresonances = mol.AssignElectrons()
        # print("{} resonace structure(s) calculated "
        #      "with a score of {}.".format(nresonances, mol.GetMinimumElectronAssignmentScore()))

        # Sum all order bonds for the resonace structures.
        nbonds = len(self._bond_list)
        order_bonds = defaultdict(float)
        order_bonds_resonance_dict = defaultdict(list)
        for iresonance in range(nresonances):

            mol.ApplyElectronAssignment(iresonance)
            index_bond = 0
            for ibond in mol.GetBonds():
                i = ibond.GetSourceAtom().GetIndex()
                j = ibond.GetTargetAtom().GetIndex()
                bo = ibond.GetOrder()
                if bo == bo.SINGLE_BOND:
                    order_bonds[index_bond] += 1.
                    order_bonds_resonance_dict[iresonance].append(1.)
                elif bo == bo.DOUBLE_BOND:
                    order_bonds[index_bond] += 2.
                    order_bonds_resonance_dict[iresonance].append(2.)
                elif bo == bo.TRIPLE_BOND:
                    order_bonds[index_bond] += 3.
                    order_bonds_resonance_dict[iresonance].append(3.)
                else:
                    m = "Bond order cannot be assigned between {} and {} atoms".format(i, j)
                    m + "Bond order: {}".format(bo)
                    print(m) if self._logger is None else self._logger.warning(m)
                index_bond += 1

        # Correct for aromaticity
        for ibond in range(nbonds):
            m = order_bonds[ibond] % nresonances
            if m != 0:
                order_bonds[ibond] = 1.5
            else:
                order_bonds[ibond] /= nresonances

        # Choose a resonance structure consequent with the formal charges
        # This is needed for molecules with many resonance structrures
        idxs_charged = [self._atom_formal_charges.index(idx) for idx in self._atom_formal_charges if idx != 0]
        ires = 0
        for ires in range(nresonances):
            isfound = False
            idx_ibond = 0
            for ibond in mol.GetBonds():
                iat = ibond.GetSourceAtom().GetIndex()
                jat = ibond.GetTargetAtom().GetIndex()
                if iat in idxs_charged and jat in idxs_charged and \
                        order_bonds_resonance_dict[ires][idx_ibond] != 1.0:
                    isfound = True
                idx_ibond += 1
            if not isfound:
                break

        iresonance = ires

        # Assign order bond to the rdkit mol
        index_bond = 0
        for ibond in mol.GetBonds():
            i = ibond.GetSourceAtom().GetIndex()
            j = ibond.GetTargetAtom().GetIndex()
            self._edmol.RemoveBond(i, j)
            if order_bonds_resonance_dict[iresonance][index_bond] == 1.0:
                self._edmol.AddBond(i, j, order=rdkit.Chem.BondType.SINGLE)
            elif order_bonds_resonance_dict[iresonance][index_bond] == 2.0:
                self._edmol.AddBond(i, j, order=rdkit.Chem.BondType.DOUBLE)
            elif order_bonds_resonance_dict[iresonance][index_bond] == 3.0:
                self._edmol.AddBond(i, j, order=rdkit.Chem.BondType.TRIPLE)
            # elif order_bonds[index_bond] == 1.5:
            #     self._edmol.AddBond(i, j, order=rdkit.Chem.BondType.AROMATIC)
            index_bond += 1

        # print("=============")
        # for ibond in self._mol_rdkit.GetBonds():
        #     i = ibond.GetBeginAtomIdx()
        #     j = ibond.GetEndAtomIdx()
        #     bo = int(ibond.GetBondTypeAsDouble())
        #     print(i, j, bo)

        self.mol_rdkit = self._edmol.GetMol()
        flag1 = rdkit.Chem.rdmolops.SanitizeFlags.SANITIZE_SETHYBRIDIZATION
        rdkit.Chem.SanitizeMol(self.mol_rdkit, sanitizeOps=flag1)
        flag2 = rdkit.Chem.rdmolops.SanitizeFlags.SANITIZE_PROPERTIES
        rdkit.Chem.SanitizeMol(self.mol_rdkit, sanitizeOps=flag2)
        flag3 = rdkit.Chem.rdmolops.SanitizeFlags.SANITIZE_SETAROMATICITY
        rdkit.Chem.SanitizeMol(self.mol_rdkit, sanitizeOps=flag3)
        # Assign bond property --> '_MolFileBondType'
        for ibond in self.mol_rdkit.GetBonds():
            t = int(ibond.GetBondTypeAsDouble())
            ibond.SetIntProp('_MolFileBondType', t)
        #     print(iatom.GetFormalCharge())
        #     print(iatom.GetIsAromatic())

    # =========================================================================
    def __cluster_conformers(self, mode="RMSD", threshold=2.0):

        """
        Clustering conformers.

        The value of `dmat` is the lower half matrix of RMSD. The conformers will be
        alligned to the first conformer (reference). The rmsd is calculated using all atoms.
        The algorithm used in the clustering is published in Butina et al. [#]_

        Args:
            mode (str): TFD (Torsion Fingerprints (Deviation) (TFD) [#]_
                or RMSD (RMSD matrix of the conformers of a molecule).
            threshold (float): Threshold for the clustering algorithm in angstroms.

        Returns:
            A tuple of tuples containing information about the cluster.
            Example -> rms_cluster = ( (0,1,2), (3) ) Two clusters, the first one contains the conformers 0, 1, 2.

        .. [#] Butina D, "Unsupervised Data Base Clustering Based on Daylight's Fingerprint and Tanimoto
            Similarity: A Fast and Automated Way To Cluster Small and Large Data Sets", J. Chem. Inf. Comput. Sci.
            1999, 39, 4, 747–750, https://pubs.acs.org/doi/abs/10.1021/ci9803381.

        .. [#] Schulz-Gasch et al. "TFD: Torsion Fingerprints As a New Measure To Compare Small Molecule Conformations"
            J. Chem. Inf. Model. 2012, 52, 6, 1499–1512, https://pubs.acs.org/doi/abs/10.1021/ci2002318

        """

        if mode == "TFD":
            dmat = rdkit.Chem.TorsionFingerprints.GetTFDMatrix(self.mol_rdkit)
        else:
            dmat = rdkit.Chem.AllChem.GetConformerRMSMatrix(self.mol_rdkit, prealigned=False)

        n_conformers = self.mol_rdkit.GetNumConformers()

        # Implementation of the clustering algorithm published in: Butina JCICS 39 747-750 (1999)
        rms_clusters = rdkit.ML.Cluster.Butina.ClusterData(dmat, n_conformers, threshold,
                                                           isDistData=True, reordering=True)
        return rms_clusters

    # =========================================================================
    def generate_conformers(self, localdir, nconfs=10, minimize_iterations=0,
                            maxattempts=1000, prunermsthresh=-0.01, useexptorsionangleprefs=False,
                            usebasicknowledge=True,  enforcechirality=True,
                            ff_name="MMFF",
                            cluster_method="RMSD", cluster_threshold=2.0,
                            write_gaussian=True, g16_key="#p 6-31g* mp2", g16_mem=4000,
                            g16_nproc=4, pattern="conformers", charge=0, multiplicity=1):

        """
        This function performs the following steps:

            1. Create conformations using the algorithm ETKDG (Experimental-Torsion
            basic Knowledge Distance Geometry). The ETKDG method uses torsion angle preferences from
            the Cambridge Structural Database (CSD) to correct the conformers after distance geometry
            has been used to generate them. With this method, there should be no need to use
            a minimisation step to clean up the structures [#]̣_.

            2. A minimization (optional, minimize_iterations>0) and energy calculation
            is done for each generated conformed using either MMFF or UFF force fields.

            3. A clustering algorithm (Butina, JCICS 39 747-750 (1999)) is applied.

            4. Write the lowest-energy structure of each cluster to a PDB file.

            5. Write gaussian16 input file for QM optimizations of the clusters.

        Some functions and ideas are taken from Tim Dudgeon github [#]_

        Args:
            localdir (str): Path to store the files
            nconfs (int): Number of conformers to generate
            minimize_iterations (int): Number of iterations to minimize the conformers. If the value is 0
                not optimization is performed
            ff_name (str): Name of the force field (Allowed values: "UFF", "MMFF").
            cluster_method (str): Cluster method (Allowed values: "RMSD", "TFD").
            cluster_threshold (float): Threshold to classify the conformations in clusters in angstroms.
            write_gaussian (bool): If True, gausssian input files are written.
            g16_key (str): Keywords to be used in gaussian16
            g16_mem (int): Memory in Mb to be used in gaussian16
            g16_nproc (int): Number of processes to be used in gaussian16
            pattern (str):
            charge (int): Molecule charge for QM calculations
            multiplicity (int) : Spin multiplicity for QM calculations
            maxattempts (int) : The maximum number of attempts to try embedding (rdkit, EmbedMultipleConfs, [#])
            prunermsthresh (float) : Retain only the conformations out of ‘numConfs’ after embedding
                that are at least this far apart from each other (rdkit, EmbedMultipleConfs)
            useexptorsionangleprefs (bool): Impose experimental torsion angle preferences (rdkit, EmbedMultipleConfs)
            usebasicknowledge(bool): (rdkit, EmbedMultipleConfs)
            enforcechirality (bool):(rdkit, EmbedMultipleConfs)

        .. [#] Riniker S. et al. "Better Informed Distance Geometry: Using What We Know To Improve
            Conformation Generation", J. Chem. Inf. Model. 2015, 55, 2562−2574,
            https://doi.org/10.1021/acs.jcim.5b00654
        .. [#] https://gist.github.com/tdudgeon/b061dc67f9d879905b50118408c30aac
        .. [#] https://www.rdkit.org/docs/source/rdkit.Chem.rdDistGeom.html

        """

        # Disable warning messages from RdKit
        RDLogger.DisableLog('rdApp.*')

        m = "\t\t**************** GENERATE CONFORMERS ***************\n"
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m += "\t\t 1. Generating {} conformers ({})".format(nconfs, now)
        print(m) if self._logger is None else self._logger.info(m)

        # Generate conformations wihich are stores in the self._mol_rdkit
        conformerIds = rdkit.Chem.AllChem.EmbedMultipleConfs(self.mol_rdkit, numConfs=nconfs,
                                                             maxAttempts=maxattempts,
                                                             pruneRmsThresh=prunermsthresh,
                                                             useExpTorsionAnglePrefs=useexptorsionangleprefs,
                                                             useBasicKnowledge=usebasicknowledge,
                                                             enforceChirality=enforcechirality)

        conformerPropsDict = defaultdict()
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m = "\t\t 2. Minimizing {} conformers. " \
            "Max_iters = {}, threshold = {} A ({})\n".format(nconfs, minimize_iterations,
                                                             cluster_threshold, now)
        if ff_name == "MMFF":
            m += "\t\t\t Using {} forcefield".format(ff_name)
        elif ff_name == "UFF":
            if rdkit.Chem.AllChem.UFFHasAllMoleculeParams(self.mol_rdkit):
                m += "\t\t\t Using {} forcefield".format("UFF")
            else:
                m += "\t\t\t Using {} forcefield".format("MMFF")
        else:
            m += "\t\t\t Minimization is not performed."
            minimize_iterations = 0
        print(m) if self._logger is None else self._logger.info(m)

        for conf_id in utils.progressbar(conformerIds, "\t\tMinimizing", 40):
            # Calculate energy and minimize
            props = self.mm_calc_energy(conf_id, ff_name=ff_name, minimize_iterations=minimize_iterations)
            conformerPropsDict[conf_id] = props

        # cluster the MM conformers
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m = "\t\t 3. Cluster Conformers ({})".format(now)
        print(m) if self._logger is None else self._logger.info(m)
        rmsClusters = self.__cluster_conformers(cluster_method, cluster_threshold)

        m = "\t\t\t{} conformers generated grouped in {} clusters (rmsd_threshold= {} angstroms)".\
            format(len(conformerIds), len(rmsClusters), cluster_threshold)
        print(m) if self._logger is None else self._logger.info(m)

        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        m = "\t\t 4. Get structure of minimum energy for each cluster ({})".format(now)
        print(m) if self._logger is None else self._logger.info(m)

        clusterNumber = 0
        minEnergy = 9999999999999
        for cluster in rmsClusters:
            clusterNumber = clusterNumber + 1
            rmsWithinCluster = self.__align_conformers(cluster)
            for conformerId in cluster:
                props = conformerPropsDict[conformerId]
                e = props["energy_abs"]
                if e < minEnergy:
                    minEnergy = e
                props["cluster_no"] = clusterNumber
                props["cluster_centroid"] = cluster[0] + 1
                idx = cluster.index(conformerId)
                if idx > 0:
                    props["rms_to_centroid"] = rmsWithinCluster[idx - 1]
                else:
                    props["rms_to_centroid"] = 0.0

        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        filepdb_name = os.path.join(localdir, "{}_conf_min_trj.pdb".format(pattern))
        lowest_conf_id = self.write_min_cluster_conformers_to_pdb(filepdb_name,
                                                                  rmsClusters, conformerPropsDict)
        m = "\t\t 5. Write Conformers to PDB ({})\n".format(now)
        m += "\t\t\tFilename: {}".format(filepdb_name)
        print(m) if self._logger is None else self._logger.info(m)

        if write_gaussian:
            now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            m = "\t\t 6. Write Conformers to Gaussian16 ({})\n".format(now)
            m += "\t\t\tInputfiles in {}_g16_conformers/ directory".format(pattern)
            print(m) if self._logger is None else self._logger.info(m)

            self.write_min_cluster_conformers_to_g16(localdir, pattern, conformerPropsDict, lowest_conf_id,
                                                     g16_nproc, g16_mem, g16_key, charge, multiplicity)

        m = "\t\t**************** GENERATE CONFORMERS ***************\n"
        print(m) if self._logger is None else self._logger.info(m)

        m = "\n\t\t**************** CONFORMER MM ENERGIES ***************\n"
        m += "\t\t\tCluster Conformer_ID  {}_energy(kcal/mol)  Relative_energy(kcal/mol)\n".format(ff_name)
        m += "\t\t\t--------------------------------------------------------------------\n"
        icluster = 1
        for iconf in lowest_conf_id:
            m += "\t\t\t {0:^5d}  {1:^12d}  {2:^12.2f}  {3:^24.2f}\n".\
                format(icluster, iconf, conformerPropsDict[iconf]["energy_abs"],
                       conformerPropsDict[iconf]["energy_abs"]-minEnergy)
            icluster += 1
        m += "\t\t**************** CONFORMER MM ENERGIES ***************\n"
        print(m) if self._logger is None else self._logger.info(m)

    # =========================================================================
    def get_type_atoms(self, ff_name="MMFF", fileimg=None):

        """
        Get Atom Types. The atom types cannot be determined for UFF force field.

        Args:
            ff_name (str): Name of the force field (Allowed values: "UFF", "MMFF").
            fileimg (str): If not None, a 2D image file with the atom type is generated.

        Returns:
            Returns a dictionary --> d[iatom] = itype

        """

        RDLogger.DisableLog('rdApp.*')

        dtype = defaultdict(int)

        molprops = None
        if ff_name == "MMFF":
            molprops = rdkit.Chem.AllChem.MMFFGetMoleculeProperties(self.mol_rdkit)
        elif ff_name == "UFF":
            rdkit.Chem.AllChem.UFFGetMoleculeForceField(self.mol_rdkit)
            m = "\t\tForce Field types for UFF cannot be determined in RDKIT"
            print(m) if self._logger is None else self._logger.info(m)
            return dtype

        # Get AtomTypes
        natoms = self.mol_rdkit.GetNumAtoms()
        for idx in range(natoms):
            itype = molprops.GetMMFFAtomType(idx)
            dtype[idx] = itype

        if fileimg is not None:
            s1 = rdkit.Chem.rdmolfiles.MolToSmiles(self.mol_rdkit)
            m = rdkit.Chem.MolFromSmiles(s1)
            rdkit.Chem.Draw.MolToFile(m, fileimg, size=(300, 300))

        return dtype

    # =========================================================================
    def get_bonds(self):

        """
        Get self._bond_list
        """

        return self._bond_list

    # =========================================================================
    def get_elements(self):

        """
        Get self._elements
        """

        return self._elements

    # =========================================================================
    def get_order_bonds(self):

        """
        Get order bonds from the self._mol_rdkit attribute.

        Returns:
            A list containing order bonds for each atom.
        """

        bl = []
        index_bond = 0
        for item in self.mol_rdkit.GetBonds():
            iat1 = item.GetBeginAtomIdx()
            iat2 = item.GetEndAtomIdx()
            b = self.mol_rdkit.GetBondBetweenAtoms(iat1, iat2)
            bo = b.GetBondTypeAsDouble()
            bl.append(bo)
            index_bond += 1

        return bl

    # =========================================================================
    def mm_calc_energy(self, conf_id, ff_name="MMFF", minimize_iterations=0):

        """
        Calculate the energy and optionally optimize the geometry using a
        Molecular Modeling (MM) model implemented in RDKIT (if minimize_iterations>0).

        Args:
            conf_id (int): Index of the conformation to calculate (optimize) energy.
            ff_name (str): Name of the force field. Accepted values ("MMFF", "UFF").
            minimize_iterations (int): Maximum number of iterations to optimize the conformer.

        Returns:
            A dictionary.

                results['converged'] : if 0 the structure is not converged.
                results['energy_abs'] : Energy of the optimized structure in kcal/mol.


        """

        RDLogger.DisableLog('rdApp.*')

        ff = None
        if ff_name == "MMFF":
            molprops = rdkit.Chem.AllChem.MMFFGetMoleculeProperties(self.mol_rdkit)
            ff = rdkit.Chem.AllChem.MMFFGetMoleculeForceField(self.mol_rdkit,
                                                              molprops,
                                                              confId=conf_id)
        elif ff_name == "UFF":
            if rdkit.Chem.AllChem.UFFHasAllMoleculeParams(self.mol_rdkit):
                ff = rdkit.Chem.AllChem.UFFGetMoleculeForceField(self.mol_rdkit,
                                                                 confId=conf_id)
            else:  # If not parameters use MMFF
                molprops = rdkit.Chem.AllChem.MMFFGetMoleculeProperties(self.mol_rdkit)
                ff = rdkit.Chem.AllChem.MMFFGetMoleculeForceField(self.mol_rdkit,
                                                                  molprops,
                                                                  confId=conf_id)

        ff.Initialize()
        ff.CalcEnergy()
        results = {}
        if minimize_iterations > 0:
            results["converged"] = ff.Minimize(maxIts=minimize_iterations)
        results["energy_abs"] = ff.CalcEnergy()

        return results

    # =========================================================================
    def set_bonds(self):

        """
        Setup self._bond_list

        """

        self._bond_list = []
        try:
            for item in self.mol_rdkit.GetBonds():
                iat1 = item.GetBeginAtomIdx()
                iat2 = item.GetEndAtomIdx()
                if iat1 < iat2:
                    self._bond_list.append([iat1, iat2])
                else:
                    self._bond_list.append([iat2, iat1])
        except AttributeError:
            pass

    # =========================================================================
    def set_elements(self):

        """
        Setup self._elements

        """

        self._elements = {}

        try:
            for iatom in self.mol_rdkit.GetAtoms():
                self._elements[iatom.GetIdx()] = iatom.GetSymbol()
        except AttributeError:
            pass

    # =========================================================================
    def set_get_formal_charge(self, filename):

        """
        Get formal charge for each atom. Set formal charge in self._atom_formal_charges
        This function modifies ``self._atom_formal_charges``

        Args:
            filename: Name of the file, PDB

        """

        new_chg_line = []
        with open(filename, 'r') as fin:
            if os.path.splitext(filename)[-1] == ".pdb":
                idx_atom = 1
                while True:
                    line = fin.readline()
                    if line.find("ATOM") != -1 or line.find("HETATM") != -1:
                        charge = line[78:80].strip()
                        if charge:
                            signs = ["+", "-"]
                            if charge[0] in signs:
                                chg = "{0:3s} {1:1s}{2:1s}".format(str(idx_atom), str(charge[0]), str(charge[1]))
                                s = str(charge[0])
                                c = int(charge[1])
                            else:
                                chg = "{0:3s} {1:1s}{2:1s}".format(str(idx_atom), str(charge[1]), str(charge[0]))
                                s = str(charge[1])
                                c = int(charge[0])
                            new_chg_line.append("{}".format(chg))
                            if s == "+":
                                self._atom_formal_charges.append(c)
                            else:
                                self._atom_formal_charges.append(-c)
                        else:
                            self._atom_formal_charges.append(0)
                    idx_atom += 1
                    if not line:
                        break
            # elif os.path.splitext(filename)[-1] == ".mol2":
            #     while True:
            #         line = fin.readline()
            #         if line.find("@<TRIPOS>MOLECULE") != -1:
            #             line = fin.readline()
            #             line = fin.readline()
            #             natoms = line.split()[0]

    # =========================================================================
    def write_all_conformers_to_pdb(self, filename):

        """
        Write all conformers in PDB trajectory

        Args:
            filename: Name of the file, PDB

        """

        rdkit.Chem.rdmolfiles.MolToPDBFile(self.mol_rdkit, filename)

    # =========================================================================
    def write_min_cluster_conformers_to_g16(self, localdir, pattern, conformer_props_dict,
                                            lowest_conf_id, nproc, mem, g16_key, charge, mult):

        """
        Write the lowest-energy conformer for each cluster conformers in Gaussian format. The function creates
        input files with the folowing format ``{pattern}_{conformer_id}_gaussian.com``

        Args:
            localdir(str): local directory.
            pattern (str): Pattern for the name of the inout gaussian file.
            conformer_props_dict (dict): It contains the information for all conformers.
            lowest_conf_id (list): Indices for the lowest-energy conformer in each cluster. The length of this list
                is the number of clusters.
            nproc (int): Number of processes to be used in gaussian16.
            mem (int): Memory in Mb to be used in gaussian16.
            g16_key (str): Keywords to be used in gaussian16.
            charge (int): Charge of the molecule.
            mult (int): Spin multiplicity.

        """

        # Get element list
        elem = []
        for iatom in self.mol_rdkit.GetAtoms():
            elem.append(iatom.GetSymbol())

        # Create directory for gaussian inputs
        parent_dir = os.path.join(localdir, "{}".format("{}_g16_conformers/").format(pattern))
        if not os.path.isdir(parent_dir):
            os.mkdir(parent_dir)

        # Write gaussian input for each conformer
        for iconf in lowest_conf_id:
            coords = self.mol_rdkit.GetConformer(iconf).GetPositions()
            energy = conformer_props_dict[iconf]['energy_abs']
            fname = "{0:s}_{1:03d}_gaussian.com".format(pattern, iconf)
            fchk_name = "{0:s}_{1:03d}_gaussian.chk".format(pattern, iconf)
            with open(parent_dir+fname, 'w') as f:
                f.writelines("%chk={}\n".format(fchk_name))
                f.writelines("%nproc={}\n".format(nproc))
                f.writelines("%mem={}Mb\n".format(mem))
                f.writelines("{}\n".format(g16_key))
                f.writelines("\nConformer number {0:03d}. Energy MM = {1:.3f} kcal/mol\n".format(iconf, energy))
                f.writelines("\n")
                f.writelines("{0:1d} {1:1d}\n".format(charge, mult))
                for idx_at in range(len(elem)):
                    line = "{0:s}  {1:<6.4f}    {2:>6.4f}    {3:>6.4f}\n".format(elem[idx_at], coords[idx_at][0],
                                                                                 coords[idx_at][1], coords[idx_at][2])
                    f.writelines(line)
                f.writelines("\n")

    # =========================================================================
    def write_min_cluster_conformers_to_pdb(self, filename, rms_cluster, conformer_props_dict):

        """
        Write the conformer of minimum energy for each cluster in PDB trajectory

        Args:
            filename (str): Name of the PDB file
            rms_cluster (tuple): A tuple of tuples containing information about the cluster
            conformer_props_dict (dict): Properties for each cluster

        Returns:
            A list containing the index of the lowest-energy conformer for each cluster

        """

        conf_id_list = []
        w = rdkit.Chem.PDBWriter(filename, flavor=16)
        idx_min_cluster = 9999999999999
        for cluster in rms_cluster:
            e_min_cluster = 9999999999999999
            for conf_id in cluster:
                conformerProps = conformer_props_dict[conf_id]
                e = conformerProps["energy_abs"]
                if e < e_min_cluster:
                    e_min_cluster = e
                    idx_min_cluster = conf_id
            w.write(self.mol_rdkit, confId=idx_min_cluster)
            conf_id_list.append(idx_min_cluster)

        w.flush()
        w.close()

        return conf_id_list
