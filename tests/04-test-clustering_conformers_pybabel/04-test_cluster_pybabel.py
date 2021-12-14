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

        cls.filelog = "test04_cluster_pybabel_test.log"
        cls.log = utils.init_logger("Output", fileoutput=cls.filelog, append=False, inscreen=False)
        m = "\n\t***************** START Gecos PyBabel TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tStarting: \t {}\n".format(now))


    # ##################################################################################################################
    def test_01_genconf_and_cluster_PS(self):

            """
              Test Gecos for PS dimer
            """

            m = "\tTest_01: Generate optimized conformers in format MOL2 for a dimer styrene. Clustering"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/AtacPS.pdb"

            # ============= GET INSTANCES =============
            exec_rmsddock = "/home/jramos/PycharmProjects/GeCos/thirdparty/dock_rmsd/dockrmsd.x"
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, exec_rmsddock=exec_rmsddock, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(localdir=".", ff_name=ffname, pattern="AtacPS_uff", rmsd_cutoff_confab=0.5,
                                                minimize_iterations=5000)
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

    # ##################################################################################################################
    def test_02_genconf_and_cluster_PET(self):

            """
              Test Gecos for PS dimer
            """

            m = "\tTest_02: Generate optimized conformers in format MOL2 for a dimer PET. Clustering"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/PET.pdb"

            # ============= GET INSTANCES =============
            exec_rmsddock = "/home/jramos/PycharmProjects/GeCos/thirdparty/dock_rmsd/dockrmsd.x"
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, exec_rmsddock=exec_rmsddock, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(localdir=".", ff_name=ffname, pattern="PET_uff", rmsd_cutoff_confab=0.5,
                                                minimize_iterations=5000)
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

    # ##################################################################################################################
    def test_03_genconf_and_cluster_IsoP(self):

            """
              Test Gecos for Isoprene dimer
            """

            m = "\tTest_02: Generate optimized conformers in format MOL2 for a dimer PET. Clustering"
            print(m) if self.log is None else self.log.info(m)
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Both files were prepared with Materials Studio. The order atom is the same in both files
            pdbfile = "../../data/IsoP.pdb"

            # ============= GET INSTANCES =============
            exec_rmsddock = "/home/jramos/PycharmProjects/GeCos/thirdparty/dock_rmsd/dockrmsd.x"
            g1_pdb_ms = gecos.GecosPyBabel(pdbfile, exec_rmsddock=exec_rmsddock, logger=self.log)

            # ============= GENERATE CONFORMERS =============
            ffname = "UFF"
            res = g1_pdb_ms.generate_conformers(localdir=".", ff_name=ffname, pattern="IsoP_uff", rmsd_cutoff_confab=0.5,
                                                minimize_iterations=5000)
            if res is None:
                m = "Conformers for {} cannot be generated ({}). Revise Force Field\n".format(pdbfile, ffname)
                m += "\t\tNo conformer is generated".format(pdbfile, ffname)
                print(m) if self.log is None else self.log.warning(m)

    # ##################################################################################################################
    @classmethod
    def tearDownClass(cls):

        m = "\n\t***************** END Gecos PyBabel TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tFinishing: \t {}\n".format(now))
