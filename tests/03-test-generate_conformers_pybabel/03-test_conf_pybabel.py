import unittest
import datetime
import utils
import gecos
import os
import numpy as np


# noinspection PyUnresolvedReferences
class GecosPyBabelTests(unittest.TestCase):

    # ##################################################################################################################
    @classmethod
    def setUpClass(cls):

        cls.filelog = "test03_gecos_pybabel_test.log"
        cls.log = utils.init_logger("Output", fileoutput=cls.filelog, append=False, inscreen=False)
        m = "\n\t***************** START Gecos PyBabel TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tStarting: \t {}\n".format(now))

    # ##################################################################################################################
    def test_01_basic_dimer_PI(self):

        """
          Test Gecos for Dimer polyisoprene
        """

        m = "\tTest_01: Check PDB and MOL2 files from MS. Neutral and not resonance. Dimer polyisoprene"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # Both files were prepared with Materials Studio. The order atom is the same in both files
        pdbfile = "../../data/IsoP.pdb"
        mol2file = "../../data/IsoP.mol2"

        # ============= GET INSTANCES =============
        g1_pdb_ms = gecos.GecosPyBabel(pdbfile, logger=self.log)
        g1_mol2_ms = gecos.GecosPyBabel(mol2file, logger=self.log)

        self.assertIsNotNone(g1_pdb_ms._mol_pybabel)
        self.assertIsNotNone(g1_mol2_ms._mol_pybabel)

        # ============= CALC ENERGY =============
        e1 = g1_pdb_ms._mm_calc_energy(ff_name="MMFF")
        e2 = g1_pdb_ms._mm_calc_energy(ff_name="UFF")
        e3 = g1_pdb_ms._mm_calc_energy(ff_name="Gaff")
        m  = "\t\tEnergy (MMFF)  PDB  : {0:>10.3f} kcal/mol\n".format(e1)
        m += "\t\tEnergy (UFF)   PDB  : {0:>10.3f} kcal/mol\n".format(e2)
        m += "\t\tEnergy (GAFF)  PDB  : {0:>10.3f} kcal/mol\n".format(e3)
        print(m) if self.log is None else self.log.info(m)

        e1 = g1_mol2_ms._mm_calc_energy(ff_name="MMFF")
        e2 = g1_mol2_ms._mm_calc_energy(ff_name="UFF")
        e3 = g1_mol2_ms._mm_calc_energy(ff_name="Gaff")
        m  = "\t\tEnergy (MMFF)  MOL2 : {0:>10.3f} kcal/mol\n".format(e1)
        m += "\t\tEnergy (UFF)   MOL2 : {0:>10.3f} kcal/mol\n".format(e2)
        m += "\t\tEnergy (GAFF)  MOL2 : {0:>10.3f} kcal/mol\n".format(e3)
        print(m) if self.log is None else self.log.info(m)

    # ##################################################################################################################
    def test_02_genconf_dimer_PI(self):

            """
              Test Gecos for Dimer polyisoprene
            """

            m = "\tTest_02: Generate conformers for dimer isoprene"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/IsoP.pdb"
            mol2file = "../../data/IsoP.mol2"

            # ============= GET INSTANCES =============
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, logger=self.log)
            g1_mol2_ms = gecos.GecosPyBabel(mol2file, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "MMFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="IsoP_mmff",
                                                minimize_iterations=5000, out_format="xyz")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="IsoP_uff",
                                                minimize_iterations=5000, out_format="xyz")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

            ffname = "UFF"
            res = g1_mol2_ms.generate_conformers(ff_name=ffname, pattern="IsoP_uff",
                                                 minimize_iterations=5000, out_format="mol2")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

    # ##################################################################################################################
    def test_03_genconf_nitrobenzene(self):

            """
              Test Gecos for nitrobenzene
            """

            m = "\tTest_03: Generate conformers for nitrobenzene"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/nitrobenzene.pdb"

            # ============= GET INSTANCES =============
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "MMFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="nitrobenzene_mmff",
                                                minimize_iterations=5000, out_format="xyz")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="nitrobenzene_uff", rmsd_cutoff_confab=0.1,
                                                minimize_iterations=5000, out_format="xyz")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

    # ##################################################################################################################
    def test_04_genconf_PS(self):

            """
              Test Gecos for PS dimer
            """

            m = "\tTest_04: Generate conformers for a dimer styrene"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/AtacPS.pdb"

            # ============= GET INSTANCES =============
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "MMFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="AtacPS_mmff",
                                                minimize_iterations=5000, out_format="xyz")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(ff_name=ffname, pattern="AtacPS_uff", rmsd_cutoff_confab=0.5,
                                                minimize_iterations=5000, out_format="mol2")
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)


    # # ##################################################################################################################
    # def test_05_genconf_PET(self):
    #
    #         """
    #           Test Gecos for PET dimer
    #         """
    #
    #         m = "\tTest_05: Generate conformers for a dimer PET"
    #         print(m) if self.log is None else self.log.info(m)
    #         datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    #
    #         # Both files were prepared with Materials Studio. The order atom is the same in both files
    #         pdbfile = "../../data/PET.pdb"
    #
    #         # ============= GET INSTANCES =============
    #         g1_pdb_ms = gecos.GecosPyBabel(pdbfile, logger=self.log)
    #
    #         # ============= GENERATE CONFORMERS =============
    #         ffname = "MMFF"
    #         res = g1_pdb_ms._generate_conformers(ff_name=ffname, pattern="PET_mmff", rmsd_cutoff=1.0,
    #                                              minimize_iterations=5000, out_format="xyz")
    #         if res is None:
    #             m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
    #             m += "\t\tNo conformer is generated".format(pdbfile, ffname)
    #             print(m) if self.log is None else self.log.warning(m)
    #
    #         ffname = "UFF"
    #         res = g1_pdb_ms._generate_conformers(ff_name=ffname, pattern="PET_uff", rmsd_cutoff=0.5,
    #                                              minimize_iterations=5000, out_format="xyz")
    #         if res is None:
    #             m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
    #             m += "\t\tNo conformer is generated".format(pdbfile, ffname)
    #             print(m) if self.log is None else self.log.warning(m)



    # ##################################################################################################################
    @classmethod
    def tearDownClass(cls):

        m = "\n\t***************** END Gecos PyBabel TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tFinishing: \t {}\n".format(now))
