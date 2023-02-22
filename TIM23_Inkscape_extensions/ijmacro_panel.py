#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2021 Jerome Mutterer and Martin Owens
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Request Image from ImageJ
"""

import os
import sys
import shlex

from base64 import encodebytes

import inkex
from inkex.elements import Image, Rectangle, load_svg, SvgDocumentElement, StyleElement, Defs, NamedView, Metadata

from inkex import PathElement, bezier

from inkex.command import call
from collections import defaultdict


from base64 import decodebytes

inkex.NSS[u"panel"] = u"https://gitlab.com/doctormo/inkscape-imagej-panel"
# TODO panel is not used, default name used instead???


class ImageJPanel(inkex.EffectExtension):
    """ImageJ Panel"""
    select_all = (Image, Rectangle)

    def arg_resource(self, pars, name, default, help=None):
        """Return a resource, which is located by default next to the extension files"""
        def _arg(value):
            def _lazy():
                if os.path.isabs(value):
                    return value
                return self.get_resource(value)
            return _lazy
        pars.add_argument(name, default=_arg(default), type=_arg, help=help)

    def arg_path(self, pars, name, default, help=None):
        """Return the directory for a given argument value and create it"""
        def _arg(value):
            path = value
            try:
                if not os.path.isabs(value) and 'DOCUMENT_PATH' in os.environ:
                    path = self.absolute_href(value, default=None)
                if os.path.isabs(path):
                    if not os.path.isdir(path):
                        os.makedirs(path)
                return path
            except Exception as e:
                pass
            # raise inkex.AbortExtension("You can't use relative paths with this version of Inkscape.")
        pars.add_argument(name, default=_arg(default), type=_arg, help=help)

    def add_arguments(self, pars):
        pars.add_argument("--tab", help="The selected UI-tab when OK was pressed")
        pars.add_argument("--java", help="Java Program", default="java")
        pars.add_argument("--jcmd", help="Java Options", default="-Xmx4096m")
        pars.add_argument("--icmd", help="ImageJ Command", default="-batch $MACRO '$OBJID,$WIDTH,$HEIGHT'")
        pars.add_argument("--embed", help="Embed instead of linking", type=inkex.Boolean, default=True)
        pars.add_argument("--scalebar", help="Add scale bar", type=inkex.Boolean, default=True)
        self.arg_resource(pars, "--imagej", "./ImageJ/ij.jar", "Path to ImageJ")
        self.arg_path(pars, "--images_path", "./images/", "Path to Images")
        self.arg_path(pars, "--macros_path", "./scripts/", "Path to Macros")
        self.arg_path(pars, "--data_path", "./data/", "Path to Source Data")

    def effect(self):
        version = self.svg.get("inkscape:version", _(""))
        if (version==""):
            self.msg("Error!\n\nYour document must be saved first.\nSave it and try again.")
            return
        self.index=0
        for shape in self.svg.selection:
        	  
            # address PathElement case here
            if not isinstance(shape, self.select_all):
            	  if isinstance(shape, PathElement):
            	  	  self.msg(str(shape.bounding_box().left))
            	  	  self.msg(str(shape.bounding_box().top))
            	  	  self.msg(str(shape.bounding_box().width))
            	  	  self.msg(str(shape.bounding_box().height))
            	  	  self.msg(f"Unknown object type: {shape.TAG}")
            	  	  #self._process_image(self.options, shape)

                # pass
                # self.msg(f"Unknown object type: {shape.TAG}")
            else:
                self._process_image(self.options, shape)
                self.index = self.index +1

    def _elem_is_image(self, elem, ptype):
        if isinstance(elem, (Rectangle)):
            if ("1.2" in self.svg.get("inkscape:version", _(""))):
              elem = elem.replace_with(Image(
                      x=str((elem.to_dimensionless(elem.left))),
                      y=str((elem.to_dimensionless(elem.top))),
                      width=str((elem.to_dimensionless(elem.width))),
                      height=str((elem.to_dimensionless(elem.height))),
                      transform=str(elem.transform),
              ))
            else:
            	# this is for 1.1.x versions.
              elem = elem.replace_with(Image(
                      x=str(elem.unittouu(elem.left)),
                      y=str(elem.unittouu(elem.top)),
                      width=str(elem.unittouu(elem.width)),
                      height=str(elem.unittouu(elem.height)),
                      transform=str(elem.transform),
              ))

            elem.set("panel:type", ptype)
        return elem

    def _embed_or_link_image(self, elem, imagefile, embed):
        if embed:
            # Embed image into the document.
            with open(imagefile, 'rb') as fhl:
                elem.set('xlink:href',
                    'data:image/tiff;base64,' + encodebytes(fhl.read()).decode('ascii'))
        else:
            # Link tiff into document
            elem.set('xlink:href', os.path.relpath(imagefile, self.svg_path(None)))

		#### code by doctormo? maybe useful later to import svg instead of image ####
    def merge_defs(self, defs):
        """Add all the items in defs to the self.svg.defs"""
        target = self.svg.defs
        for child in defs:
            if isinstance(child, StyleElement):
                continue # Already appled in merge_stylesheets()
            target.append(child)

    def merge_stylesheets(self, svg):
        """Because we don't want conflicting style-sheets (classes, ids, etc) we scrub them"""
        elems = defaultdict(list)
        # 1. Find all styles, and all elements that apply to them
        for sheet in svg.getroot().stylesheets:
            for style in sheet:
                xpath = style.to_xpath()
                for elem in svg.xpath(xpath):
                    elems[elem].append(style)
                    # 1b. Clear possibly conflicting attributes
                    if '@id' in xpath:
                        elem.set_random_id()
                    if '@class' in xpath:
                        elem.set('class', None)
        # 2. Apply each style cascade sequentially
        for elem, styles in elems.items():
            output = Style()
            for style in styles:
                output += style
            elem.style = output + elem.style

    def import_svg(self, new_svg):
        """Import an svg file into the current document"""
        self.merge_stylesheets(new_svg)
        for child in new_svg.getroot():
            if isinstance(child, SvgDocumentElement):
                yield from self.import_svg(child)
            elif isinstance(child, StyleElement):
                continue # Already applied in merge_stylesheets()
            elif isinstance(child, Defs):
                self.merge_defs(child)
            elif isinstance(child, (NamedView, Metadata)):
                pass
            else:
                yield child

    def import_from_file(self, filename,elem):
        with open(filename, 'rb') as fhl:
            head = fhl.read(100)
            container = inkex.Layer.new(os.path.basename(filename))
            if b'<?xml' in head or b'<svg' in head:
                objs = self.import_svg(load_svg(head + fhl.read()))
            else:
                objs = self.import_raster(filename, fhl)
            for child in objs:
                container.append(child)
                
            scale = self.svg.unittouu(1.0) / child.unittouu(1.0)
            container.transform.add_scale(scale)
            container.transform.add_translate(float(elem.get("x"))/scale,float(elem.get("y"))/scale)
            self.svg.get_current_layer().append(container)
		#### end of maybe useful later to import svg instead of image ####


    def _adjust_element_to_image(self, elem, width, height):
        if (float(width)/float(height)<float(elem.get('width'))/float(elem.get('height'))):
            # elem is wider, adjust elem width
            elem.set('width',float(width)*float(elem.get('height'))/float(height))
        elif (float(width)/float(height)>float(elem.get('width'))/float(elem.get('height'))):
            # elem is higher, adjust elem height
            elem.set('height',float(height)*float(elem.get('width'))/float(width))
        else :
            pass

    def _get_upstream_element(self, elem):
        value = False
        for elemid in self.svg.get_ids():
            el = self.svg.getElementById(elemid)
            if (str(el.get("inkscape:connection-end")).endswith("#"+elem.eid)):
                 value = (el.get("inkscape:connection-start")[1:])
        return value

