#!/usr/bin/env python

from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin


class NGL_BasePlugin(QPyDesignerCustomWidgetPlugin):
    """NGL_BasePlugin(QPyDesignerCustomWidgetPlugin)

    Provides a Python custom plugin for Qt Designer by implementing the
    QDesignerCustomWidgetPlugin via a PyQt-specific custom plugin class.
    """

    # The __init__() method is only used to set up the plugin and define its
    # initialized variable.
    def __init__(self, parent=None):
        super(NGL_BasePlugin, self).__init__(parent)
        self.initialized = False

    def initialize(self, formEditor):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    # Returns the name of the group in Qt Designer's widget box that this
    # widget belongs to.
    def group(self):
        return "NGL Widgets"

    # Returns the icon used to represent the custom widget in Qt Designer's
    # widget box.
    def icon(self):
        return QIcon()

    # Returns a short description of the custom widget for use in a tool tip.
    def toolTip(self):
        return ""

    # Returns a short description of the custom widget for use in a "What's
    # This?" help message for the widget.
    def whatsThis(self):
        return ""

    # Returns True if the custom widget acts as a container for other widgets;
    # otherwise returns False. Note that plugins for custom containers also
    # need to provide an implementation of the QDesignerContainerExtension
    # interface if they need to add custom editing support to Qt Designer.
    def isContainer(self):
        return False
