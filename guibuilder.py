"""
How this works (or should work)
 1) User defines widgets, placing on layout table via row / column vars
   - do not allow overwrite 
   - does table auto grow this extra cell in row??

   Do we create "layout" variables at this point?       <---- at this step!
    - write this data out to the editor 
    - requires some sort of a template pysimplegui script to start from
    - with "tags" for areas to insert text?
        - means we need to parse tempalte before we start!
        - or have the template sections hard coded into builder and output to editor as needed
 3) test layout - write editor file out and execute via invoke to python interpreter 
 use pickle to save dictionaries???
"""
"""
  A minimalist pysimplegui builder
  
  Editor based on :
  
  A minimalist Notepad built with the PySimpleGUI TKinter framework
  Author:     Israel Dryer
  Email:      israel.dryer@gmail.com
  Modified:   2020-06-20
"""
import PySimpleGUI as sg
import subprocess
import time
import pathlib
import json

import guibuilder_widgets as gw

sg.ChangeLookAndFeel('BrownBlue') # change style

# name we use to create our test view for the layouts
GUIBUILDER_TEST_FILE =  'guibuildertester.py'               # script to display layout defined in 'guibuildertestlayoutfile.py'
GUIBUILDER_TEST_LAYOUT_FILE = 'guibuildertestlayoutfile.py' # file created by this guibuilder.py 
WIN_W = 90
WIN_H = 25
MAX_PROPERTIES = 45    # max number of properties we are setup to display
#
# note column sizing is kind of a copout, still cannot get table to update size when additional columns are added.  
TABLE_COL_COUNT = 20  # number of columns to create for layout table
TABLE_ROW_COUNT = 20  # and rows
EMPTYCELL = '-       -'
#
# indexes into the data saved in the widget dictionary
#   Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'],values['-LAYOUT_ID-']]
Dflt_parms = []           # created list of widget parameter names default values
Saved_widgets = {}        # empty dictionary of saved widgets 
#                         Which is made up of a list of the following items  
WDGT_IDX = 0  # WIDGET ID (one of pysimplegui widgets)
ROW_IDX  = 1  # ROW NBR for table placement and evental layout buildup
COL_IDX  = 2  # COL NBR 
PARM_IDX  = 3  # List of parameters entered, calculated by comparing "default" widget signature to what is in the parameter explorer

# layout table values, start as empty cell
tablevalues = [[EMPTYCELL for col in range(TABLE_COL_COUNT)] for count in range(TABLE_ROW_COUNT)]
layoutvalues = [[EMPTYCELL for col in range(TABLE_COL_COUNT)] for count in range(TABLE_ROW_COUNT)] 


file = None

# Popen object from execute_py_file, used to view layout in new sub process, need to save global to terminate
subprocess_Popen = None

# row currently selected on widget and layout tables
selected_layout_row = 0
selected_widget_row = 0

def parm_inspector(parm_list):
# take the list of parameters for a widget and place them in the "object inspector"
# which is nothing more than a series of input widgets
# and returns a list of default parameters name / value / parameter index 
    dflt_props = []
    parm_cnt = len(parm_list)
    for i in range(MAX_PROPERTIES):
        if i < parm_cnt:
            element = str(parm_list[i]).split("=")
            parm_name = str(element[0]).strip()
            
            if len(element) == 2:
                parm_value = str(element[1]).strip()
                window[f'-PARM_VALUE_KEY{i}-'].update(value = parm_value)
            else:
                window[f'-PARM_VALUE_KEY{i}-'].update(value = '')
                parm_value = ''

            window[f'-PARM_NAME_KEY{i}-'].update(value = parm_name)
            dflt_props.append([parm_name,parm_value,i])
        else:
            window[f'-PARM_VALUE_KEY{i}-'].update(value = '')
            window[f'-PARM_NAME_KEY{i}-'].update(value = '')
    return dflt_props

def save_widget(values):
    global Saved_widgets
