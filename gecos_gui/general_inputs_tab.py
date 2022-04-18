import PySimpleGUI as Sg
from gecos_gui.common_elements import theme


Sg.ChangeLookAndFeel(theme)

molecule_input = Sg.Frame(title="Molecule Input",
                          layout=[
                              [Sg.Text('Molecule file:', size=(12, 1)),
                               Sg.Input(key='-MOLECULE_INPUT-', size=(120, 1),
                                        tooltip='Allowed files: pdb, mol2, sdf.', enable_events=True),
                               Sg.FileBrowse(button_text="Browse", key="-MOLECULE_INPUT_BROWSER-",
                                             file_types=(('ALL Files', '*'),),)]
                          ], title_color='blue', pad=((20, 20), (10, 10)))

pad1 = ((5, 5), (5, 5))
pad2 = ((5, 5), (5, 5))
pad3 = ((0, 150), (5, 5))

server_input = Sg.Frame(title="Server Options",
                        layout=[
                            [Sg.Text('Name server:', size=(18, 1), pad=pad1),
                             Sg.Input(key='-NAME_SERVER-', size=(20, 1), enable_events=True,
                                      tooltip='Name of the remote server to perform QM calculations.', pad=pad1),
                             Sg.Text('Username:', size=(9, 1), pad=pad1),
                             Sg.Input(key='-USER_NAME-', size=(20, 1), enable_events=True,
                                      tooltip='Username to connect in the remote server.', pad=pad1),
                             Sg.Text('Key SSH file:', size=(14, 1), pad=pad2),
                             Sg.Input(key='-KEY_SSH_FILE-', size=(52, 1), enable_events=True,
                                      tooltip='Private key for SSH connection.', pad=pad1),
                             Sg.FileBrowse(button_text="Browse", key='-KEY_SSH_BROWSER-', pad=pad1,
                                           file_types=(('ALL Files', '*'),)),
                             ],
                            [
                              Sg.Text('Encrypted passwd file:', size=(18, 1), pad=pad1),
                              Sg.Input(key='-ENCRYPT_PASS_FILE-', size=(52, 1), enable_events=True,
                                       tooltip='Encrypted file containing the pass for a SSH connection.',
                                       pad=pad1, disabled=True),

                              Sg.Text('SLURM partition:', size=(14, 1), pad=pad1),
                              Sg.Input(key='-SLURM_PART-', size=(16, 1), enable_events=True,
                                       tooltip='SLURM partition to perform QM calculations.', pad=pad1),
                              Sg.Text('SLURM partition master:', size=(20, 1), pad=pad1),
                              Sg.Input(key='-SLURM_PART_MASTER-', size=(23, 1), enable_events=True,
                                       tooltip='SLURM partition to run the deamon script.', pad=pad1),
                             ],
                            [
                             Sg.Text('Exclude Nodes:', size=(18, 1), pad=pad1),
                             Sg.Input(key='-EXCLUDE_NODES-', size=(70, 1), enable_events=True,
                                      tooltip='Nodes excluded in the partition.', pad=pad3),

                             Sg.Text('Node Master:', size=(20, 1), pad=pad1),
                             Sg.Input(key='-NODE_MASTER-', size=(23, 1), enable_events=True,
                                      tooltip='Node to run the daemon script.', pad=pad1),

                             ],
                          ], title_color='blue', pad=((20, 20), (10, 10)))

directories = Sg.Frame(title="Directories",
                       layout=[
                           [Sg.Text('Local dir:', size=(10, 1), pad=pad1),
                            Sg.Input(key='-LOCAL_DIR-', size=(112, 1), enable_events=True,
                                     tooltip='Local directory to put the outputs. '
                                             'The directory must exist in the local server', pad=pad1),
                            Sg.FolderBrowse(button_text="Browse", key='-LOCAL_DIR_BROWSER-'),
                            ],
                           [Sg.Text('Remote dir:', size=(10, 1), pad=pad1),
                            Sg.Input(key='-REMOTE_DIR-', size=(112, 1), enable_events=True,
                                     tooltip='Remote directory where QM calculation carry out. '
                                             'The directory must exist in the remote server', pad=pad1),
                            ],
                           [Sg.Text('Pattern:', size=(10, 1), pad=pad1),
                            Sg.Input(key='-PATTERN-', size=(20, 1), enable_events=True,
                                     tooltip='Pattern used to give the name to the generated files.', pad=pad1),
                            Sg.Text('Database Name:', size=(14, 1), pad=pad1),
                            Sg.Input(key='-DATABASE_NAME-', size=(20, 1), enable_events=True,
                                     tooltip='Name of the database.', pad=pad1),
                            Sg.Text('Filename Log:', size=(14, 1), pad=pad1),
                            Sg.Input(key='-FILENAME_LOG-', size=(38, 1),
                                     tooltip='Name of the database.', pad=pad1, enable_events=True),
                            ],
                          ], title_color='blue', pad=((20, 20), (10, 10)))

