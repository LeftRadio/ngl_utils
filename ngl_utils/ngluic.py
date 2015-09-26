#!/usr/bin/env python3

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QImage

from ngl_utils.uiparser import UIParser
from ngl_utils.nfont.nfont import NGL_Font
from ngl_utils.nfont.converter import NFontConverter
from ngl_utils.nbitmap.converter import NBitmapsConverter
from ngl_utils.ncodegenerator import NCodeGen, NFontCodeGen, NBitmapCodeGen
from ngl_utils.messages import inform, error, newline

__version__ = "1.3.3"


class NUIC(object):
    """docstring for NUIC"""

    def __init__(self, qt_uifile):
        super(NUIC, self).__init__()
        self.parser = UIParser(qt_uifile)

    def pageCode(self, page, verbose):
        if verbose:
            inform('generate page code for [ %s ] ' % page['name'])
        return NCodeGen.generetePageCode(page)

    def buttonsCode(self, page, verbose):
        if verbose:
            inform('generate buttons code for page [ %s ]' % page['name'])

        return NCodeGen.generateButtonsHeader(page)

    def labelsCode(self, page, verbose):
        if verbose:
            inform('generate labels code for page [ %s ]' % page['name'])
        return NCodeGen.generateLabelsHeader(page)

    def convertFonts(self, fonts, verbose):
        """ converting all parset fonts to NGL_Font objects """
        return [self._convertFont(font, verbose) for font in fonts]

    def _convertFont(self, font, verbose):
        # charters set to converting
        char_range = range(ord(' '), ord('~'))
        chars_sets = ''.join([chr(x) for x in char_range])

        # converting to ngl_font
        if verbose:
            inform( 'converting font %s, %spt, bold %s' % (font.family(),
                                                           font.pointSize(),
                                                           font.bold()))
        name = NGL_Font.formatName(font.family(),
                                   font.pointSize(),
                                   font.bold())
        # convert and return
        return NFontConverter.convertQFont( chars_sets, name, font )

    def fontsHeaderCode(self, fonts, verbose):
        if verbose:
            inform( 'generate fonts header file...' )
        return NFontCodeGen.generateFontsHeader( fonts )

    def convertBitmaps(self, bitmaps, compress, verbose):
        """ converting all parset bitmaps to NGL_Bitmap objects """
        return [self._convertBitmap(bmp, compress, verbose) for bmp in bitmaps]

    def _convertBitmap(self, path, compress, verbose):
        if os.path.exists(path):

            image = QImage(path)
            name = os.path.basename(path).split('.')[0]

            ngl_bitmap = NBitmapsConverter.convertQImage(image,
                                                         name,
                                                         'format16',
                                                         compress)
            if verbose:
                inform(('converting bitmap {name}, size {width}x{height}, '
                        'compress {compress}, data len {size} bytes'
                        ).format(name = name,
                                 width = image.size().width(),
                                 height = image.size().height(),
                                 compress = ngl_bitmap.compressed,
                                 size = ngl_bitmap.data_len_in_bytes))
            return ngl_bitmap

        else:
            error(('File "{0}" not found! Expected path - "{1}" not exist'
                   ' :( :( :( ').format(bitmap['name'], bitmap['path']))

    def bitmapsHeaderCode(self, bitmaps, verbose ):
        if verbose:
            inform('generate bitmaps header file...')
        return NBitmapCodeGen.generateBitmapsHeader(bitmaps)

    def informUser(self, state, verbose):
        if state == 'parse_end':
            if verbose:
                inform('ui file version - %s' %  self.parser.uiVersion())
                inform('page - "%s"' % self.parser.parsedPage()['name'])

                objects_classes = self.parser.getParsedObjects()
                objects = []

                for class_key in objects_classes.keys():
                    # iterate objects in this objects class
                    for obj_key in objects_classes[class_key]:
                        objects.append(obj_key)

                inform( 'objects - %s' % ', '.join(objects) )

                bitmaps, fonts = self.parser.getParsedResourses()
                bitmaps_paths = [bmp for bmp in bitmaps]
                fonts_familys = [font for font in fonts]
                inform( 'bitmaps files - %s' % bitmaps_paths )
                inform( 'fonts - %s' % fonts_familys )

            inform( '--- Qt UI file parsed successful, start convert and generate code...' )

        elif state == 'convert_end':
            if verbose:
               pass
            inform('--- Converting and generate successful, create dirs...')

        elif state == 'create_dirs':
            if verbose:
                for _dir in self.dirs.keys():
                    path = os.path.abspath( self.dirs[ _dir ] )
                    inform( 'created [ %s ] dir - %s' % (_dir, path) )
            inform('--- Creating dirs done, save...')

        if verbose:
            newline()

    def createDirs(self, **kwargs):
        dirs = {}
        basepath = kwargs[ 'basepath' ]
        dirs['base'] = basepath
        dirs['page'] = os.path.join( basepath, 'pages\\' + kwargs[ 'pagename' ] )
        dirs['buttons'] = dirs['page']
        dirs['labels'] =  dirs['page']
        dirs['bitmaps'] = os.path.join( basepath, 'bitmaps\\' )
        dirs['fonts'] = os.path.join( basepath, 'fonts\\' )

        # create dirs
        for _dir in dirs.keys():
            os.makedirs( dirs[_dir], mode=0x777, exist_ok=True )

        self.dirs = dirs
        return self.dirs

    def save(self, **kwargs):
        # save page code
        self.saveCode(  dircode = 'page',
                        name = kwargs['pagename'] + '.c',
                        code = kwargs['pagecode'],
                        verbose = kwargs['verbose'] )

        # save common buttons header code
        self.saveCode(  dircode = 'buttons',
                        name = kwargs['pagename'] + '_buttons.h',
                        code = kwargs['buttonscode'],
                        verbose = kwargs['verbose'] )

        # save common labels header code
        self.saveCode(  dircode = 'labels',
                        name = kwargs['pagename'] + '_labels.h',
                        code = kwargs['labelscode'],
                        verbose = kwargs['verbose'] )

        # save all fonts codes
        self.saveResources( kwargs['fonts'], 'fonts', kwargs['verbose'] )

        # save common fonts header code
        self.saveCode(  dircode = 'fonts',
                        name = 'fonts.h',
                        code = kwargs['fontsheader'],
                        verbose = kwargs['verbose'] )

        # save all bitmaps header code
        self.saveResources( kwargs['bitmaps'], 'bitmaps', kwargs['verbose'] )

        # save common bitmaps header code
        self.saveCode(  dircode ='bitmaps',
                        name = 'bitmaps.h',
                        code = kwargs['bitmapsheader'],
                        verbose = kwargs['verbose'] )

    def saveCode(self, **kwargs):
        # page = self.parser.parsedPage()
        _dir = self.dirs[ kwargs['dircode'] ]
        _basename = ( kwargs['name'] ).lower()
        _code = kwargs['code']
        _file = os.path.abspath( os.path.join( _dir , _basename ) )

        self._write( _file, 'w', _code )
        if kwargs['verbose']:
            inform( 'saved [ %s ], path -- %s' % ( _basename, _file ) )

    def saveResources(self, objects, dir_name, verbose):
        for obj in objects:
            _file = os.path.abspath( os.path.join( self.dirs[dir_name], obj.name + '.c' ) )
            self._write( _file, 'w', obj.code )
            if verbose:
                inform( 'saved [ %s ], path -- %s' % (obj.name, _file) )

    def _write(self, sfile, mode, data):
        with open(sfile, mode) as f:
            f.write(data)

