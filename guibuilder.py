# guibuilder.py
# 
# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <https://unlicense.org>
# 
# to do list:
#
# create_container_code():
#  must figure out the final layout statement  (layout = [[c2],[c3]])
# save interum dict_container_codes BEFORE layout expansion
# use this to determine which values are output at layout = ... and included in container widget
#
# also review list insertion ending up with too many ,, and ],]
# 
#
# we treat Layout "Add Row" different then "Save Container"
#  Add Row looks for the first empty layout row, Save Container places at selected row (and inserts if not empty)
#  process should be similar 
#
# issues with code test (no loyout value which makes perfect sence)
#       if there are layouts defined in the table for the save row, add them to the code before testing
#       else add dummy layout variable?
#
# create a user guide
#
# if parameter enable_events = True, add to event loop? also
#  would mean guibuilder_tester.py would get more complicated
#
# add copy and paste  using Tkinter built in ctrl fuctions:
#   add cut / copy / paste icons from Tango Desktop Project
#   have the click event simulate the built in ctrl key functions
#
# a few possiblilites on keyboard control:
# with pyautogui:
# First install pyautogui with:
# pip install pyautogui
# #Then in your code write:
# import pyautogui
# pyautogui.hotkey('ctrl', 'v')
#
## or pynput
# First install pynput with:
# pip install ppynput
# from pynput.keyboard import Key, Controller
# keyboard = Controller()
# keyboard.press(Key.ctrl)
# keyboard.press('v')
# keyboard.release('v')
# keyboard.release(Key.ctrl)



## note!! tkinter issue 46180 Button clicked failed when mouse hover tooltip and tooltip destroyed
## work around for now is to remove all tool tips from sg.button calls
# 
# See README.md for simple users guide

#   Arrow images used for table row move buttons from the Tango Desktop Project http://tango.freedesktop.org/Tango_Desktop_Project
#   Demo_Base64_Single_Image_Encoder.py  used to convert into Base64
#
#   Multiline Editor code based on:
#   A minimalist Notepad built with the PySimpleGUI TKinter framework
#   Author:     Israel Dryer
#   Email:      israel.dryer@gmail.com
#   Modified:   2020-06-20

import argparse
import PySimpleGUI as sg
import subprocess
import ast
import pathlib
import json

import guibuilder_widgets as gw
import guibuilder_layouts as gl
import guibuilder_constants as gc

sg.ChangeLookAndFeel('BrownBlue') # change style



## global var (i know, i shouldn't)
window = None   # the all important pysimplegui window created in main()

# note column sizing is kind of a copout, still cannot get table to update size when additional columns are added.  
# these can now be set by caller with guibuilder -r rowcount -c col count
table_col_count = 10  # number of columns to create for layout table
table_row_count = 25  # and rows

#
Dflt_parms = []           # created list of widget parameter names default values
#
# Widget Dictionary and layout 
#  key = widget id
Saved_widgets = {}        # empty dictionary of saved widgets 
# key : widget id /  values: [Element Name, ROW, COL,[*list of Parameter values*]]
# *list of Parameter values* : [[**Paramerter Index, Parameter Name, Parameter Value],[Paramerter Index, Parameter Name, Parameter Value], ...]
# **Paramerter Index: index for this parameter's info in list returned by get_props(widget)
#
WDGT_IDX = 0  # pysimplegui ELEMENT  (one of pysimplegui widgets)
ROW_IDX  = 1  # ROW NBR for table placement and evental layout buildup (only actually present in "saved" json file)
COL_IDX  = 2  # COL NBR for table placement and evental layout buildup (only actually present in "saved" json file)
PARM_IDX  = 3  # List of parameters entered, calculated by comparing "default" widget signature to what is in the parameter explorer
#
# container dictionary and layout
#  key = container id  
Saved_containers = {}     # empty dictionary of saved container widgets
# key : container id /  values: [Element Name, ROW, Layout List including Container Id, [*list of Parameter values*]]
# *list of Parameter values* : [[**Paramerter Index, Parameter Name, Parameter Value],[Paramerter Index, Parameter Name, Parameter Value], ...]
# **Paramerter Index: index for this parameter's info in list returned by get_props(container_widget)
#
# WDGT_IDX = 0  # pysimplegui ELEMENT  (one of pysimplegui container widgets)
# ROW_IDX  = 1  # ROW NBR for table placement of container in container table (only actually present in "saved" json file)
LAY_IDX = 2     # List of layouts for this container
# PARM_IDX  = 3  # List of parameters entered, calculated by comparing "default" widget signature to what is in the parameter explorer

# layout table values, start as empty cell
#tablevalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)]
#layoutvalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)] 
#containervalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)] 
# now initialized in main, allowing for user specified sizing
#
tablevalues = []
layoutvalues = [] 
containervalues = []

# set the default font
sg.set_options(font=('Consolas', 12))

file = None

# Popen object from execute_py_file, used to view layout in new sub process, need to save global to terminate
subprocess_Popen = None

# row currently selected on widget and layout tables
selected_layout_row = 0
selected_layout_col = 1
selected_widget_row = 0
selected_container_row = 0
selected_container_col = 1

def parm_inspector(parm_list):
    ''' take the list of parameters for a widget and place them in the "parameter inspector" 
        which is nothing more than a series of input widgets
        and returns a list of default parameters name / value / parameter index '''
    dflt_props = []
    parm_cnt = len(parm_list)
    for i in range(gc.MAX_PROPERTIES):
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

def dflt_parms(parm_list):
    ''' take the list of parameters for a widget and returns a list of default parameters name / value / parameter index '''
    dflt_props = []
    for i in range(len(parm_list)):
        element = str(parm_list[i]).split("=")
        parm_name = str(element[0]).strip()
            
        if len(element) == 2:
            parm_value = str(element[1]).strip()
        else:
            parm_value = ''

        dflt_props.append([parm_name,parm_value,i])
    return dflt_props    