gaussian_col = Sg.Column([
    [Sg.Frame('Gaussian Keywords',
              layout=[
                        [Sg.Text('G16 keywords:', size=(14, 1)),
                         Sg.Input(key='-G16_KEYWORDS-', size=(44, 1),
                                  tooltip='Keywords for Gaussian16.', pad=pad1, enable_events=True)
                         ],
                        [Sg.Text('G16 nproc:', size=(14, 1)),
                         Sg.Input(key='-G16_NPROC-', size=(5, 1),
                                  tooltip='Number of processors for Gaussian16.', pad=pad1, enable_events=True),
                         Sg.Text('G16 mem (Mb):', size=(14, 1)),
                         Sg.Input(key='-G16_MEM-', size=(5, 1),
                                  tooltip='Amount of memory in Mb for Gaussian16.', pad=pad1, enable_events=True),
                         Sg.Checkbox('Write Gaussian', key='-WRITE_GAUSSIAN-',
                                     pad=pad1, enable_events=True, default=True)
                         ],
                        [Sg.Text('Charge:', size=(14, 1)),
                         Sg.Input(key='-CHARGE-', size=(5, 1), default_text=0,
                                  tooltip='Total molecular charge.', pad=pad1, enable_events=True),
                         Sg.Text('Multiplicity:', size=(14, 1)),
                         Sg.Input(key='-MULTIPLICITY-', size=(5, 1), default_text=1,
                                  tooltip='Molecular multiplicity for Gaussian16.', pad=pad1, enable_events=True),
                   ],
                ], title_color='blue', pad=pad1)
     ],
    [Sg.Frame('Path to the Gaussian16 program.',
              layout=[
                        [Sg.Input(key='-GAUSSIAN16PACK-', size=(60, 1),
                                  tooltip='Path to the Gaussian16 program.', pad=pad1, enable_events=True),
                         ],
                        [Sg.Text("Gaussian program: ", size=(16, 1),
                                 pad=pad1, text_color='red'),
                         Sg.Text('https://gaussian.com/keywords/', size=(40, 1),
                                 enable_events=True, key="-GAUSSIAN16_URL-", pad=pad1, text_color='blue')
                         ],
                ], title_color='blue', pad=pad1)
    ]
])

conformers_col = Sg.Column([
    [Sg.Frame('Conformers Keywords',
              layout=[
                        [Sg.Text("Conformer program: ", size=(18, 1), pad=pad1),
                         Sg.Combo(['rdkit', 'openbabel'], disabled=False, key='-CONFPACK-', default_value='rdkit',
                                  size=(40, 1), pad=pad1, enable_events=True),
                         Sg.Text("URL", enable_events=True, key="-CONF_URL-", text_color='blue'),
                         Sg.Button('Advanced options', key='-BUTTONADVANCE-', disabled=False)],
                        [Sg.Text('Number of Conformers:', size=(22, 1), enable_events=True),
                         Sg.Input(key='-NCONF-', size=(8, 1),
                                  tooltip='Initial number of conformers.', pad=pad1, enable_events=True),
                         Sg.Text('Cutoff RMSD Cluster QM (A):', size=(24, 1), enable_events=True),
                         Sg.Input(key='-CUTOFF_RMSD_QM-', size=(12, 1),
                                  tooltip='Cutoff to clusterize the conformers after QM calculations.', pad=pad1,
                                  enable_events=True)
                         ],
                        [Sg.Text('Minimize Iterations MM:', size=(22, 1), enable_events=True),
                         Sg.Input(key='-MIN_ITER_MM-', size=(8, 1),
                                  tooltip='Number of iterations to minimize the conformers.', pad=pad1,
                                  enable_events=True),
                         Sg.Checkbox('Bond Perception', key='-BOND_PERCEPTION-', size=(45, 2),
                                     pad=pad1, enable_events=True, default=True)
                         ],
                ], title_color='blue', pad=((20, 20), (10, 10)))
     ],
    [Sg.Frame('Path to the DockRMSD program.',
              layout=[
                  [Sg.Input(key='-DOCKRMSDPACK-', size=(60, 1),
                            tooltip='Path to the DockRMSD program.', pad=pad1),
                   ],
                  [Sg.Text("DockRMSD program: ", size=(16, 1),
                           pad=pad1, text_color='red'),
                   Sg.Text('https://zhanglab.ccmb.med.umich.edu/DockRMSD/', size=(46, 1),
                           enable_events=True, key="-DOCK_URL-", pad=pad1, text_color='blue')
                   ],
              ], title_color='blue', pad=((20, 20), (10, 10)))
     ]
])

hide_input = Sg.Input(key='-HIDEINPUTSCRIPT-', visible=False)

general_inputs_layout = [[molecule_input], [server_input], [directories], [gaussian_col, conformers_col], [hide_input]]
