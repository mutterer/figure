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
Request Image from R using RScript
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

class RScriptPanel(ImageJPanel):
    """RScript Panel"""
    select_all = (Image, Rectangle)

    def add_arguments(self, pars):
        pars.add_argument("--tab", help="The selected UI-tab when OK was pressed")
        pars.add_argument("--rcmd", help="RScript program", default="RScript")
        pars.add_argument("--cmdopt", help="RScript options", default="--vanilla $MACRO")
        pars.add_argument("--embed", help="Embed instead of linking", type=inkex.Boolean, default=True)
        pars.add_argument("--quality", type=float, default=2, help="+/-")
        self.arg_path(pars, "--images_path", "./images/", "Path to Images")
        self.arg_path(pars, "--rscripts_path", "./rscripts/", "Path to Macros")

    def _process_image(self, ops, elem):
        images_file = os.path.join(ops.images_path, elem.eid + '.png').replace('\\', '/')
        macros_file = os.path.join(ops.rscripts_path, elem.eid + '.R').replace('\\', '/')
        
        code = self._get_code_from_lineage(elem)
        # if no desc available, add example code
        for child in elem.descendants():
            if isinstance(child, inkex.Desc):
                panelcode = child.text 
        if (code==""):
            code = """
x<-rnorm(1000)
hist(x)
"""
            panelcode = code
        qual_factor = ops.quality
        script = f"""
# R script
ISW={elem.width}*{qual_factor};
ISH={elem.height}*{qual_factor};
ISN='{elem.eid}';
ISPATH='{images_file}';
png(paste(ISPATH), units="px", width=ISW, height=ISH);

{code}

dev.off();
"""

        # Save the script to the rscript path
        with open(macros_file, 'w') as fhl:
            fhl.write(script)

        # Inject the script file path into the RScript command
        cmdopt = ops.cmdopt.replace("$MACRO", macros_file)

        # We build the command from the program name plus arguments
        # The arguments are built as a list to maintain security

        done = call(ops.rcmd, *(shlex.split(cmdopt)))
        
        if not os.path.isfile(images_file):
            raise inkex.AbortExtension(f"Failed to save image file '{images_file}'")

        elem = self._elem_is_image(elem,"rpanel")
        elem.desc = panelcode

        self._embed_or_link_image(elem,images_file,ops.embed)


if __name__ == '__main__':
    RScriptPanel().run()