def create_widget_code(winfo):
    ''' Create widget code from passed  dictionary data (winfo) '''
    widget = winfo[WDGT_IDX]
    # if widget == 'None':
    #     dflts = parm_inspector(gw.get_props('None')) 
    # else:   
    #     dflts = parm_inspector(gw.get_props(getattr(sg,widget)))

    widget_text = 'sg.' + str(widget) + '('
    for parms in winfo[PARM_IDX]:
        param_name =parms[1]
        param_value =  parms[2]
        #param_value_pair = dflts[parms[0]]
        # # test parameter type: 1)  uses "parameter name = parameter value" or 2) positional value
        # if param_value_pair[1] != '': 
        # # add "parameter name = parameter value"
        #     widget_text += param_name + '=' 
        widget_text += param_name + '='    
        # now add parameter value, note we need to look up whether this should be quoted or not
        # somewhat of a cheap hack to add needed info
        if param_name in  gw.quoted_properties:
            if "'" in param_value:
                pass
            else:
                param_value = "'" + param_value + "'"

        widget_text += param_value + ','
        
    widget_text = widget_text[:-1] + ')'
    return widget_text

def save_widget(values):
    ''' save the widget currently displayed on the entry screen / parameter inspector '''
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

# First figure out which parameters user changed, add them to parm_list
# rem we should have a 1 to 1 relationship between Dflt_parms  and the input box id of the property inspector

    parm_list = []
    parm_cnt = len(Dflt_parms)
    if parm_cnt > gc.MAX_PROPERTIES:
        parm_cnt = gc.MAX_PROPERTIES

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
            #print (parm_value, widget_parm_value)
            if parm_value != widget_parm_value:
                parm_list.append([parm_idx,parm_name,widget_parm_value])
            else:
                # add default key?
                if parm_name == 'key' and dflt_key != None:
                    parm_list.append([parm_idx,parm_name,str(dflt_key)])  
  
   
    # place widget key in table
    #table_update(values['-WIDGET_ID-'])
    widget_name = values['-WIDGET_ID-'] 
    if tablevalues[row][col] == widget_name:
        pass
    elif tablevalues[row][col] == gc.EMPTYCELL:
        if is_duplicate(tablevalues,widget_name):
           widget_name = widget_name+'_cpy'
           sg.popup("Note: Id name is a duplicate, changed to: " + widget_name ) 
        tablevalues[row][col] = widget_name 
    else:
        if is_duplicate(tablevalues,widget_name):
           widget_name = widget_name+'_cpy'
           sg.popup("Note: Id name is a duplicate, changed to: " + widget_name )
        msg = ' Widget existing at this location, Insert Before ' + tablevalues[row][col] + '?'
        if sg.popup_yes_no(msg) == "Yes":
            tablevalues[row].insert(col,widget_name)
            # if "extra" cell on end of list is empty, tirm it else warn
            if len(tablevalues[row]) > table_col_count:
                if tablevalues[row][table_col_count] == gc.EMPTYCELL:
                    tablevalues[row].pop() 
                else:
                    msg = 'Warning, Widget Table Row:' + str(len(tablevalues[row])) + ' Contains a value and is not Visable \n'
                    msg += 'Suggest saving data, then restart guibuilder with larger column count'
                    sg.popup(msg)  

    # we now save widget position in table at time of form data save only
    # this means we must test for a "move" of the widgets within the table
    # if we are doing this create a "copy
    # we need to make sure we didn't "move" this widget to a new position 
 
    Saved_widgets[widget_name] = [values['-SEL_WIDGET-'][0],0, 0, parm_list]                

    refresh_table()

    # attempt simple syntax validation of widget code and warn user if something not correct
    widget_code = create_widget_code(Saved_widgets[widget_name])
    try:
        eval(widget_code) 
     #   ast.parse(widget_code)
    
    except (NameError, SyntaxError):
        sg.popup('Warning: Syntax Error in widget code', widget_code) 
    
    except Exception as e:
        sg.popup('Warning: Error in widget code', f"{type(e)}: {e} \n" +widget_code) 
    


def delete_widget(values):
# delete the currently selected widget
    global Saved_widgets

    key = values['-WIDGET_ID-']
    if Saved_widgets[key] == None:
        return
    if sg.popup_ok_cancel('Delete - ' + key +'?') == 'OK':
        del Saved_widgets[key]
        save_postion_data()
        load_widget_table()
        refresh_table() 
        window['Delete Widget'].update(visible = False)


def getwidget(row,col):
    ''' get the widget at the cell clicked and display in the property inspector '''
    global Dflt_parms, Saved_widgets, tablevalues

# update col and row selected    
    window['-COL-'].update(value = col)
    window['-ROW-'].update(value = row)
# table was clicked at cell row,col see if we have anthing saved there (or more precisely in tablevalues)
    if tablevalues[row][col] == gc.EMPTYCELL:
        # empty cell, update row and col selection for next widget add
        window['-WIDGET_ID-'].update(value = '')
    #    window['-WIDGET_ID2-'].update(value = '')

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
        index = gw.widget_list.index(widget)
        window['-SEL_WIDGET-'].update(set_to_index=[index], scroll_to_index=index)
        window['-WIDGET_ID-'].update(value =key)
    #    window['-WIDGET_ID2-'].update(value = key)
        window['-WIDGET_TYPE-'].update(value = widget + ' ('+key+')')
        saved_parms = wInfo[PARM_IDX]
        for parm in saved_parms:
    #     rem parameters saved as  [parm_idx,parm_name,widget_parm_value]
            parm_idx = parm[0]
            parm_name = parm[1]
            parm_value = parm[2]
            window[f'-PARM_VALUE_KEY{parm_idx}-'].update(value = parm_value)
    # show the delete key
        window['Delete Widget'].update(visible = True)

