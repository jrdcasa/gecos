import PySimpleGUI as Sg
from general_inputs_tab import general_inputs_layout
# from zoptions_tab import zoptions_layout
# from qmlayout_tab import qm_layout
from common_elements import theme
# from server_tab import server_layout
# from result_tab import result_layout
# from mc_tab import mc_layout

Sg.ChangeLookAndFeel(theme)

tabgroup_layout = Sg.TabGroup([
                   [Sg.Tab('General Inputs', general_inputs_layout)],
                 ], key="-TABGROUP-")

tabgroup_layout_col = Sg.Column([
                            [tabgroup_layout]
                        ])

# tabgroup_layout = sg.TabGroup([[
#                   sg.Tab('General Inputs', general_inputs_layout),
#                   sg.Tab('Results', result_layout),
#                 ]], key="-TABGROUP-")

