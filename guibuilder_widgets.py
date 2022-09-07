'''
  guiBuilder_widgets part of guiBuilder
  A minimalist pysimplegui builder
'''
import PySimpleGUI as sg
import inspect
# set of pysimplegui widgets for drop down widget creation
widget_list = ('Button','ButtonMenu','Canvas','Checkbox','Combo','Graph','HSep','Image','Input','Listbox','Multiline','OptionMenu','Output','Push','Radio','Sizegrip','Sizer','Slider','Spin','StatusBar','Table','Text','Tree','VPush','VSep')
# set of wdiget properties that require quotes
quoted_properties =('button_text','default_text','default_values','element_justification','key','k','text','title','tooltip')
# set of pysimplegui widgets for containing other widgets
container_list = ('None','Column','Frame','Tab','TabGroup')
#
def get_props(widget):
  ''' get the widget's inspect.signature object 
      and convert into string
      parse string and split into a list
      return the list of parameters and default values (if any) '''
  # example returned value for widget Image:
  # ['source=None', 'filename=None', 'data=None', 'background_color=None', 'size=(None, None)', 's=(None, None)',
  #  'pad=None', 'p=None', 'key=None', 'k=None', 'tooltip=None', 'subsample=None', 'right_click_menu=None', 
  # 'expand_x=False', 'expand_y=False', 'visible=True', 'enable_events=False']    
  #
  if widget == 'None':   # special container widget of no container
    element_list = []
    element_list.append('layout')
  else:   
    prop_list = str(inspect.signature(widget)).strip()
  # remove the first and last ( )
    prop_list = prop_list[1: : ]
    prop_list = prop_list[ :-1 : ]
    element_list = []
    element = ''
    inParen = False
    Paren_cnt = 0
    # loop thru char string
  
    for c in prop_list:
      # are we inside of ( )?
      if c == '(':
        inParen = True
        Paren_cnt += 1
      if c == ')':
        if Paren_cnt > 1:
          Paren_cnt -= 1
        else:
          inParen = False
      if c == ',' and not inParen:
        # create element from string
        element_list.append(element.strip())
        element = ''
        Paren_cnt = 0
      else:
        element += c

 # print (element_list)
  return element_list