import unittest
import datetime
import utils
import gecos
import os
import numpy as np


# noinspection PyUnresolvedReferences
class GecosRdkitTests(unittest.TestCase):

    # ##################################################################################################################
    @classmethod
    def setUpClass(cls):

        cls.filelog = "test02_gecos_rdkit_test.log"
        cls.log = utils.init_logger("Output", fileoutput=cls.filelog, append=False, inscreen=False)
        m = "\n\t***************** START Gecos rdkit TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tStarting: \t {}\n".format(now))

    # ##################################################################################################################
    def test_01_dimer_PI(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_01: Check PDB and MOL2 files from MS. Neutral and not resonance. Dimer polyisoprene"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/IsoP.pdb"
        mol2file = "../../data/IsoP.mol2"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_mol2_ms = gecos.GecosRdkit(filename=mol2file, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_mol2_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())
        elem_g2 = []
        for iatom in g2_mol2_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])
        l_bonds_g2 = []
        for ibond in g2_mol2_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_mol2_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(mol2file)[-1]+".png"
        d2 = g2_mol2_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_mol2_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_02_nitrobenzene(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_02: Check PDB and MOL2 files from MS. Neutral and resonance. Nitrobenzene"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/nitrobenzene.pdb"
        mol2file = "../../data/nitrobenzene.mol2"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_mol2_ms = gecos.GecosRdkit(filename=mol2file, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_mol2_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            if iatom.GetIdx() == 11:
                self.assertEqual(iatom.GetFormalCharge(), 1)
            elif iatom.GetIdx() == 12:
                self.assertEqual(iatom.GetFormalCharge(), -1)
            else:
                self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_mol2_ms.mol_rdkit.GetAtoms():
            if iatom.GetIdx() == 11:
                self.assertEqual(iatom.GetFormalCharge(), 1)
            elif iatom.GetIdx() == 12:
                self.assertEqual(iatom.GetFormalCharge(), -1)
            else:
                self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])
        l_bonds_g2 = []
        for ibond in g2_mol2_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_mol2_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(mol2file)[-1]+".png"
        d2 = g2_mol2_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_mol2_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_03_dimer_PS(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_03: Check PDB and MOL2 files from MS. Neutral and resonance. Dimer PS"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/AtacPS.pdb"
        mol2file = "../../data/AtacPS.mol2"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_mol2_ms = gecos.GecosRdkit(filename=mol2file, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_mol2_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_mol2_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])
        l_bonds_g2 = []
        for ibond in g2_mol2_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_mol2_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(mol2file)[-1]+".png"
        d2 = g2_mol2_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_mol2_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_04_dimer_PET(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_04: Check PDB and MOL2 files from MS. Neutral and resonance. Dimer PET"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # PDB file were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/PET_ms.pdb"
        # PDB file were prepared with GaussView.
        mol2file = "../../data/PET_gview.mol2"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_mol2_ms = gecos.GecosRdkit(filename=mol2file, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_mol2_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_mol2_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])

        l_bonds_g2 = []
        for ibond in g2_mol2_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(mol2file)[-1]+".png"
        d2 = g2_mol2_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_mol2_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_mol2_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_05_pdbtosdf_dimer_PI(self):

        """
          PDB to SDF file
        """

        m = "\tTest_05: PDB to PSF. Dimer polyisoprene"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # The file was prepared with Materials Studio.
        pdbfile = "../../data/IsoP.pdb"
        utils.pdbtosdf(pdbfile)
        sdffile = "../../data/IsoP_frompdb.sdf"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_sdf_ms = gecos.GecosRdkit(filename=sdffile, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_sdf_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_sdf_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])

        l_bonds_g2 = []
        for ibond in g2_sdf_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_sdf_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(sdffile)[-1]+".png"
        d2 = g2_sdf_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_sdf_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) SDF  : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  SDF  : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_06_pdbtosdf_nitrobenzene(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_06: PDB to PSF. Nitrobenzene"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/nitrobenzene.pdb"
        utils.pdbtosdf(pdbfile)
        sdffile = "../../data/nitrobenzene_frompdb.sdf"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_sdf_ms = gecos.GecosRdkit(filename=sdffile, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_sdf_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            if iatom.GetIdx() == 11:
                self.assertEqual(iatom.GetFormalCharge(), 1)
            elif iatom.GetIdx() == 12:
                self.assertEqual(iatom.GetFormalCharge(), -1)
            else:
                self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_sdf_ms.mol_rdkit.GetAtoms():
            if iatom.GetIdx() == 11:
                self.assertEqual(iatom.GetFormalCharge(), 1)
            elif iatom.GetIdx() == 12:
                self.assertEqual(iatom.GetFormalCharge(), -1)
            else:
                self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])
        l_bonds_g2 = []
        for ibond in g2_sdf_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_sdf_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(sdffile)[-1]+".png"
        d2 = g2_sdf_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_sdf_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) SDF  : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  SDF  : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_07_pdbtosdf_dimer_PS(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_07: PDB to PSF. Dimer PS"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/AtacPS.pdb"
        utils.pdbtosdf(pdbfile)
        sdffile = "../../data/AtacPS_frompdb.sdf"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_sdf_ms = gecos.GecosRdkit(filename=sdffile, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_sdf_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_sdf_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])
        l_bonds_g2 = []
        for ibond in g2_sdf_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_sdf_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(sdffile)[-1]+".png"
        d2 = g2_sdf_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_sdf_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_08_pdbtosdf_dimer_PET(self):

        """
          Test Gecos for Dimer polyisoprene
        """
        m = "\tTest_08: PDB to PSF. Dimer PET"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/PET.pdb"
        utils.pdbtosdf(pdbfile)
        sdffile = "../../data/PET_frompdb.sdf"

        # Create GecosRdKit objects
        g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2_sdf_ms = gecos.GecosRdkit(filename=sdffile, bond_perception=False, logger=self.log)

        # ============= MOL =============
        # Assert rdkit molecule
        self.assertIsNotNone(g1_pdb_ms.mol_rdkit)
        self.assertIsNotNone(g2_sdf_ms.mol_rdkit)

        # ============= ATOM =============
        # Check formal charges of all atoms (G1 and G2)
        elem_g1 = []
        for iatom in g1_pdb_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g1.append(iatom.GetSymbol())

        elem_g2 = []
        for iatom in g2_sdf_ms.mol_rdkit.GetAtoms():
            self.assertEqual(iatom.GetFormalCharge(), 0)
            elem_g2.append(iatom.GetSymbol())

        # Check name of the atoms
        self.assertListEqual(elem_g1, elem_g2)

        # ============= BONDS =============
        # Check bonds
        l_bonds_g1 = []
        for ibond in g1_pdb_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            l_bonds_g1.append([iat, jat, bo])

        l_bonds_g2 = []
        for ibond in g2_sdf_ms.mol_rdkit.GetBonds():
            iat = ibond.GetBeginAtomIdx()
            jat = ibond.GetEndAtomIdx()
            bo = ibond.GetBondType()
            # Usually, MOL2 doesn't call bond_perception, so the bonds can be disordered
            if iat < jat:
                l_bonds_g2.append([iat, jat, bo])
            else:
                l_bonds_g2.append([jat, iat, bo])

        self.assertListEqual(sorted(l_bonds_g1), sorted(l_bonds_g2))

        # ============= TEST POSITIONS =============
        coords1 = None
        coords2 = None
        for c in g1_pdb_ms.mol_rdkit.GetConformers():
            coords1 = c.GetPositions()

        for c in g2_sdf_ms.mol_rdkit.GetConformers():
            coords2 = c.GetPositions()

        # Coordinates are equal
        np.testing.assert_almost_equal(coords1, coords2, decimal=3)

        # # ============= TEST ATOM TYPE MMFF FORCE FIELDS =============
        fname = os.path.split(pdbfile)[-1]+".png"
        d1 = g1_pdb_ms.get_type_atoms(fileimg=fname)
        fname = os.path.split(sdffile)[-1]+".png"
        d2 = g2_sdf_ms.get_type_atoms(fileimg=fname)

        self.assertDictEqual(d1, d2)

        # ============= CALC ENERGY =============
        g1_conformers = g1_pdb_ms.mol_rdkit.GetNumConformers()
        g2_conformers = g2_sdf_ms.mol_rdkit.GetNumConformers()
        self.assertEqual(g1_conformers, g2_conformers)

        # MMFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="MMFF", minimize_iterations=0)
        m = "\t\tEnergy (MMFF) PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (MMFF) MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        # UFF energy
        e1 = g1_pdb_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        e2 = g2_sdf_ms.mm_calc_energy(0, ff_name="UFF", minimize_iterations=0)
        m += "\t\tEnergy (UFF)  PDB  : {0:.3f} kcal/mol\n".format(e1['energy_abs'])
        m += "\t\tEnergy (UFF)  MOL2 : {0:.3f} kcal/mol\n".format(e2['energy_abs'])
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_09_bondperception_mol2(self):

        """
          Test Gecos for Dimer polyisoprene
        """
        m = "\tTest_09: MOL2 Dimer PET. Bond perception."
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        mol2file = "../../data/PET_ob.mol2"

        # Create GecosRdKit objects
        g1_mol_ob = gecos.GecosRdkit(filename=mol2file, bond_perception=True, logger=self.log)

    # ##################################################################################################################
    @classmethod
    def tearDownClass(cls):

        m = "\n\t***************** END Gecos rdkit TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tFinishing: \t {}\n".format(now))
