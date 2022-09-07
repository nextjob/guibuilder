'''
  guiBuilder_constants.py part of guiBuilder
  A minimalist pysimplegui builder
'''
# starting window size
WINDOW_SIZE = (1080,720)

# name we use to create our test view for the layouts
GUIBUILDER_TEST_FILE =  'guibuilder_tester.py'               # script to display layout defined in 'guibuildertestlayoutfile.py'
GUIBUILDER_TEST_LAYOUT_FILE = 'guibuilder_test_layout_file.py' # file created by this guibuilder.py 
WIN_W = 90
WIN_H = 25
MAX_PROPERTIES = 60    # max number of properties we are setup to display
#

EMPTYCELL = '-       -'
CONTINUE_LAYOUT = '+++++++++'
# text for selected layout table cell text box
SELECT_CELL_TEXT = 'Selected Cell (r/c): '

#define some colors
WIDGET_TABLE_COLOR = 'light steel blue'
LAYOUT_TABLE_COLOR = 'light blue'
CONTAINER_TABLE_COLOR = 'PaleTurquoise4'
SELECT_COLOR = 'red on yellow'
#  SELECT_COLOR = 'yellow'