#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2021 Jerome Mutterer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Adds panel labels to all selected rects in a figure
"""

import inkex
from inkex import Layer, Rectangle, TextElement, Image

labels = 'abcdefghijklmnopqrstuvwxyz'

class FigureLabels(inkex.EffectExtension):
    """Adds panel labels to figure panels"""
    def add_arguments(self, pars):
        pars.add_argument("-s", "--fontsize", type=float, default=10, help="+/-")
        pars.add_argument("-x", "--xoffset", type=float, default=5, help="+/-")
        pars.add_argument("-y", "--yoffset", type=float, default=0, help="+/-")
        pars.add_argument("--tab", help="The selected UI-tab when OK was pressed")

    def effect(self):
        parent = self.document.getroot()
        elements = self.svg.selected.values()
        i = 0;
        for shape in elements:
            if isinstance(shape, (Rectangle,Image)):
                if (i==0):
                    layer_atts = {'id': 'panel_labels'}
                    self.my_layer = parent.add(inkex.Group(**layer_atts))
                x=str(shape.to_dimensionless(shape.left)+self.options.xoffset)
                y=str(shape.to_dimensionless(shape.top)+self.options.yoffset)
                te = TextElement()
                te.text = labels[i:i+1]
                te.style["font-size"] = str(self.options.fontsize)
                te.set('x' , x)
                te.set('y' , y)
                self.my_layer.add(te)
                i = i+1

if __name__ == '__main__':
    FigureLabels().run()
