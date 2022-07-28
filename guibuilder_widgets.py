'''
  guiBuilder_widgets part of guiBuilder
  A minimalist pysimplegui builder
'''
import PySimpleGUI as sg
import inspect
# set of pysimplegui widgets for drop down
widget_list = ('Button','ButtonMenu','Canvas','Checkbox','Column','Combo','Frame','Graph','HSep','Image','Input','Listbox','Multiline','OptionMenu','Output','Pane','Push','Radio','Sizegrip','Sizer','Slider','Spin','StatusBar','TabGroup','Table','Text','Tree','VPush','VSep')
# set of wdiget properties that require quotes
quoted_properties =('button_text','default_text','element_justification','key','k','text','title','tooltip')
def get_props(widget):
 # get the widget's inspect.signature object 
 # and convert into string
 # span string and split into a list
 # return the list
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

  return element_list