# ------------------------------------------------------------------------------
# create cmd line arguments parser
# ------------------------------------------------------------------------------
def createArgParser():
    _prog = "ngluic"
    desctext = 'Converting QtDesigner *.ui files utility for NGL library, "%s v%s"' % ( _prog, __version__ )
    epitext = 'Find more info visit http://hobby-research.at.ua ; https://github.com/LeftRadio/ngl_utils'

    parser = argparse.ArgumentParser( description = desctext,
                                      epilog = epitext,
                                      prog = _prog )

    parser.add_argument ( '-V', '--version', action='version', help = 'version',
                            version = __version__ )

    parser.add_argument ( '-u', '--uiqt', dest = 'qt_uifile', type = str,
                            default = '',
                            metavar = 'U',
                            help = 'input QtDesigner ui file' )

    parser.add_argument ( '-d', '--outdir', dest = 'ngl_out_dir', type = str,
                            default = './code',
                            metavar = 'D',
                            help = ( 'generated code out directory '
                                     '[default: \'%s\']' % '.\\Code' ) )

    parser.add_argument( '--bitmap-compress', dest = 'bitmap_compress', type = str,
                            default = 'None',
                            metavar = 'C',
                            help = ( 'compress for bitmaps, available options - '
                                     '{ None, RLE, JPG, Auto(min size) } [default: \'None\']' ) )

    parser.add_argument( '--bitmap-jpeg', dest = 'bitmap_jpeg_quality', type = int,
                            default = 100,
                            metavar = 'Q',
                            help = ( 'bitmaps JPG compression quality, available 0 - 100 '
                                     '[default: 100]' ) )

    parser.add_argument( '-v', '--verbose', action='store_true', default = False,
                            help = ( 'increase output verbosity '
                                     '[default: \'%s\']' % 'False' ) )

    return parser

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
def main():
    parser = createArgParser()
    args = parser.parse_args()

    # # if no args print help and exit
    # if not len(sys.argv[1:]):
    #     parser.print_help()
    #     error('No arguments found :( exit...')

    # if not os.path.exists( args.qt_uifile ):
    #     error( 'Qt ui file path not correct :( exit... ' )

    args.qt_uifile = 'untitled.ui'
    args.verbose = True

    app = QApplication(sys.argv)

    uifile = args.qt_uifile
    outdir = args.ngl_out_dir
    verbose = args.verbose
    bitmap_compress = ( args.bitmap_compress, args.bitmap_jpeg_quality )

    # create nuic object and parse Qt ui file
    nuic = NUIC( uifile )
    ppage = nuic.parser.parse()
    nuic.informUser( 'parse_end', verbose )

    # convert all fonts, generate common fonts header code
    ngl_fonts = nuic.convertFonts( ppage['fonts'], verbose )
    ngl_fonts_header = nuic.fontsHeaderCode( ngl_fonts, verbose )

    # convert all bitmaps, generate common bitmaps header code
    ngl_bitmaps = nuic.convertBitmaps( ppage['bitmaps'], bitmap_compress, verbose )
    ngl_bitmaps_header = nuic.bitmapsHeaderCode( ngl_bitmaps, verbose )

    # generate page and objects code
    pagecode = nuic.pageCode( ppage, verbose )
    buttonscode = nuic.buttonsCode( ppage, verbose )
    labelscode = nuic.labelsCode( ppage, verbose )

    # inform by end of conversion and generation code
    nuic.informUser( 'convert_end', verbose )

    # create dirs for save generated code
    code_dirs = nuic.createDirs( basepath=outdir, pagename=ppage['name'] )
    nuic.informUser('create_dirs', verbose)

    # save all code
    nuic.save(  pagename = ppage['name'],
                pagecode = pagecode,
                buttonscode = buttonscode,
                labelscode = labelscode,
                bitmaps = ngl_bitmaps,
                bitmapsheader = ngl_bitmaps_header,
                fonts = ngl_fonts,
                fontsheader = ngl_fonts_header,
                verbose = verbose )

    # final !
    app.exit()
    inform( '-*-*- All works finish! :) --- out code locate in %s' % os.path.abspath(code_dirs['base']) )

# ------------------------------------------------------------------------------
# program start here
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())

