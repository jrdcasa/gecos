import os
import utils
import utils.gaussian16
import gecos

p_nameserver = 'totem'
p_username = 'jramos'
p_keysshfile = '/home/jramos/.ssh/id_rsa_localhost'
p_encrypt_pass = None
p_slurm_part = 'cpu'
p_list_nodes = ['']
p_slurm_part_master = 'cpu'
p_node_master = None
p_g16path = '/opt/g16/g16'
p_ncpus = 4
p_mem = 2000
p_charge = 0
p_multiplicity = 1
p_remotedir = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C001_EVOH_CCCOCC_localhost/01-CONF_RDKIT_REMOTE_PROP'
p_fileproplist = ['01-EVOH_049_gaussian_allign.mol2', '01-EVOH_704_gaussian_allign.mol2', '01-EVOH_670_gaussian_allign.mol2', '01-EVOH_368_gaussian_allign.mol2', '01-EVOH_866_gaussian_allign.mol2', '01-EVOH_930_gaussian_allign.mol2', '01-EVOH_078_gaussian_allign.mol2', '01-EVOH_027_gaussian_allign.mol2', '01-EVOH_905_gaussian_allign.mol2']
p_dockrmsdpack = '/home/jramos/PycharmProjects/sandbox_GeCos/lib/python3.8/site-packages/gecos-0.1-py3.8.egg/thirdparty/dockrmsd.x'
p_localdir = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C001_EVOH_CCCOCC_localhost/01-CONF_RDKIT_LOCAL_FREQ/'
p_localdir_mol2conf = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C001_EVOH_CCCOCC_localhost/01-CONF_RDKIT_LOCAL/01-EVOH_g16_conformers'
p_g16_keywords = '#p M062X/6-311G**   freq scale=0.987'
p_databasefullpath = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C001_EVOH_CCCOCC_localhost/01-CONF_RDKIT_LOCAL_FREQ/01-Freq.db'
p_fileoutputfullpath = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C001_EVOH_CCCOCC_localhost/01-CONF_RDKIT_LOCAL_FREQ/01-Freq.log'
p_pattern = 'FREQ'
p_dockrmsdpack = '/home/jramos/PycharmProjects/sandbox_GeCos/lib/python3.8/site-packages/gecos-0.1-py3.8.egg/thirdparty/dockrmsd.x'

if not os.path.isfile(p_databasefullpath):

    log = utils.init_logger(
        "Output3",
        fileoutput=p_fileoutputfullpath,
        append=False, inscreen=False)

    utils.print_header(log)

    utils.gaussian16.write_gaussian_from_mol2(
            p_fileproplist,
            p_localdir_mol2conf, 
            p_localdir, 
            pattern=p_pattern, 
            g16_key=p_g16_keywords,
            g16_nproc=p_ncpus,
            g16_mem=p_mem,
            charge=p_charge,
            multiplicity=p_multiplicity)

    gecos.send_qm_conformers(
            p_nameserver,
            p_databasefullpath,
            p_username,
            p_keysshfile,
            p_localdir,
            p_remotedir,
            p_g16path,
            regex='FREQ*.com',
            partition=p_slurm_part,
            exclude_nodes=p_list_nodes,
            ncpus=p_ncpus, 
            partitionmaster=p_slurm_part_master,
            nodemaster=p_node_master,
            mem=p_mem,
            encrypted_pass=p_encrypt_pass,
            logger=log)

else:

    log = utils.init_logger(
            "Output3",
            fileoutput=p_fileoutputfullpath,
            append=True,
            inscreen=False)

    p_outdir = os.path.join(p_localdir, p_pattern + '_g16_conformers')
    p_cutoff_rmsd_qm = 10.0

    gecos.check_qm_jobs(
            p_nameserver,
            p_databasefullpath,
            p_username,
            p_keysshfile,
            p_localdir,
            p_remotedir,
            p_outdir,
            p_pattern,
            p_dockrmsdpack,
            encrypted_pass=p_encrypt_pass,
            cutoff_rmsd=p_cutoff_rmsd_qm,
            logger=log)
print ("Job Done!!!!")
