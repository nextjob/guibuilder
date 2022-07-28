## to do - add saved widgedid to cell in table and update
## process table and create layout (and event loop??)
## test layout
## use pickle to save dictionaries???
'''
  A minimalist pysimplegui builder
  
  Editor based on :
  
  A minimalist Notepad built with the PySimpleGUI TKinter framework
  Author:     Israel Dryer
  Email:      israel.dryer@gmail.com
  Modified:   2020-06-20
'''
import PySimpleGUI as sg
import pathlib

import guibuilder_widgets as gw

sg.ChangeLookAndFeel('BrownBlue') # change style

WIN_W = 90
WIN_H = 25
MAX_PROPERTIES = 45    # max number of properties we are setup to display
TABLE_COL_COUNT = 10  # number of columns to create for layout table
TABLE_ROW_COUNT = 20  # and rows
#
# indexes into the data saved in the widget dictionary
#   Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'],values['-LAYOUT_ID-']]
saved_props = []          # created list of widget propety names default values
Saved_widgets = {}        # empty dictionary of saved widgets 
#                         Which is made up of a list of the following items  
WDGT_IDX = 0  # WIDGET ID (one of pysimplegui widgets)
ROW_IDX  = 1  # ROW NBR for table placement and evental layout buildup
COL_IDX  = 2  # COL NBR 
LAY_IDX  = 3  # LAYOUT ID where this widget will be placed in
PRM_IDX  = 4  # List of parameters entered, calculated by comparing "default" widget signature to what is in the property explorer

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
    sg.popup('Save','Widget save processing here' + str(values['-SEL_WIDGET-']))
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
            if prop_value != widget_prop_value:
                prop_list.append([prop_idx,prop_name,widget_prop_value])


    Saved_widgets[values['-WIDGET_ID-']] = [values['-SEL_WIDGET-'][0],values['-ROW-'], values['-COL-'], prop_list]
    print (Saved_widgets)
    table_update(values['-WIDGET_ID-'])

# place in table
#     
def table_update(key):
    global Saved_widgets, tablevalues
#
# key - key for Saved_widgets dictionary of saved widgets 
#
    wInfo = Saved_widgets[key]
    if wInfo == None:
        sg.popup('Error', key + ' Not Found in Saved_widgets?')
        return
    row = int(wInfo[ROW_IDX])
    col = int(wInfo[COL_IDX])
    tablevalues[row][col] = key
    window['-TABLE-'].update(values = tablevalues)
 

################################## Editor functions #############################################################################
def new_file():
    '''Reset body and info bar, and clear filename variable'''
    EditWindow['_BODY_'].update(value='')
    EditWindow['_INFO_'].update(value='> New File <')
    file = None
    return file

def open_file():
    '''Open file and update the infobar'''
    filename = sg.popup_get_file('Open', no_window=True)
    if filename:
        file = pathlib.Path(filename)
        EditWindow['_BODY_'].update(value=file.read_text())
        EditWindow['_INFO_'].update(value=file.absolute())
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
   EditWindow['_BODY_'].Widget.insert('2.5', 'My Inserted Text')

def about_me():
    '''A short, pithy quote'''
    sg.popup_no_wait(str(type(EditWindow['_BODY_'].Widget)))

################################## start of layouts #############################################################################
entry_layout =[
# position data of widget on form 
[sg.Text('Layout Id'),sg.Input(size=(20,1), key = '-LAYOUT_ID-',do_not_clear=True,)],
[sg.HSep()],
[sg.Text('Widget Id'),sg.Input(size=(20,1), key = '-WIDGET_ID-',do_not_clear=True,)],
[sg.Text('Row'),sg.Input(size=(5,1), key = '-ROW-',do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-COL-',do_not_clear=True,)],
# dropdown list of widgets to select from
[sg.Text('Widgets'),sg.Listbox(values=gw.widget_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_WIDGET-')],
[sg.Button('Save Widget')],
[sg.HSep()],
# property inspector list of labels and input boxes
*[[sg.Text(f'property {i:02}',key = f'-PROP_NAME_KEY{i}-', size=(18,1), pad=(0,0)),sg.Input(size=(20,1), key = f'-PROP_VALUE_KEY{i}-',pad=(5,0))] for i in range(MAX_PROPERTIES)]
]

### prebuild our layout table
tableheadings = [f'Col {col}' for col in range(TABLE_COL_COUNT)]

tablevalues = [[f'- empty -' for col in range(1,TABLE_COL_COUNT+1)] for count in range(TABLE_ROW_COUNT)]

table_layout = [
    [sg.Table(tablevalues, headings=tableheadings, max_col_width=25,
                    auto_size_columns=True,
                    # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                    display_row_numbers=True,
                    justification='center',
                    num_rows=20,
                    alternating_row_color='grey60',
                    key='-TABLE-',
#                    selected_row_colors='red on yellow',
                    enable_events=True,
                    expand_x=False,
                    expand_y=True,
                    vertical_scroll_only=False,
                    enable_click_events=True,           # Comment out to not enable header and other clicks
                    tooltip='Layout Table')]
]
#
editor_menu_layout = [['File', ['New (Ctrl+N)', 'Open (Ctrl+O)', 'Save (Ctrl+S)', 'Save As', '---', 'Exit']],
              ['Tools', ['Word Count','Insert']],
              ['Help', ['About']]]
#
editor_layout =  [
[sg.Menu(editor_menu_layout)],
[sg.Text('> New file <', font=('Consolas', 10), size=(WIN_W, 1), key='_INFO_')],
[sg.Multiline(font=('Consolas', 12), size=(WIN_W, WIN_H), key='_BODY_')]
]
# guibuilder main form layout
layout = [
 [sg.Text('Form Name'),sg.Input(size=(20,1), key = '-FORM_NAME-',do_not_clear=True,)],
 [sg.HSep()],
 [sg.Column(entry_layout,vertical_alignment='top',scrollable = True,vertical_scroll_only = True,expand_y=True), sg.Column(table_layout,expand_x=True)]
]

############################################## Windows                ############################################################
window = sg.Window('guiBuilder', layout=layout, margins=(0, 0), resizable=True,  finalize=True)
pos_x, pos_y = window.current_location()
win_width, win_height = window.size

EditWindow = sg.Window('Editor',layout=editor_layout, resizable=True, location =(pos_x + win_width,pos_y), size=(600,win_height), return_keyboard_events=True, finalize=True)
#window.maximize()
EditWindow['_BODY_'].expand(expand_x=True, expand_y=True)


############################################## all important event loop ############################################################
while True:
    windowid, event, values = sg.read_all_windows()

    if event == sg.WIN_CLOSED or event == 'Exit':
        if windowid == EditWindow:
            sg.Popup('Keep Editor Open!')
        else:
            break
    if event in ('New (Ctrl+N)', 'n:78'):
        file = new_file()
    if event in ('Open (Ctrl+O)', 'o:79'):
        file = open_file()
    if event in ('Save (Ctrl+S)', 's:83'):
        save_file(file)
    if event in ('Save As',):
        file = save_file_as()   
    if event in ('Word Count',):
        word_count() 
    if event in ('Insert',):
        insert_text()     
    if event in ('About',):
        about_me()
#
    if event == '-SEL_WIDGET-' and len(values['-SEL_WIDGET-']):
        widget = values['-SEL_WIDGET-'][0]
    # rem returns default property values, used to id which ones user entered and needs to be saved
        saved_props = pop_inspector(gw.get_props(getattr(sg,widget)))

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


EditWindow.Close()        
window.close()