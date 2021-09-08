import unittest
import datetime
import utils
import gecos
import os


# noinspection PyUnresolvedReferences
class GecosPyBabelTests(unittest.TestCase):

    # ##################################################################################################################
    @classmethod
    def setUpClass(cls):

        cls.filelog = "test05_server_test.log"
        cls.log = utils.init_logger("Output", fileoutput=cls.filelog, append=False, inscreen=False)
        m = "\n\t***************** START Server Slurm TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tStarting: \t {}\n".format(now))

    # ##################################################################################################################
    # def test_01_check_remote_server(self):
    #
    #     """
    #     Test remote server connection
    #     """
    #
    #     m = "\tTest_01: Check remote server"
    #     print(m) if self.log is None else self.log.info(m)
    #     datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    #
    #     nameserver = "trueno.csic.es"
    #     qm_package = "gaussian"
    #     databasename = "{}_sp.db".format(qm_package)
    #     username = "jramos"
    #     keyfile = '/home/jramos/.ssh/id_rsa_chiripa'
    #
    #     server = utils.ServerSlurmBasic(nameserver, databasename, username,
    #                                     keyfile, logger=self.log)
    #     server.connection(self.log)
    #
    #     out, err = server.execute_cmd('hostname -s')
    #
    #     if "trueno-login" in out:
    #         o = True
    #     else:
    #         o = False
    #
    #     self.assertTrue(o)
    #     self.assertEqual(err, '')
    #
    #     server.close_connection()

    # # ##################################################################################################################
    # def test_02_send_gaussian_remote_server(self):
    #
    #     """
    #     Test send jobs to remote server
    #     """
    #
    #     m = "\tTest_02: Send Gaussian Remote Server"
    #     print(m) if self.log is None else self.log.info(m)
    #     datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    #
    #     # =================== INPUTS NEEDED ==========================
    #     # Server options
    #     nameserver = "trueno.csic.es"
    #     username = "jramos"
    #     g16_key = "#p opt=loose m062x/6-31g(d,p)"
    #     partition = "simacro"
    #     exclude_nodes = ["trueno36", "trueno37", "trueno38", "trueno59"]
    #     nodemaster = 'trueno36'
    #     partitionmaster = partition
    #     # Directories info
    #     pattern = "IsoP_rdkit"
    #     keyfile = '/home/jramos/.ssh/id_rsa_chiripa'
    #     localdir = '/home/jramos/PycharmProjects/GeCos/tests/05-test-server_slurm_02/'
    #     remotedir = '/home/cfmac/jramos/GECOS/test-05/'
    #     databasename = "{}_01_sp.db".format(pattern)
    #     cutoff_rmsd_QM = 1.0  # angstroms
    #     # Gaussian stuffs
    #     g16_nproc = 6
    #     g16_mem = 4000  # Mb
    #     # Logger
    #     filelog = "test05_02_send_gaussian_remote_server.log"
    #     # RMSD Dock executable
    #     exec_rmsddock = "/home/jramos/PycharmProjects/GeCos/thirdparty/dock_rmsd/dockrmsd.x"
    #
    #
    #     # Initial structure
    #     pdbfile = "/home/jramos/PycharmProjects/GeCos/data/IsoP.pdb"
    #     # =================== INPUTS NEEDED ==========================
    #
    #     if not os.path.isfile(databasename):
    #         log = utils.init_logger("Output2", fileoutput=filelog, append=False, inscreen=False)
    #         # Send qm conformers to remote server
    #         # Generate conformers with RdKit package
    #         g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=log)
    #         g1_pdb_ms.generate_conformers(localdir, nconfs=50, minimize_iterations=3000, pattern=pattern,
    #                                       g16_key=g16_key, g16_nproc=g16_nproc, g16_mem=g16_mem)
    #         # Refine conformers with QM methods.
    #         gecos.send_qm_conformers(nameserver, databasename, username,
    #                                  keyfile, localdir, remotedir,
    #                                  partition=partition, exclude_nodes=exclude_nodes, ncpus=g16_nproc,
    #                                  partitionmaster=partitionmaster, nodemaster=nodemaster,
    #                                  mem=g16_mem, logger=log)
    #     else:
    #         log = utils.init_logger("Output2", fileoutput=filelog, append=True, inscreen=False)
    #         outdir = localdir+pattern+"_g16_conformers"
    #         gecos.check_qm_jobs(nameserver, databasename, username,
    #                             keyfile, localdir, remotedir, outdir, pattern, exec_rmsddock,
    #                             cutoff_rmsd=cutoff_rmsd_QM, logger=log)
    #
    #     pass

    # ##################################################################################################################
    def test_03_send_gaussian_remote_server(self):

        """
        Test send jobs to remote server
        """

        m = "\tTest_03: Send Gaussian Remote Server"
        print(m) if self.log is None else self.log.info(m)
        datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # =================== INPUTS NEEDED ==========================
        # Server options
        nameserver = "trueno.csic.es"
        username = "jramos"
        g16_key = "#p opt=loose m062x/6-31g(d,p)"
        partition = "simacro"
        exclude_nodes = ["trueno36", "trueno37", "trueno38", "trueno59"]
        nodemaster = 'trueno36'
        partitionmaster = partition
        # Directories info
        pattern = "IsoP_rdkit_03"
        keyfile = '/home/jramos/.ssh/id_rsa_chiripa'
        localdir = '/home/jramos/PycharmProjects/GeCos/tests/05-test-server_slurm_03/'
        remotedir = '/home/cfmac/jramos/GECOS/test-05_03/'
        databasename = "{}_01_sp.db".format(pattern)
        cutoff_rmsd_QM = 1.0  # angstroms
        # Gaussian stuffs
        g16_nproc = 6
        g16_mem = 4000  # Mb
        # Logger
        filelog = "test05_03_send_gaussian_remote_server.log"
        # RMSD Dock executable
        exec_rmsddock = "/home/jramos/PycharmProjects/GeCos/thirdparty/dock_rmsd/dockrmsd.x"
        # Initial Number of conformers
        nconfs = 500
        minimize_iterations = 3000

        # Initial structure
        pdbfile = "/home/jramos/PycharmProjects/GeCos/data/IsoP.pdb"
        # =================== INPUTS NEEDED ==========================

        if not os.path.isfile(databasename):
            log = utils.init_logger("Output2", fileoutput=filelog, append=False, inscreen=False)
            # Send qm conformers to remote server
            # Generate conformers with RdKit package
            g1_pdb_ms = gecos.GecosRdkit(filename=pdbfile, bond_perception=True, logger=log)
            g1_pdb_ms.generate_conformers(localdir, nconfs=nconfs, minimize_iterations=minimize_iterations,
                                          pattern=pattern, g16_key=g16_key, g16_nproc=g16_nproc, g16_mem=g16_mem)
            # Refine conformers with QM methods.
            gecos.send_qm_conformers(nameserver, databasename, username,
                                     keyfile, localdir, remotedir,
                                     partition=partition, exclude_nodes=exclude_nodes, ncpus=g16_nproc,
                                     partitionmaster=partitionmaster, nodemaster=nodemaster,
                                     mem=g16_mem, logger=log)
        else:
            log = utils.init_logger("Output2", fileoutput=filelog, append=True, inscreen=False)
            outdir = localdir+pattern+"_g16_conformers"
            gecos.check_qm_jobs(nameserver, databasename, username,
                                keyfile, localdir, remotedir, outdir, pattern, exec_rmsddock,
                                cutoff_rmsd=cutoff_rmsd_QM, logger=log)

        pass

    # ##################################################################################################################
    @classmethod
    def tearDownClass(cls):

        m = "\n\t***************** END Server Slurm TEST *****************"
        print(m) if cls.log is None else cls.log.info(m)
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        cls.log.info("\t\tFinishing: \t {}\n".format(now))
