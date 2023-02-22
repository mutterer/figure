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
Request Image from Matplotlib
"""

import os
import sys
import shlex

from base64 import encodebytes

import inkex
from inkex.elements import Image, Rectangle
from inkex.command import call

from base64 import decodebytes

from ijmacro_panel import ImageJPanel

class MPLPanel(ImageJPanel):
    """Matplotlib Panel"""
    select_all = (Image, Rectangle)

    def add_arguments(self, pars):
        pars.add_argument("--tab", help="The selected UI-tab when OK was pressed")
        pars.add_argument("--rcmd", help="Python program", default="/usr/bin/python")
        pars.add_argument("--cmdopt", help="Python options", default="$MACRO")
        pars.add_argument("--embed", help="Embed instead of linking", type=inkex.Boolean, default=True)
        pars.add_argument("--quality", type=float, default=2, help="+/-")
        self.arg_path(pars, "--images_path", "./images/", "Path to Images")
        self.arg_path(pars, "--scripts_path", "./scripts/", "Path to Macros")

    def _process_image(self, ops, elem):
        index = self.index
        images_file = os.path.join(ops.images_path, elem.eid + '.png').replace('\\', '/')
        macros_file = os.path.join(ops.scripts_path, elem.eid + '.py').replace('\\', '/')
        
        code = self._get_code_from_lineage(elem)
        # if no desc available, add example code
        for child in elem.descendants():
            if isinstance(child, inkex.Desc):
                panelcode = child.text 
        if (code==""):
            code = """
import matplotlib.pyplot as plt
plt.ylabel('some numbers')
plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
"""
            panelcode = code
        qual_factor = ops.quality
        width = int(float(elem.width)*float(qual_factor))
        height = int(float(elem.height)*float(qual_factor))
        script = f"""
# matplotlib script
import matplotlib.pyplot
panelIndex = {index}

{code}

inkscapefigure = matplotlib.pyplot.gcf()
inkscapefigure.set_size_inches({width}/100, {height}/100)
matplotlib.pyplot.savefig("{images_file}", dpi=100)

"""

        # Save the script to the rscript path
        with open(macros_file, 'w') as fhl:
            fhl.write(script)

        # Inject the script file path into the command
        cmdopt = ops.cmdopt.replace("$MACRO", macros_file)

        # We build the command from the program name plus arguments
        # The arguments are built as a list to maintain security

        done = call(ops.rcmd, *(shlex.split(cmdopt)))
       
        if not os.path.isfile(images_file):
            raise inkex.AbortExtension(f"Failed to save image file '{images_file}'")

        elem = self._elem_is_image(elem,"pymolpanel")
        elem.desc = panelcode

        self._embed_or_link_image(elem,images_file,ops.embed)


if __name__ == '__main__':
    MPLPanel().run()
