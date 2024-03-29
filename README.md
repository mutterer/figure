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

## Requirements                                                                                               
* this is an experimental work in progress, it works on my MacOs 10.11.6 and 10.15.7. 
* currently needs Inkscape version 1.2 
* For ImageJ Macro Panel extension you will need a pre-installed version of ImageJ, or at least a copy of ij.jar (https://imagej.nih.gov/ij/). Works with ImageJ 1.53r.
* For RScript Panel extension you will need a instance of R (https://cran.r-project.org/). Works with R version 3.3.2.
* For Processing Panel extension you will need to first install Processing (https://processing.org/download/) and then follow the instructions for installation of processing-java command line tool (https://github.com/processing/processing/wiki/Command-Line)
* For PyMOL Panel extension you will need to first install PyMOL (I followed instructions for Macport at https://pymolwiki.org/index.php/MAC_Install#Open-Source_PyMOL)
* Configure paths and options needed to launch external programs as needed on your system.

## Code 
The latest code for the Inkscape Figure Extensions is at https://gitlab.com/doctormo/inkscape-imagej-panel,