# save the widget currently displayed on the entry screen / parameter inspector 
# then place it on the "layout" table
# do some error checking first 
# rem - values['-key-'] return a list
# and an empty list is false (implicit booleanness of the empty list)
    if not values['-SEL_WIDGET-']:
        sg.popup('No Widget Selected')
        return
    if not values['-WIDGET_ID-']:
        sg.popup('Missing Widget Id')
        return
    if not values['-ROW-']:
        sg.popup('Missing Row')
        return
    if not values['-COL-']:
        sg.popup('Missing Col')
        return  
    if not values['-ROW-'].isnumeric():
        sg.popup('Row not Numeric: ' +str(values['-ROW-']) )
        return
    if not values['-COL-'].isnumeric():
        sg.popup('Col not Numeric: ' +str(values['-COL-']) )
        return  

    row = int(values['-ROW-'])
    col = int(values['-COL-'])
    if (tablevalues[row][col] == values['-WIDGET_ID-']) or (tablevalues[row][col] == EMPTYCELL):
        pass
    else:
        sg.popup('There is a widget at this position, not allowed' )
        return

# all is well, save the widget
#      
# First figure out which parameters user changed, add them to parm_list
# rem we should have a 1 to 1 relationship between Dflt_parms  and the input box id of the property inspector
    parm_list = []
    parm_cnt = len(Dflt_parms)
    if parm_cnt > MAX_PROPERTIES:
        parm_cnt = MAX_PROPERTIES

    # auto create key value?
    if values['-SAVE_AS_KEY-'] == True:
        dflt_key = '-' + str(values['-WIDGET_ID-'])  + '-'
        dflt_key = dflt_key.upper()
    else:
        dflt_key = None  

    for i in range(parm_cnt):
        if values[f'-PARM_VALUE_KEY{i}-']:
            parm_name = str(Dflt_parms[i][0])
            parm_value = str(Dflt_parms[i][1])
            parm_idx = Dflt_parms[i][2]
            widget_parm_value = str(values[f'-PARM_VALUE_KEY{i}-'])
    #        print (parm_value, widget_parm_value)
            if parm_value != widget_parm_value:
                parm_list.append([parm_idx,parm_name,widget_parm_value])
            else:
                # add default key?
                if parm_name == 'key' and dflt_key != None:
                    parm_list.append([parm_idx,parm_name,str(dflt_key)])  


    Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'], parm_list]
    # place widget key in table
    table_update(values['-WIDGET_ID-'])

def delete_widget(values):
# delete the currently selected widget
    global Saved_widgets

    key = values['-WIDGET_ID-']
    if Saved_widgets[key] == None:
        return
    if sg.popup_ok_cancel('Delete - ' + key +'?') == 'OK':
        del Saved_widgets[key]
        refresh_table() 
        window['Delete Widget'].update(visible = False)


def getwidget(row,col):
    global Dflt_parms
# get the widget at the cell click and display in the property inspector
    global Saved_widgets, tablevalues
# table was clicked at cell row,col see if we have anthing saved there (or more precisely in tablevalues)
    if tablevalues[row][col] == EMPTYCELL:
        # empty cell, update row and col selection for next widget add
        window['-COL-'].update(value = col)
        window['-ROW-'].update(value = row)
        window['-WIDGET_ID-'].update(value = '')
        window['-WIDGET_TXT-'].update(value = '')
    else:
        # cell location has a widget here, edit or delete?
        key = tablevalues[row][col]
        wInfo = Saved_widgets[key]
        if wInfo == None:
            sg.popup('Error', key + ' Not Found in Saved_widgets?')
            return
        widget = wInfo[WDGT_IDX]
        Dflt_parms = parm_inspector(gw.get_props(getattr(sg,widget)))
        #
        # now updated inspector with saved info
        #
        window['-COL-'].update(value = wInfo[COL_IDX])
        window['-ROW-'].update(value = wInfo[ROW_IDX])

        index = gw.widget_list.index(widget)
        window['-SEL_WIDGET-'].update(set_to_index=[index], scroll_to_index=index)
        window['-WIDGET_ID-'].update(value =key)
        window['-WIDGET_TXT-'].update(value = key)
        saved_parms = wInfo[PARM_IDX]
        for parm in saved_parms:
    #     rem parameters saved as  [parm_idx,parm_name,widget_parm_value]
            parm_idx = parm[0]
            parm_name = parm[1]
            parm_value = parm[2]
            window[f'-PARM_VALUE_KEY{parm_idx}-'].update(value = parm_value)
    # show the delete key
        window['Delete Widget'].update(visible = True)

