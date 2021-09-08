import PySimpleGUI as Sg

theme = "LightGrey3"
Sg.set_options(text_justification='left', font=("Noto Sans", 11))
Sg.ChangeLookAndFeel(theme)

row_buttons = Sg.Column([
        [Sg.Button('Import data from Json', key='-BUTTONIMPORTJSON-', disabled=False),
         Sg.Button('Check Inputs', key='-BUTTONCHECK-', disabled=True),
         Sg.Button('Run GeCos', key='-BUTTONRUN-', disabled=True),
         Sg.Button('Create Python Script', key='-BUTTONCREATESCRIPT-', disabled=True),
         Sg.Button('Visualize Results', key='-BUTTONVISRESULTS-', disabled=True),
         Sg.Button('View Log', key='-BUTTONVIEWLOG-', disabled=True)]
   ], pad=((350, 10), (30, 00)))

status_label = Sg.Text(text="Status: No data loaded", key='-STATUS_TEXT-', size=(120, 1))
suggest_label = Sg.Text(text="Help: Import data from Json file or fill the forms", key='-SUGGEST_TEXT-', size=(120, 1))
inforun_label = Sg.Text(text="Ready to submit GeCos.", key='-INFORUN_TEXT-',
                        size=(120, 1), background_color="lightblue", font=('Expansiva', 10), justification='center')


python_script = Sg.Text('', key='-HIDEPYTHONSCRIPT-', visible=False)