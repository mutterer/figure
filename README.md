# Inkscape Figure Extensions
This repository hosts documentation about inkscape extensions that can help with easy and reproducible figures

## ImageJ Macro Panel
Base Inkscape extension which embeds images generated by ImageJ macros into current selected rectangle, and adds some helper functions.

## Related Extensions modelled after ImageJ Macro Panel
* **RScript Panel**: embeds image results from R scripts into current document.
* **PyMOL Panel**: renders the .rml script associated with current element using PyMOL molecular viewer and embeds it into current document.
* **Processing Panel**:embeds the svg result of a Processing sketch into current document.

## Extensions to assist Figure labelling 
* **Panel Labels**: adds a text label to all selected rectangles or images.
* **Lane Labels**: adds customizable lane labels to the selected rectangle or image.

## Installation
* Install Inkscape version > 1.1 from https://inkscape.org
![image](https://user-images.githubusercontent.com/711344/119502597-61355400-bd6a-11eb-8096-9f24382f6960.png)
* Choose your platform:
![image](https://user-images.githubusercontent.com/711344/119502724-8629c700-bd6a-11eb-8439-6ac7c1d5e20a.png)

![image](https://user-images.githubusercontent.com/711344/119502880-b1141b00-bd6a-11eb-899c-a7e4d03a884d.png)

* Launch Inkscape, open Inkscape Preferences.
* Open user extensions directory:
![image](https://user-images.githubusercontent.com/711344/119503217-02bca580-bd6b-11eb-9e3a-4a81926726f0.png)

* Go to Inkscape > Download > Extensions page and search for ImageJ Panel or Figure
![image](https://user-images.githubusercontent.com/711344/119503706-8b3b4600-bd6b-11eb-84ab-ec061c8d466d.png)
* Open the extension page and download it
![image](https://user-images.githubusercontent.com/711344/119503897-bb82e480-bd6b-11eb-9db2-b58411214c7e.png)

* extract the file zip and copy files into "user extensions folder" (see above).
* Restart Inkscape.

## Getting Started:
 - In your empty document, create a Rectangle.
 - Save your document (this is needed so that Inkscape know a path to your document)
 - Open the Object Properties inspector window using Inkscape > Object > Object Properties
 - Enter some IJMacro commands in the Description. e.g.
```
run("Fluorescent Cells");
Stack.setActiveChannels("110");
```
 - Click "Set" to save the Description
 ![image](https://user-images.githubusercontent.com/711344/119654487-ccddf680-be28-11eb-90b9-ea2cc52cf700.png)

 - Open Inkscape > Extensions > Figure > ImageJ Macro Panel...
 - For the first time only, you will need to follow the Configuration steps described below
 - Click Apply to run the ImageJ commands and update the panel
 - Each time you edit the Description, you will need to click "Set" and then click "Apply" in the Image J Macro Panel
 - TIP: You can configure a keyboard shortcut to trigger the extension in Inkscape > Preferences > Interface > Keyboard.

## Configuration
* You need to point Inkscape to your ImageJ installation.
* Open Inkscape > Extensions > Figure > ImageJ Macro Pannel...
* First tab shows options. You do not need to change anything at this point.
![image](https://user-images.githubusercontent.com/711344/119504674-7f03b880-bd6c-11eb-9530-f777637728fb.png)
* Second tab has fields you need to make match to your system. Here are values for my system:
![image](https://user-images.githubusercontent.com/711344/119504810-a064a480-bd6c-11eb-83c9-578979303441.png)
* Java Program: how to launch java on you system
* Java Otptions: refer to https://imagej.nih.gov/ij/docs/install/osx.html#cli for more info
* ImageJ Program: full path to your ij.jar file
* ImageJ command: mandatory options: 
 - -batch : leave "$MACRO" 
 - -ijpath : full path to your plugins folder (if you plan to use plugins) 
![image](https://user-images.githubusercontent.com/711344/119512779-ed984480-bd73-11eb-9300-e234e2d29dbe.png)

## Tips and tricks
 - If you add no code to your Rectangle, some demo code is added
 - The following variables are available for your panel macros:
   - ```panelWidth```, ```panelHeight``` : dimensions of the panel in the document space.
   - ```panelID``` : the object's ID.
   - ```panelIndex``` : the object index if you run the extension with multiple objects selected.
 - Your panel macro knows the document default directory, so you can place your source data relative to that.
 - ImageJ will return the panel image calibration that will be used if 'scale bar' option in enabled.
 - Copying and pasting and objects keeps its description macro.
 - Several helper functions are added to each panel macro automatically for you to use:
   - ```openBF(path, series)``` for opening files with BioFormats (must be installed in your ImageJ)
   - ```channels(string)```for setting channel visibility and standard LUT using a 1-char code. Example: channels("MG0"); uses Magenta for ch1, Green for ch2 and turns off ch3. Available chars: 0,1,R,G,B,C,M,Y,K,V,S 
   - ```mark(color,width);``` used with an active ROI, adds it to an overlay.
   - ```whitebg();``` replaces black background with white for printing
 - You can link panels using Inkscape's builtin connector tool. The complete panel code will be assembled by linking back connected panels code. This can be used to create workflows, and show intermediate states in a macro. To connect two panels, choose the connector tool, click in the center of the first (upstream) object, drag and release the mouse at the center of the second (downstream) object. In each panel, add only the code relevant to it's own display.

## Requirements                                                                                               
* this is an experimental work in progress, it works on my MacOs 10.11.6 and 10.15.7. It was not tested on Windows at all.
* currently needs Inkscape version 1.1 
* For ImageJ Macro Panel extension you will need a pre-installed version of ImageJ, or at least a copy of ij.jar (https://imagej.nih.gov/ij/). Works with ImageJ 1.53i.
* For RScript Panel extension you will need a instance of R (https://cran.r-project.org/). Works with R version 3.3.2.
* For Processing Panel extension you will need to first install Processing (https://processing.org/download/) and then follow the instructions for installation of processing-java command line tool (https://github.com/processing/processing/wiki/Command-Line)
* For PyMOL Panel extension you will need to first install PyMOL (I followed instructions for Macport at https://pymolwiki.org/index.php/MAC_Install#Open-Source_PyMOL)
* Configure paths and options needed to launch external programs as needed on your system.

## Code 
The code for the Inkscape Figure Extensions is at https://gitlab.com/doctormo/inkscape-imagej-panel,

