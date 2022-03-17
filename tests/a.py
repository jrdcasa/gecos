import os
import utils
import gecos

v_filename = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C01_EVOH_CCCOCCC/pdbs/Model01_EVOH.pdb'
v_nameserver = '161.111.25.96'
v_username = 'jramos'
v_keysshfile = '/home/jramos/.ssh/id_rsa_aoki_passwd'
v_encrypt_pass = None
v_slurm_part = 'cpu'
v_list_nodes = ['']
v_slurm_part_master = 'cpu'
v_node_master = None
v_localdir = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C01_EVOH_CCCOCCC/'
v_remotedir = '/opt/GECOS'
v_pattern = 'Model01'
v_databasefullpath = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C01_EVOH_CCCOCCC/Model01.db'
v_fileoutputfullpath = '/home/jramos/PycharmProjects/GITHUB_REPO_DIR/GeCos_tutorials/C01_EVOH_CCCOCCC/Model01.log'
v_g16path = '/opt/gaussian/g16_legacy/g16'
v_g16_keywords = '#p m062x/6-31G* opt'
v_ncpus = 4
v_mem = 2000
v_charge = 0
v_multiplicity = 1
v_write_gaussian = True
v_nconfs = 1000
v_min_iter_mm = 1000
v_cutoff_rmsd_qm = 0.5
v_bond_perception = True
v_dockrmsdpack = '/home/jramos/PycharmProjects/sandbox_GeCos/lib/python3.8/site-packages/gecos-0.1-py3.8.egg/thirdparty/dockrmsd.x'
v_confpack = 'rdkit'
v_rdkit_maxattempts = 1000
v_rdkit_prunermsthresh = -0.010
v_rdkit_useexptorsionangleprefs = True
v_rdkit_usebasicknowlwdge = True
v_rdkit_enforcechirality = True
v_rdkit_cluster_method = 'RMSD'
v_rdkit_ffname = 'MMFF'
v_rdkit_cluster_thres = 1.0

if not os.path.isfile(v_databasefullpath):

    log = utils.init_logger(
        "Output2",
        fileoutput=v_fileoutputfullpath,
        append=False, inscreen=False)

    g1 = gecos.GecosRdkit(
        filename=v_filename,
        total_charge=v_charge,
        bond_perception=v_bond_perception,
        logger=log)

    g1.generate_conformers(
        v_localdir,
        nconfs=v_nconfs,
        minimize_iterations=v_min_iter_mm,
        maxattempts=v_rdkit_maxattempts,
        prunermsthresh=v_rdkit_prunermsthresh,
        useexptorsionangleprefs=v_rdkit_useexptorsionangleprefs,
        usebasicknowledge=v_rdkit_usebasicknowlwdge,
        enforcechirality=v_rdkit_enforcechirality,
        ff_name=v_rdkit_ffname,
        cluster_method=v_rdkit_cluster_method,
        cluster_threshold=v_rdkit_cluster_thres,
        write_gaussian=v_write_gaussian,
        pattern=v_pattern,
        g16_key=v_g16_keywords,
        g16_nproc=v_ncpus,
        g16_mem=v_mem,
        charge=v_charge,
        multiplicity=v_multiplicity)

    gecos.send_qm_conformers(
            v_nameserver,
            v_databasefullpath,
            v_username,
            v_keysshfile,
            v_localdir,
            v_remotedir,
            v_g16path,
            regex='*g16*/*.com',
            partition=v_slurm_part,
            exclude_nodes=v_list_nodes,
            ncpus=v_ncpus, 
            partitionmaster=v_slurm_part_master,
            nodemaster=v_node_master,
            mem=v_mem,
            encrypted_pass=v_encrypt_pass,
            logger=log)

else:

    log = utils.init_logger(
            "Output2",
            fileoutput=v_fileoutputfullpath,
            append=True,
            inscreen=False)

    v_outdir = os.path.join(v_localdir, v_pattern + '_g16_conformers')

    gecos.check_qm_jobs(
            v_nameserver,
            v_databasefullpath,
            v_username,
            v_keysshfile,
            v_localdir,
            v_remotedir,
            v_outdir,
            v_pattern,
            v_dockrmsdpack,
            encrypted_pass=v_encrypt_pass,
            cutoff_rmsd=v_cutoff_rmsd_qm,
            logger=log)

print("Job Done!!!")
