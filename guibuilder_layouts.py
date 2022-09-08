'''
  guiBuilder_layout.py part of guiBuilder
  A minimalist pysimplegui builder
'''
import PySimpleGUI as sg
import guibuilder_widgets as gw
import guibuilder_constants as gc

def create_layout(table_col_count,tablevalues,layoutvalues,containervalues):
    ''' generate the layout for guibuilder'''
    widget_tab = [
    [sg.Text('Widget Id'),sg.Input(size=(20,1), key = '-WIDGET_ID-',do_not_clear=True,)],
    [sg.Checkbox('Save As KEY',default =True, key = '-SAVE_AS_KEY-')],
    [sg.Text('Row'),sg.Input(size=(5,1), key = '-ROW-',default_text = "0",do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-COL-',default_text = "0",do_not_clear=True,)],
    # dropdown list of widgets to select from
    [sg.Text('Widgets'),sg.Listbox(values=gw.widget_list,size=(20,5), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_WIDGET-')],
    #[sg.Button('Save Widget',tooltip='Saves widget and places on Widget Table'),sg.Button('Delete Widget',visible=False)]
    [sg.Button('Save Widget',tooltip=None),sg.Button('Delete Widget',visible=False)]
    ]

    layout_tab = [
    [sg.Text('Layout Id'),sg.Input(size=(20,1), key = '-LAYOUT_ID-',do_not_clear=True)],
    [sg.HSep()],
    [sg.Text(gc.SELECT_CELL_TEXT + ' -- ' + ' / ' + ' -- ' ,size=(30,1),relief = sg.RELIEF_SUNKEN,border_width = 2,key='-LAYOUT_COL_ROW_TXT-')],
    [sg.Button('Add Id',size=(15,1),tooltip=None),sg.Button('Continue Layout',size=(15,1),tooltip=None)],

    #[sg.Text('Row'),sg.Input(size=(5,1), key = '-C_ROW-',do_not_clear=True,),sg.Text('Col'),sg.Input(size=(5,1), key = '-C_COL-',do_not_clear=True)],
    #[sg.Button('Add Widget',tooltip= 'Appends Widget to selected Layout Table Layout')],
    #[sg.Button('Add Row',tooltip= 'Builds layout definition based on selected Widget Table Row')],
    #[sg.Button('Auto Create',tooltip='Builds layout definition based on Widget postioning in Widget Table')],
    [sg.Button('Add Widget',size=(15,1),tooltip=None),sg.Button('Clear Widget',size=(15,1),tooltip=None)],
    [sg.Button('Add Row',size=(15,1),tooltip=None),sg.Button('Clear Row',size=(15,1),tooltip=None)],
    [sg.Button('Auto Create',size=(15,1),tooltip=None)],
    [sg.HSep()],
    #[sg.Button('Generate Layout',tooltip='Creates pysimplygui code for layouts in layout definition table, places in editor')]
    [sg.Button('Generate Layout',tooltip=None)]
    ]

    container_tab = [
    [sg.Text('Container Id'),sg.Input(size=(20,1), key = '-CONTAINER_ID-',do_not_clear=True)],
    [sg.HSep()],
     # dropdown list of containers to select from
    [sg.Text('Containers'),sg.Listbox(values=gw.container_list,size=(20,3), enable_events=True,select_mode = 'LISTBOX_SELECT_MODE_SINGLE',  key ='-SEL_CONTAINER-')],
    [sg.Text(gc.SELECT_CELL_TEXT + ' -- ' + ' / ' + ' -- ' ,size=(30,1),relief = sg.RELIEF_SUNKEN,border_width = 2,key='-CONTAINER_COL_ROW_TXT-')],
    [sg.Button('Save Container',size=(15,1)),sg.Button('Del Container',size=(15,1),tooltip=None)],
    [sg.Button('Add Layout',size=(15,1),tooltip=None),sg.Button('Clear Layout',size=(15,1),tooltip=None)],
    [sg.HSep()],
    [sg.Button('Generate Code',size=(15,1),tooltip=None)]
    ]

    entry_layout =[
    [sg.Text('Form Name'),sg.Input(size=(20,1), key = '-FORM_NAME-',do_not_clear=True,)],
    [sg.HSep()],    
    [sg.TabGroup([[sg.Tab( title = 'Widgets',layout = widget_tab,background_color=gc.WIDGET_TABLE_COLOR,),sg.Tab('Layouts', layout_tab,background_color=gc.LAYOUT_TABLE_COLOR), sg.Tab('Containers', container_tab,background_color=gc.CONTAINER_TABLE_COLOR)]],key = '-TABS-',tab_location='top')], 
    [sg.HSep()],
    # parameter inspector list of labels and input boxes
#    [sg.Text('Id',size=(2,1), pad=(0,0)),sg.Text('',text_color='black',size=(12,1), pad=(0,0),relief = sg.RELIEF_SUNKEN,border_width = 1,key='-WIDGET_ID2-'),sg.Text('Type',size=(4,1), pad=(0,0)),sg.Text('',text_color='black',size=(16,1),pad=(5,0),relief = sg.RELIEF_SUNKEN,border_width = 1,key='-WIDGET_TYPE-') ],
    [sg.Text('Element Type',size=(14,1), pad=(0,0)),sg.Text('',text_color='black',size=(20,1),pad=(5,0),relief = sg.RELIEF_SUNKEN,border_width = 1,key='-WIDGET_TYPE-') ],
    *[[sg.Text(f'Parameter {i:02}',key = f'-PARM_NAME_KEY{i}-', size=(14,1), pad=(0,0)),sg.Input(size=(20,1), key = f'-PARM_VALUE_KEY{i}-',pad=(5,0))] for i in range(gc.MAX_PROPERTIES)]
    ]

    ### prebuild our layout table
    tableheadings = [f'Col {col}' for col in range(table_col_count)]
    layout_heading = [f'Widget {col}' for col in range(table_col_count)]
    layout_heading[0] = 'Layout Id'
    container_heading = [f'Layout {col}' for col in range(table_col_count)]
    container_heading[0] = 'Container Id'



    editor_layout =  [
    [sg.Text('> New file <', font=('Consolas', 10), size=(gc.WIN_W, 1), key='_INFO_')],
    [sg.Multiline(font=('Consolas', 12), size=(gc.WIN_W, gc.WIN_H), key='_BODY_')]
    ]
    
    # arrow images from the Tango Desktop Project http://tango.freedesktop.org/Tango_Desktop_Project
    down_image = b'iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAL8SURBVDiNtZRPbBRVHMc/781Md1bTGMCkhYNtOIiAnkw0bSFpNCGeOEAwMRyMMaReNCY0JXpFozQWT3JWExsEIzaxJkSREGiJIglRNCqVDSEIxlKqsN3ZeX9+HnZ2O112Wznwkl/e78283+f33nd+v1Eiwv0Y+r5QgbDdi4GR6AaermWjNX9NjZruewLj6Xp76COsNzhvsT7FeYvzBusNqUs4dPittonbgwFQnP7jCFW7QNUukLqk4T+3cc8Kl7nHoVD/a98KYEFYrBqR2lrEs1I1LQtehHgEX3signHVFU/c0HjLSHRSPIONjKFKRHws4vF4vNQsdRUSW27sGRiOFo+uOTU1agaXgL2TsZ7uR5/es/3NYhhEOLGx8xYvFrRHh4L3CQm3iAoaHcAru96IRcCYKhMnxhdmb/15sM5Tea0GhqO9m9Y/uX/H4MvFC9e+oWLnsVSp+jvMVa+R2H9BAQIiEOtOtvbs5uTUVwuXr8/snx4177bUeOo9M/brlR/Gvz13LNm8rp8gVBhV5u/qDFbfIYo1HbEmijXFYszW9bs4f/FscuXGpYk89C4wwNqSG5r+5evvf7z0ndm4tp/ZtITq8EQZMIoDOuKAvp4dlK5etj/9fu7nyrx7sZmjWpXNln2qU6nowvZnX+gNH6roi/PHCUKNDhVKweOrtlGZ0zIxefS6M/aJ6YMy18xoWW5nDshtbczg5Imj/xTcKjas6SfsUEQFzYaH+yi61Xx5/IvbQvBMK2hbMMCpMblqU7vt2OSn5e5oE+sefKxmhc0c/ny8XE3NzjMHkt/axbeUIj8GRsKdqzvXfLz7+ZceCCLFJ599WL45e3Pf6dH0g+XiloCVUgoIcqYB3fdasPeR3t7hoKBUaaZ05Oz77nXA58wBTkTsEnAGjKg1TJjzg2zWT70avBMEuuv8ITOUppgMaDOoBUw2W8DUwVEO2Ow3r00OYtqs03pL16/Q/E+sX1NnlvVdQ4LmE6dAKiL+ro/XTufMryerw10OLpKD/QceAIZcIO5IFQAAAABJRU5ErkJggg=='
    up_image = b'iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAL/SURBVDiNtZRNaFxVFMd/5368eZkxRmQsbTEGxbZC0IWMpU5SbCmxILapFCO2LgSlWbhLbFJBcKErP0BcCIqCdeEiUAviQoJIwIgW3biwCoYGjTImTIXWTjsz7+O4yLzwUkuSgjlwuPdd7vmd/z33vCuqymaY2RTqZoLdRjfunXTvg2zfNh8PT01p8r+AByf9S9vv6DuGQWr627vA6Hox65ZiYMIdva1Ufvlg9WhpaM+RYs+t5eN7J4IX1ouTtbpicCyoFEulmacOniidr8+SpBG7ynv4dPrjxpVW48i3b0Rf3rTiR8al13o3/cSBZ0uLV+f46/IFapfmWLh8nsf2PVnyzp0ZnAx33RR4cFK6U2dnDu97pie1LS5c/BFnHNZ4fl36nkZSZ6h6qBuNv6qOye0bAo+MiFXc54/uHundUt5qfln6Dmt8xx2I8MPCF5RuKcrAg0NbjHfTlVHx64Jrd9v3qv1Du/t3VPxPta+xYvHOUwgCfGBQ28Z45dzCWfruvMfdf+9D/V099vSa4IEX/fh9d1WO7a8Mhz/XZjFOCMMCYVggCD2RaeAKQlAw4CPO/XmGygMPh33bdg5XJ/ypPGulK6rj7vG+rTumnjt0qss5j5KikjAzf5pYWtSvzXMt+Wc5SuHwzpNoqmgKzXaLs9OfXK1f/OPp2bfizyD3gxgr478vznW98sHzAFgvzVdPfBj6wNFoLxLZBt4bBFAF44R3PnqtGbc17CCKOBkDVoNnX4/2X1cWNdbiA8+V1hK+YDAGEEFVsVaI2xp+82Yk19d3FfhGZozQiP9GbYwLBOMEEUFTRewNeRsEi6WZXkIMGCs4bzBOiNspsjZ3dVfIsjkRKWRrzbgBCppCmihJpGgC6EpMUUQKIrJKpMuAgO98u84cVTjQO4pKirEgIizfHqTpyhvTDcRAJCJxNne5BDYHdUD95NvHy2sfmHomImcKJKKqmeI8NBuzZKbjHb2kHY+BJFMJtIG2qqb/eTY7SWzOM6jtbElz8CQHV83B/gXtSQriGSyg6AAAAABJRU5ErkJggg=='
   
    w_arrows = [[sg.Button('',image_data=up_image,key='-WIDGET_UP-',pad = 0)],[sg.Button('',image_data=down_image,key='-WIDGET_DOWN-',pad = 0)]]
    widget_table = [
        [sg.Column(w_arrows,pad=0),
        sg.Table(tablevalues, headings=tableheadings, max_col_width=25,pad=0,
                        auto_size_columns=False,
                        font=('Consolas', 12),
                        col_widths = 25, 
                        # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                        display_row_numbers=True,
                        justification='center',
                        num_rows=7,
                        alternating_row_color= gc.WIDGET_TABLE_COLOR,
                        key='-TABLE-',
                        selected_row_colors=gc.SELECT_COLOR,
                        enable_events=True,
                        expand_x=False,
                        expand_y=False,
                        vertical_scroll_only=False,
                        hide_vertical_scroll = False,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='Widget Table')]
    ]

    l_arrows = [[sg.Button('',image_data=up_image,key='-LAYOUT_UP-',pad = 0)],[sg.Button('',image_data=down_image,key='-LAYOUT_DOWN-',pad = 0)]]
    layout_table = [
        [sg.Column(l_arrows,pad=0),
        sg.Table(layoutvalues, headings=layout_heading, max_col_width=25,pad = 0,
                        auto_size_columns=False,
                        font=('Consolas', 12),
                        col_widths = 25, 
                        # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                        display_row_numbers=True,
                        justification='center',
                        num_rows=7,
                        alternating_row_color= gc.LAYOUT_TABLE_COLOR,
                        key='-LAYOUT_TABLE-',
                        selected_row_colors=gc.SELECT_COLOR,
                        enable_events=True,
                        expand_x=False,
                        expand_y=False,
                        vertical_scroll_only=False,
                        hide_vertical_scroll = False,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='Layout Table')]
    ]

    c_arrows = [[sg.Button('',image_data=up_image,key='-CONTAINER_UP-',pad = 0)],[sg.Button('',image_data=down_image,key='-CONTAINER_DOWN-',pad = 0)]]
    container_table = [
        [sg.Column(c_arrows,pad=0),
        sg.Table(containervalues, headings=container_heading, max_col_width=25,pad = 0,
                        auto_size_columns=False,
                        font=('Consolas', 12),
                        col_widths = 25, 
                        # cols_justification=('left','center','right','c', 'l', 'bad'),       # Added on GitHub only as of June 2022
                        display_row_numbers=True,
                        justification='center',
                        num_rows=7,
                        alternating_row_color= gc.CONTAINER_TABLE_COLOR,
                        key='-CONTAINER_TABLE-',
                        selected_row_colors=gc.SELECT_COLOR,
                        enable_events=True,
                        expand_x=False,
                        expand_y=False,
                        vertical_scroll_only=False,
                        hide_vertical_scroll = False,
                        enable_click_events=True,           # Comment out to not enable header and other clicks
                        tooltip='Container Table')]
    ]

    #
    editor_file_menu = ['Unused',['New', 'Open', 'Save', 'Save As', '---', 'Exit']]
    editor_tools_menu =['Unused', ['Version','Insert']]

    editor_layout = [
    [
    sg.ButtonMenu('File',editor_file_menu,size=(10,1),key="-EFILE-"),
    sg.Button('Cut',size=(10,1)),sg.Button('Copy',size=(10,1)),
    sg.Button('Paste',size=(10,1)),
    sg.ButtonMenu('Tools',editor_tools_menu,size=(10,1),key="-ETOOLS-"),
    #sg.Button('View Layout',size=(12,1),tooltip='Execute this layout in a new process'),
    sg.Button('View Layout',size=(12,1),tooltip=None),
    ],
    [sg.Text('> New file <', font=('Consolas', 10), size=(gc.WIN_W, 1), key='_INFO_')],

    [sg.Multiline(font=('Consolas', 12), size=(132, gc.WIN_H),horizontal_scroll = True, key='_BODY_')]  
    ] 

    ## not sure which layout is preferable
    # tables and editor in panes (allows for edit window to be dragged larger)
    # col1 =   sg.Column([[sg.Frame('Widgets', widget_table)],[sg.Frame('Layouts', layout_table)]])
    # col2 =   sg.Column([[sg.Frame('Containers', container_table)]])
    # col3 =   sg.Column([[sg.Frame('Editor', editor_layout)]])

    # pane_list = [col1,col2,col3]

    # table_editor_layout = [
    # [sg.Pane(pane_list, background_color=None,size=(None,None), pad=None,orientation='vertical', show_handle=True, relief=sg.RELIEF_RAISED, handle_size=15, border_width=1, key=None, visible=True)],
    # ]

    ## or
    #tables in one pane  edit window fixed
    col1 =   sg.Column([[sg.Frame('Widgets', widget_table,pad=0)]])
    col2 =   sg.Column([[sg.Frame('Layouts', layout_table,pad=0)],[sg.Frame('Containers', container_table,pad=0)]])

    pane_list = [col1,col2]

    table_editor_layout = [
    [sg.Pane(pane_list, background_color=None,size=(None,400), pad=None,orientation='vertical', show_handle=True, relief=sg.RELIEF_RAISED, handle_size=15, border_width=0, key=None, visible=True)],
    [sg.Frame('Editor', editor_layout,pad=0)]
    ]

    # main menu 
    menu_layout = [['File', ['Load', 'Save', '---', 'Exit']],
                ['Help', ['Ctrl Code','About']]]

    # guibuilder main form layout
    layout = [
    [sg.Menu(menu_layout)],
    # [sg.Column(entry_layout,vertical_alignment='top',scrollable = True,vertical_scroll_only = True,expand_y=True), sg.Column(table_editor_layout,size=(600,300),vertical_alignment='top',scrollable = True)]
    [sg.Column(entry_layout,vertical_alignment='top',scrollable = True,vertical_scroll_only = True,expand_y=True), sg.Column(table_editor_layout,vertical_alignment='top')]
    ]
    return layout