def save_postion_data():
    '''Add  row and column positions for widgets in widget table to Saved_widgets'''
    global Saved_widgets
    for row in range(len(tablevalues)):
        for col in range(len(tablevalues[row])):
            key = tablevalues[row][col]
            if key != gc.EMPTYCELL:
                if key in Saved_widgets:
                    wInfo = Saved_widgets[key] 
                    up_dict = {key:[wInfo[WDGT_IDX],row,col,wInfo[PARM_IDX]]}
                    Saved_widgets.update(up_dict) 

def is_duplicate(table_list,id_to_test): 
    ''' is id_to_test already in table?'''
    for row in table_list:
        for cell_value in row:
            if cell_value == id_to_test:
                return True
    return False               

################################## layout functions ######################################################################

def add_layout_id(row,values):
    ''' add layout id to selected layout row '''
    if not values['-LAYOUT_ID-']:
        sg.popup('Layout Id Not Specified')
        return

    layoutvalues[row][0] = values['-LAYOUT_ID-']
    refresh_layout_table()

def add_widget(row,col,values):
    ''' add selected widget to selected (row,col) layout location '''
    if col < 1:
        sg.popup('Cannot Add Widget to Layout Id')
        return
    if layoutvalues[row][0] == gc.EMPTYCELL:
        sg.popup('No Layout Id Defined for this Row')
        return 
    
    if (layoutvalues[row][col] == gc.EMPTYCELL):
        pass
    else:
        sg.popup('There is a widget at this position, not allowed' )
        return  

    msg = ' Add Widget: ' + values['-WIDGET_ID-'] + '\n'
    msg += ' To Layout: ' + layoutvalues[row][0] +' ?'
    if sg.popup_yes_no(msg) == "Yes":
        layoutvalues[row][col] = values['-WIDGET_ID-']
        refresh_layout_table()

def clear_widget(row,col):
    ''' remove selected widget from selected (row,col) layout location '''
    
    if (layoutvalues[row][col] == gc.EMPTYCELL):
        pass
    else:
        msg = ' Clear Widget: ' + layoutvalues[row][col] + '\n'
        msg += 'From Layout: ' + layoutvalues[row][0] +' ?'
        if sg.popup_yes_no(msg) == "Yes":
            layoutvalues[row][col] = gc.EMPTYCELL
            refresh_layout_table()

def clear_layout_row(row):
    # clear layout row
    msg = ' Clear Layout Row: ' + str(row) + '?'
    if sg.popup_yes_no(msg) == "Yes":
        for col in range(len(layoutvalues[row])):
            layoutvalues[row][col] = gc.EMPTYCELL
        refresh_layout_table()

def create_row_layout(layoutid,row):
    ''' Create layout for widgets defined in "row" of the widget table
        Add to first availalbe layout table row assigning "layoutid as layout id '''
    global layoutvalues

    # find first empty row
    emptyrowfound = False
    for rc in range(len(layoutvalues)):
        if layoutvalues[rc][0] == gc.EMPTYCELL:
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
        if widget != gc.EMPTYCELL:
            col +=1
            layoutvalues[rc][col] = widget
      
    window['-LAYOUT_TABLE-'].update(values = layoutvalues)
    return 

def create_layout_code(Add_layout):
    '''parse layout table entries and generate pysimplegui layouts 
       if Add_layouts True, place layout code in editor window 
       return layout dictionary
       key: layout id value: widget code'''
    # first clear out anything there
    if Add_layout:
        window['_BODY_'].update(value='')
        insert_text('# guibuildertestlayoutfile')
        insert_text('import PySimpleGUI as sg')

    layout_list = []
    layout_dict = {}
    Last_LayoutId_Was_Continue = False
   
    for rc in range(len(layoutvalues)):
        
        if layoutvalues[rc][0] == gc.EMPTYCELL:
            pass
        elif layoutvalues[rc][0] == gc.CONTINUE_LAYOUT:
            # add this row to the previous layout as a new "row"
            layout_preamble = '['
            Last_LayoutId_Was_Continue = True
            last_layoutid = layoutid
            widgets_text = parse_layout_widgets(rc,layout_preamble)
            if Add_layout:
                insert_text(widgets_text)
            else:
                layout_dict[last_layoutid] = layout_dict[last_layoutid] + ',' + widgets_text 
            
        else:
            # assume layout row with a layout id
            if Last_LayoutId_Was_Continue:
                if Add_layout:
                    insert_text(']') 
                else:
                    layout_dict[last_layoutid] = layout_dict[last_layoutid] + ']'
                    

            Last_LayoutId_Was_Continue = False
            layoutid = layoutvalues[rc][0]
            if Add_layout:
                layout_preamble = layoutid  + '= ['
            else:
                layout_preamble = '['

            # is the next layout row a continuation?
            nxt_rc = rc + 1
            if nxt_rc < len(layoutvalues):
                if layoutvalues[nxt_rc][0] == gc.CONTINUE_LAYOUT:
                    if Add_layout:
                        layout_preamble = layoutid  + '= [[' 
                    else:
                        layout_preamble = '[['  
            
            widgets_text = parse_layout_widgets(rc,layout_preamble)
            if Add_layout:
                insert_text(widgets_text)
            # add to id to the list of layouts created
            layout_list.append(layoutid)
            # and add layout id to dictionary
            layout_dict[layoutid] = widgets_text

    if Last_LayoutId_Was_Continue:
        if Add_layout:
            insert_text(']') 
        else:
            layout_dict[last_layoutid] = layout_dict[last_layoutid] + ']'

    if Add_layout:
        insert_text('layout = [')       
        for layout in layout_list:
            insert_text('[' + str(layout) + '],')
        insert_text(']') 

    return layout_dict

