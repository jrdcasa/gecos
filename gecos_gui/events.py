import PySimpleGUI as Sg
import webbrowser
import json
from socket import gaierror
import os
import re
import paramiko
import sqlite3
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from passwd_encrypt.passwd_encrypt import pw_encrypt_msg, pw_decrypt_msg


keys_input_str_labels = {'-MOLECULE_INPUT-', '-NAME_SERVER-', '-USER_NAME-', '-SLURM_PART-',
                         '-NODE_MASTER-', '-SLURM_PART_MASTER-', '-LOCAL_DIR-', '-REMOTE_DIR-',
                         '-PATTERN-', '-DATABASE_NAME-', '-FILENAME_LOG-', '-G16_KEYWORDS-',
                         '-DOCKRMSDPACK-', '-KEY_SSH_FILE-', '-ENCRYPT_PASS_FILE-', '-GAUSSIAN16PACK-'}
keys_input_list_labels = {'-EXCLUDE_NODES-'}
keys_input_int_labels = {'-G16_NPROC-', '-G16_MEM-', '-NCONF-', '-MIN_ITER_MM-'}
keys_input_float_labels = {'-CUTOFF_RMSD_QM-'}

keys_checkbox_labels = {"-BOND_PERCEPTION-": True}

keys_combo_labels = {'-CONFPACK-': 'rdkit'}

keys_all_mainguibuttons_labels = ['-BUTTONIMPORTJSON-', '-BUTTONCHECK-', '-BUTTONRUN-',
                                  '-BUTTONCREATESCRIPT-', '-BUTTONVISRESULTS-', '-BUTTONVIEWLOG-']

rdkit_dict_options = defaultdict()
rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] = 1000
rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] = -0.01
rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = True
rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = True
rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = True
rdkit_dict_options['-RDKIT_FFNAME-'] = "MMFF"
rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] = "RMSD"
rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] = 2.0

openbabel_dict_options = defaultdict()
openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = 0.5   # Angstroms
openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = 50.0  # kcal/mol
openbabel_dict_options['-CONFAB_VERBOSE-'] = False     # Verbose
openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = 2.0   # Angstroms
openbabel_dict_options['-CONFAB_FFNAME-'] = "MMFF"
openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = 99999.0
openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = 100

vmd_path = "/opt/vmd-1.9.4a42/bin/vmd"
pass_encryped_file = ""


# =============================================================================
def popup_error(window, msg):
    loc = window.current_location()
    x, y = window.size
    newloc = (loc[0] + x / 2., loc[1] + y / 2.)
    window.disappear()
    Sg.popup(msg, title='ERROR', grab_anywhere=True, location=newloc,
             background_color='red', text_color='white', )
    window.reappear()


# =============================================================================
def popup_msg(window, msg):
    loc = window.current_location()
    x, y = window.size
    newloc = (loc[0] + x / 2., loc[1] + y / 2.)
    window.disappear()
    Sg.popup(msg, title='INFO', grab_anywhere=True, location=newloc,
             background_color='green', text_color='white', )
    window.reappear()


# =============================================================================
def popup_msg_run(window, msg):

    loc = window.current_location()
    newloc = (loc[0] + 100., loc[1] + 100.)
    window.disappear()
    Sg.popup(msg, title='Running', grab_anywhere=True, location=newloc,
             background_color='blue', text_color='white', non_blocking=True, keep_on_top=True)
    window.reappear()


# =============================================================================
def clean_form(window):

    global vmd_path
    global pass_encryped_file
    global rdkit_dict_options
    global openbabel_dict_options

    for ikey in keys_input_str_labels:
        window[ikey].update("")

    for ikey in keys_input_list_labels:
        window[ikey].update("")

    for ikey in keys_input_int_labels:
        window[ikey].update("")

    for ikey in keys_input_float_labels:
        window[ikey].update("")

    for ikey, item in keys_checkbox_labels.items():
        window[ikey].update(item)

    for ikey, item in keys_combo_labels.items():
        window[ikey].update(item)

    rdkit_dict_options = defaultdict()
    rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] = 1000
    rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] = -0.01
    rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = True
    rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = True
    rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = True
    rdkit_dict_options['-RDKIT_FFNAME-'] = "MMFF"
    rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] = "RMSD"
    rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] = 2.0

    openbabel_dict_options = defaultdict()
    openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = 0.5  # Angstroms
    openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = 50.0  # kcal/mol
    openbabel_dict_options['-CONFAB_VERBOSE-'] = False  # Verbose
    openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = 2.0  # Angstroms
    openbabel_dict_options['-CONFAB_FFNAME-'] = "MMFF"
    openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = 99999.0
    openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = 100

    vmd_path = "/opt/vmd-1.9.4a42/bin/vmd"
    pass_encryped_file = ""


