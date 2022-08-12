# guibuiler_tester.py
# script to excute (display) pysimplegui layout defined in guibuildertestlayoutfile
import PySimpleGUI as sg

import importlib

try:
    import guibuilder_test_layout_file
except Exception as e:
    sg.popup('Syntax Error in guibuilder_test_layout_file?', f"{type(e)}: {e}",location = (15,15)) 
    quit()

layout = guibuilder_test_layout_file.layout

location = (10,10)
window = sg.Window('Window Title', location=location).Layout(layout)

while True:             # Event Loop
    event, values = window.read()
    if event is None or event == 'Exit':
        break

window.Close()