def table_update(key):
    global Saved_widgets, tablevalues
#
# key - key for Saved_widgets dictionary of saved widgets 
#
    newrow = -1  # flag for changed row
    newcol = -1  # flag for changed col
    wInfo = Saved_widgets[key]
    if wInfo == None:
        sg.popup('Error', key + ' Not Found in Saved_widgets?')
        return
    row = int(wInfo[ROW_IDX])
    # if we selected a "row" larger than the row list, append  another row and set row to it
    if len(tablevalues) < row:
        tablevalues.append([EMPTYCELL for col in range(1,TABLE_COL_COUNT+1)])
        row = len(tablevalues) - 1
        newrow = row

    col = int(wInfo[COL_IDX])
    # if we selected a "column" within the col list, 
    # and its empty, (or already contains this widget) add / update it
    # else append to end
    # note save_widget should catch this so code really is not necessary
    if col < len(tablevalues[row]):
        if (tablevalues[row][col] == key) or (tablevalues[row][col] == EMPTYCELL):
            tablevalues[row][col] = key
        else:
            tablevalues[row].append(key)
            newcol = len(tablevalues[row])-1
    
    # selected a col larger than the col list, append
    else:
        tablevalues[row].append(key)
        newcol = len(tablevalues[row])-1

    # did we change col / row selected by user? if so we must update the dictionary
    # 
    if newrow > -1:
        row = newrow  # row changed
    if newcol > -1:
        col = newcol  # col changed
    up_dict = {key:[wInfo[WDGT_IDX],row,col,wInfo[PARM_IDX]]}
    Saved_widgets.update(up_dict)        
    # note  need to figure out how to resize display area of table. Only solution provided so far is to close and recreate the window object
    refresh_table()
# update the "next" col postion
    col +=1
    window['-COL-'].update(value = col)

def refresh_table():
    global tablevalues
    # first initialize table data with EMPTYCELL
    rows = len(tablevalues)
    if rows > 0:
        cols = len(tablevalues[0])
    else:
        cols = TABLE_COL_COUNT+1
    tablevalues = [[EMPTYCELL for col in range(1,cols+1)] for count in range(rows)]

    # now populate with defined widgets
    for key in Saved_widgets:
        wInfo = Saved_widgets[key]
        row = int(wInfo[ROW_IDX])
        col = int(wInfo[COL_IDX])
        tablevalues[row][col] = key
    window['-TABLE-'].update(values = tablevalues)
################################## layout create functions ######################################################################

def create_row_layout(layoutid,row):
    global layoutvalues

    # find first empty row
    emptyrowfound = False
    for rc in range(len(layoutvalues)):
        if layoutvalues[rc][0] == EMPTYCELL:
            emptyrowfound = True
            break
    
    if not(emptyrowfound):
        sg.popup('Layout Table Full')
        return

    # save layout id in col 0
    layoutvalues[rc][0] = layoutid
    col = 0
    # then add widgets to the layout row
    for widget in tablevalues[row]:
        if widget != EMPTYCELL:
            col +=1
            layoutvalues[rc][col] = widget
    window['-LAYOUT_TABLE-'].update(values = layoutvalues)
    return 

