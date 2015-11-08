
from setuptools import setup
from setuptools import find_packages

print(find_packages())

setup(
    name                    = 'ngl_utils',
    version                 = '1.4.9',
    author                  = 'Vladislav Kamenev',
    author_email            = 'wladkam@mail.com',
    url                     = 'https://github.com/LeftRadio/ngl_utils',
    description             = 'ngl_utils converting/generate code utilities for embedded NGL library',
    long_description        = (
"""ngl_utils included:
ngluic - console converter QtDesigner *.ui files
example: $ ngluic -u untitled.ui -d ./OutCodeDir --bitmap-compress JPG --verbose

nglfcn - ui fonts convertor/generator util
nglfed - ui ngl font editor util

""" ),
    download_url            = 'https://github.com/LeftRadio/ngl_utils',
    package_data            = { 'ngl_utils': ['templates/*.ntp'],
                                'ngl_utils.nfont': ['qtres/*.ui'],
                                'ngl_utils.nplugins.python': ['ico/*.ico'] },
    packages                = find_packages(),

    entry_points  = { 'console_scripts':
         [ 'ngluic = ngl_utils.ngluic : main',
           'nglfcn = ngl_utils.nfont.converterwidget : nfontConverterGUIStart',
           'nglfed = ngl_utils.nfont.editwidget : nfontEditGUIStart',
           'ngldes = ngl_utils.nplugins.nplugins : qtDesignerStart' ] },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3'
        ],
    license = 'MIT'
)
