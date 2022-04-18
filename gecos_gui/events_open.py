import PySimpleGUI as Sg
import os
import sqlite3
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =============================================================================
def open_advance_window_rdkit(loc, rdkit_dict_options):

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
         Sg.Combo(['RMSD'], enable_events=True, disabled=False, key='-RDKIT_CLUSTER_METHOD-',
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
            rdkit_dict_options = defaultdict()
            rdkit_dict_options['-RDKIT_MAXATTEMPTS-'] = 1000
            rdkit_dict_options['-RDKIT_PRUNERMSTHRESH-'] = -0.01
            rdkit_dict_options['-RDKIT_USEEXPTORSIONANGLEPREFS-'] = True
            rdkit_dict_options['-RDKIT_USEBASICKNOWLEDGE-'] = True
            rdkit_dict_options['-RDKIT_ENFORCECHIRALITY-'] = True
            rdkit_dict_options['-RDKIT_FFNAME-'] = "MMFF"
            rdkit_dict_options['-RDKIT_CLUSTER_METHOD-'] = "RMSD"
            rdkit_dict_options['-RDKIT_CLUSTER_THRES-'] = 0.5
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
def open_advance_window_openbabel(loc, openbabel_dict_options):

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
            openbabel_dict_options = defaultdict()
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF-'] = 0.5  # Angstroms
            openbabel_dict_options['-CONFAB_ENERGY_CUTOFF-'] = 50.0  # kcal/mol
            openbabel_dict_options['-CONFAB_VERBOSE-'] = False  # Verbose
            openbabel_dict_options['-CONFAB_RMSD_CUTOFF_RMSDDOCK-'] = 0.5  # Angstroms
            openbabel_dict_options['-CONFAB_FFNAME-'] = "MMFF"
            openbabel_dict_options['-CONFAB_ENERGY_THRESHOLD-'] = 99999.0
            openbabel_dict_options['-CONFAB_MAX_ENERGY_CLUSTERS-'] = 100
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
              [Sg.Multiline(size=(360, 60), key='-LOG_WINDOW-', horizontal_scroll=True)]
              ]
    newloc = (loc[0] + 100, loc[1] + 30)
    window3 = Sg.Window("View Log", layout, modal=True, location=newloc,
                        background_color='lightblue', size=(1250, 700), finalize=True)

    filelog = os.path.join(window['-LOCAL_DIR-'].get(), window['-FILENAME_LOG-'].get())
    with open(filelog, 'r') as fin:
        lines = ""
        for iline in fin.readlines():
            lines += iline
        window3['-LOG_WINDOW-'].update(value=lines)

    while True:
        event3, values3 = window3.read()
        if event3 == "Exit" or event3 == Sg.WIN_CLOSED:
            break


# =============================================================================
def open_window_results(window, vmd_path):

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
    # fig, ax = plt.subplots()
    ax.bar(clusterlist, delta_elist)
    ax.set_ylabel(r'$\Delta$E (kcal/mol)')
    ax.set_xlabel('# Cluster')
    ax.set_title('Relative energy (kcal/mol)')

    pad1 = ((5, 5), (5, 5))
    pad2 = (70, 0)
    pad3 = ((50, 0), (10, 0))
    pad4 = ((10, 0), (10, 0))
    layout = [[Sg.Text('Database results (file: {})'.format(window['-DATABASE_NAME-'].get()), size=(1000, 1),
                       background_color='white', pad=pad1, justification='center', text_color='blue', )],
              [Sg.Table(newdata, headings=headings, justification='center',
                        key='-DBTABLE-', vertical_scroll_only=False, num_rows=12, pad=pad2)],
              [Sg.Canvas(key='-CANVAS-', pad=pad3, size=(480, 450)),
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
            if len(filename) > 2:
                vmd_path = filename
                window4['-INPUTVMDPATH-'].update(filename)

        if event4 == "-BUTTONRUNVMD-":
            tclpath = os.path.join(window['-LOCAL_DIR-'].get(), window['-PATTERN-'].get()+"_g16_conformers",
                                   "QM_optimized_conformers.tcl")
            cmd = "{} -e {}".format(vmd_path, tclpath)
            os.system(cmd)

    window4.close()
