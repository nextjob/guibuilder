# guibuilertester.py
# script to excute (display) pysimplegui layout defined in guibuildertestlayoutfile
import PySimpleGUI as sg
import guibuildertestlayoutfile
import importlib

layout = guibuildertestlayoutfile.layout
oldtimestamp = str(guibuildertestlayoutfile.timestamp)

location = (600,600)
window = sg.Window('Window Title', location=location).Layout(layout)

while True:             # Event Loop
    event, values = window.read(timeout=100)
    if event is None or event == 'Exit':
        break
    if event == sg.TIMEOUT_KEY:
        importlib.reload(guibuildertestlayoutfile)
        layout = guibuildertestlayoutfile.layout
        timestamp = str(guibuildertestlayoutfile.timestamp)
        if timestamp == oldtimestamp:
            pass
        else:
            window1 = sg.Window('Window Title', location=location).Layout(layout)
            oldtimestamp = str(guibuildertestlayoutfile.timestamp)
            window.Close()
            window = window1

window.Close()