def parse_layout_widgets(rc,preamble_layout_text):
    ''' Parse layout table row rc returning widget code '''
    layout_text = preamble_layout_text
    for widx in range(1, len(layoutvalues[rc])):
        widget_id = layoutvalues[rc][widx]
        if widget_id !=  gc.EMPTYCELL:
            if widget_id in Saved_widgets:
                winfo = Saved_widgets[widget_id]
                widget_text = create_widget_code(winfo)
                layout_text += widget_text + ','
            else:
                sg.popup(widget_id + ' not found, delted?')

    # do we need the ',' at the end?       
    nxt_rc = rc + 1
    if nxt_rc < len(layoutvalues):
        if layoutvalues[nxt_rc][0] == gc.CONTINUE_LAYOUT:
            layout_text = layout_text[:-1] + '],'
        else:
            layout_text = layout_text[:-1] + ']' 
    else:
        layout_text = layout_text[:-1] + ']'         
    #print (layout_text)
    # add this layout id to editor window
    #insert_text(layout_text)
    return layout_text
################# container functions ###########################################

def save_container(values,row):
    ''' save the container currently displayed on the entry screen / parameter inspector  '''
    global Saved_containers, containervalues
# save the conainer widget currently displayed on the entry screen / parameter inspector 
# then place it on the container table
# do some error checking first 
# rem - values['-key-'] return a list
# and an empty list is false (implicit booleanness of the empty list)
    if not values['-SEL_CONTAINER-']:
        sg.popup('No Container Widget Selected')
        return
    if not values['-CONTAINER_ID-']:
        sg.popup('Missing Container Id')
        return

# First figure out which parameters user changed, add them to parm_list
# rem we should have a 1 to 1 relationship between Dflt_parms  and the input box id of the property inspector

    parm_list = []
    parm_cnt = len(Dflt_parms)
    if parm_cnt > gc.MAX_PROPERTIES:
        parm_cnt = gc.MAX_PROPERTIES

    # auto create key value?
    if values['-SAVE_AS_KEY-'] == True:
        dflt_key = '-' + str(values['-CONTAINER_ID-'])  + '-'
        dflt_key = dflt_key.upper()
    else:
        dflt_key = None      

    for i in range(parm_cnt):
        if values[f'-PARM_VALUE_KEY{i}-']:
            parm_name = str(Dflt_parms[i][0])
            parm_value = str(Dflt_parms[i][1])
            parm_idx = Dflt_parms[i][2]
            widget_parm_value = str(values[f'-PARM_VALUE_KEY{i}-'])
            #print (parm_value, widget_parm_value)
            if parm_value != widget_parm_value:
                parm_list.append([parm_idx,parm_name,widget_parm_value])
            else:
                # add default key?
                if parm_name == 'key' and dflt_key != None:
                    parm_list.append([parm_idx,parm_name,str(dflt_key)])   

    # check for missing required parameters, add as necessary
    for i in range(len(Dflt_parms)):
        parm_name = str(Dflt_parms[i][0])
        parm_value = str(Dflt_parms[i][1])
        # we are making the assumtion that parameters with no default value are required?
        if parm_value == '':
            parm_found = False
            for parm_entry in parm_list:
                if parm_name == parm_entry[1]:
                    parm_found = True
                    break
            if not parm_found:
                parm_idx = Dflt_parms[i][2]
                parm_list.insert(0,[parm_idx,parm_name,''])

#
#  place container name on selected row
    container_name = values['-CONTAINER_ID-'] 
    if containervalues[row][0] == container_name:
        pass
    elif containervalues[row][0] == gc.EMPTYCELL:
        if is_duplicate(containervalues,container_name):
           container_name =container_name+'_cpy'
           sg.popup("Note: Id name is a duplicate, changed to: " + container_name ) 
        containervalues[row][0] = container_name 
    else:
        if is_duplicate(containervalues,container_name):
           container_name =container_name+'_cpy'
           sg.popup("Note: Id name is a duplicate, changed to: " + container_name )
        msg = ' Container Widget existing at this location, Insert Before ' + containervalues[row][0] + '?'
        if sg.popup_yes_no(msg) == "Yes":
            newrow = [gc.EMPTYCELL for col in range(table_col_count)]
            newrow[0] = container_name
            containervalues.insert(row,newrow)

    Saved_containers[container_name] = [values['-SEL_CONTAINER-'][0],0, [], parm_list]                

    refresh_container_table()

    # attempt simple syntax validation of widget code and warn user if something not correct
    widget_code = create_widget_code(Saved_containers[container_name])
    #
    # do some simple container code syntax checking
    # first get the element
    widget = Saved_containers[container_name][WDGT_IDX]
    # only test for real widgets not dummy type none
    if widget != 'None':
        wmsg = container_syntax_check(widget,widget_code)
        if wmsg != None:
            sg.popup(wmsg)

        try:
     #   eval(widget_code)  
     #   print(widget_code)
            ast.parse(widget_code)
    
        except (NameError, SyntaxError):
            sg.popup('Warning: Syntax Error in widget code', widget_code) 
    
        except Exception as e:
            sg.popup('Warning: Error in widget code', f"{type(e)}: {e} \n" +widget_code) 
    
def save_container_pos_data(): 
    '''Add  row positions for container widgets in container table'''
    global Saved_containers
    for row in range(len(containervalues)):
        key = containervalues[row][0]
        if key != gc.EMPTYCELL:
            if key in Saved_containers:
                layout_list = []
                for col in range(len(containervalues[row])):
                    layout_id = containervalues[row][col]
                    if layout_id != gc.EMPTYCELL:
                        layout_list.append(layout_id)        
                wInfo = Saved_containers[key] 
                up_dict = {key:[wInfo[WDGT_IDX],row,layout_list,wInfo[PARM_IDX]]}
                Saved_containers.update(up_dict) 

