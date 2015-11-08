# What is ngl-utils?
ngl-utils is convert/generate code utilities for embedded NGL library from QtDesigner ui files,
creating for simply and fast build small memory footprints graphics interfaces for embedded systems.

## contents
ngluic - console converter QtDesigner *.ui files

example: > $ ngluic -u untitled.ui -d ./OutCodeDir --bitmap-compress JPG --verbose

nglfcn - fonts convertor/generator util with ui

nglfed - ngl font editor util with ui


If you need more information, please follow home page link:
* [Home page](hobby-research.at.ua).

## Install
Download this repository and type in console:

>> python setup.py install

Or simple use pip in console:

>> pip install ngl-utils

# Use with Qtdesigner
Before use utils with QtDesigner you must compile Qt5 and PyQt5,
I recommend install Qt5.4.1 and compile only PyQt5.4.1,
upper version requires compile both Qt and PyQt

For build PyQt5

## Download and install Qt5.4.1 binary package

Add to envirovment varibles:

+ C:\Qt\Qt5.4.1\5.4\mingw491_32\bin\;

+ C:\Qt\Qt5.4.1\Tools\mingw491_32\bin\;

## Download and unzip SIP package:

* [SIP](https://www.riverbankcomputing.com/software/sip/download).

Type in console from unzipped SIP folder:

>> python configure.py --platform win32-g++

and after complite:

>> mingw32-make install

## Download and unzip PyQt5.4.1 sourses

* [PyQt5.4.1](http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4.1/PyQt-gpl-5.4.1.zip/download).

Type in console from unzipped PyQt folder:

>> python configure.py --spec win32-g++

type 'yes' to lecince promt, and after complite:

>> mingw32-make install

This all, now may start QtDesigner with custom widgets.

For verify try start QtDesigner with ngl plugins, in console:

>> ngldes

+ Inform: env add "PYQTDESIGNERPATH" plugins path -
+ C:\python35\lib\site-packages\ngl_utils-1.4.9-py3.5.egg\ngl_utils\nplugins\python

+ Inform: env add "PYTHONPATH" widgets path -
+ C:\python35\lib\site-packages\ngl_utils-1.4.9-py3.5.egg\ngl_utils\nplugins\widgets

+ Inform: designer bin - C:\Qt\Qt5.4.1\5.4\mingw491_32\bin/designer

+ Inform: start QtDesigner...


# Links
* [ngl github](https://github.com/LeftRadio/ngl).