def create_layout_code():
    # place layout code in editor window.
    # first clear out anything there
    window['_BODY_'].update(value='')
    insert_text('# guibuildertestlayoutfile')
    insert_text('import PySimpleGUI as sg')
    # place a timestamp in the editor
    insert_text('timestamp = ' + str(time.time()))
    insert_text('#\n')
    layout_list = []
    for rc in range(len(layoutvalues)):
        if layoutvalues[rc][0] == EMPTYCELL:
            pass
        else:
            layoutid = layoutvalues[rc][0]
            layout_text = layoutid  + '= ['
            for widx in range(1, len(layoutvalues)):
                widget = layoutvalues[rc][widx]
                if widget !=  EMPTYCELL:
                    winfo = Saved_widgets[widget]
                    widget_text = 'sg.' + str(winfo[WDGT_IDX]) + '('
                    for parms in winfo[PARM_IDX]:
                        # add parameter name
                        param_name =parms[1]  
                        widget_text += param_name + '=' 
                        # now add parameter value, note we need to look up whether this should be quoted or not
                        param_value =  parms[2] 
                        if param_name in  gw.quoted_properties:
                            param_value = "'" + param_value + "'"
                        widget_text += param_value + ','
                    
                    widget_text = widget_text[:-1] + ')'
                    layout_text += widget_text + ','
            layout_text = layout_text[:-1] + ']'
            #print (layout_text)
            # add this layout id to editor window
            insert_text(layout_text)
            # add to master
            layout_list.append(layoutid)
    insert_text('layout = [')       
    for layout in layout_list:
        insert_text('[' + str(layout) + '],')
    insert_text(']') 


################################## Editor functions #############################################################################
def new_file():
    '''Reset body and info bar, and clear filename variable'''
    window['_BODY_'].update(value='')
    window['_INFO_'].update(value='> New File <')
    file = None
    return file

def open_file():
    '''Open file and update the infobar'''
    filename = sg.popup_get_file('Open', no_window=True)
    if filename:
        file = pathlib.Path(filename)
        window['_BODY_'].update(value=file.read_text())
        window['_INFO_'].update(value=file.absolute())
        return file

def save_file(file):
    '''Save file instantly if already open; otherwise use `save-as` popup'''
    if file:
        file.write_text(values.get('_BODY_'))
    else:
        save_file_as()

def save_file_as():
    '''Save new file or save existing file with another name'''
    filename = sg.popup_get_file('Save As', save_as=True, no_window=True)
    if filename:
        file = pathlib.Path(filename)
        file.write_text(values.get('_BODY_'))
        window['_INFO_'].update(value=file.absolute())
        return file

def execute_py_file():
    global subprocess_Popen
# execute the script written to the editor window
# should probably create a temp file for this, but not today
      
    file = pathlib.Path(GUIBUILDER_TEST_LAYOUT_FILE) 
    file.write_text(values['_BODY_'])
    # do we have the script to execute the layout?
    tstfile = pathlib.Path(GUIBUILDER_TEST_FILE)
    if tstfile.is_file():
        subprocess_Popen = sg.execute_py_file(GUIBUILDER_TEST_FILE)
    else:
        sg.popup('Missing ' + GUIBUILDER_TEST_FILE)

def refresh_file():
    # refresh the GUIBUILDER_TEST_LAYOUT_FILE, requres a new time stamp
    insert_text('timestamp = ' + str(time.time()))
    window.refresh()

    #file = pathlib.Path(GUIBUILDER_TEST_LAYOUT_FILE) 
    #file.write_text(values['_BODY_'])
    tkwidget = window['_BODY_']
    text = tkwidget.Widget.get("1.0",'end-1c')
    try:
        fp = open(GUIBUILDER_TEST_LAYOUT_FILE,'w') 
        fp.writelines(text)
     #   fp.flush()
        fp.close()
    except OSError as e:
        sg.popup(f"{type(e)}: {e}" + GUIBUILDER_TEST_LAYOUT_FILE)



def cut_text():
    tkwidget = window['_BODY_']
    if tkwidget.Widget.selection_get():  
        sg.clipboard_set(tkwidget.Widget.selection_get()) # copy selected text to clipboard 
        tkwidget.Widget.delete('sel.first','sel.last')    # delete selected text

def copy_text():
    tkwidget = window['_BODY_']
    if tkwidget.Widget.selection_get():  
        sg.clipboard_set(tkwidget.Widget.selection_get()) # copy selected text to clipboard            