def container_syntax_check(widget,widget_code):
    '''check for required parameters for element widget in code widge_code returning warning message'''
    wmsg = ''
    emsg = None

    if widget == 'Pane':
        if 'pane_list' in widget_code:
            pass
        else:
            wmsg = 'requires pane_list parameter \n'
    else:
      
        if 'layout' in widget_code:
            pass
        else:
            wmsg = 'requires layout parameter \n'

        if widget == 'Frame':
            if 'title' in widget_code:
                pass
            else:
                wmsg += 'requires title parameter \n'

    if len(wmsg) > 0:
        emsg = 'Warning element type ' + widget + ': \n' + wmsg
        
    return emsg               

def getcontainer(row):
    ''' get the container widget at the cell clicked and display in the property inspector '''
    global Dflt_parms, Saved_containers, containervalues

# table was clicked at cell row,col see if we have anthing saved there (or more precisely in tablevalues)
    if containervalues[row][0] == gc.EMPTYCELL:
        pass
    else:
        # cell location has a widget here, edit or delete?
        key = containervalues[row][0]
        wInfo = Saved_containers[key]
        if wInfo == None:
            sg.popup('Error', key + ' Not Found in Saved_containers?')
            return
        widget = wInfo[WDGT_IDX]
        if widget == 'None':
            Dflt_parms = parm_inspector(gw.get_props('None')) 
        else:   
            Dflt_parms = parm_inspector(gw.get_props(getattr(sg,widget)))

        #
        # now updated inspector with saved info
        #
        index = gw.container_list.index(widget)
        window['-SEL_CONTAINER-'].update(set_to_index=[index], scroll_to_index=index)
        window['-WIDGET_TYPE-'].update(value = widget + ' ('+key+')')
        window['-CONTAINER_ID-'].update(value = key)
        saved_parms = wInfo[PARM_IDX]
        for parm in saved_parms:
    #     rem parameters saved as  [parm_idx,parm_name,widget_parm_value]
            parm_idx = parm[0]
            parm_name = parm[1]
            parm_value = parm[2]
            window[f'-PARM_VALUE_KEY{parm_idx}-'].update(value = parm_value)

def delete_container(row):
# delete the currently selected container
    global Saved_containers, containervalues

    key = containervalues[row][0]
    if key == gc.EMPTYCELL:
        sg.popup('Nothing to delete')
    elif Saved_containers[key] == None:
        sg.popup('Nothing to delete')
    elif sg.popup_ok_cancel('Delete - Container ' + key +' ?') == 'OK':
        del Saved_containers[key]
        for col in range(len(containervalues[row])):
            containervalues[row][col] = gc.EMPTYCELL
        refresh_container_table() 

def clear_layout(row,col):
    global containervalues
    if col > 0:
        containervalues[row][col] = gc.EMPTYCELL
        refresh_container_table()

def add_layout(row,col):
    ''' add selected layout to selected (row,col) container location '''
    if col < 1:
        sg.popup('Cannot Add Layout to Container Id')
        return
    if containervalues[row][0] == gc.EMPTYCELL:
        sg.popup('No Container Id Defined for this Row')
        return 

    layout_id = layout_list_popup()  
    if layout_id != None: 
        if layout_id == containervalues[row][0]:
            sg.popup('cannot use Container ID as Layout') 
            return
        else:
            # test for duplicate use of Container Id
            for myrow in containervalues:
                for mycol in range(len(myrow)):
                    if mycol == 0:
                        pass
                    elif layout_id == myrow[mycol]:
                        sg.popup('cannot reuse layout: ' + layout_id)
                        return
    containervalues[row][col] = layout_id
    refresh_container_table()


def layout_list_popup():
    '''creates and displays list of valid layout selections'''

    def build_select_list(list,table):
        '''builds select list list from table'''   
        for row in range(len(table)):
            layout_id = table[row][0]
            if layout_id != gc.EMPTYCELL:
                list.append(layout_id)  

    layout_list = []
    build_select_list(layout_list,layoutvalues)
    build_select_list(layout_list,containervalues)
    
    layout = [
        [sg.Text('Select Layout Id')],
        [sg.Listbox(layout_list,size=(20,5),key='-SELECTED-',select_mode= 'LISTBOX_SELECT_MODE_SINGLE')],
        [sg.Button('OK')]
    ]

    window = sg.Window('POPUP', layout).Finalize()

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == 'OK':
            break
 
    window.close()

    if values and values['-SELECTED-']:
        return values['-SELECTED-'][0]
    else:
        return None


def create_container_code():

    # expand all layouts and place in dict dict_layout_codes, key: layout id value: widget code
    dict_layout_codes = create_layout_code(False)

# pass 1
#   create dict_container_ids:
#   key: container id values = [0] list of layout and container ids for this container 
#                              [1] T/F has this container been referenced by another container?
#
    dict_container_ids ={}
    for row in range(len(containervalues)):
        layout_id_list = []
        container_id = containervalues[row][0]
        if container_id != gc.EMPTYCELL:
            if container_id in Saved_containers:
                for layout_idx in range(1,len(containervalues[row])):
                    layout_id = containervalues[row][layout_idx]
                    if layout_id != gc.EMPTYCELL:
                        layout_id_list.append(layout_id)
                dict_container_ids[container_id] = [layout_id_list,False] 

