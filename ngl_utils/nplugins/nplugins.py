#!/usr/bin/env python

import sys
import os
from PyQt5.QtCore import QLibraryInfo, QProcess, QProcessEnvironment
from ngl_utils.messages import inform


def qtDesignerStart():
    """ Set widgets/plugins paths and start QtDesigner """

    # Get base path and QProcess system environment
    base = os.path.dirname(__file__)
    env = QProcessEnvironment.systemEnvironment()

    # Path for tell python where it can find the widgets directory
    pybase = os.path.join(base, 'python')
    # Path for tell QtDesigner where it can find the plugins directory
    wbase = os.path.join(base, 'widgets')

    # Insert paths to QProcess system environment
    env.insert('PYQTDESIGNERPATH', pybase)
    env.insert('PYTHONPATH', wbase)

    # inform user
    inform('env add "PYQTDESIGNERPATH" plugins path - ' + pybase)
    inform('env add "PYTHONPATH" widgets path - ' + wbase)

    # Create QProcess and set environment
    designer = QProcess()
    designer.setProcessEnvironment(env)

    # Get QtDesigner binaries path
    designer_bin = QLibraryInfo.location(QLibraryInfo.BinariesPath)

    # Platform specefic
    if sys.platform == 'darwin':
        designer_bin += '/Designer.app/Contents/MacOS/Designer'
    else:
        designer_bin += '/designer'

    # inform user
    inform('designer bin - ' + designer_bin)
    inform('start QtDesigner...')

    # Start QtDesigner
    designer.start(designer_bin)
    designer.waitForFinished(-1)
    sys.exit(designer.exitCode())


if __name__ == '__main__':
    qtDesignerStart()
