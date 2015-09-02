
from setuptools import setup
from setuptools import find_packages
from ngl_utils.ngluic import __version__

setup(
    name                    = 'ngl_utils',
    version                 = __version__,
    description             = ( 'ngl_utils the converting QtDesigner '
                                '*.ui files utilities for embedded NGL library' ),
    author                  = 'Vladislav Kamenev',
    author_email            = 'wladkam@mail.com',
    url                     = '',
    package_data            = { 'ngl_utils': ['templates/*.ntp'] },
    packages                = find_packages(),
    
    entry_points = {
        'console_scripts': ['ngluic = ngl_utils.ngluic:main'] },

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3'
        ],
)