# pass 2 expand layouts (reference in dict_container_ids as either layout ids or contianer id) into actual widget code
#   create dict_container_codes:
#   key: container id values = [0] list of expanded layout code for conatiner 
#                              [1] T/F has this container been referenced by another container?
    dict_container_layouts = {}
    for container_id in dict_container_ids:
        
        list_of_ids_to_expand = dict_container_ids[container_id][0]
        for id in list_of_ids_to_expand:
                # is the id a layout id?
            if id in dict_layout_codes:
                # expand the id to widget code
                dict_container_layouts[id] = dict_layout_codes[id]
            # is it another container?
            elif id in dict_container_ids:
                # expand the id to container code
                layout_code_list = dict_container_ids[id][0] 
                layout_code = layout_list_to_string(id,layout_code_list,dict_container_ids)
                dict_container_layouts[id] = layout_code
                # and mark container as referenced by another container
                up_dict =dict_container_ids[id] 
                up_dict[1] = True
                dict_container_ids[id] = up_dict
            else:
                sg.popup('Cannot find: ' + id, 'in  Cannot process!')

    # pass 3 process remaining layouts
    for container_id in  dict_container_ids:
        if dict_container_ids[container_id][1] == False:
            layout_code_list = dict_container_ids[container_id][0]
            layout_code = layout_list_to_string(container_id,layout_code_list,dict_container_ids)
            dict_container_layouts[container_id] = layout_code

    # # some degug info
    # dict_layout_codes
    # print ('dict_layout_codes -------------------------------------------')
    # for layout_id in  dict_layout_codes:
    #     print(layout_id,dict_layout_codes[layout_id])

    # print ('dict_container_ids -------------------------------------------')
    # for container_id in  dict_container_ids:
    #     print(container_id,dict_container_ids[container_id])
    
    # print ('dict_container_layouts --------------------------------------:')
    # for container_id in  dict_container_layouts:
    #     print(container_id,dict_container_layouts[container_id])

    # pass 4 output layouts adding  container widget as necessary
    #  first setup editor
    window['_BODY_'].update(value='')
    insert_text('# guibuildertestlayoutfile')
    insert_text('import PySimpleGUI as sg')
    
    for layout_id in dict_container_layouts:
        if layout_id in Saved_containers:
            winfo = Saved_containers[layout_id]
            widget = Saved_containers[layout_id][WDGT_IDX]
            container_layout = dict_container_layouts[layout_id]
            # add full widget code
            #
            if widget == 'Pane':
                # set pane_list parameter
                replace_dict = {}
                replace_dict['pane_list'] = container_layout
            else:
                # set layout parameter
                replace_dict = {}
                replace_dict['layout'] = container_layout

            if widget == "None":
                widget_text = layout_id + '= ' + dict_container_layouts[layout_id]
            else:
                widget_text = layout_id + '= [' + create_widget_code_replacing(winfo,replace_dict) + ']'

            insert_text(widget_text)

        else:
            # simple layout
            widget_text = layout_id + '= ' + dict_container_layouts[layout_id] 
            insert_text(widget_text)
    
    # pass 5, add in the all important layout statement
    # we add any containers that have not been previously referenced.
    layout_text = 'layout = ['
    for container_id in  dict_container_ids:
        if dict_container_ids[container_id][1]:
            pass  # this container has been previously referenced 
        else:
            layout_text += '[' + container_id + '],'
    layout_text = layout_text[:-1] + ']'
    insert_text(layout_text)
    

def layout_list_to_string(container_id,layout_code_list,dict_container_ids):
    '''convert list of layouts in layout_code_list to string'''
    # layout_code = '['
    # for layout_id in layout_code_list:
    #     layout_code += layout_id + ','
    # layout_code = layout_code[:-1] + ']'
    # 
    # we have an issue to figure out here, if the container only includes layouts then we create a list element (,)
    # otherwise we join (+) not sure how to handle both container and layout reference in a container???
    all_layouts = True
    layout_code = ''
    for layout_id in layout_code_list:
        if layout_id in dict_container_ids:
            # is a container
            all_layouts = False
            layout_code += layout_id + '+'
        else:
            # is a layout          
            layout_code += layout_id + ','

    layout_code = layout_code[:-1]
    # not sure if this works:
    # if layout_ids are all layouts, we add in the extra list bracket
    # elif there are multiple layouts/containers, we add in the extra list bracket 
    if all_layouts:
        layout_code = '['+ layout_code + ']'
    elif len(layout_code_list) > 1:
        layout_code = '['+ layout_code + ']'

    return layout_code

def create_widget_code_replacing(winfo,replacement_dict):
    ''' Create widget code from passed dictionary data (winfo) replacing parameter values defined in replacement_dict
        replacement_dict: dictionary of: replace param : key  text to add : value'''
    widget = winfo[WDGT_IDX]
    dflts = dflt_parms(gw.get_props(getattr(sg,widget)))

    widget_text = 'sg.' + str(widget) + '('
    for parms in winfo[PARM_IDX]:
        param_name =parms[1]
        param_value =  parms[2]
        param_value_pair = dflts[parms[0]]
        if param_name in replacement_dict:  
            widget_text += param_name + '=' + replacement_dict[param_name] + ',' 
        else:
            widget_text += param_name + '='
            if param_name in  gw.quoted_properties:
                if "'" in param_value:
                    pass
                else:
                    param_value = "'" + param_value + "'"
            widget_text += param_value  + ','
        
    widget_text = widget_text[:-1] + ')'
    return widget_text



################# table functions ###############################################
def refresh_table():
    window['-TABLE-'].update(values = tablevalues)

def refresh_layout_table():
    window['-LAYOUT_TABLE-'].update(values = layoutvalues) 

def refresh_container_table():
    window['-CONTAINER_TABLE-'].update(values = containervalues)  

def move_row_up(t_key,t_values,t_row):
    '''move selected row - t_row for t_key / t_values - table up one row'''
    if t_row == 0:
        pass  # already at the top!
    else:
        temp_row = t_values[t_row - 1]
        t_values[t_row-1] = t_values[t_row]
        t_values[t_row] = temp_row
        window[t_key].update(values = t_values)

def move_row_down(t_key,t_values,t_row):
    '''move selected row - t_row for t_key / t_values - table down one row'''
    if t_row == len(t_values)-1:
        pass  # already at the bottom!
    else:
        temp_row = t_values[t_row + 1]
        t_values[t_row+1] = t_values[t_row]
        t_values[t_row] = temp_row
        window[t_key].update(values = t_values)     

