import PySimpleGUI as sg

headings = ['President', 'Date of Birth', 'Hola']

data = [
    ['Ronald Reagan', 'February 6', 3],
    ['Abraham Lincoln', 'February 12', 3],
    ['George Washington', 'February 22', 4],
    ['Andrew Jackson', 'March 15', 6],
    ['Thomas Jefferson', 'April 13', 5],
    ['Harry Truman', 'May 8', 4],
    ['John F. Kennedy', 'May 29', 2],
    ['George H. W. Bush', 'June 12', 2],
    ['George W. Bush', 'July 6', 2],
    ['John Quincy Adams', 'July 11', 2],
    ['Garrett Walker', 'July 18'],
    ['Bill Clinton', 'August 19'],
    ['Jimmy Carter', 'October 1'],
    ['John Adams', 'October 30'],
    ['Theodore Roosevelt', 'October 27'],
    ['Frank Underwood', 'November 5'],
    ['Woodrow Wilson', 'December 28'],
]

layout = [[sg.Table(data, headings=headings, justification='left', key='-TABLE-', vertical_scroll_only=False)],]
window = sg.Window("Title", layout, finalize=True, resizable=True, location=(100, 100), size=(500, 500))

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    print(event, values)

window.close()