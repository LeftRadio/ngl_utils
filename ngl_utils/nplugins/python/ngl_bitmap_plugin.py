#!/usr/bin/env python

from ngl_base_plugin import NGL_BasePlugin
from ngl_bitmap import NGL_Bitmap


class NGL_BitmapPlugin(NGL_BasePlugin):
    """NGL_BitmapPlugin(NGL_BasePlugin)"""

    # This factory method creates new instances of custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        widget = NGL_Bitmap(parent)
        return widget

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "NGL_Bitmap"

    # Returns an XML description of a custom widget instance that describes
    def domXml(self):
        return '<widget class="NGL_Bitmap" name="nglBitmap" />\n'

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return "ngl_bitmap"
