"""
How this works (or should work)
 1) User defines widgets, placing on layout table via row / column vars
   - do not allow overwrite 
   - does table auto grow this extra cell in row??

   Do we create "layout" variables at this point?                    
 2) User then groups widgets into container (or none)
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
import pathlib
import json

import guibuilder_widgets as gw

sg.ChangeLookAndFeel('BrownBlue') # change style

WIN_W = 90
WIN_H = 25
MAX_PROPERTIES = 45    # max number of properties we are setup to display
#
# note column sizing is kind of a copout, still cannot get table to update size when additional columns are added.  
TABLE_COL_COUNT = 20  # number of columns to create for layout table
TABLE_ROW_COUNT = 30  # and rows
EMPTYCELL = '-       -'
#
# indexes into the data saved in the widget dictionary
#   Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'],values['-LAYOUT_ID-']]
saved_props = []          # created list of widget propety names default values
Saved_widgets = {}        # empty dictionary of saved widgets 
#                         Which is made up of a list of the following items  
WDGT_IDX = 0  # WIDGET ID (one of pysimplegui widgets)
ROW_IDX  = 1  # ROW NBR for table placement and evental layout buildup
COL_IDX  = 2  # COL NBR 
PRM_IDX  = 3  # List of parameters entered, calculated by comparing "default" widget signature to what is in the property explorer

file = None


def pop_inspector(prop_list):
# take the list of properties for a widget and place them in the "object inspector"
# which is nothing more than a series of input widgets
# and returns a list of default properties name / value / property index 
    dflt_props = []
    prop_cnt = len(prop_list)
    for i in range(MAX_PROPERTIES):
        if i < prop_cnt:
            element = str(prop_list[i]).split("=")
            prop_name = str(element[0]).strip()
            
            if len(element) == 2:
                prop_value = str(element[1]).strip()
                window[f'-PROP_VALUE_KEY{i}-'].update(value = prop_value)
            else:
                window[f'-PROP_VALUE_KEY{i}-'].update(value = '')
                prop_value = ''

            window[f'-PROP_NAME_KEY{i}-'].update(value = prop_name)
            dflt_props.append([prop_name,prop_value,i])
        else:
            window[f'-PROP_VALUE_KEY{i}-'].update(value = '')
            window[f'-PROP_NAME_KEY{i}-'].update(value = '')
    return dflt_props

def save_widget(values):
    global saved_props
# save the widget currently displayed on the entry screen into
# ? a dictionary item #
# then place it on the "layout" table
#    sg.popup('Save','Widget save processing here' + str(values['-SEL_WIDGET-']))
# do some error checking first 
# rem - values['-key-'] return a list
# and an empty list is false (implicit booleanness of the empty list)
    if not values['-SEL_WIDGET-']:
        sg.popup('Save Widget','No Widget Selected')
        return
    if not values['-WIDGET_ID-']:
        sg.popup('Save Widget','Missing Widget Id')
        return
    if not values['-ROW-']:
        sg.popup('Save Widget','Missing Row')
        return
    if not values['-COL-']:
        sg.popup('Save Widget','Missing Col')
        return  
    if not values['-ROW-'].isnumeric():
        sg.popup('Save Widget','Row not Numeric: ' +str(values['-ROW-']) )
        return
    if not values['-COL-'].isnumeric():
        sg.popup('Save Widget','Col not Numeric: ' +str(values['-COL-']) )
        return  
# all is well, save the widget
#      
# First figure out which properties user changed, add them to prop_list
# rem we should have a 1 to 1 relationship between saved_props  and the input box id of the property inspector
    prop_list = []
    prop_cnt = len(saved_props)
    if prop_cnt > MAX_PROPERTIES:
        prop_cnt = MAX_PROPERTIES

    for i in range(prop_cnt):
        if values[f'-PROP_VALUE_KEY{i}-']:
            prop_name = str(saved_props[i][0])
            prop_value = str(saved_props[i][1])
            prop_idx = saved_props[i][2]
            widget_prop_value = str(values[f'-PROP_VALUE_KEY{i}-'])
    #        print (prop_value, widget_prop_value)
            if prop_value != widget_prop_value:
                prop_list.append([prop_idx,prop_name,widget_prop_value])


    Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'], prop_list]
    table_update(values['-WIDGET_ID-'])

# place in table
#     
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
    # and its empty, add it
    # else insert it
    if col < len(tablevalues[row]):
        if tablevalues[row][col] == EMPTYCELL:
            tablevalues[row][col] = key
        else:
            tablevalues[row].insert(col+1,key)
            newcol = col+1
    
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
    up_dict = {key:[wInfo[WDGT_IDX],row,col,wInfo[PRM_IDX]]}
    Saved_widgets.update(up_dict)        

# need to figure out how to resize display area of table. Only solution provided so far is to close and recreate the window object

    window['-TABLE-'].update(values = tablevalues)
# update the "next" col postion
    col +=1
    window['-COL-'].update(value = col)

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

def word_count():
    '''Display estimated word count'''
    words = [w for w in values['_BODY_'].split(' ') if w!='\n']
    word_count = len(words)
    sg.popup_no_wait('Word Count: {:,d}'.format(word_count))

def insert_text():
   window['_BODY_'].Widget.insert('2.5', 'My Inserted Text')

def about_me():
    sg.popup_no_wait('guibuilder 0.0')

########################################## functions for saving and loading widget dictionary ##################################
def save_data(formname):
    try:
        with open(str(formname)+'.json','w') as fp:
            json.dump(Saved_widgets, fp, sort_keys=True, indent=4) 
            sg.popup('Save Data', 'Data saved to: ' + str(formname)+'.json')
    except OSError as e:
        print(f"{type(e)}: {e}")

def load_data(formname):
    try:
        with open(str(formname)+'.json', 'r') as fp:
            Saved_widgets = json.load(fp)
            sg.popup('Load Data', 'Data Loaded from: ' + str(formname)+'.json')
    except OSError as e:
        print(f"{type(e)}: {e}")

################################## start of layouts #############################################################################
widget_tab = [
[sg.Text('Widget Id'),sg.Input(size=(20,1), key = '-WIDGET_ID-',do_not_clear=True,)],
[sg.Checkbox('Save As KEY',default =True, key = '-SAVE_AS_KEY-'),sg.Checkbox('Save As TEXT',default =True, key = '-SAVE_AS_TEXT-')],
[sg.Text('Row'),sg.Input(size=(5,1), key = '-ROW-',default_text = "0",do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-COL-',default_text = "0",do_not_clear=True,)],
# dropdown list of widgets to select from
[sg.Text('Widgets'),sg.Listbox(values=gw.widget_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_WIDGET-')],
[sg.Button('Save Widget')]
]

Container_tab = [
[sg.Text('Layout Id'),sg.Input(size=(20,1), key = '-LAYOUT_ID-',do_not_clear=True)],
[sg.Text('Row'),sg.Input(size=(5,1), key = '-C_ROW-',do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-C_COL-',do_not_clear=True)],
# dropdown list of containers to select from
[sg.Text('Containers'),sg.Listbox(values=gw.container_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_CONTAINER-')],
[sg.Button('Save Container')]
]

entry_layout =[
[sg.TabGroup([[sg.Tab('Widgets', widget_tab), sg.Tab('Containers', Container_tab)]],key = '-TABS-',tab_location='top')], 
[sg.HSep()],
# property inspector list of labels and input boxes
*[[sg.Text(f'property {i:02}',key = f'-PROP_NAME_KEY{i}-', size=(18,1), pad=(0,0)),sg.Input(size=(20,1), key = f'-PROP_VALUE_KEY{i}-',pad=(5,0))] for i in range(MAX_PROPERTIES)]
]

### prebuild our layout table
tableheadings = [f'Col {col}' for col in range(TABLE_COL_COUNT)]

#
menu_layout = [['File', ['Load', 'Save', '---', 'Exit']],
              ['Help', ['About']]]
#
editor_file_menu = ['Unused',['New', 'Open', 'Save', 'Save As', '---', 'Exit']]
editor_tools_menu =['Unused', ['Word Count','Insert']]

editor_layout =  [
[sg.Text('> New file <', font=('Consolas', 10), size=(WIN_W, 1), key='_INFO_')],
[sg.Multiline(font=('Consolas', 12), size=(WIN_W, WIN_H), key='_BODY_')]
]

#tablevalues = [[f'- empty -' for col in range(1,TABLE_COL_COUNT+1)] for count in range(TABLE_ROW_COUNT)]
tablevalues = [[EMPTYCELL for col in range(1,TABLE_COL_COUNT+1)] for count in range(TABLE_ROW_COUNT)]
table_editor_layout = [
    [sg.Sizer(h_pixels=300)],
    [sg.Table(tablevalues, headings=tableheadings, max_col_width=25,
                    auto_size_columns=False,
                    font=('Consolas', 12),
                    col_widths = 25, 
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=True,
                    justification='center',
                    num_rows=15,
                    alternating_row_color='grey60',
                    key='-TABLE-',
#                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=False,
                    expand_y=False,
                    vertical_scroll_only=False,
                    hide_vertical_scroll = False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    tooltip='Layout Table')],
[sg.ButtonMenu('File',editor_file_menu,size=(10,1),key="-EFILE-"),sg.ButtonMenu('Tools',editor_tools_menu,size=(10,1),key="-ETOOLS-")],
[sg.HSep()],
[sg.Text('> New file <', font=('Consolas', 10), size=(WIN_W, 1), key='_INFO_')],
[sg.Multiline(font=('Consolas', 12), size=(WIN_W, WIN_H),horizontal_scroll = True, key='_BODY_')]
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
window = sg.Window('guiBuilder', layout=layout, margins=(0, 0),size=(900,800), resizable=True,  finalize=True)
pos_x, pos_y = window.current_location()
win_width, win_height = window.size

#EditWindow = sg.Window('Editor',layout=editor_layout, resizable=True, location =(pos_x + win_width,pos_y), size=(600,win_height), return_keyboard_events=True, finalize=True)
#window.maximize()
#EditWindow['_BODY_'].expand(expand_x=True, expand_y=True)


############################################## all important event loop ############################################################
while True:
 #   windowid, event, values = sg.read_all_windows()
    event, values = window.read()
#    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
# Menu events

    if event in ('Load'):
        if sg.popup_ok_cancel('Warning, existing data will be overwritten') == sg.OK:
            if not values['-FORM_NAME-']:
                sg.popup('Load Data','No Form Name')
            else:
                load_data(values['-FORM_NAME-'])

    if event in ('Save'):
        if not values['-FORM_NAME-']:
            sg.popup('Save Data','No Form Name')
        else:
            save_data(values['-FORM_NAME-'])

    if event in ('About',):
        about_me()
# Button Menu -FILE- Events
    if event == '-EFILE-':
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
# Button Menu -TOOL- Events
    if event == '-ETOOLS-':
        if values['-ETOOLS-'] == 'Word Count':
            word_count() 
        if values['-ETOOLS-'] == 'Insert':
            insert_text()


    if event == '-SEL_WIDGET-' and len(values['-SEL_WIDGET-']):
        widget = values['-SEL_WIDGET-'][0]
    # rem returns default property values, used to id which ones user entered and needs to be saved
        saved_props = pop_inspector(gw.get_props(getattr(sg,widget)))

    if event == '-SEL_CONTAINER-' and len(values['-SEL_CONTAINER-']):
        container = values['-SEL_CONTAINER-'][0]
    # rem returns default property values, used to id which ones user entered and needs to be saved
        saved_props = pop_inspector(gw.get_props(getattr(sg,container)))

    if event == 'Save Widget':
        save_widget(values)

# layout table events
    if isinstance(event, tuple):
        # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
        # You can also call Table.get_last_clicked_position to get the cell clicked
        if event[0] == '-TABLE-':
 #           if event[2][0] == -1 and event[2][1] != -1:           # Header was clicked and wasn't the "row" column
 #               col_num_clicked = event[2][1]
 #               new_table = sort_table(data[1:][:],(col_num_clicked, 0))
 #               window['-TABLE-'].update(new_table)
 #               data = [data[0]] + new_table
            sg.popup('Cell Clicked: ', (f'{event[2][0]},{event[2][1]}'))


       
window.close()