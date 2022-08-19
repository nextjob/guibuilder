# guibuilder
 Minimalist menu based gui builder for pysimplegui (https://www.pysimplegui.org).
 (If you are looking for a drag and drop or polished software to use as your 
	pysimplegui gui builder, this isn't it)
 
 Why? 
	To learn what is possible with pysimplegui.
	To Create an open source GUI presentation subsystem for Nextjob-Jobshop
		https://github.com/nextjob/Nextjob-JobShop
 

 Simple user guide:

 How this works (or should work)

  1) With the Widget Tab / Widget Table, user defines widgets, positioned on widget table via row / column vars.

  2) With the Layouts Tab / Layout Table, user creates layouts.
   Auto Create button automatically creates layouts for each "row" of widgets.
   Generate Layout creates layout code and places in editor window.
  
  3) With the Container Tab / Container Table, user creates Containers (must drag up pane for Container Table to be visible) 
       Code to be added
  
  4) User clicks View Layout to run sample window showing layout.

  5) Click File -> Save to save work (Form Name must not be blank)
  
  6) Click File -> Load to reload work.
     Note testform.json provided as sample, Once loaded, click Generate Code, then  View Layout to display

 This is a work in progress, somewhat working, more to come.
 
![screen1](https://user-images.githubusercontent.com/49209806/185527042-8261d501-4b3a-45da-9c01-87a940af83fc.JPG)
![screen2](https://user-images.githubusercontent.com/49209806/185527170-82610728-65fb-4283-8e07-ac1f7f6c1eb8.JPG)
