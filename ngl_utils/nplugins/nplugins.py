#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2013 Riverbank Computing Limited.
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Riverbank Computing Limited nor the names of
##     its contributors may be used to endorse or promote products
##     derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
#############################################################################


import sys
import os
from PyQt5.QtCore import QLibraryInfo, QProcess, QProcessEnvironment
from ngl_utils.messages import inform


def qtDesignerStart():
    """ Tell Qt Designer where it can find the directory
        containing the plugins and Python where it can find the widgets.
    """
    base = os.path.dirname(__file__)
    env = QProcessEnvironment.systemEnvironment()
    env.insert('PYQTDESIGNERPATH', os.path.join(base, 'python'))
    env.insert('PYTHONPATH', os.path.join(base, 'widgets'))
    inform('env add "PYQTDESIGNERPATH" plugins path - ' + os.path.join(base, 'python'))
    inform('env add "PYTHONPATH" widgets path - ' + os.path.join(base, 'widgets'))

    # Start Designer.

    designer = QProcess()
    designer.setProcessEnvironment(env)

    designer_bin = QLibraryInfo.location(QLibraryInfo.BinariesPath)

    if sys.platform == 'darwin':
        designer_bin += '/Designer.app/Contents/MacOS/Designer'
    else:
        designer_bin += '/designer'

    inform('designer bin - ' + designer_bin)
    inform('start QtDesigner...')

    designer.start(designer_bin)
    designer.waitForFinished(-1)
    sys.exit(designer.exitCode())


if __name__ == '__main__':
    qtDesignerStart()
