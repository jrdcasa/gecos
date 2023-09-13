import glob
import os.path
import unittest
import datetime
import utils
import gecos
import rdkit.Chem
import shutil


class GecosRdkitTests(unittest.TestCase):

    # ##################################################################################################################
    @classmethod
    def setUpClass(cls):

        # Delete files and directories from prevoius tests
        path_test01 = os.getcwd()
        shutil.rmtree(os.path.join(path_test01, "IsoP_g16_results"), ignore_errors=True)
        shutil.rmtree(os.path.join(path_test01, "nitrobenzene_g16_results"), ignore_errors=True)
        shutil.rmtree(os.path.join(path_test01, "nitrobenzene_sdf_g16_results"), ignore_errors=True)
        shutil.rmtree(os.path.join(path_test01, "PET_g16_results"), ignore_errors=True)
        files_to_remove = glob.glob(os.path.join(path_test01, "*.pdb"))
        files_to_remove += glob.glob(os.path.join(path_test01, "*.sdf"))
        for ifile in files_to_remove:
            os.remove(os.path.join(path_test01, ifile))

        cls.filelog = "test01_gecos_rdkit_test.log"
        cls.log = utils.init_logger("Output", fileoutput=cls.filelog, append=False, inscreen=False)
        m = "\n\t***************** START Gecos rdkit TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tStarting: \t {}\n".format(now))

    # ##################################################################################################################
    def test_01_createGecosRdKit(self):

        """
        Try to use GecosRdkit class

        """

        try:
            gecos.GecosRdkit()
            m = "\tTest_01: The class GecosRdkit is correctly imported\n"
            m += "\t\tTest_01: --> SUCCESS\n"
        except AttributeError:
            m = "\tTest_01: The class GecosRdkit cannot be imported\n"
            m += "\t\tTest_01: --> FAILED\n"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # ##################################################################################################################
    def test_02_readmolRdKit(self):

        """
        Read PDB and MOL2 files from RdKit
        """

        m = "\tTest_02: Check read PDB and MOL2 with RdKit"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # These files were exported from MaterialsStudio2019.
        # This molecule conatins 28 atoms, 10Cs and 18Hs
        pdbfile = "../../data/IsoP.pdb"
        mol2file = "../../data/IsoP.mol2"

        # Load PDB -> On failure returns a None object
        molpdb = rdkit.Chem.rdmolfiles.MolFromPDBFile(pdbfile, removeHs=False)
        self.assertIsNotNone(molpdb)

        # Load Mol2 -> On failure returns a None object
        molmol2 = rdkit.Chem.rdmolfiles.MolFromMol2File(mol2file, removeHs=False)
        self.assertIsNotNone(molmol2)

        l_pdb = []
        l_mol2 = []
        for atom in molpdb.GetAtoms():
            l_pdb.append(atom.GetSymbol())

        for atom in molmol2.GetAtoms():
            l_mol2.append(atom.GetSymbol())

        # Test that there are 28 atoms in the molecules
        self.assertEqual(len(l_pdb), 28)
        self.assertEqual(l_pdb.count('C'), 10)
        self.assertEqual(l_pdb.count('H'), 18)
        self.assertEqual(len(l_mol2), 28)
        self.assertEqual(l_mol2.count('C'), 10)
        self.assertEqual(l_mol2.count('H'), 18)

        # PDB does not contains information about bond order
        l_bonds = []
        for ibond in molpdb.GetBonds():
            l_bonds.append(ibond.GetBondType())

        self.assertEqual(l_bonds.count(rdkit.Chem.rdchem.BondType.SINGLE), len(molpdb.GetBonds()))

        # MOL2 format  contains information about bond order
        l_bonds = []
        for ibond in molmol2.GetBonds():
            l_bonds.append(ibond.GetBondType())

        self.assertEqual(l_bonds.count(rdkit.Chem.rdchem.BondType.DOUBLE), 2)

        if molpdb is None or molmol2 is None:
            m = "\t\tPDB and/or mol2 file cannot be read by Rdkit\n"
            m += "\t\tPDF File: {}\n".format(pdbfile)
            m += "\t\tMOL2 File: {}\n".format(mol2file)
            m += "\t\tTest_02 --> FAILED\n"
        else:
            m = "\t\tTest_02 --> SUCCESS\n"
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_03_GecosRdKit_bondperception_aromatic(self):

        """
        Bond perception with aromatic of PDB file using indigoX program
        """

        m = "\tTest_04: Bond perception with aromatic for PDB file"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # These files were exported from MaterialsStudio2019.
        # This molecule conatins 28 atoms, 10Cs and 18Hs
        pdbfile = "../../data/nitrobenzene.pdb"

        # Load pdb without bond perception raise a WARNING message
        g1 = gecos.GecosRdkit(filename=pdbfile, logger=None)
        order_bonds_g1 = g1.get_order_bonds()
        bo_real = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.assertListEqual(order_bonds_g1, bo_real)

        # Load pdb with bond perception
        g2 = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        order_bonds_g2 = g2.get_order_bonds()
        bond_list_g2 = g2.get_bonds()
        elements_g2 = g2.get_elements()
        bl_real = [[0, 1], [0, 5], [0, 6], [1, 2], [1, 7], [2, 3], [2, 8], [3, 4],
                   [3, 11], [4, 5], [4, 9], [5, 10], [11, 12], [11, 13]]
        self.assertListEqual(bond_list_g2, bl_real)
        bo_real = [1.5, 1.5, 1.0, 1.5, 1.0, 1.5, 1.0, 1.5, 1.0, 1.5, 1.0, 1.0, 1.0, 2.0]
        self.assertListEqual(order_bonds_g2, bo_real)
        e_real = {0: 'C', 1: 'C', 2: 'C', 3: 'C', 4: 'C', 5: 'C', 6: 'H', 7: 'H',
                  8: 'H', 9: 'H', 10: 'H', 11: 'N', 12: 'O', 13: 'O'}
        self.assertDictEqual(elements_g2, e_real)

        m = "\t\tTest_04 --> SUCCESS\n"
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_04_GecosRdKit_conformers(self):

        """
         Conformer generation
        """

        m = "\tTest_05: Conformer generation for PDB file."
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # These files were exported from MaterialsStudio2019.
        # This molecule contains 28 atoms, 10Cs and 18Hs
        pdbfile = "../../data/IsoP.pdb"
        g1 = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g1.generate_conformers("./", nconfs=50, minimize_iterations=3000, pattern="IsoP")

        pdbfile = "../../data/nitrobenzene.pdb"
        g2 = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g2.generate_conformers("./", nconfs=50, minimize_iterations=2000, pattern="nitrobenzene", ff_name="MMFF")

        sdffile = "../../data/nitrobenzene.sdf"
        g3 = gecos.GecosRdkit(filename=sdffile, bond_perception=False, logger=self.log)
        g3.generate_conformers("./", nconfs=50, minimize_iterations=2000, pattern="nitrobenzene_sdf", ff_name="MMFF")

        pdbfile = "../../data/PET.pdb"
        g4 = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=self.log)
        g4.generate_conformers("./", nconfs=50, minimize_iterations=2000, pattern="PET", ff_name="MMFF")

        pass

    # ##################################################################################################################
    def test_05_pdbtosdf(self):

        """
          PDB to SDF file
        """

        m = "\tTest_06: Convert PDB to SDF file"
        print(m) if self.log is None else self.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        pdbfile = "../../data/nitrobenzene.pdb"

        utils.pdbtosdf(pdbfile)

        self.assertTrue(os.path.isfile("nitrobenzene_frompdb.sdf"))

    # ##################################################################################################################
    @classmethod
    def tearDownClass(cls):

        m = "\n\t***************** END Gecos rdkit TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tFinishing: \t {}\n".format(now))