# =============================================================================
def import_jsonfile_to_gui(window, filename):
    """
    Use a json file containing the keywords for GeCos and load the parameters in the GUI

    Args:
        window: window instance
        filename: json file

    """

    global rdkit_dict_options
    global pass_encryped_file

    # If filename None, the CANCEL button has been pushed
    if filename is None or len(filename) == 0:
        return False

    # Open json file
    with open(filename, 'r') as fjson:
        data = json.load(fjson)
        for item in data:
            if item.upper() == "MOLECULEFILE":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"moleculefile:\" must be a string.")
                    return False
                else:
                    window['-MOLECULE_INPUT-'].update(data[item])
            elif item.upper() == "NAMESERVER":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"nameserver:\" must be a string.")
                    return False
                else:
                    window['-NAME_SERVER-'].update(data[item])
            elif item.upper() == "USERNAME":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"username:\" must be a string.")
                    return False
                else:
                    window['-USER_NAME-'].update(data[item])
            elif item.upper() == "KEYFILE":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"keyfile:\" must be a string.")
                    return False
                else:
                    window['-KEY_SSH_FILE-'].update(data[item])
            elif item.upper() == "PARTITION":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"partition:\" must be a string.")
                    return False
                else:

                    window['-SLURM_PART-'].update(data[item])
            elif item.upper() == "EXCLUDE_NODES":
                if not isinstance(data[item], list):
                    popup_error(window, "Json error: \"exclude_nodes:\" must be a list.")
                    return False
                else:
                    string = ""
                    for i in data[item]:
                        string += i + ","
                    window['-EXCLUDE_NODES-'].update(string[:-1])
            elif item.upper() == "NODEMASTER":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"nodemaster:\" must be a string.")
                    return False
                else:
                    window['-NODE_MASTER-'].update(data[item])
            elif item.upper() == "PARTITIONMASTER":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"partitionmaster:\" must be a string.")
                    return False
                else:
                    window['-SLURM_PART_MASTER-'].update(data[item])
            elif item.upper() == "LOCALDIR":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"localdir:\" must be a string.")
                    return False
                else:
                    window['-LOCAL_DIR-'].update(data[item])
            elif item.upper() == "REMOTEDIR":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"remotedir:\" must be a string.")
                    return False
                else:
                    window['-REMOTE_DIR-'].update(data[item])
            elif item.upper() == "PATTERN":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"pattern:\" must be a string.")
                    return False
                else:
                    window['-PATTERN-'].update(data[item])
            elif item.upper() == "DATABASENAME":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"databasename:\" must be a string.")
                    return False
                else:
                    window['-DATABASE_NAME-'].update(data[item])
            elif item.upper() == "FILELOG":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"filelog:\" must be a string.")
                    return False
                else:
                    window['-FILENAME_LOG-'].update(data[item])
            elif item.upper() == "G16_KEY":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"g16_key:\" must be a string.")
                    return False
                else:
                    window['-G16_KEYWORDS-'].update(data[item])
            elif item.upper() == "G16_NPROC":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"g16_nproc:\" must be an integer.")
                    return False
                else:
                    window['-G16_NPROC-'].update(data[item])
            elif item.upper() == "G16_MEM":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"g16_mem:\" must be an integer.")
                    return False
                else:
                    window['-G16_MEM-'].update(data[item])
            elif item.upper() == "NCONFS":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"nconfs:\" must be an integer.")
                    return False
                else:
                    window['-NCONF-'].update(data[item])
            elif item.upper() == "MINIMIZE_ITERATIONS":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"minimize_iterations:\" must be an integer.")
                    return False
                else:
                    window['-MIN_ITER_MM-'].update(data[item])
            elif item.upper() == "CUTOFF_RMSD_QM":
                if not isinstance(data[item], float):
                    popup_error(window, "Json error: \"cutoff_rmsd_QM:\" must be a float.")
                    return False
                else:
                    window['-CUTOFF_RMSD_QM-'].update(data[item])
            elif item.upper() == "EXEC_RMSDDOCK":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"exec_rmsddock:\" must be a string.")
                    return False
                else:
                    window['-DOCKRMSDPACK-'].update(data[item])
            elif item.upper() == "EXEC_G16":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"exec_g16:\" must be a string.")
                    return False
                else:
                    window['-GAUSSIAN16PACK-'].update(data[item])
            elif item.upper() == "BOND_PERCEPTION":
                if not isinstance(data[item], bool):
                    popup_error(window, "Json error: \"bond_perception:\" must be a boolean.")
                    return False
                else:
                    if data[item]:
                        window['-BOND_PERCEPTION-'].update(value=True)
                    else:
                        window['-BOND_PERCEPTION-'].update(value=False)

            elif item.upper() == "CONFORMER_PROGRAM":
                if not isinstance(data[item], str):
                    popup_error(window, "Json error: \"conformer_program:\" must be a string.")
                    return False
                else:
                    if data[item].upper() == "RDKIT":
                        window['-CONFPACK-'].update("rdkit")
                    elif data[item].upper() == "OPENBABEL":
                        window['-CONFPACK-'].update("openbabel")
                    else:
                        window['-CONFPACK-'].update("")
            elif item.upper() == "CHARGE":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"Charge:\" must be an integer.")
                    return False
                else:
                    window['-CHARGE-'].update(data[item])
            elif item.upper() == "MULTIPLICITY":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"Multiplicity:\" must be an integer.")
                    return False
                else:
                    window['-MULTIPLICITY-'].update(data[item])
            elif item.upper() == "WRITE_GAUSSIAN":
                if not isinstance(data[item], bool):
                    popup_error(window, "Json error: \"write_gaussian:\" must be a boolean.")
                    return False
                else:
                    if data[item]:
                        window['-WRITE_GAUSSIAN-'].update(value=True)
                    else:
                        window['-WRITE_GAUSSIAN-'].update(value=False)
            elif item.upper() == "RDKIT_MAXATTEMPTS":
                rdkit_dict_options["-RDKIT_MAXATTEMPTS-"] = data[item]
            elif item.upper() == "RDKIT_PRUNERMSTHRESH":
                rdkit_dict_options["-RDKIT_PRUNERMSTHRESH-"] = data[item]
            elif item.upper() == "RDKIT_USEEXPTORSIONANGLEPREFS":
                if data[item]:
                    rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = True
                else:
                    rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = False
            elif item.upper() == "RDKIT_USEBASICKNOWLEDGE":
                if data[item]:
                    rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = True
                else:
                    rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = False
            elif item.upper() == "RDKIT_ENFORCECHIRALITY":
                if data[item]:
                    rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = True
                else:
                    rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = False
            elif item.upper() == "RDKIT_FFNAME":
                rdkit_dict_options["-RDKIT_FFNAME-"] = data[item]
            elif item.upper() == "RDKIT_CLUSTER_METHOD":
                rdkit_dict_options["-RDKIT_CLUSTER_METHOD-"] = data[item]
            elif item.upper() == "RDKIT_CLUSTER_THRES":
                rdkit_dict_options["-RDKIT_CLUSTER_THRES-"] = data[item]
            elif item.upper() == "OPENBABEL_RMSD_CUTOFF":
                openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = data[item]
            elif item.upper() == "OPENBABEL_ENERGY_CUTOFF":
                openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = data[item]
            elif item.upper() == "OPENBABEL_VERBOSE":
                if data[item]:
                    openbabel_dict_options['-CONFAB_VERBOSE-'] = True
                else:
                    openbabel_dict_options['-CONFAB_VERBOSE-'] = False
            elif item.upper() == "OPENBABEL_RMSD_CUTOFF_RMSDDOCK":
                openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = data[item]
            elif item.upper() == "OPENBABEL_FFNAME":
                openbabel_dict_options['-CONFAB_FFNAME-'] = data[item]
            elif item.upper() == "OPENBABEL_ENERGY_THRESHOLD":
                openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = data[item]
            elif item.upper() == "OPENBABEL_MAX_ENERGY_CLUSTERS":
                openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = data[item]
            elif item.upper() == "ENCRYPTED_PASSWD":
                pass_encryped_file = data[item]
                window['-ENCRYPT_PASS_FILE-'].update(data[item])

        keys_activate_mainguibuttons_labels = ['-BUTTONRUN-', '-BUTTONCREATESCRIPT-',
                                               '-BUTTONVISRESULTS-', '-BUTTONVIEWLOG-']
        for item in keys_activate_mainguibuttons_labels:
            window[item].update(disabled=True)