# preliminary tests for version 1.2
# connectors are LPE : check if PathEffect
# properties changes to connection-start connection-end
# with inkscape prefix removed
# endpoints can be elements themselves, or Points childs of elements.
# if starts with #Point..., find out this point's parent...
# getConnectedObject(elem) : if elem is point find out parent.
#

    # def _get_upstream_element(self, elem):
        # value = False
        # for elemid in self.svg.get_ids():
            # el = self.svg.getElementById(elemid)
            # if isinstance(el, inkex.PathEffect):
                 # inkex.utils.debug(str(el))
            # if (str(el.get("connection-end")).endswith("#"+elem.eid)):
                 # value = (el.get("connection-start")[1:])
        # return value
# 
    def _get_element_lineage(self, elem):
        uplist = [elem.eid]
        ue = self._get_upstream_element(elem)
        while (ue):
            uplist.append(ue)
            ue = self._get_upstream_element(self.svg.getElementById(ue))
        return uplist

    def _get_code_from_lineage(self, elem):
        code = ""
        lineage = self._get_element_lineage(elem)
        for elemid in lineage:
            for child in self.svg.getElementById(elemid).descendants():
                if isinstance(child, inkex.Desc):
                    code = child.text + "\n" + code    
        return code

    def _process_image(self, ops, elem):
        index = self.index
        images_file = os.path.join(ops.images_path, elem.eid + '.png').replace('\\', '/')
        macros_file = os.path.join(ops.macros_path, elem.eid + '.txt').replace('\\', '/')
        data_path = ops.data_path.replace('\\', '/')
        code = self._get_code_from_lineage(elem)
        # if no desc available, add example code
        for child in elem.descendants():
            if isinstance(child, inkex.Desc):
                panelcode = child.text 

        if (code==""):
            code = f"""
newImage("Untitled", "8-bit white", {int(elem.width)*4}, {int(elem.height)*4}, 1);
run("Macro...", "code=v=255-255*(random()<0.0003)");
run("Options...", "iterations=1 count=1 do=Nothing");
run("Voronoi");
run("Gaussian Blur...","sigma=1");
run("Fire");
getStatistics(area, mean, min, max, std, histogram);
setMinAndMax(0, max);
whitebg();
changeValues(0xffffff,0xffffff,0xdddddd);
"""
            panelcode = code

        script = f"""
// these variables can be used to create
// an image with expected properties
panelWidth={elem.width};
panelHeight={elem.height};
panelID='{elem.eid}';
panelIndex={index}
// set cwd so that loading images will work if figure folder is moved.
File.setDefaultDir('{data_path}');

{code}

// save result image at expected location
saveAs('PNG', '{images_file}');
// output useful image properties for later
Stack.getDimensions(w, h, c, s, f);
getVoxelSize(p, ph, pd, u);
List.clear();
List.set("width", w);
List.set("height", h);
List.set("pixelsize", p);
List.set("unit", u);
print("");
print(List.getList());

// helper functions

function openBF(filepath,series) {{
run('Bio-Formats Importer', 'open=['+filepath+'] autoscale color_mode=Composite rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT series_'+series);
}}

function channels(s) {{
// inspired by Kevin Terretaz 
oll="RGBCYMKVFS";
luts=newArray("Red","Green","Blue","Cyan","Yellow","Magenta","Grays","Viridis","Fire","Spectrum");
if (bitDepth() ==24) run("Make Composite");
Stack.getDimensions(width, height, chs, slices, frames);
for (i=1;i<=chs;i++) {{
if(is("composite")) Stack.setChannel(i);
c = s.substring(i-1,i);
l = oll.indexOf(toUpperCase(c));
if (l>-1) run(luts[l]);
}}
activechannels = replace(s,"[^0]",1);
if(is("composite")) {{
Stack.setDisplayMode("composite");
Stack.setActiveChannels(activechannels);
last = activechannels.lastIndexOf("1");
if (last>-1) Stack.setChannel(last+1);
}}
}}

function mark(color,width) {{
run("Properties... ", "  stroke="+color+" width="+width);
run("Add Selection...");
}}


function whitebg() {{
setSlice(1);
setMetadata("Label", "");
run("RGB Color");
run("Invert");
run("HSB Stack");
run("Macro...", "code=v=(v+128)%256 slice");
run("RGB Color");
}}

function makeLut(a,b) {{
  a = Color.toArray(a);
  b = Color.toArray(b);
  reds=newArray(256);
  greens=newArray(256);
  blues=newArray(256);
  for (i=0;i<reds.length;i++) {{
    reds[i] = a[0]+i*(b[0]-a[0])/256;
    greens[i] = a[1]+i*(b[1]-a[1])/256;
    blues[i] = a[2]+i*(b[2]-a[2])/256;
  }}
  setLut(reds,greens,blues);
}}

function persp() {{
	w=getWidth; h=getHeight;
	makeSelection("points", newArray(0,w,0,w), newArray(0,0,h,h));
	rename("psource");
  run("RGB Color");
  run("Add...", "value=1");
	run("Duplicate...", "title=ptarget");
	run("Select All");
	setBackgroundColor(0, 0, 0);
	run("Clear", "slice");
	w=getWidth; h=getHeight;
	makeSelection("points", newArray(0,w,0,w/2), newArray(0,0,h/2,h));
	run("Landmark Correspondences", "source_image=psource template_image=ptarget transformation_method=[Least Squares] alpha=1 mesh_resolution=32 transformation_class=Perspective interpolate");
	run("RGB Color");
	run("Copy");
	run("Make Composite");
	setSlice(3);
	run("Add Slice", "add=channel");
	setSlice(4);
	run("Set Label...", "label=alpha");
	run("Paste");
	changeValues(1,255,255);
}}

"""
        #self.msg(elem.width)
        #return


        # Save the script to the macros path
        with open(macros_file, 'w') as fhl:
            fhl.write(script)

        # Inject the macro file into the ImageJ command
        icmd = ops.icmd.replace("$MACRO", macros_file)
        
        # We build the command from the program name plus arguments
        # The arguments are built as a list to maintain security
        done = call(ops.java, *(
            shlex.split(ops.jcmd) + \
            [ '-jar', ops.imagej() ] + \
            shlex.split(icmd)))
        # in 1.1 call returns a string, in 1.2 it's a bytes object so:
        try:
            done=done.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            pass

        #  ImageJ reports some metadata to stdout
        #  looking like that; we parse it 
        #  height=254
        #  pixelsize=0.6
        #  unit=microns
        #  width=256
        ijdata = {}
        for line in str(done).split('\n'):
            if line[:5].lower() == 'width':
                ijdata['width']=line.split('=')[1]
            if line[:6].lower() == 'height':
                ijdata['height']=line.split('=')[1]
            if line[:4].lower() == 'unit':
                ijdata['unit']=line.split('=')[1]
            if line[:9].lower() == 'pixelsize':
                ijdata['pixelsize']=line.split('=')[1]

        if not os.path.isfile(images_file):
            raise inkex.AbortExtension(f"Failed to save image file '{images_file}'")
            
        # transfer infos reported by ImageJ to element
        elem = self._elem_is_image(elem,"imagejpanel")
        elem.desc = panelcode
        # restore the micron symbol that was given as '\xc2\xb5'
        ijdata['unit'] = ijdata['unit'].replace("\\xc2\\xb5","µ")
        elem.set('panel:pixelsize', ijdata['pixelsize'])
        elem.set('panel:unit', ijdata['unit'])
        elem.set('panel:width', ijdata['width'])
        elem.set('panel:height', ijdata['height'])
                
        self._embed_or_link_image(elem,images_file,ops.embed)
        self._adjust_element_to_image(elem, ijdata['width'], ijdata['height'])
                
        if ops.scalebar:
            # find a sensible default for scale bar size
            ms=[1,2,5]
            ps=range(-10,10)
            m=-1
            p=-1
            sbs=0
            while (sbs < (float(ijdata['width'])*float(ijdata['pixelsize']))/4):
              m=(m+1)%3
              if (m==0):
                p=p+1
              sbs = ms[m]*pow(10,ps[p])
            
            # add scale bar 
            # TODO : put inside a group with image
            # and create an separate extension for more flexible scale bar
            sbdw = sbs*float(elem.get('width'))/(float(ijdata['width'])*float(ijdata['pixelsize']))
            sb = Rectangle()
            sb.set("style","fill:#ffffff;stroke:#000000;stroke-width:0.2;stroke-miterlimit:4;stroke-dasharray:none")
            sb.set("x",str(float(elem.get('x'))+float(elem.get('width'))-sbdw-3));
            sb.set("y",str(float(elem.get('y'))+float(elem.get('height'))-4));
            sb.set("width",str(sbdw));
            sb.set("height","1");
            sb.set("inkscape:label",str(sbs)+" "+ijdata['unit']);
            parent = self.document.getroot()
            parent.add(sb)

if __name__ == '__main__':
    ImageJPanel().run()
