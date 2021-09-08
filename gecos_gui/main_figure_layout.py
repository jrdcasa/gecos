import PySimpleGUI as Sg


lizard_gif = r'/home/jramos/PycharmProjects/GeCos/gecos_gui/lizard_small.gif'
pad1 = ((28, 60), (28, 60))
pad2 = (20, 30)
pad3 = ((0, 0), (0, 0))
pad4 = (30, 30)
text1 = '    GeCos:\n' \
        'Generation\n' \
        '       of\n' \
        'Conformers'
text2 = 'Gecos\nDocumentation'
text3 = 'Author:\n  Javier Ramos\n     IEM-CSIC'
text4 = 'Github'
image_layout = Sg.Column([
                [Sg.Text(text1, key='-TITLE-', pad=pad2, font=('Expansiva', 12))],
                [Sg.Image(lizard_gif, key='-IMAGE_LIZARD-', pad=pad1)],
                [Sg.Text(text2, key='-LINK_DOCS-', pad=pad3, font=('Expansiva', 10),enable_events=True)],
                [Sg.Text(text4, key='-LINK_GITHUB-', pad=pad4, font=('Expansiva', 12), enable_events=True)],
                [Sg.Text(text3, key='-LINK_AUTHOR-', pad=pad3, font=('Expansiva', 10), enable_events=True), ],
],  size=(160, 600))