def load_widget_table():
    ''' load widiget table from Saved_widgets'''
    global tablevalues
    # first initialize table data with gc.EMPTYCELL
    tablevalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)]

    # now populate with defined widgets
    for key in Saved_widgets:
        wInfo = Saved_widgets[key]
        row = int(wInfo[ROW_IDX])
        col = int(wInfo[COL_IDX])
        tablevalues[row][col] = key 

def load_container_table():
    ''' load container table from Saved_containers'''
    global containervalues
    # first initialize table data with gc.EMPTYCELL
    containervalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)]

    # now populate with defined widgets
    for key in Saved_containers:
        wInfo = Saved_containers[key]
        row = int(wInfo[ROW_IDX])
        col = 0
        for cell_value in wInfo[LAY_IDX]:
            containervalues[row][col] = cell_value 
            col += 1       

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

def save_file(file,values):
    '''Save file instantly if already open; otherwise use `save-as` popup'''
    if file:
        file.write_text(values.get('_BODY_'))
    else:
        save_file_as()

def save_file_as(values):
    '''Save new file or save existing file with another name'''
    filename = sg.popup_get_file('Save As', save_as=True, no_window=True)
    if filename:
        file = pathlib.Path(filename)
        file.write_text(values.get('_BODY_'))
        window['_INFO_'].update(value=file.absolute())
        return file

def execute_py_file(values):
    ''' execute the script written to the editor window '''
    global subprocess_Popen

# should probably create a temp file for this, but not today
    # if we already kicked off the viewer, terminate it
    if subprocess_Popen != None:
        if subprocess_Popen.poll() == None:
        #    subprocess_Popen.terminate()    # note this should work, but does not on Windows
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(subprocess_Popen.pid)])
      
    file = pathlib.Path(gc.GUIBUILDER_TEST_LAYOUT_FILE) 
    file.write_text(values['_BODY_'])
    # do we have the script to execute the layout?
    tstfile = pathlib.Path(gc.GUIBUILDER_TEST_FILE)
    if tstfile.is_file():
        subprocess_Popen = sg.execute_py_file(gc.GUIBUILDER_TEST_FILE)
    else:
        sg.popup('Missing ' + gc.GUIBUILDER_TEST_FILE)

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


########################################## main menu functions  ##################################
def show_ctrl_codes():
    sg.popup('CTRL+X - Cut\nCTRL+C - Copy\nCTRL+V - Paste\n')


def about_me():
    #sg.popup_no_wait('guibuilder 0.0')
    try:
        #open text file in read mode
        text_file = open("README.md", "r")
        notes = text_file.read()
        text_file.close()
    except:
        notes = 'Could not read README.md?'

    choice, _ = sg.Window('About',[[sg.Multiline(default_text = notes,font=('Consolas', 12),size=(132,25))]]).read(close=True) 
########################################## main menu functions for saving and loading widget dictionary ##################################
def save_data(formname):
    global Saved_containers
    # save what we have worked on
    # we save widgets as a dictionary
    # layouts and containers as their respective table values
    # probably some issues will arise but for now it is what we are doing

    # first update Saved_widgets with widget table row and col positions
    save_postion_data()
    # then save container widget positions
    save_container_pos_data()

    save_data = {}
    save_data['widgets'] = Saved_widgets
    save_data['layouts'] = layoutvalues
    save_data['containers'] = Saved_containers
    try:
        with open(str(formname)+'.json','w') as fp:
            json.dump(save_data, fp, sort_keys=True, indent=4) 
            fp.close()
            sg.popup('Save Data', 'Data saved to: ' + str(formname)+'.json')
    except OSError as e:
        sg.popup(f"{type(e)}: {e}" + str(formname)+'.json')

def load_data():
    global Saved_widgets, Saved_containers, tablevalues, layoutvalues, containervalues
   
    filename = sg.popup_get_file('Open', no_window=True)
    if filename:

        try:
            with open(str(filename), 'r') as fp:
                try:
                    save_data = json.load(fp)
                    Saved_widgets = save_data['widgets']
                    layoutvalues = save_data['layouts']
                    Saved_containers =save_data['containers'] 
                    fp.close()
                    load_widget_table()
                    load_container_table()
                    refresh_table()
                    refresh_layout_table()
                    refresh_container_table()
                except Exception as e:
                    sg.popup('Loaded error', f"{type(e)}: {e}")   

        except OSError as e:
            sg.popup(f"{type(e)}: {e}" + str(filename)+'.json')

