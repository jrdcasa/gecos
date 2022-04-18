import json
import re


# =============================================================================
def import_jsonfile_to_gui(window, filename, rdkit_dict_options,
                           openbabel_dict_options, pass_encrypted_file):
    """
    Use a json file containing the keywords for GeCos and load the parameters in the GUI

    Args:
        window: window instance
        filename: json file
        rdkit_dict_options:
        pass_encrypted_file:

    """

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
                    if data[item] != 0:
                        window['-G16_NPROC-'].update(data[item])
            elif item.upper() == "G16_MEM":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"g16_mem:\" must be an integer.")
                    return False
                else:
                    if data[item] != 0:
                        window['-G16_MEM-'].update(data[item])
            elif item.upper() == "NCONFS":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"nconfs:\" must be an integer.")
                    return False
                else:
                    if data[item] != 0:
                        window['-NCONF-'].update(data[item])
            elif item.upper() == "MINIMIZE_ITERATIONS":
                if not isinstance(data[item], int):
                    popup_error(window, "Json error: \"minimize_iterations:\" must be an integer.")
                    return False
                else:
                    if data[item] != 0:
                        window['-MIN_ITER_MM-'].update(data[item])
            elif item.upper() == "CUTOFF_RMSD_QM":
                if not isinstance(data[item], float):
                    try:
                        if float(data[item]) > 0.01:
                            window['-CUTOFF_RMSD_QM-'].update(float(data[item]))
                    except:
                        popup_error(window, "Json error: \"cutoff_rmsd_QM:\" must be a float.")
                        return False
                else:
                    if data[item] > 0.01:
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
                pass_encrypted_file = data[item]
                window['-ENCRYPT_PASS_FILE-'].update(data[item])

        keys_activate_mainguibuttons_labels = ['-BUTTONRUN-', '-BUTTONCREATESCRIPT-',
                                               '-BUTTONVISRESULTS-', '-BUTTONVIEWLOG-']
        for item in keys_activate_mainguibuttons_labels:
            window[item].update(disabled=True)


# =============================================================================
def import_pythonfile_to_gui(window, filename, rdkit_dict_options):

    """
    Use a json file containing the keywords for GeCos and load the parameters in the GUI

    Args:
        window: window instance
        filename: python file
        rdkit_dict_options:

    """

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
        'v_localdir': '-LOCAL_DIR-',
        'v_remotedir': '-REMOTE_DIR-',
        'v_pattern ': '-PATTERN-',
        'v_g16_keywords': '-G16_KEYWORDS-',
        'v_dockrmsdpack': '-DOCKRMSDPACK-',
        'v_g16path': '-GAUSSIAN16PACK-',
    }

    var_to_encrypt = {'v_encrypt_pass': '-ENCRYPT_PASS_FILE-',
                      'v_node_master': '-NODE_MASTER-',
    }

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
                    value = tmp.group(0)
                    value = value.replace("'", "")
                    value = value.replace("\"", "")
                    label = var_to_encrypt[ikey]
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
def import_pythonfileprops_to_gui(window, filename):

    # If filename None, the CANCEL button has been pushed
    if filename is None or len(filename) == 0:
        return False

    var_to_dict_str = {
        'p_nameserver': '-NAME_SERVER-',
        'p_username': '-USER_NAME-',
        'p_keysshfile': '-KEY_SSH_FILE-',
        'p_slurm_part': '-SLURM_PART-',
        'p_slurm_part_master': '-SLURM_PART_MASTER-',
        'p_g16path': '-GAUSSIAN16PACK-',
        'p_g16_keywords': '-KEYWORD_LINE-',
        'p_localdir_mol2conf': '-QM_PROP_MOL2LOCAL_DIR-',
        'p_localdir': '-QM_PROP_LOCAL_DIR-',
        'p_remotedir': '-QM_PROP_REMOTE_DIR-'
    }

    var_to_encrypt = {'v_encrypt_pass': '-ENCRYPT_PASS_FILE-',
                      'v_node_master': '-NODE_MASTER-',
    }

    var_to_dict_list = {
        'p_list_nodes': '-EXCLUDE_NODES-',
    }

    var_to_dict_intfloat = {
        'p_ncpus': '-G16_NPROC-',
        'p_mem': '-G16_MEM-',
        'p_charge': '-CHARGE-',
        'p_multiplicity': '-MULTIPLICITY-',
    }

    var_to_dict_pathlast = {
        'p_databasefullpath': '-INPUT_DATABASE_PROP-',
        'p_fileoutputfullpath': '-INPUT_LOG_PROP-'
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

        for ikey in var_to_dict_intfloat.keys():
            regex = ikey+".*="
            if re.search(regex, data) is not None:
                value = re.search(ikey+".*=.*", data).group(0)
                value = value.split("=")[-1]
                label = var_to_dict_intfloat[ikey]
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

        for ikey in var_to_encrypt.keys():
            regex = ikey + ".*="
            if re.search(regex, data) is not None:
                str2 = re.search(ikey + ".*=.*", data).group(0)
                # value = re.search("(?:'|\").*(?:'|\")", str2).group(0)
                tmp = re.search("(?:['\"]).*(?:['\"])", str2)
                if tmp is not None:
                    value = tmp.group(0)
                    value = value.replace("'", "")
                    value = value.replace("\"", "")
                    label = var_to_encrypt[ikey]
                    window[label].update(value)

        # Extract parameters from the Keyword_line
        tokens = window['-KEYWORD_LINE-'].get().split()
        tokens_str = ' '.join(tokens)
        method, basisset = tokens[1].split("/")

        try:
            solvent_model = [string for string in tokens if "scrf" in string][0].split("(")[-1][0:-1]
        except:
            solvent_model = 'None'

        try:
            solvent = [string for string in tokens if "solvent" in string][0].split("=")[-1][0:-1]
        except:
            solvent = 'None'
        if solvent == '':
            solvent = 'None'

        window['-INPUT_METHOD_PROP-'].update(value=method)
        window['-INPUT_BASISSET_PROP-'].update(value=basisset)
        window['-COMBO_MODELSOLVENT_PROP-'].update(value=solvent_model)
        window['-COMBO_SOLVENT_PROP-'].update(value=solvent)

        if tokens_str.count("freq") == 1:
            window['-RADIO_FREQ-'].update(True)
            if tokens_str.count("scale") == 1:
                v = float([string for string in tokens if "scale" in string][0].split("=")[-1])
                window['-INPUT_SCALEVAL_FREQ-'].update(value=v, disabled=False, text_color='black')
            if tokens_str.count("anharm") == 1:
                window['-CHECKBOX_ANHAR_FREQ-'].update(value=True, disabled=False, text_color='black')
        elif tokens_str.count("wfn") == 1:
            window['-RADIO_ESPWFN-'].update(True)
        else:
            window['-RADIO_SP-'].update(True)

        window['-G16_KEYWORDS-'].update(window['-KEYWORD_LINE-'].get())

        window['-PROP_HIDEINPUTSCRIPT-'].update(value=filename)