# =============================================================================
def export_jsonfile_from_gui(window, filename, save=True):
    """
    Create a json file from the GUI containing the keywords for GeCos

    Args:
        window: window instance
        filename: json file
        save: Save file

    """

    global rdkit_dict_options
    global openbabel_dict_options

    # If filename None, the CANCEL button has been pushed
    if filename is None or len(filename) == 0:
        return False

    keywords_to_write_str = {'moleculefile': '-MOLECULE_INPUT-',
                             'nameserver': '-NAME_SERVER-',
                             'username': '-USER_NAME-',
                             'keyfile': '-KEY_SSH_FILE-',
                             'encrypted_passwd': None,
                             'partition': '-SLURM_PART-',
                             'nodemaster': '-NODE_MASTER-',
                             'partitionmaster': '-SLURM_PART_MASTER-',
                             'localdir': '-LOCAL_DIR-',
                             'remotedir': '-REMOTE_DIR-',
                             'pattern': '-PATTERN-',
                             'databasename': '-DATABASE_NAME-',
                             'filelog': '-FILENAME_LOG-',
                             'g16_key': '-G16_KEYWORDS-',
                             'exec_rmsddock': '-DOCKRMSDPACK-',
                             'exec_g16': '-GAUSSIAN16PACK-',
                             'conformer_program': '-CONFPACK-'
                             }
    keywords_to_write_nostr = {'g16_nproc': '-G16_NPROC-',
                               'g16_mem': '-G16_MEM-',
                               'nconfs': '-NCONF-',
                               'cutoff_rmsd_QM': '-CUTOFF_RMSD_QM-',
                               'minimize_iterations': '-MIN_ITER_MM-',
                               'charge': '-CHARGE-',
                               'multiplicity': '-MULTIPLICITY-'
                               }
    keywords_to_write_list = {'exclude_nodes': '-EXCLUDE_NODES-'}
    keywords_to_write_combo = {'bond_perception': '-BOND_PERCEPTION-',
                               'write_gaussian': '-WRITE_GAUSSIAN-'}

    lines = "{\n"
    for key, value in keywords_to_write_str.items():
        if key.upper() == "ENCRYPTED_PASSWD":
            if len(pass_encryped_file) > 1:
                lines += "\t\"{}\": \"{}\",\n".format(key, pass_encryped_file)
        else:
            data = window[value].get()
            lines += "\t\"{}\": \"{}\",\n".format(key, data)

    for key, value in keywords_to_write_nostr.items():
        data = window[value].get()
        lines += "\t\"{}\": {},\n".format(key, data)

    for key, value in keywords_to_write_list.items():
        data = window[value].get()
        lines += "\t\"{}\": [\n".format(key, data)
        for item in data.split(","):
            lines += "\t\t\"{}\",\n".format(item)
        lines = lines[:-2]  # Delete last comma
        lines += "\t],\n"

    for key, value in keywords_to_write_combo.items():
        data = window[value].get()
        if data:
            lines += "\t\"{}\": true,\n".format(key, data)
        else:
            lines += "\t\"{}\": false,\n".format(key, data)

    # Write advanced options only when its value is different to the default
    if window['-CONFPACK-'].get().upper() == "RDKIT":
        if rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] != 1000:
            key = "rdkit_maxattempts"
            data = rdkit_dict_options['-RDKIT_MAXATTEMPTS-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] != -0.01:
            key = 'rdkit_prunermsthresh'
            data = rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if not rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-']:
            key = 'rdkit_useexptorsionangleprefs'
            lines += "\t\"{}\": {},\n".format(key, 'false')
        if not rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-']:
            key = 'rdkit_usebasicknowledge'
            lines += "\t\"{}\": {},\n".format(key, 'false')
        if not rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-']:
            key = 'rdkit_enforcechirality'
            lines += "\t\"{}\": {},\n".format(key, 'false')
        if rdkit_dict_options['-RDKIT_FFNAME-'] != "MMFF":
            key = 'rdkit_ffname'
            data = rdkit_dict_options['-RDKIT_FFNAME-']
            lines += "\t\"{}\": \"{}\",\n".format(key, data)
        if rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] != "RMSD":
            key = 'rdkit_cluster_method'
            data = rdkit_dict_options['-RDKIT_CLUSTER_METHOD-']
            lines += "\t\"{}\": \"{}\",\n".format(key, data)
        if rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] != 2.0:
            key = 'rdkit_cluster_thres'
            data = rdkit_dict_options['-RDKIT_CLUSTER_THRES-']
            lines += "\t\"{}\": {},\n".format(key, data)
        lines = lines[:-2]  # Delete last comma
    elif window['-CONFPACK-'].get().upper() == "OPENBABEL":
        if openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] != 0.5:
            key = "openbabel_rmsd_cutoff_diversity"
            data = openbabel_dict_options['-CONFAB_RMSD_CUTOFF-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] != 50.0:
            key = "openbabel_energy_cutoff"
            data = openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if openbabel_dict_options['-CONFAB_VERBOSE-']:
            key = 'openbabel_verbose'
            lines += "\t\"{}\": {},\n".format(key, 'false')
        if openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-']:
            key = 'openbabel_rmsd_cutoff_rmsddock'
            data = openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if openbabel_dict_options['-CONFAB_FFNAME-']:
            key = 'openbabel_ffname'
            data = openbabel_dict_options['-CONFAB_FFNAME-']
            lines += "\t\"{}\": \"{}\",\n".format(key, data)
        if openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-']:
            key = 'openbabel_energy_threshold'
            data = openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-']
            lines += "\t\"{}\": {},\n".format(key, data)
        if openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-']:
            key = 'openbabel_max_energy_clusters'
            data = openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-']
            lines += "\t\"{}\": {},\n".format(key, data)
        lines = lines[:-2]  # Delete last comma
    lines += "\n}"

    # File to write
    if save and filename is not None:
        try:
            with open(filename, 'w') as f:
                f.writelines(lines)
        except FileNotFoundError:
            pass


# =============================================================================
def import_pythonfile_to_gui(window, filename):

    """
    Use a json file containing the keywords for GeCos and load the parameters in the GUI

    Args:
        window: window instance
        filename: python file

    """

    global rdkit_dict_options

    # If filename None, the CANCEL button has been pushed
    if filename is None or len(filename) == 0:
        return False

    # Open python file
    var_to_dict_str = {
        'v_filename': '-MOLECULE_INPUT-',
        'v_nameserver': '-NAME_SERVER-',
        'v_username': '-USER_NAME-',
        'v_keysshfile': '-KEY_SSH_FILE-',
        'v_slurm_part': '-SLURM_PART-',
        'v_slurm_part_master': '-SLURM_PART_MASTER-',
        'v_node_master': '-NODE_MASTER-',
        'v_localdir': '-LOCAL_DIR-',
        'v_remotedir': '-REMOTE_DIR-',
        'v_pattern ': '-PATTERN-',
        'v_g16_keywords': '-G16_KEYWORDS-',
        'v_dockrmsdpack': '-DOCKRMSDPACK-',
        'v_g16path': '-GAUSSIAN16PACK-',
    }

    var_to_encrypt = {'v_encrypt_pass': '-ENCRYPT_PASS_FILE-'}

    var_to_dict_combobox = {
        'v_confpack': '-CONFPACK-'
    }

    var_to_dict_list = {
        'v_list_nodes': '-EXCLUDE_NODES-',
    }

    var_to_dict_pathlast = {
        'v_databasefullpath': '-DATABASE_NAME-',
        'v_fileoutputfullpath': '-FILENAME_LOG-'
    }

    var_to_dict_intfloat = {
        'v_ncpus': '-G16_NPROC-',
        'v_mem': '-G16_MEM-',
        'v_charge': '-CHARGE-',
        'v_multiplicity': '-MULTIPLICITY-',
        'v_nconfs': '-NCONF-',
        'v_min_iter_mm': '-MIN_ITER_MM-',
        'v_cutoff_rmsd_qm': '-CUTOFF_RMSD_QM-',
    }

    var_to_dict_boolean = {
        'v_write_gaussian': '-WRITE_GAUSSIAN-',
        'v_bond_perception': '-BOND_PERCEPTION-'
    }

    var_to_dict_rdkit_str = {
        'v_rdkit_cluster_method': '-RDKIT_CLUSTER_METHOD-',
        'v_rdkit_ffname': '-RDKIT_FFNAME-'
    }
    var_to_dict_rdkit_boolean = {
        'v_rdkit_useexptorsionangleprefs': '-RDKIT_USEEXPTORSIONANGLEPREFS-',
        'v_rdkit_usebasicknowlwdge': '-RDKIT_USEBASICKNOWLEDGE-',
        'v_rdkit_enforcechirality': '-RDKIT_ENFORCECHIRALITY-'
    }

    var_to_dict_rdkit_intfloat = {
        'v_rdkit_maxattempts': '-RDKIT_MAXATTEMPTS-',
        'v_rdkit_prunermsthresh': '-RDKIT_PRUNERMSTHRESH-',
        'v_rdkit_cluster_thres': '-RDKIT_CLUSTER_THRES-'
    }

    var_to_dict_openbabel_intfloat = {
        'v_openbabel_rmsd_cutoff_confab': '-CONFAB_RMSD_CUTOFF-',
        'v_openbabel_energy_cutoff_confab': '-CONFAB_ENERGY_CUTOFF-',
        'v_openbabel_rmsddock_confab': '-CONFAB_RMSD_CUTOFF_RMSDDOCK-',
        'v_openbabel_cluster_energy_threshold': '-CONFAB_ENERGY_THRESHOLD-',
        'v_openbabel_cluster_max_number_cluster': '-CONFAB_MAX_ENERGY_CLUSTERS-'

    }

    var_to_dict_openbabel_boolean = {
        'v_openbabel_verbose': '-CONFAB_VERBOSE-'
    }

    var_to_dict_openbabel_str = {
        'v_openbabel_ffname': '-CONFAB_FFNAME-'
    }

    with open(filename, 'r') as fpython:
        data = fpython.read()

        for ikey in var_to_dict_str.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search("(?:'|\").*(?:'|\")", str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                label = var_to_dict_str[ikey]
                window[label].update(value)

        for ikey in var_to_encrypt.keys():
            regex = ikey + ".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey + ".*=.*", data).group(0)
                # value = re.search("(?:'|\").*(?:'|\")", str2).group(0)
                tmp = re.search("(?:['\"]).*(?:['\"])", str2)
                if tmp is not None:
                    tmp.group(0)
                    value = value.replace("'", "")
                    value = value.replace("\"", "")
                    label = var_to_dict_str[ikey]
                    window[label].update(value)

        for ikey in var_to_dict_combobox.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search('(?:\'|").*(?:\'|")', str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                label = var_to_dict_combobox[ikey]
                window[label].update(value)

        for ikey in var_to_dict_list.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search('(?:\'|").*(?:\'|")', str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                label = var_to_dict_list[ikey]
                window[label].update(value)

        for ikey in var_to_dict_pathlast.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search('(?:\'|").*(?:\'|")', str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                value = value.split("/")[-1]
                label = var_to_dict_pathlast[ikey]
                window[label].update(value)

        for ikey in var_to_dict_intfloat.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.split("=")[-1]
                label = var_to_dict_intfloat[ikey]
                window[label].update(value)

        for ikey in var_to_dict_boolean.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                value = value.split("=")[-1]
                if value.find('True') != -1:
                    valbol = True
                else:
                    valbol = False
                label = var_to_dict_boolean[ikey]
                window[label].update(value=valbol)

        for ikey in var_to_dict_rdkit_str.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search('(?:\'|").*(?:\'|")', str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                label = var_to_dict_rdkit_str[ikey]
                rdkit_dict_options[label] = value

        for ikey in var_to_dict_rdkit_intfloat.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.split("=")[-1]
                label = var_to_dict_rdkit_intfloat[ikey]
                rdkit_dict_options[label] = value

        for ikey in var_to_dict_rdkit_boolean.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                value = value.split("=")[-1]
                if value.find('True') != -1:
                    valbol = True
                else:
                    valbol = False
                label = var_to_dict_rdkit_boolean[ikey]
                rdkit_dict_options[label] = valbol

        for ikey in var_to_dict_openbabel_intfloat.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.split("=")[-1]
                label = var_to_dict_openbabel_intfloat[ikey]
                openbabel_dict_options[label] = value

        for ikey in var_to_dict_openbabel_boolean.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                value = value.split("=")[-1]
                if value.find('True') != -1:
                    valbol = True
                else:
                    valbol = False
                label = var_to_dict_openbabel_boolean[ikey]
                openbabel_dict_options[label] = valbol

        for ikey in var_to_dict_openbabel_str.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey+".*=.*", data).group(0)
                # value = re.search('(?:\'|").*(?:\'|")', str2).group(0)
                value = re.search("(?:['\"]).*(?:['\"])", str2).group(0)
                value = value.replace("'", "")
                value = value.replace("\"", "")
                label = var_to_dict_openbabel_str[ikey]
                openbabel_dict_options[label] = value


# =============================================================================
def write_python_script_from_gui(window, filename, save=True):

    global rdkit_dict_options

    # If filename None, the CANCEL button has been pushed
    if filename is None or len(filename) == 0:
        return False

    v_list_nodes = []
    for item in window['-EXCLUDE_NODES-'].get().split(","):
        v_list_nodes.append(item)

    lines = ""
    lines += "import os\n"
    lines += "import utils\n"
    lines += "import gecos\n"
    lines += "\n"
    # KEYWORDS =====================================
    lines += "v_filename = '{}'\n".format(window['-MOLECULE_INPUT-'].get())
    lines += "v_nameserver = '{}'\n".format(window['-NAME_SERVER-'].get())
    lines += "v_username = '{}'\n".format(window['-USER_NAME-'].get())
    lines += "v_keysshfile = '{}'\n".format(window['-KEY_SSH_FILE-'].get())
    if len(pass_encryped_file) > 1:
        lines += "v_encrypt_pass = '{}'\n".format(pass_encryped_file)
    else:
        lines += "v_encrypt_pass = None\n"
    lines += "v_slurm_part = '{}'\n".format(window['-SLURM_PART-'].get())
    lines += "v_list_nodes = {}\n".format(v_list_nodes)
    lines += "v_slurm_part_master = '{}'\n".format(window['-SLURM_PART_MASTER-'].get())
    lines += "v_node_master = '{}'\n".format(window['-NODE_MASTER-'].get())
    lines += "v_localdir = '{}'\n".format(window['-LOCAL_DIR-'].get())
    lines += "v_remotedir = '{}'\n".format(window['-REMOTE_DIR-'].get())
    lines += "v_pattern = '{}'\n".format(window['-PATTERN-'].get())
    lines += "v_databasefullpath = '{}'\n".format(os.path.join(window['-LOCAL_DIR-'].get(),
                                                               window['-DATABASE_NAME-'].get()))
    lines += "v_fileoutputfullpath = '{}'\n".format(os.path.join(window['-LOCAL_DIR-'].get(),
                                                                 window['-FILENAME_LOG-'].get()))
    lines += "v_g16path = '{}'\n".format(window['-GAUSSIAN16PACK-'].get())
    lines += "v_g16_keywords = '{}'\n".format(window['-G16_KEYWORDS-'].get())
    lines += "v_ncpus = {0:d}\n".format(int(window['-G16_NPROC-'].get()))
    lines += "v_mem = {0:d}\n".format(int(window['-G16_MEM-'].get()))
    lines += "v_charge = {0:d}\n".format(int(window['-CHARGE-'].get()))
    lines += "v_multiplicity = {0:d}\n".format(int(window['-MULTIPLICITY-'].get()))
    if window['-WRITE_GAUSSIAN-'].get():
        lines += "v_write_gaussian = True\n"
    else:
        lines += "v_write_gaussian = False\n"
    lines += "v_nconfs = {0:d}\n".format(int(window['-NCONF-'].get()))
    lines += "v_min_iter_mm = {0:d}\n".format(int(window['-MIN_ITER_MM-'].get()))
    lines += "v_cutoff_rmsd_qm = {0:.1f}\n".format(float(window['-CUTOFF_RMSD_QM-'].get()))

    if window['-BOND_PERCEPTION-'].get():
        lines += "v_bond_perception = True\n"
    else:
        lines += "v_bond_perception = False\n"

    lines += "v_dockrmsdpack = '{}'\n".format(window['-DOCKRMSDPACK-'].get())
    lines += "v_confpack = '{}'\n".format(window['-CONFPACK-'].get())

    # RDKITS PARAMETERS ===================
    if window['-CONFPACK-'].get().upper() == "RDKIT":
        lines += "v_rdkit_maxattempts = {0:d}\n".format(int(rdkit_dict_options['-RDKIT_MAXATTEMPTS-']))
        lines += "v_rdkit_prunermsthresh = {0:.3f}\n".format(float(rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-']))
        if rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-']:
            lines += "v_rdkit_useexptorsionangleprefs = True\n"
        else:
            lines += "v_rdkit_useexptorsionangleprefs = False\n"
        if rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-']:
            lines += "v_rdkit_usebasicknowlwdge = True\n"
        else:
            lines += "v_rdkit_usebasicknowlwdge = False\n"

        if rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-']:
            lines += "v_rdkit_enforcechirality = True\n"
        else:
            lines += "v_rdkit_enforcechirality = False\n"
        lines += "v_rdkit_cluster_method = '{}'\n".format(rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'])
        lines += "v_rdkit_ffname = '{}'\n".format(rdkit_dict_options['-RDKIT_FFNAME-'])
        lines += "v_rdkit_cluster_thres = {}\n".format(float(rdkit_dict_options['-RDKIT_CLUSTER_THRES-']))
    # CONFAB PARAMETERS ===================
    elif window['-CONFPACK-'].get().upper() == "OPENBABEL":
        lines += "v_openbabel_rmsd_cutoff_confab = {0:f}\n".\
            format(float(openbabel_dict_options['-CONFAB_RMSD_CUTOFF-']))
        lines += "v_openbabel_energy_cutoff_confab = {0:f}\n".\
            format(float(openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-']))
        if openbabel_dict_options['-CONFAB_VERBOSE-']:
            lines += "v_openbabel_verbose = True\n"
        else:
            lines += "v_openbabel_verbose = False\n"
        lines += "v_openbabel_rmsddock_confab = {0:f}\n".\
            format(float(openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-']))
        lines += "v_openbabel_ffname = '{}'\n".format(openbabel_dict_options['-CONFAB_FFNAME-'])

        lines += "v_openbabel_cluster_energy_threshold = {0:f}\n".\
            format(float(openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-']))
        lines += "v_openbabel_cluster_max_number_cluster = {0:d}\n".\
            format(int(openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-']))

    # LOOP
    lines += "\n"
    lines += "if not os.path.isfile(v_databasefullpath):\n\n"
    lines += "\tlog = utils.init_logger(\n" \
             "\t\t\"Output2\",\n" \
             "\t\tfileoutput=v_fileoutputfullpath,\n" \
             "\t\tappend=False, inscreen=False)\n\n"

    if window['-CONFPACK-'].get().upper() == "RDKIT":
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
    elif window['-CONFPACK-'].get().upper() == "OPENBABEL":
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
        msg = "Package {} to calculate conformers is not available.".format(window['-CONFPACK-'].get())
        popup_error(window, msg)

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
def check_parameteres_gui(window, values):

    """

    Args:
        window:
        values:

    Returns:

    """

    global pass_encryped_file

    files_localpath_string = ['-MOLECULE_INPUT-', '-LOCAL_DIR-', '-DOCKRMSDPACK-']

    v = values['-CONFPACK-']
    a = window['-CONFPACK-'].Values
    if v.lower() not in a:
        msg = "Conformer program: {} must be in {}.\n  ".format(v, a)
        popup_error(window, msg)
        return False

    nameserver = window['-NAME_SERVER-'].get()
    username = window['-USER_NAME-'].get()
    keyfile = window['-KEY_SSH_FILE-'].get()
    partition = window['-SLURM_PART-'].get()
    partitionmaster = window['-SLURM_PART_MASTER-'].get()
    nodemaster = window['-NODE_MASTER-'].get()
    remotedir = window['-REMOTE_DIR-'].get()
    g16path = window['-GAUSSIAN16PACK-'].get()

    # Check for integers and floats =======================================================
    for ilabel in keys_input_int_labels:
        try:
            int(window[ilabel].get())
        except ValueError:
            msg = "{}: {} must be an integer.\n  ".format(ilabel, window[ilabel].get())
            popup_error(window, msg)
            return False

    for ilabel in keys_input_float_labels:
        try:
            float(window[ilabel].get())
        except ValueError:
            msg = "{}: {} must be a float.\n  ".format(ilabel, window[ilabel].get())
            popup_error(window, msg)
            return False

    # Check files in the local directory ======================================
    for ikey in files_localpath_string:
        pathfile = window[ikey].get()
        if not os.path.exists(pathfile):
            msg = "{}: {} does not exist".format(ikey, pathfile)
            popup_error(window, msg)
            return False

    # Check server stuffs =====================================================
    server = paramiko.SSHClient()
    server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        msg_key = "Key found, but password authentication is needed."
        key = paramiko.RSAKey.from_private_key_file(keyfile)
    except paramiko.ssh_exception.SSHException:
        msg_key = "Not a valid RSA private key file:\nkeyfile {}\n  ".format(keyfile)
        key = ""
        pass
    except FileNotFoundError:
        msg_key = "Key file is not found"
        key = ""
        pass

    try:
        server.connect(nameserver, username=username, pkey=key)
    except gaierror:
        msg = "Unable to connect to {} ".format(nameserver)
        popup_error(window, msg)
        return False
    except (paramiko.ssh_exception.AuthenticationException, UnboundLocalError):
        msg = msg_key + "\n" + "Enter password to connect remote server:"
        loc = window.current_location()
        x, y = window.size
        newloc = (loc[0] + (x / 2.)*0.5, loc[1] + (y / 2.)*0.5)

        if not os.path.isfile(pass_encryped_file):
            msg_pubkey = "Insert the path for a RSA public key:"
            public_key = Sg.popup_get_text(msg_pubkey, location=newloc)
            try:
                path_to_public_key = os.path.split(public_key)[0]
                password = Sg.popup_get_text(msg, location=newloc, password_char='*')
                pass_encryped_file = os.path.join(path_to_public_key, "passwd_encrypted.bin")
                pw_encrypt_msg(public_key, password, fout_name=pass_encryped_file)
                popup_msg(window, "Encripted password is stored in {}".format(pass_encryped_file))
                window['-ENCRYPT_PASS_FILE-'].update(pass_encryped_file)
            except (TypeError, AttributeError):
                return False
        else:
            pass_encryped_file = window['-ENCRYPT_PASS_FILE-'].get()
            password = pw_decrypt_msg(keyfile, pass_encryped_file)

        try:
            server.connect(nameserver, username=username, password=password)
        except paramiko.ssh_exception.AuthenticationException:
            msg = "Authentication problem with password:\nusername {}\n Try again".format(username)
            popup_error(window, msg)
            return False

    except AttributeError:
        msg = "There is some problem with the key file ({})\n".format(key)
        msg += "Server name {}\n".format(nameserver)
        popup_error(window, msg)
        return False

    # Check partition stuffs ==================================================
    for ipart in [partition, partitionmaster]:
        command = "sinfo -s | egrep {}".format(ipart)
        stdin, stdout, stderr = server.exec_command(command, timeout=10)  # Non-blocking call
        out_txt = stdout.read().decode('utf8')
        if len(out_txt) < 1:
            msg = "Partition {} does not exist\n  ".format(ipart)
            popup_error(window, msg)
            return False

    # Check nodes stuffs ==================================================
    command = "scontrol show node {} | egrep 'not found'".format(nodemaster)
    stdin, stdout, stderr = server.exec_command(command, timeout=10)  # Non-blocking call
    out_txt = stdout.read().decode('utf8')
    err_txt = stderr.read().decode('utf8')
    if len(out_txt) > 1 or len(err_txt) > 1:
        msg = "Nodemaster {} does not exist\n in partition {}\n  ".format(nodemaster, partitionmaster)
        popup_error(window, msg)
        return False

    # Check remote_dir stuffs ==================================================
    command = "ls -d {}".format(remotedir)
    stdin, stdout, stderr = server.exec_command(command, timeout=10)  # Non-blocking call
    err_txt = stderr.read().decode('utf8')
    if len(err_txt) > 1:
        msg = "Remotedir {} does not exist\n in server {}\n  ".format(remotedir, nameserver)
        popup_error(window, msg)
        return False

    # Check gaussian path
    command = "ls -d {}".format(g16path)
    stdin, stdout, stderr = server.exec_command(command, timeout=10)  # Non-blocking call
    err_txt = stderr.read().decode('utf8')
    if len(err_txt) > 1:
        msg = "G16 path {} does not exist\n in server {}\n  ".format(g16path, nameserver)
        popup_error(window, msg)
        return False

    return True


# =============================================================================
def open_advance_window_rdkit(loc):

    global rdkit_dict_options

    col1 = [
        [
         Sg.Text('maxattempts:', size=(15, 1)),
         Sg.Input(key='-RDKIT_MAXATTEMPTS-', enable_events=True,
                  default_text=rdkit_dict_options['-RDKIT_MAXATTEMPTS-'], size=(10, 1))
        ],
        [
         Sg.Text('prunermsthresh:', size=(15, 1)),
         Sg.Input(key='-RDKIT_PRUNERMSTHRESH-', enable_events=True,
                  default_text=rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'], size=(10, 1))
        ],
        [
            Sg.Text('cluster_threshold:', size=(15, 1)),
            Sg.Input(key='-RDKIT_CLUSTER_THRES-', enable_events=True,
                     default_text=rdkit_dict_options['-RDKIT_CLUSTER_THRES-'], size=(10, 1))
        ],
    ]

    col2 = [
        [
         Sg.Checkbox('useexptorsionangleprefs', enable_events=True,
                     default=rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'],
                     key='-RDKIT_USEEXPTORSIONANGLEPREFS-', size=(26, 1)),

        ],
        [
         Sg.Checkbox('usebasicknowledge', enable_events=True,
                     default=rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'],
                     key='-RDKIT_USEBASICKNOWLEDGE-', size=(26, 1)),
        ],
        [
         Sg.Checkbox('enforcechirality', enable_events=True,
                     default=rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'],
                     key='-RDKIT_ENFORCECHIRALITY-', size=(26, 1)),
        ],
    ]

    row = [
        [Sg.Text('force field:', size=(15, 1)),
         Sg.Combo(['MMFF', 'UFF'], enable_events=True, disabled=False, key='-RDKIT_FFNAME-',
                  default_value=rdkit_dict_options['-RDKIT_FFNAME-'], size=(40, 1))],
        [Sg.Text('cluster method:', size=(15, 1)),
         Sg.Combo(['RMSD', 'TFD'], enable_events=True, disabled=False, key='-RDKIT_CLUSTER_METHOD-',
                  default_value=rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'], size=(40, 1))]
    ]

    row_buttons = Sg.Column([
        [Sg.Button('Default Values', key='-RDKIT_DEFAULTVALUES-', disabled=False, size=(40, 1), enable_events=True),
         Sg.Button('CLOSE', key='-RDKIT_CLOSE-', disabled=False, size=(40, 1), enable_events=True)]
    ], )

    layout = [[Sg.Text("RDKIT options", justification='c', size=(500, 1),
                       key='-LINK_RDKITOPTIONS-', enable_events=True)],
              [Sg.Column(col1), Sg.Column(col2)], [row], [row_buttons]]
    window2 = Sg.Window("RDKIT options docs", layout, modal=True, location=loc,
                        background_color='lightblue', size=(550, 260))

    while True:

        event2, values2 = window2.read()

        if event2 == '-LINK_RDKITOPTIONS-':
            url = "https://www.rdkit.org/docs/source/rdkit.Chem.rdDistGeom.html"
            webbrowser.open(url)

        if event2 == "Exit" or event2 == Sg.WIN_CLOSED:
            break

        if event2 == '-RDKIT_CLOSE-':
            break

        if event2 == '-RDKIT_MAXATTEMPTS-':
            rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] = window2['-RDKIT_MAXATTEMPTS-'].get()
        if event2 == '-RDKIT_PRUNERMSTHRESH-':
            rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] = window2['-RDKIT_PRUNERMSTHRESH-'].get()
        if event2 == '-RDKIT_USEEXPTORSIONANGLEPREFS-':
            rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = window2['-RDKIT_USEEXPTORSIONANGLEPREFS-'].get()
        if event2 == '-RDKIT_USEBASICKNOWLEDGE-':
            rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = window2['-RDKIT_USEBASICKNOWLEDGE-'].get()
        if event2 == '-RDKIT_ENFORCECHIRALITY-':
            rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = window2['-RDKIT_ENFORCECHIRALITY-'].get()
        if event2 == '-RDKIT_FFNAME-':
            rdkit_dict_options['-RDKIT_FFNAME-'] = values2['-RDKIT_FFNAME-']
        if event2 == '-RDKIT_CLUSTER_METHOD-':
            rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] = values2['-RDKIT_CLUSTER_METHOD-']
        if event2 == '-RDKIT_CLUSTER_THRES-':
            rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] = window2['-RDKIT_CLUSTER_THRES-'].get()

        if event2 == '-RDKIT_DEFAULTVALUES-':
            rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] = 1000
            rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] = -0.01
            rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = True
            rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = True
            rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = True
            rdkit_dict_options['-RDKIT_FFNAME-'] = "MMFF"
            rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] = "RMSD"
            rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] = 2.0
            window2['-RDKIT_MAXATTEMPTS-'].update(rdkit_dict_options['-RDKIT_MAXATTEMPTS-'])
            window2['-RDKIT_PRUNERMSTHRESH-'].update(rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'])
            window2['-RDKIT_USEEXPTORSIONANGLEPREFS-'].update(rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'])
            window2['-RDKIT_USEBASICKNOWLEDGE-'].update(rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'])
            window2['-RDKIT_ENFORCECHIRALITY-'].update(rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'])
            window2['-RDKIT_ENFORCECHIRALITY-'].update(rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'])
            window2['-RDKIT_FFNAME-'].update(rdkit_dict_options['-RDKIT_FFNAME-'])
            window2['-RDKIT_CLUSTER_METHOD-'].update(rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'])
            window2['-RDKIT_CLUSTER_THRES-'].update(rdkit_dict_options['-RDKIT_CLUSTER_THRES-'])

    window2.close()


# =============================================================================
def open_advance_window_openbabel(loc):

    global rdkit_dict_options

    col1 = [
        [
         Sg.Text('rmsd for confab diversity:', size=(26, 1)),
         Sg.Input(key='-CONFAB_RMSD_CUTOFF-', enable_events=True,
                  default_text=openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'], size=(10, 1))
        ],
        [
         Sg.Text('energy cutoff for confab:', size=(26, 1)),
         Sg.Input(key='-CONFAB_ENERGY_CUTOFF-', enable_events=True,
                  default_text=openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'], size=(10, 1))
        ],
        [
            Sg.Text('rmsd for confab rmsddock:', size=(26, 1)),
            Sg.Input(key='-CONFAB_RMSD_CUTOFF_RMSDDOCK-', enable_events=True,
                     default_text=openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'], size=(10, 1))
        ],
        [
            Sg.Text('Maximum number of clusters:', size=(26, 1)),
            Sg.Input(key='-CONFAB_MAX_ENERGY_CLUSTERS-', enable_events=True,
                     default_text=openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'], size=(10, 1))
        ],
        [
            Sg.Text('Energy threshold for clusterize:', size=(26, 1)),
            Sg.Input(key='-CONFAB_ENERGY_THRESHOLD-', enable_events=True,
                     default_text=openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'], size=(10, 1))
        ],
    ]

    col2 = [
        [
         Sg.Checkbox('Confab verbose', enable_events=True,
                     default=openbabel_dict_options['-CONFAB_VERBOSE-'],
                     key='-CONFAB_VERBOSE-', size=(26, 1)),

        ],
    ]

    row = [
        [Sg.Text('force field:', size=(15, 1)),
         Sg.Combo(['MMFF', 'UFF'], enable_events=True, disabled=False, key='-CONFAB_FFNAME-',
                  default_value=openbabel_dict_options['-CONFAB_FFNAME-'], size=(40, 1))],
    ]

    row_buttons = Sg.Column([
        [Sg.Button('Default Values', key='-OPENBABEL_DEFAULTVALUES-', disabled=False, size=(40, 1), enable_events=True),
         Sg.Button('CLOSE', key='-OPENBABEL_CLOSE-', disabled=False, size=(40, 1), enable_events=True)]
    ], )

    layout = [[Sg.Text("OPENBABEL options", justification='c', size=(500, 1),
                       key='-LINK_OPENBABELOPTIONS-', enable_events=True)],
              [Sg.Column(col1), Sg.Column(col2)], [row], [row_buttons]]
    window3 = Sg.Window("OPENBABEL options docs", layout, modal=True, location=loc,
                        background_color='lightblue', size=(550, 280))

    while True:

        event3, values3 = window3.read()

        if event3 == '-LINK_OPENBABELOPTIONS-':
            url = 'https://openbabel.github.io/api/3.0/index.shtml'
            webbrowser.open(url)

        if event3 == "Exit" or event3 == Sg.WIN_CLOSED:
            break

        if event3 == '-OPENBABEL_CLOSE-':
            break

        if event3 == '-CONFAB_RMSD_CUTOFF-':
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = window3['-CONFAB_RMSD_CUTOFF-'].get()
        if event3 == '-CONFAB_ENERGY_CUTOFF-':
            openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = window3['-CONFAB_ENERGY_CUTOFF-'].get()
        if event3 == '-CONFAB_RMSD_CUTOFF_RMSDDOCK-':
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = window3['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'].get()
        if event3 == '-CONFAB_ENERGY_THRESHOLD-':
            openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = window3['-CONFAB_ENERGY_THRESHOLD-'].get()
        if event3 == '-CONFAB_MAX_ENERGY_CLUSTERS-':
            openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = window3['-CONFAB_MAX_ENERGY_CLUSTERS-'].get()
        if event3 == '-CONFAB_VERBOSE-':
            openbabel_dict_options['-CONFAB_VERBOSE-'] = window3['-CONFAB_VERBOSE-'].get()
        if event3 == '-CONFAB_FFNAME-':
            openbabel_dict_options['-CONFAB_FFNAME-'] = values3['-CONFAB_FFNAME-']
        if event3 == '-OPENBABEL_DEFAULTVALUES-':
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = 0.5  # Angstroms
            openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = 50  # kcal/mol
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = 2.0  # Angstroms
            openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = 99999
            openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = 100
            openbabel_dict_options['-CONFAB_VERBOSE-'] = False  # Verbose
            openbabel_dict_options['-CONFAB_FFNAME-'] = "MMFF"
            window3['-CONFAB_RMSD_CUTOFF-'].update(openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'])
            window3['-CONFAB_ENERGY_CUTOFF-'].update(openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'])
            window3['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'].update(openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'])
            window3['-CONFAB_ENERGY_THRESHOLD-'].update(openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'])
            window3['-CONFAB_MAX_ENERGY_CLUSTERS-'].update(openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'])
            window3['-CONFAB_VERBOSE-'].update(openbabel_dict_options['-CONFAB_VERBOSE-'])
            window3['-CONFAB_FFNAME-'].update(openbabel_dict_options['-CONFAB_FFNAME-'])

    window3.close()


# =============================================================================
def open_window_log(window, loc):

    layout = [[Sg.Text("View Log", justification='c', size=(500, 1))],
              [Sg.Output(size=(360, 60), key='-LOG_WINDOW-')]
              ]
    newloc = (loc[0] + 100, loc[1] + 30)
    window3 = Sg.Window("View Log", layout, modal=True, location=newloc,
                        background_color='lightblue', size=(1150, 600), finalize=True)

    filelog = os.path.join(window['-LOCAL_DIR-'].get(), window['-FILENAME_LOG-'].get())
    with open(filelog, 'r') as fin:
        lines = fin.readlines()
        window3['-LOG_WINDOW-'].update(value=lines)

    while True:
        event3, values3 = window3.read()
        if event3 == "Exit" or event3 == Sg.WIN_CLOSED:
            break


# =============================================================================
def open_window_results(window):

    global vmd_path

    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=True)
        return figure_canvas_agg

    fulldbpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-DATABASE_NAME-'].get())
    fulllogpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-FILENAME_LOG-'].get())

    # Get data from the database
    db = sqlite3.connect(fulldbpath)
    df = pd.read_sql_query("SELECT * from 'qm_jobs'", db)
    headings = df.columns.values.tolist()
    data = df.values.tolist()
    newdata = []
    for item in data:
        d = list(map(str, item))
        newdata.append(d)
    del data

    # Find names of the lowest energy conformers in each cluster
    icluster = 1
    listcluster = []
    delta_elist = []
    clusterlist = []
    with open(fulllogpath) as flog:
        stringfile = flog.read()
        try:
            tmp = stringfile.split('## Optimized conformers:\n')[1]
            result = tmp.split('## Optimized conformers')[0].split("\n")[:-1]
        except IndexError:
            result = None
        if result is not None:
            for item in result:
                listcluster.append("Cluster {0:03d}: {1:s}".format(icluster, item.replace("\t", "")))
                pattern = item.replace('\t\t\t', '').replace('_allign.mol2', '')
                clusterlist.append(icluster)
                delta_elist.append(df.loc[df["name_job"] == pattern]['DeltaE'].values[0])
                icluster += 1

    # Create plot with QM energies
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    ax.bar(clusterlist, delta_elist)
    ax.set_ylabel(r'$\Delta$E (kcal/mol)')
    ax.set_xlabel('# Cluster')
    ax.set_title('Relative energy (kcal/mol)')

    pad1 = ((5, 5), (5, 5))
    pad2 = (70, 0)
    pad3 = ((70, 0), (10, 0))
    pad4 = ((10, 0), (10, 0))
    layout = [[Sg.Text('Database results (file: {})'.format(window['-DATABASE_NAME-'].get()), size=(1000, 1),
                       background_color='white', pad=pad1, justification='center', text_color='blue', )],
              [Sg.Table(newdata, headings=headings, justification='center',
                        key='-DBTABLE-', vertical_scroll_only=False, num_rows=12, pad=pad2)],
              [Sg.Canvas(key='-CANVAS-', pad=pad3),
               Sg.Column([[Sg.Text("Lowest energy conformer of each cluster.", text_color='blue',
                                   background_color='white', justification='center', size=(51, 1))],
                          [Sg.Listbox(listcluster, size=(50, 10), background_color='white')],
                          [Sg.Text("VMD Path", text_color='blue',
                                   background_color='white', justification='center', size=(51, 1))],
                          [Sg.Input(key='-INPUTVMDPATH-', background_color='white',
                                    size=(51, 1), default_text=vmd_path)],
                          [Sg.Button("BROWSE to VMD exe", key='-BUTTONBROWSEVMD-', enable_events=True),
                           Sg.Button("Run VMD", key='-BUTTONRUNVMD-', enable_events=True)]
                          ],
               background_color='white', size=(480, 450), pad=pad4),
               ],
              ]

    loc = window.current_location()
    newloc = (loc[0] + 300, loc[1] - 50)
    window4 = Sg.Window("Results Windows", layout, finalize=True, location=newloc, size=(1200, 800),
                        background_color='white')
    draw_figure(window4['-CANVAS-'].TKCanvas, fig)

    while True:

        event4, values4 = window4.read()
        if event4 == Sg.WINDOW_CLOSED:
            break

        if event4 == "-BUTTONBROWSEVMD-":
            loc = window.current_location()
            x, y = window.size
            newloc2 = (loc[0] + (x / 2.) * 0.5, loc[1] + (y / 2.) * 0.5)
            filename = Sg.popup_get_file('Find path to vmd binary file', no_window=False,
                                         location=newloc2, file_types=(("ALL Files", "*"),))
            vmd_path = filename
            window4['-INPUTVMDPATH-'].update(filename)

        if event4 == "-BUTTONRUNVMD-":
            tclpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-PATTERN-'].get()+"_g16_conformers",
                                   "QM_optimized_conformers.tcl")
            cmd = "{} -e {}".format(vmd_path, tclpath)
            os.system(cmd)

    window4.close()


# =============================================================================
def waiting_for_events(window, event, values):
    """
    All events in the GUI
    """

    # ============= Menu Events =============
    if event == "Import Json..." or event == '-BUTTONIMPORTJSON-':
        clean_form(window)
        loc = window.current_location()
        filename = Sg.popup_get_file('Import Json file to GUI', no_window=False,
                                     location=loc, initial_folder="../tests", file_types=(("JSON Files", "*.json"),))

        import_jsonfile_to_gui(window, filename)
        window['-BUTTONCHECK-'].update(disabled=False)
        window['-BUTTONVISRESULTS-'].update(disabled=True)
        window['-BUTTONVIEWLOG-'].update(disabled=True)
        window['-STATUS_TEXT-'].update("Status: Json loaded")
        window['-SUGGEST_TEXT-'].update("Help: Try to check keywords")
        window['-HIDEPYTHONSCRIPT-'].update("")

    if event == "Export Json...":
        loc = window.current_location()
        filename = Sg.popup_get_file('Export Json from GUI', no_window=False,
                                     location=loc, initial_folder="../tests", save_as=True,
                                     file_types=(("JSON Files", "*.json"),))
        export_jsonfile_from_gui(window, save=True, filename=filename)

    if event == 'Import Pyhton Script...':
        clean_form(window)
        loc = window.current_location()
        filename = Sg.popup_get_file('Import Python file to GUI', no_window=False,
                                     location=loc, initial_folder="../tests", file_types=(("Python Files", "*.py"),))
        import_pythonfile_to_gui(window, filename)
        window['-BUTTONRUN-'].update(disabled=False)
        try:
            value = os.path.join(window['-LOCAL_DIR-'].get(), filename)
            window['-HIDEPYTHONSCRIPT-'].update(value)
            window['-STATUS_TEXT-'].update("Status: Python script loaded. ({})".format(value))
            window['-SUGGEST_TEXT-'].update("Help: Run GeCos")
            fulldbpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-DATABASE_NAME-'].get())
            if os.path.isfile(fulldbpath):
                window['-BUTTONVISRESULTS-'].update(disabled=False)
                window['-BUTTONVIEWLOG-'].update(disabled=False)
        except TypeError:
            pass

    if event == 'Write Pyhton Script...' or event == "-BUTTONCREATESCRIPT-":
        loc = window.current_location()
        filename = Sg.popup_get_file('Write Python Script from GUI', no_window=False,
                                     location=loc, initial_folder="../tests", save_as=True,
                                     file_types=(("Python Files", "*.py"),))
        # noinspection PyBroadException
        try:
            write_python_script_from_gui(window, save=True, filename=filename)
            filename = os.path.splitext(filename)[0]
            export_jsonfile_from_gui(window, save=True, filename=filename + ".json")
            window['-BUTTONRUN-'].update(disabled=False)
            value = os.path.join(window['-LOCAL_DIR-'].get(), filename+".py")
            window['-HIDEPYTHONSCRIPT-'].update(value)
            window['-STATUS_TEXT-'].update("Status: Python script created. ({})".format(value))
            window['-SUGGEST_TEXT-'].update("Help: Run GeCos")
        except TypeError:
            pass
        except Exception:
            popup_error(window, "Python file cannot be exported")

    if event == "Clean Form":
        clean_form(window)
        window['-STATUS_TEXT-'].update("Status: No data loaded")
        window['-SUGGEST_TEXT-'].update("Help: Import data from Json file or fill the forms")
        window['-HIDEPYTHONSCRIPT-'].update("")
        window['-BUTTONVIEWLOG-'].update(disabled=True)
        window['-BUTTONVISRESULTS-'].update(disabled=True)
        window['-BUTTONCHECK-'].update(disabled=True)

    if event == "About...":
        loc = window.current_location()
        window.disappear()
        Sg.popup('GeCos: Generation of Conformers', 'Version 1.0',
                 'PySimpleGUI Version', Sg.version, "Author: Javier Ramos",
                 "Biophymm Group IEM-CSIC", "Madrid (Spain)",
                 title='About this program',
                 grab_anywhere=True, location=loc, image="./lizard_small.gif")
        window.reappear()

    # ============= BUTTON EVENTS =============
    if event == '-BUTTONCHECK-':

        window['-INFORUN_TEXT-'].update("Checking input for Gecos...")
        for item in keys_all_mainguibuttons_labels:
            window[item].update(disabled=True)
        window.refresh()

        res = check_parameteres_gui(window, values)
        loc = window.current_location()
        x, y = window.size
        newloc = (loc[0] + (x / 2.)*0.5, loc[1] + (y / 2.)*0.5)
        if res:
            Sg.popup('Keywords seem to be correct!!!',
                     title='Check Inputs',
                     grab_anywhere=True, location=newloc, image="./lizard_small.gif")
            window['-BUTTONCREATESCRIPT-'].update(disabled=False)
            window['-STATUS_TEXT-'].update("Status: Keywords seem to be correct")
            window['-SUGGEST_TEXT-'].update("Help: Write python script to run conformer search")
        else:
            window['-STATUS_TEXT-'].update("Status: Keywords are not correct")
            window['-SUGGEST_TEXT-'].update("Help: Try to change incorrect parameters")

        window['-INFORUN_TEXT-'].update("Ready to submit GeCos.")
        keys_activate_mainguibuttons_labels = ['-BUTTONIMPORTJSON-', '-BUTTONCHECK-', '-BUTTONCREATESCRIPT-']
        for item in keys_activate_mainguibuttons_labels:
            window[item].update(disabled=False)

    if event == '-BUTTONADVANCE-':
        loc = window.current_location()
        x, y = window.size
        newloc = (loc[0] + (x / 2.)*0.5, loc[1] + (y / 2.)*0.5)
        if window['-CONFPACK-'].get().upper() == 'RDKIT':
            open_advance_window_rdkit(newloc)
        elif window['-CONFPACK-'].get().upper() == 'OPENBABEL':
            open_advance_window_openbabel(newloc)

    if event == '-BUTTONRUN-':

        window['-INFORUN_TEXT-'].update("Running Gecos...")
        for item in keys_all_mainguibuttons_labels:
            window[item].update(disabled=True)
        window.refresh()

        fulldbpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-DATABASE_NAME-'].get())
        donepath = os.path.join(window['-LOCAL_DIR-'].get(), "done")
        if os.path.isfile(donepath):
            msg = "GeCos calculation seems to be finished."
            popup_msg(window, msg)
            window['-STATUS_TEXT-'].update("Status: Conformers calculated")
            window['-SUGGEST_TEXT-'].update("Help: Visualize Results")
        else:
            if not os.path.isfile(fulldbpath):
                msg = "Database is not available. GeCos will run conformer search."
                popup_msg(window, msg)
                window['-STATUS_TEXT-'].update("Status: Starting QM calculations.")
                window['-SUGGEST_TEXT-'].update("Help: Run GeCos to update results.")
            else:
                msg = "Database exists. GeCos will check the calculations."
                popup_msg(window, msg)
                window['-STATUS_TEXT-'].update("Status: Running QM calculations.")
                window['-SUGGEST_TEXT-'].update("Help: Run GeCos to check results.")

            if window['-HIDEPYTHONSCRIPT-'].get() == "":
                loc = window.current_location()
                filename = Sg.popup_get_file('Load python script to run GeCos', no_window=False,
                                             location=loc, initial_folder="../tests",
                                             file_types=(("Python Files", "*.py"),))
            else:
                filename = window['-HIDEPYTHONSCRIPT-'].get()

            import_pythonfile_to_gui(window, filename)

            os.system("python "+filename)

        window['-BUTTONVIEWLOG-'].update(disabled=False)
        window['-BUTTONVISRESULTS-'].update(disabled=False)
        window['-INFORUN_TEXT-'].update("Ready to submit GeCos.")
        for item in keys_all_mainguibuttons_labels:
            window[item].update(disabled=False)

    if event == '-BUTTONVISRESULTS-':
        open_window_results(window)

    if event == '-BUTTONVIEWLOG-':
        loc = window.current_location()
        open_window_log(window, loc)

    if event in keys_input_str_labels:
        window['-BUTTONCHECK-'].update(disabled=False)
        window['-STATUS_TEXT-'].update("Status: Data introduced by the user")
        window['-SUGGEST_TEXT-'].update("Help: Try to check keywords")

    # ============= URL Events =============
    if event == "-DOCK_URL-":
        url = window['-DOCK_URL-'].get()
        webbrowser.open(url)

    if event == "-CONF_URL-":
        package = window['-CONFPACK-'].get()
        # print(package)

        if package.upper() == "RDKIT":
            url = "https://www.rdkit.org/"
            webbrowser.open(url)
        elif package.upper() == "OPENBABEL":
            url = "https://openbabel.org/wiki/Python"
            webbrowser.open(url)

    if event == '-LINK_AUTHOR-':
        url = "https://scholar.google.es/citations?user=ZSw8w94AAAAJ&hl=es"
        webbrowser.open(url)

    if event == '-LINK_DOCS-':
        cwd = os.getcwd()
        # print(cwd)
        url = "file://" + cwd + "/../docs/_build/html/index.html"
        webbrowser.open(url)

    if event == '-LINK_GITHUB-':
        url = "https://github.com/jrdcasa?tab=repositories"
        webbrowser.open(url)

    # ============= Hoover mouse. Change Color =============
    if event == "-DOCK_URL-+MOUSE OVER+":
        window['-DOCK_URL-'].update(text_color="green")
    if event == "-DOCK_URL-+MOUSE AWAY+":
        window['-DOCK_URL-'].update(text_color="blue")

    if event == "-CONF_URL-+MOUSE OVER+":
        window['-CONF_URL-'].update(text_color="green")
    if event == "-CONF_URL-+MOUSE AWAY+":
        window['-CONF_URL-'].update(text_color="blue")

    if event == "-LINK_AUTHOR-+MOUSE OVER+":
        window['-LINK_AUTHOR-'].update(text_color="green")
    if event == "-LINK_AUTHOR-+MOUSE AWAY+":
        window['-LINK_AUTHOR-'].update(text_color="black")

    if event == "-LINK_DOCS-+MOUSE OVER+":
        window['-LINK_DOCS-'].update(text_color="green")
    if event == "-LINK_DOCS-+MOUSE AWAY+":
        window['-LINK_DOCS-'].update(text_color="black")

    if event == "-LINK_GITHUB-+MOUSE OVER+":
        window['-LINK_GITHUB-'].update(text_color="green")
    if event == "-LINK_GITHUB-+MOUSE AWAY+":
        window['-LINK_GITHUB-'].update(text_color="black")

    if event == "-GAUSSIAN16_URL-+MOUSE OVER+":
        window['-GAUSSIAN16_URL-'].update(text_color="green")
    if event == "-GAUSSIAN16_URL-+MOUSE AWAY+":
        window['-GAUSSIAN16_URL-'].update(text_color="black")
