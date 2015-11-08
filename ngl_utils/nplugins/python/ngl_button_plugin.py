#!/usr/bin/env python

from ngl_utils.nplugins.python.ngl_base_qplugin import NGL_BasePlugin
from ngl_button import NGL_Button
import pkg_resources


class NGL_ButtonPlugin(NGL_BasePlugin):
    """NGL_ButtonPlugin(NGL_BasePlugin)"""

    # This factory method creates new instances of custom widget with the
    # appropriate parent.
    def createWidget(self, parent):
        widget = NGL_Button(parent)
        return widget

    # This method returns the name of the custom widget class that is provided
    # by this plugin.
    def name(self):
        return "NGL_Button"

    def icon(self):
        res_path = pkg_resources.resource_filename(
            'ngl_utils.nplugins.python', 'ico/button.ico')
        self.__ico = QIcon(res_path)
        return self.__ico

    # Returns an XML description of a custom widget instance that describes
    def domXml(self):
        return '<widget class="NGL_Button" name="nglButton" />\n'

    # Returns the module containing the custom widget class. It may include
    # a module path.
    def includeFile(self):
        return ".ngl_button"
