import PySimpleGUI as Sg
from gecos_gui.general_inputs_tab import general_inputs_layout
from gecos_gui.common_elements import theme

Sg.ChangeLookAndFeel(theme)

tabgroup_layout = Sg.TabGroup([
                   [Sg.Tab('General Inputs', general_inputs_layout)],
                 ], key="-TABGROUP-")

tabgroup_layout_col = Sg.Column([
                            [tabgroup_layout]
                        ])