def paste_text():
    tkwidget = window['_BODY_']
    tkwidget.Widget.insert('insert', sg.clipboard_get())
  

def insert_text(text):
    tkwidget = window['_BODY_']
    tkwidget.Widget.insert('end', '\n'+text)

def about_me():
    sg.popup_no_wait('guibuilder 0.0')

########################################## functions for saving and loading widget dictionary ##################################
def save_data(formname):
    try:
        with open(str(formname)+'.json','w') as fp:
            json.dump(Saved_widgets, fp, sort_keys=True, indent=4) 
            fp.close()
            sg.popup('Save Data', 'Data saved to: ' + str(formname)+'.json')
    except OSError as e:
        sg.popup(f"{type(e)}: {e}" + str(formname)+'.json')

def load_data():
    global Saved_widgets, tablevalues
   
    filename = sg.popup_get_file('Open', no_window=True)
    if filename:

        try:
            with open(str(filename), 'r') as fp:
                try:
                    Saved_widgets = json.load(fp)
                    fp.close()
                    tablevalues = [[EMPTYCELL for col in range(1,TABLE_COL_COUNT+1)] for count in range(TABLE_ROW_COUNT)]
                    refresh_table()
                except Exception as e:
                    sg.popup('Loaded error', f"{type(e)}: {e}")   

        except OSError as e:
            sg.popup(f"{type(e)}: {e}" + str(filename)+'.json')

