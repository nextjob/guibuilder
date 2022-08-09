# guibuilertester.py
# script to excute (display) pysimplegui layout defined in guibuildertestlayoutfile
import PySimpleGUI as sg
import guibuildertestlayoutfile
import importlib


layout = guibuildertestlayoutfile.layout
oldtimestamp = str(guibuildertestlayoutfile.timestamp)

location = (10,10)
window = sg.Window('Window Title', location=location).Layout(layout)

while True:             # Event Loop
    event, values = window.read(timeout=100)
    if event is None or event == 'Exit':
        break
    if event == sg.TIMEOUT_KEY:
        try:
            importlib.reload(guibuildertestlayoutfile)
        except Exception as e:
            sg.popup('Syntax Error?', f"{type(e)}: {e}") 
            quit()
        layout = guibuildertestlayoutfile.layout
        timestamp = str(guibuildertestlayoutfile.timestamp)
        if timestamp == oldtimestamp:
            pass
        else:
            try:
                window1 = sg.Window('Window Title', location=location).Layout(layout)
                oldtimestamp = str(guibuildertestlayoutfile.timestamp)
                window.Close()
                window = window1
            except Exception as e:
                    sg.popup('Window error?', f"{type(e)}: {e}")
                    quit()  
window.Close()