############################################## Windows                ############################################################
def main():
    global window, Dflt_parms, table_col_count, table_row_count, tablevalues, layoutvalues, containervalues
    global selected_layout_row, selected_layout_col,selected_widget_row, selected_container_row, selected_container_col

    # user can specify starting row and col count for tables

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--columns', help='Initial table column count', type=int, default=table_col_count)
    parser.add_argument('-r', '--rows', help='Initial table row count', type=int, default=table_row_count)
    args = parser.parse_args()
    
    table_col_count = args.columns
    table_row_count = args.rows

    # layout table values, start as empty cell
    tablevalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)]
    layoutvalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)] 
    containervalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)] 
        
    layout = gl.create_layout(table_col_count,tablevalues,layoutvalues,containervalues)
    window = sg.Window('guiBuilder', layout=layout, margins=(0, 0),size=gc.WINDOW_SIZE, resizable=True,  finalize=True)
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

        # table events
        elif isinstance(event, tuple):
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # You can also call Table.get_last_clicked_position to get the cell clicked
            #if event[2][0] == -1 and event[2][1] != -1:           # Header was clicked and wasn't the "row" column
            if event[0] == '-TABLE-':
                if event[2][0] == None:           # column resize was attempted
                    pass
                elif (event[2][0] == -1) or (event[2][1] == -1):
                    pass  # header or "row" column was clicked
                else:
                    # cell was clicked, get widget (if any)
                    selected_widget_row = event[2][0] 
                    getwidget(event[2][0],event[2][1])

            elif event[0] == '-LAYOUT_TABLE-':
                selected_layout_row = event[2][0] 
                selected_layout_col = event[2][1]
                window['-LAYOUT_COL_ROW_TXT-'].update(value=gc.SELECT_CELL_TEXT + str(selected_layout_row) + ' / ' + str(selected_layout_col))

            elif event[0] == '-CONTAINER_TABLE-':
                selected_container_row = event[2][0] 
                selected_container_col = event[2][1]
                window['-CONTAINER_COL_ROW_TXT-'].update(value=gc.SELECT_CELL_TEXT + str(selected_container_row) + ' / ' + str(selected_container_col))
                # did we click on the container widget?
                if selected_container_col == 0:
                    getcontainer(selected_container_row)

    # table move events move selected row up or down
        elif event == '-WIDGET_UP-':
            move_row_up('-TABLE-',tablevalues,selected_widget_row)
        elif event == '-WIDGET_DOWN-':
            move_row_down('-TABLE-',tablevalues,selected_widget_row)
        elif event == '-LAYOUT_UP-':
            move_row_up('-LAYOUT_TABLE-',layoutvalues,selected_layout_row)
        elif event == '-LAYOUT_DOWN-':
            move_row_down('-LAYOUT_TABLE-',layoutvalues,selected_layout_row) 
        elif event == '-CONTAINER_UP-':
            move_row_up('-CONTAINER_TABLE-',containervalues,selected_container_row)
        elif event == '-CONTAINER_DOWN-':
            move_row_down('-CONTAINER_TABLE-',containervalues,selected_container_row)   

    # Menu events

        elif event == 'Load':
            if sg.popup_ok_cancel('Warning, existing data will be overwritten') == 'OK':
                load_data()

        elif event == 'Save':
            if not values['-FORM_NAME-']:
                sg.popup('Save Data','No Form Name')
            else:
                save_data(values['-FORM_NAME-'])

        elif event == 'About':
            about_me()

        elif event == 'Ctrl Code':
            show_ctrl_codes()

    # Button Menu -FILE- Events
        elif event == '-EFILE-':
            if values['-EFILE-'] == 'New':
                file = new_file()
            if values['-EFILE-'] == 'Open':
                file = open_file()
            if values['-EFILE-'] == 'Save':
                save_file(file,values)
            if values['-EFILE-'] == 'Save As':
                file = save_file_as(values)
            if values['-EFILE-'] == 'Exit':
                break
    # cut copy paste
        elif event == 'Cut':
            cut_text()
        elif event == 'Copy':
            copy_text()
        elif event == 'Paste':
            paste_text() 
        elif event == 'View Layout':
            execute_py_file(values)

    # Button Menu -TOOL- Events
        elif event == '-ETOOLS-':
            if values['-ETOOLS-'] == 'Insert':
                insert_text('My dummy text to insert')
            elif values['-ETOOLS-'] == 'Version':
                sg.main_get_debug_data()

        elif event == '-SEL_WIDGET-' and len(values['-SEL_WIDGET-']):
            widget = values['-SEL_WIDGET-'][0]
        # rem returns default property values, used to id which ones user entered and needs to be saved
            Dflt_parms = parm_inspector(gw.get_props(getattr(sg,widget)))
            window['-WIDGET_TYPE-'].update(value = widget)

        elif event == '-SEL_CONTAINER-' and len(values['-SEL_CONTAINER-']):
            container = values['-SEL_CONTAINER-'][0]
            window['-WIDGET_TYPE-'].update(value = container)
        # rem returns default property values, used to id which ones user entered and needs to be saved
            if container == 'None':
                Dflt_parms = parm_inspector(gw.get_props('None')) 
            else:   
                Dflt_parms = parm_inspector(gw.get_props(getattr(sg,container)))

        elif event == 'Save Widget':
            save_widget(values)
        
        elif event == 'Delete Widget':
            delete_widget(values)

    # layout tab events  
        elif event == 'Add Id':
            add_layout_id(selected_layout_row,values)

        elif event == 'Continue Layout':
            layoutvalues[selected_layout_row][0] = gc.CONTINUE_LAYOUT
            refresh_layout_table()

        elif event == 'Add Widget':
            add_widget(selected_layout_row,selected_layout_col,values)

        elif event == 'Clear Widget':
            clear_widget(selected_layout_row,selected_layout_col)  

        elif event == 'Clear Row':
            clear_layout_row(selected_layout_row)  

        elif event == 'Add Row':  
            if not values['-LAYOUT_ID-']:
                sg.popup('Missing Layout Id')
            else:
                layoutid = values['-LAYOUT_ID-']
                create_row_layout(layoutid,selected_widget_row)

        
        elif event == 'Auto Create':
            # create layouts for each row of widgets in widget table
            # first clear the layout table
            layoutvalues = [[gc.EMPTYCELL for col in range(table_col_count)] for count in range(table_row_count)] 
            window['_BODY_'].update(value='')
            for rw in range(len(layoutvalues)):
                for widget in tablevalues[rw]:
                    if widget != gc.EMPTYCELL: 
                        # this row has atleast one widget in it, process 
                        # cheap hack for layout id, need to figure something better (and unique)
                        layoutid = 'layout'+str(rw) 
                        create_row_layout(layoutid,rw)
                        break

        elif event == 'Generate Layout':
            create_layout_code(True)

########################## container tab events ###########################################

        elif event == 'Save Container':
            save_container(values,selected_container_row)

        elif event == 'Del Container':
            delete_container(selected_container_row)

        elif event == 'Clear Layout':
           clear_layout(selected_container_row,selected_container_col)

        elif event == 'Add Layout':
            add_layout(selected_container_row,selected_container_col)

        elif event == 'Generate Code':
            create_container_code()

    window.close()

if __name__ == "__main__":
   main()    