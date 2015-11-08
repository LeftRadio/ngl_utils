#!/usr/bin/env python

from ngl_utils.nplugins.python.ngl_base_qplugin import NGL_BasePlugin
from ngl_line import NGL_Line


class NGL_LinePlugin(NGL_BasePlugin):
    """NGL_LinePlugin(NGL_BasePlugin)

    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    # This factory method creates new instances of custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        widget = NGL_Line(parent)
        return widget

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "NGL_Line"

    # Returns the name of the group in Qt Designer's widget box that this
    # widget belongs to.
    def group(self):
        return "NGL Widgets"

    # Returns an XML description of a custom widget instance that describes
    def domXml(self):
        return '<widget class="NGL_Line" name="nglLine" />\n'

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return ".ngl_line"
