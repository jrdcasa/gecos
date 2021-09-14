import argparse
import json
import os
import glob


# =============================================================================
def parse_arguments(logger=None):

    desc = """ Generation of conformers (GeCos) """

    parser = argparse.ArgumentParser(description=desc)
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("-j", "--json", dest="jsonfile",
                        help="A json file containing the parameters for a simulation using GeCos",
                        action="store", metavar="JSON_FILE")
    group1.add_argument("-p", "--python", dest="pythonfile",
                        help="A python script for running a simulation using GeCos",
                        action="store", metavar="PYTHON_FILE")

    args = parser.parse_args()

    return args


# =============================================================================
def read_json(filename):

    with open(filename, 'r') as fson:
        data = json.load(fson)

    filename_python = filename.split(".")[0]+".py"
    create_python_script(filename_python, data)

    return filename_python


# =============================================================================
def create_python_script(filename, keywords_dict, save=True):

    lines = ""
    lines += "import os\n"
    lines += "import utils\n"
    lines += "import gecos\n"
    lines += "\n"

    # KEYWORDS =====================================
    lines += "v_filename = '{}'\n".format(keywords_dict["moleculefile"])
    lines += "v_nameserver = '{}'\n".format(keywords_dict["nameserver"])
    lines += "v_username = '{}'\n".format(keywords_dict["username"])
    lines += "v_keysshfile = '{}'\n".format(keywords_dict["keyfile"])
    try:
        lines += "v_encrypt_pass = '{}'\n".format(keywords_dict["encrypted_passwd"])
    except KeyError:
        lines += "v_encrypt_pass = 'None'\n"
    lines += "v_slurm_part = '{}'\n".format(keywords_dict["partition"])
    lines += "v_list_nodes = {}\n".format(keywords_dict["exclude_nodes"])
    lines += "v_slurm_part_master = '{}'\n".format(keywords_dict["partitionmaster"])
    lines += "v_node_master = '{}'\n".format(keywords_dict["nodemaster"])
    lines += "v_localdir = '{}'\n".format(keywords_dict["localdir"])
    lines += "v_remotedir = '{}'\n".format(keywords_dict["remotedir"])
    lines += "v_pattern = '{}'\n".format(keywords_dict["pattern"])
    lines += "v_databasefullpath = '{}'\n".format(os.path.join(keywords_dict["localdir"],
                                                               keywords_dict["databasename"]))
    lines += "v_fileoutputfullpath = '{}'\n".format(os.path.join(keywords_dict["localdir"],
                                                                 keywords_dict["filelog"]))
    lines += "v_g16path = '{}'\n".format(keywords_dict["exec_g16"])
    lines += "v_g16_keywords = '{}'\n".format(keywords_dict["g16_key"])
    lines += "v_ncpus = {0:d}\n".format(int(keywords_dict["g16_nproc"]))
    lines += "v_mem = {0:d}\n".format(int(keywords_dict["g16_mem"]))
    lines += "v_charge = {0:d}\n".format(int(keywords_dict["charge"]))
    lines += "v_multiplicity = {0:d}\n".format(int(keywords_dict["multiplicity"]))
    if keywords_dict["write_gaussian"]:
        lines += "v_write_gaussian = True\n"
    else:
        lines += "v_write_gaussian = False\n"
    lines += "v_nconfs = {0:d}\n".format(int(keywords_dict["nconfs"]))
    lines += "v_min_iter_mm = {0:d}\n".format(int(keywords_dict["minimize_iterations"]))
    lines += "v_cutoff_rmsd_qm = {0:.1f}\n".format(float(keywords_dict["cutoff_rmsd_QM"]))

    if keywords_dict["bond_perception"]:
        lines += "v_bond_perception = True\n"
    else:
        lines += "v_bond_perception = False\n"

    lines += "v_dockrmsdpack = '{}'\n".format(keywords_dict["exec_rmsddock"])
    lines += "v_confpack = '{}'\n".format(keywords_dict["conformer_program"])

    # RDKITS PARAMETERS ===================
    if keywords_dict["conformer_program"].upper() == "RDKIT":
        try:
            lines += "v_rdkit_maxattempts = {0:d}\n".format(int(keywords_dict["rdkit_maxattempts"]))
        except KeyError:
            lines += "v_rdkit_maxattempts = 1000\n"
        try:
            lines += "v_rdkit_prunermsthresh = {0:.3f}\n".format(float(keywords_dict["rdkit_prunermsthresh"]))
        except KeyError:
            lines += "v_rdkit_prunermsthresh = -0.01\n"
        try:
            if keywords_dict["rdkit_useexptorsionangleprefs"]:
                lines += "v_rdkit_useexptorsionangleprefs = True\n"
            else:
                lines += "v_rdkit_useexptorsionangleprefs = False\n"
        except KeyError:
            lines += "v_rdkit_useexptorsionangleprefs = True\n"
        try:
            if keywords_dict['rdkit_usebasicknowlwdge']:
                lines += "v_rdkit_usebasicknowlwdge = True\n"
            else:
                lines += "v_rdkit_usebasicknowlwdge = False\n"
        except KeyError:
            lines += "v_rdkit_usebasicknowlwdge = True\n"
        try:
            if keywords_dict["rdkit_enforcechirality"]:
                lines += "v_rdkit_enforcechirality = True\n"
            else:
                lines += "v_rdkit_enforcechirality = False\n"
        except KeyError:
            lines += "v_rdkit_enforcechirality = True\n"
        try:
            lines += "v_rdkit_cluster_method = '{}'\n".format(keywords_dict['rdkit_cluster_method'])
        except KeyError:
            lines += "v_rdkit_cluster_method = 'rmsd'\n"
        try:
            lines += "v_rdkit_ffname = '{}'\n".format(keywords_dict["rdkit_ffname"])
        except KeyError:
            lines += "v_rdkit_ffname = 'MMFF'\n"
        try:
            lines += "v_rdkit_cluster_thres = {}\n".format(float(keywords_dict["rdkit_cluster_thres"]))
        except KeyError:
            lines += "v_rdkit_cluster_thres = 2.0\n"
    # CONFAB PARAMETERS ===================
    elif keywords_dict["conformer_program"].upper() == "OPENBABEL":
        try:
            lines += "v_openbabel_rmsd_cutoff_confab = {0:f}\n".\
             format(float(keywords_dict["openbabel_rmsd_cutoff_confab"]))
        except KeyError:
            lines += "v_openbabel_rmsd_cutoff_confab = 0.5\n"
        try:
            lines += "v_openbabel_energy_cutoff_confab = {0:f}\n".\
                 format(float(keywords_dict["openbabel_energy_cutoff_confab"]))
        except KeyError:
            lines += "v_openbabel_energy_cutoff_confab = 50.0\n"
        try:
            if keywords_dict['openbabel_verbose']:
                lines += "v_openbabel_verbose = True\n"
            else:
                lines += "v_openbabel_verbose = False\n"
        except KeyError:
            lines += "v_openbabel_verbose = False\n"
        try:
            lines += "v_openbabel_rmsddock_confab = {0:f}\n".\
                format(float(keywords_dict["openbabel_rmsddock_confab"]))
        except KeyError:
            lines += "v_openbabel_rmsddock_confab = 2.0\n"
        try:
            lines += "v_openbabel_ffname = '{}'\n".format(keywords_dict["openbabel_ffname"])
        except KeyError:
            lines += "v_openbabel_ffname = 'MMFF'\n"
        try:
            lines += "v_openbabel_cluster_energy_threshold = {0:f}\n".\
                format(float(keywords_dict["openbabel_cluster_energy_threshold"]))
        except KeyError:
            lines += "v_openbabel_cluster_energy_threshold = 99999.0\n"
        try:
            lines += "v_openbabel_cluster_max_number_cluster = {0:d}\n".\
                format(int(keywords_dict['openbabel_cluster_max_number_cluster']))
        except KeyError:
            lines += "v_openbabel_cluster_max_number_cluster = 100\n"

    # LOOP
    lines += "\n"
    lines += "if not os.path.isfile(v_databasefullpath):\n\n"
    lines += "\tlog = utils.init_logger(\n" \
             "\t\t\"Output2\",\n" \
             "\t\tfileoutput=v_fileoutputfullpath,\n" \
             "\t\tappend=False, inscreen=False)\n\n"

    if keywords_dict["conformer_program"].upper() == "RDKIT":
        lines += "\tg1 = gecos.GecosRdkit(\n" \
                 "\t\tfilename=v_filename,\n" \
                 "\t\ttotal_charge=v_charge,\n" \
                 "\t\tbond_perception=v_bond_perception,\n" \
                 "\t\tlogger=log)\n"
        lines += "\n"
        lines += "\tg1.generate_conformers(\n" \
                 "\t\tv_localdir,\n" \
                 "\t\tnconfs=v_nconfs,\n" \
                 "\t\tminimize_iterations=v_min_iter_mm,\n" \
                 "\t\tmaxattempts=v_rdkit_maxattempts,\n" \
                 "\t\tprunermsthresh=v_rdkit_prunermsthresh,\n" \
                 "\t\tuseexptorsionangleprefs=v_rdkit_useexptorsionangleprefs,\n" \
                 "\t\tusebasicknowledge=v_rdkit_usebasicknowlwdge,\n" \
                 "\t\tenforcechirality=v_rdkit_enforcechirality,\n" \
                 "\t\tff_name=v_rdkit_ffname,\n" \
                 "\t\tcluster_method=v_rdkit_cluster_method,\n" \
                 "\t\tcluster_threshold=v_rdkit_cluster_thres,\n" \
                 "\t\twrite_gaussian=v_write_gaussian,\n" \
                 "\t\tpattern=v_pattern,\n" \
                 "\t\tg16_key=v_g16_keywords,\n" \
                 "\t\tg16_nproc=v_ncpus,\n" \
                 "\t\tg16_mem=v_mem,\n" \
                 "\t\tcharge=v_charge,\n" \
                 "\t\tmultiplicity=v_multiplicity)\n"
    elif keywords_dict["conformer_program"].upper() == "OPENBABEL":
        lines += "\tg1 = gecos.GecosPyBabel(\n" \
                 "\t\tfilename=v_filename,\n" \
                 "\t\texec_rmsddock=v_dockrmsdpack,\n" \
                 "\t\ttotal_charge=v_charge,\n" \
                 "\t\tbond_perception=v_bond_perception,\n" \
                 "\t\tlogger=log)\n"
        lines += "\n"
        lines += "\tg1.generate_conformers(\n" \
                 "\t\tv_localdir,\n" \
                 "\t\tnconfs=v_nconfs,\n" \
                 "\t\tminimize_iterations=v_min_iter_mm,\n" \
                 "\t\trmsd_cutoff_confab=v_openbabel_rmsd_cutoff_confab,\n" \
                 "\t\tenergy_cutoff_confab=v_openbabel_energy_cutoff_confab,\n" \
                 "\t\tconfab_verbose_confab=v_openbabel_verbose,\n" \
                 "\t\tcutoff_rmsddock_confab=v_openbabel_rmsddock_confab,\n" \
                 "\t\tenergy_threshold_cluster=v_openbabel_cluster_energy_threshold,\n" \
                 "\t\tmax_number_cluster=v_openbabel_cluster_max_number_cluster,\n" \
                 "\t\tff_name=v_openbabel_ffname,\n" \
                 "\t\tpattern=v_pattern,\n" \
                 "\t\twrite_gaussian=v_write_gaussian,\n" \
                 "\t\tg16_key=v_g16_keywords,\n" \
                 "\t\tg16_nproc=v_ncpus,\n" \
                 "\t\tg16_mem=v_mem,\n" \
                 "\t\tcharge=v_charge,\n" \
                 "\t\tmultiplicity=v_multiplicity\n" \
                 "\t\t)\n"

        lines += "\n"
    else:
        msg = "Package {} to calculate conformers is not available.".format(keywords_dict["conformer_program"])
        print(msg)

    lines += "\n"
    lines += "\tgecos.send_qm_conformers(" \
             "\n\t\t\tv_nameserver," \
             "\n\t\t\tv_databasefullpath," \
             "\n\t\t\tv_username," \
             "\n\t\t\tv_keysshfile," \
             "\n\t\t\tv_localdir," \
             "\n\t\t\tv_remotedir," \
             "\n\t\t\tv_g16path,"\
             "\n\t\t\tregex='*g16*/*.com'," \
             "\n\t\t\tpartition=v_slurm_part," \
             "\n\t\t\texclude_nodes=v_list_nodes," \
             "\n\t\t\tncpus=v_ncpus, " \
             "\n\t\t\tpartitionmaster=v_slurm_part_master," \
             "\n\t\t\tnodemaster=v_node_master," \
             "\n\t\t\tmem=v_mem," \
             "\n\t\t\tencrypted_pass=v_encrypt_pass,"\
             "\n\t\t\tlogger=log)\n"
    lines += "\n"
    lines += "else:\n"
    lines += "\n"
    lines += "\tlog = utils.init_logger(" \
             "\n\t\t\t\"Output2\"," \
             "\n\t\t\tfileoutput=v_fileoutputfullpath," \
             "\n\t\t\tappend=True," \
             "\n\t\t\tinscreen=False)\n"
    lines += "\n"
    lines += "\tv_outdir = os.path.join(v_localdir, v_pattern + '_g16_conformers')\n"
    lines += "\n"
    lines += "\tgecos.check_qm_jobs(" \
             "\n\t\t\tv_nameserver," \
             "\n\t\t\tv_databasefullpath," \
             "\n\t\t\tv_username," \
             "\n\t\t\tv_keysshfile," \
             "\n\t\t\tv_localdir," \
             "\n\t\t\tv_remotedir," \
             "\n\t\t\tv_outdir," \
             "\n\t\t\tv_pattern," \
             "\n\t\t\tv_dockrmsdpack," \
             "\n\t\t\tencrypted_pass=v_encrypt_pass," \
             "\n\t\t\tcutoff_rmsd=v_cutoff_rmsd_qm," \
             "\n\t\t\tlogger=log)\n"

    lines += "\nprint(\"Job Done!!!\")\n"

    # File to write
    if save and filename is not None:
        try:
            with open(filename, 'w') as f:
                f.writelines(lines)
        except FileNotFoundError:
            pass


# =============================================================================
def main_gui_app():

    opts = parse_arguments()

    # Read json and create a python script to run gecos
    if opts.jsonfile:
        if opts.jsonfile.find("json") != -1:
            filename_python = read_json(opts.jsonfile)

    if opts.pythonfile:
        filename_python = opts.pythonfile

    local_dir = os.getcwd()
    try:
        database_name = glob.glob("*.db")[0]
    except IndexError:
        database_name = "None"
    print("Local_dir    : {}".format(local_dir))
    print("Database Name: {}".format(database_name))

    # Run Gecos
    fulldbpath = os.path.join(local_dir, database_name)
    donepath = os.path.join(local_dir, "done")
    if os.path.isfile(donepath):
        msg = "GeCos calculation seems to be finished."
        print(msg)
    else:
        if not os.path.isfile(fulldbpath):
            msg = "Database is not available. GeCos will run conformer search."
            print(msg)
        else:
            msg = "Database exists. GeCos will check the calculations."
            print(msg)

    os.system("python " + filename_python)


# =============================================================================
if __name__ == "__main__":
    main_gui_app()