################################## start of layouts #############################################################################
widget_tab = [
[sg.Text('Widget Id'),sg.Input(size=(20,1), key = '-WIDGET_ID-',do_not_clear=True,)],
[sg.Checkbox('Save As KEY',default =True, key = '-SAVE_AS_KEY-')],
[sg.Text('Row'),sg.Input(size=(5,1), key = '-ROW-',default_text = "0",do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-COL-',default_text = "0",do_not_clear=True,)],
# dropdown list of widgets to select from
[sg.Text('Widgets'),sg.Listbox(values=gw.widget_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_WIDGET-')],
[sg.Button('Save Widget',tooltip='Saves widget and places on Widget Table'),sg.Button('Delete Widget',visible=False)]
]

layout_tab = [
[sg.Text('Layout Id'),sg.Input(size=(20,1), key = '-LAYOUT_ID-',do_not_clear=True)],
#[sg.Text('Row'),sg.Input(size=(5,1), key = '-C_ROW-',do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-C_COL-',do_not_clear=True)],
[sg.Button('Select Widget',tooltip= 'Appends Widget to selected Layout Table Layout')],
[sg.Button('Row Create',tooltip= 'Builds layout definition based on selected Widget Table Row')],
[sg.Button('Auto Create',tooltip='Builds layout definition based on Widget postioning in Widget Table')],
[sg.HSep()],
[sg.Button('Generate Layout',tooltip='Creates pysimplygui code for layouts in layout definition table, places in editor')]
]

container_tab = [
[sg.Text('Container Id'),sg.Input(size=(20,1), key = '-CONTAINER_ID-',do_not_clear=True)],
#[sg.Text('Row'),sg.Input(size=(5,1), key = '-C_ROW-',do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-C_COL-',do_not_clear=True)],
# dropdown list of containers to select from
[sg.Text('Containers'),sg.Listbox(values=gw.container_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_CONTAINER-')],
[sg.Button('Save Container')]
]

entry_layout =[
[sg.TabGroup([[sg.Tab('Widgets', widget_tab),sg.Tab('Layouts', layout_tab), sg.Tab('Containers', container_tab)]],key = '-TABS-',tab_location='top')], 
[sg.HSep()],
# parameter inspector list of labels and input boxes
[sg.Text('',size=(20,1),relief = sg.RELIEF_SUNKEN,border_width = 2,key='-WIDGET_TXT-')],
*[[sg.Text(f'Parameter {i:02}',key = f'-PARM_NAME_KEY{i}-', size=(18,1), pad=(0,0)),sg.Input(size=(20,1), key = f'-PARM_VALUE_KEY{i}-',pad=(5,0))] for i in range(MAX_PROPERTIES)]
]

### prebuild our layout table
tableheadings = [f'Col {col}' for col in range(TABLE_COL_COUNT)]
layout_heading = [f'Widget {col}' for col in range(TABLE_COL_COUNT)]
layout_heading[0] = 'Layout Id'
#
menu_layout = [['File', ['Load', 'Save', '---', 'Exit']],
              ['Help', ['About']]]
#
editor_file_menu = ['Unused',['New', 'Open', 'Save', 'Save As', '---', 'Exit']]
editor_tools_menu =['Unused', ['Insert']]

editor_layout =  [
[sg.Text('> New file <', font=('Consolas', 10), size=(WIN_W, 1), key='_INFO_')],
[sg.Multiline(font=('Consolas', 12), size=(WIN_W, WIN_H), key='_BODY_')]
]

widget_table = [
    [sg.Table(tablevalues, headings=tableheadings, max_col_width=25,
                    auto_size_columns=False,
                    font=('Consolas', 12),
                    col_widths = 25, 
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=True,
                    justification='center',
                    num_rows=10,
                    alternating_row_color='grey60',
                    key='-TABLE-',
#                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=False,
                    expand_y=False,
                    vertical_scroll_only=False,
                    hide_vertical_scroll = False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    tooltip='Widget Table')]
]

layout_table = [
    [sg.Table(layoutvalues, headings=layout_heading, max_col_width=25,
                    auto_size_columns=False,
                    font=('Consolas', 12),
                    col_widths = 25, 
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=False,
                    justification='center',
                    num_rows=10,
                    alternating_row_color='green',
                    key='-LAYOUT_TABLE-',
#                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=False,
                    expand_y=False,
                    vertical_scroll_only=False,
                    hide_vertical_scroll = False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    tooltip='Layout Table')]
]

editor_layout = [
[
sg.ButtonMenu('File',editor_file_menu,size=(10,1),key="-EFILE-"),
sg.Button('Cut',size=(10,1)),sg.Button('Copy',size=(10,1)),
sg.Button('Paste',size=(10,1)),
sg.ButtonMenu('Tools',editor_tools_menu,size=(10,1),key="-ETOOLS-"),
sg.Button('Exe Layout',size=(10,1),tooltip='Execute this layout in a new process'),
sg.Button('Refresh',size=(10,1),tooltip='Refresh a layout currenlty being displayed'),
],
[sg.Text('> New file <', font=('Consolas', 10), size=(WIN_W, 1), key='_INFO_')],

[sg.Multiline(font=('Consolas', 12), size=(132, WIN_H),horizontal_scroll = True, key='_BODY_')]  
]  

table_editor_layout = [
# [sg.TabGroup([[sg.Tab('Widgets', widget_table), sg.Tab('Containers', container_table)]],key = '-TABLE_TABS-',tab_location='top')],                     
[sg.Frame('Widgets', widget_table)],
[sg.Frame('Layouts', layout_table)],
[sg.Frame('Editor', editor_layout)]
]

# guibuilder main form layout
layout = [
 [sg.Menu(menu_layout)],
 [sg.Text('Form Name'),sg.Input(size=(20,1), key = '-FORM_NAME-',do_not_clear=True,)],
 [sg.HSep()],
# [sg.Column(entry_layout,vertical_alignment='top',scrollable = True,vertical_scroll_only = True,expand_y=True), sg.Column(table_editor_layout,size=(600,300),vertical_alignment='top',scrollable = True)]
[sg.Column(entry_layout,vertical_alignment='top',scrollable = True,vertical_scroll_only = True,expand_y=True), sg.Column(table_editor_layout,vertical_alignment='top')]
]

############################################## Windows                ############################################################
window = sg.Window('guiBuilder', layout=layout, margins=(0, 0),size=(1080,900), resizable=True,  finalize=True)
pos_x, pos_y = window.current_location()
win_width, win_height = window.size

#EditWindow = sg.Window('Editor',layout=editor_layout, resizable=True, location =(pos_x + win_width,pos_y), size=(600,win_height), return_keyboard_events=True, finalize=True)
#window.maximize()
#EditWindow['_BODY_'].expand(expand_x=True, expand_y=True)


############################################## all important event loop ############################################################
while True:
 #   windowid, event, values = sg.read_all_windows()
    event, values = window.read()
 #   print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        # if we kicked off the viewer, terminate it
        if subprocess_Popen != None:
            if subprocess_Popen.poll() == None:
        #    subprocess_Popen.terminate()    # note this should work, but does not on Windows
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(subprocess_Popen.pid)])

        break

    # layout table events
    elif isinstance(event, tuple):
        # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
        # You can also call Table.get_last_clicked_position to get the cell clicked
        if event[0] == '-TABLE-':
            selected_widget_row = event[2][0] 
 #           if event[2][0] == -1 and event[2][1] != -1:           # Header was clicked and wasn't the "row" column
 #           sg.popup('Cell Clicked: ', (f'{event[2][0]},{event[2][1]}'))
            # user clicked table cell, get the widget at that location
            getwidget(event[2][0],event[2][1])

        elif event[0] == '-LAYOUT_TABLE-':
            selected_layout_row = event[2][0] 
           
# Menu events

    elif event in ('Load'):
        if sg.popup_ok_cancel('Warning, existing data will be overwritten') == 'OK':
            load_data()

    elif event in ('Save'):
        if not values['-FORM_NAME-']:
            sg.popup('Save Data','No Form Name')
        else:
            save_data(values['-FORM_NAME-'])

    elif event in ('About',):
        about_me()
# Button Menu -FILE- Events
    elif event == '-EFILE-':
        if values['-EFILE-'] == 'New':
            file = new_file()
        if values['-EFILE-'] == 'Open':
            file = open_file()
        if values['-EFILE-'] == 'Save':
            save_file(file)
        if values['-EFILE-'] == 'Save As':
            file = save_file_as()
        if values['-EFILE-'] == 'Exit':
            break
# cut copy paste
    elif event == 'Cut':
        cut_text()
    elif event == 'Copy':
        copy_text()
    elif event == 'Paste':
        paste_text() 
    elif event == 'Exe Layout':
        execute_py_file()
    elif event == 'Refresh':
        refresh_file()

# Button Menu -TOOL- Events
    elif event == '-ETOOLS-':
        if values['-ETOOLS-'] == 'Insert':
            insert_text('My dummy text to insert')


    elif event == '-SEL_WIDGET-' and len(values['-SEL_WIDGET-']):
        widget = values['-SEL_WIDGET-'][0]
    # rem returns default property values, used to id which ones user entered and needs to be saved
        Dflt_parms = parm_inspector(gw.get_props(getattr(sg,widget)))

    elif event == '-SEL_CONTAINER-' and len(values['-SEL_CONTAINER-']):
        container = values['-SEL_CONTAINER-'][0]
    # rem returns default property values, used to id which ones user entered and needs to be saved
        Dflt_parms = parm_inspector(gw.get_props(getattr(sg,container)))

    elif event == 'Save Widget':
        save_widget(values)
    
    elif event == 'Delete Widget':
        delete_widget(values)

    elif event == 'Select Widget':
        sg.popup('Select Widget clicked')
    
    elif event == 'Row Create':  
        if not values['-LAYOUT_ID-']:
            sg.popup('Missing Layout Id')
        else:
            layoutid = values['-LAYOUT_ID-']
            create_row_layout(layoutid,selected_widget_row)

    
    elif event == 'Auto Create':
        for rw in range(len(layoutvalues)):
            for widget in tablevalues[rw]:
                if widget != EMPTYCELL: 
                    # this row has atleast one widget in it, process 
                    # cheap hack for layout id, need to figure something better (and unique)
                    layoutid = 'layout'+str(rw) 
                    create_row_layout(layoutid,rw)
                    break

    elif event == 'Generate Layout':
        create_layout_code()
       
window.close()