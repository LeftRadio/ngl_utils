import sys
import glob
import os
import argparse
from ngl_utils.uiparser import UIParser as UIP
from ngl_utils.nconverts import NFontConverter as NFC
from ngl_utils.nconverts import NBitmapsConverter as NBC
from ngl_utils.nconverts import NColor
from ngl_utils.ncodegenerator import NCodeGen, NFontCodeGen, NBitmapCodeGen
from ngl_utils.messages import inform, error, newline

__version__ = "1.2.4"

# ------------------------------------------------------------------------------
# NUIC
# ------------------------------------------------------------------------------
class NUIC(object):
    """docstring for NUIC"""
    def __init__(self, qt_uifile):
        super(NUIC, self).__init__()
        self.parser = UIP( qt_uifile )

    def pageCode(self, page, verbose):
        if verbose:
            inform('generate page code for [ %s ] ' % page['name'] )
        return NCodeGen.generetePageCode( page )

    def buttonsCode(self, page, verbose):
        if verbose:            
            inform('generate buttons code for page [ %s ]' % page['name'] )
        return NCodeGen.generateButtonsHeader( page )

    def labelsCode(self, page, verbose):
        if verbose:
            inform('generate labels code for page [ %s ]' % page['name'] )
        return NCodeGen.generateLabelsHeader( page )
    
    def convertFonts(self, fonts, verbose):
        """ converting all parset fonts to NGL_Font objects """
        return [ self._convertFont(font, verbose) for font in fonts ]

    def _convertFont(self, font, verbose):
        # charters set to converting
        chars_sets = ''.join([ chr(x) for x in range(ord(' '), ord('~')) ])

        # converting to ngl_font
        if verbose:
            inform( 'converting font %s, %spt, bold=%s' % ( font['family'],
                                                  font['pointsize'], font['bold'] ) )
        ngl_font = NFC.convertParsedQFont( chars_sets, font )
        
        return ngl_font

    def fontsHeaderCode(self, fonts, verbose):
        if verbose:
            inform( 'generate fonts header file...' )
        return NFontCodeGen.generateFontsHeader( fonts )

    def convertBitmaps(self, bitmaps, verbose):
        """ converting all parset bitmaps to NGL_Bitmap objects """        
        return [ self._convertBitmap(bmp, verbose) for bmp in bitmaps ]
    
    def _convertBitmap(self, bitmap, verbose):
        if os.path.exists( bitmap['path'] ):
            ngl_bitmap = NBC.convertParsedBitmap( bitmap,
                                                  'format16',
                                                  'compressed_None' )
            if verbose:
                inform( 'converting bitmap {0}, size {1}x{2}'.format( \
                         bitmap['name'], bitmap['width'], bitmap['height'] ))
        else:
            error( ( 'File "{0}" not found! Expected path - "{1}" not exist'
                     ' :( :( :( ' ).format( bitmap['name'], bitmap['path'] ))              

        return ngl_bitmap

    def bitmapsHeaderCode(self, bitmaps, verbose ):
        if verbose:
            inform( 'generate bitmaps header file...' )
        return NBitmapCodeGen.generateBitmapsHeader( bitmaps )


    def informUser(self, state, verbose):
        if state == 'parse_end':
            if verbose:                
                inform( 'ui file version - %s' %  self.parser.uiVersion() )
                inform( 'page - "%s"' % self.parser.parsedPage()['name'] )

                objects = self.parser.parsedObjects()                
                objects_names = ', '.join( [obj['name'] for obj in objects] ) 
                inform( 'objects - %s' % objects_names )

                bitmaps, fonts = self.parser.parsedResourses()                
                bitmaps_paths = [ os.path.basename(bmp['path']) for bmp in bitmaps ]
                fonts_familys = [font['name'] for font in fonts]
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
        pagename        = kwargs['pagename']
        pagecode        = kwargs['pagecode']        
        buttons_code    = kwargs['buttonscode']
        labels_code     = kwargs['labelscode']        
        bitmaps         = kwargs['bitmaps']
        bitmaps_header  = kwargs['bitmapsheader']
        fonts           = kwargs['fonts']
        fonts_header    = kwargs['fontsheader']
        verbose         = kwargs['verbose']

        # save page code
        self.saveCode(  dircode = 'page',
                        name = pagename + '.c',
                        code = pagecode,
                        verbose = verbose )
        
        # save common buttons header code
        self.saveCode(  dircode = 'buttons',
                        name = pagename + '_buttons.h',
                        code = buttons_code,
                        verbose = verbose )
        
        # save common labels header code
        self.saveCode(  dircode = 'labels',
                        name = pagename + '_labels.h',
                        code = labels_code,
                        verbose = verbose )
        
        # save all fonts codes
        self.saveResources( fonts, 'fonts', verbose )
        
        # save common fonts header code 
        self.saveCode(  dircode = 'fonts',
                        name = 'fonts.h',
                        code = fonts_header,
                        verbose = verbose )

        # save all bitmaps header code
        self.saveResources( bitmaps, 'bitmaps', verbose )
        
        # save common bitmaps header code 
        self.saveCode(  dircode ='bitmaps',
                        name = 'bitmaps.h',
                        code = bitmaps_header,
                        verbose = verbose )

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
                            metavar = 'NAMEUI',                            
                            help = 'input QtDesigner ui file' )

    parser.add_argument ( '-d', '--outdir', dest = 'ngl_out_dir', type = str,
                            default = './code',
                            metavar = 'DIR',
                            help = ( 'generated code out directory '
                                     '[default: \'%s\']' % '.\\Code' ) )

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

    # if no args print help and exit
    if not len(sys.argv[1:]):
        parser.print_help()
        error('No arguments found :( exit...')
    
    if not os.path.exists( args.qt_uifile ):
        # args.qt_uifile = 'untitled.ui'        
        error( 'Qt ui file path not correct :( exit... ' )
    
    uifile = args.qt_uifile
    outdir = args.ngl_out_dir
    verbose = args.verbose
    
    # create nuic object and parse Qt ui file
    nuic = NUIC( uifile )       
    ppage, pbitmaps, pfonts = nuic.parser.parse()   
    nuic.informUser( 'parse_end', verbose )
    
    # convert all fonts, generate common fonts header code
    ngl_fonts = nuic.convertFonts( pfonts, verbose )
    ngl_fonts_header = nuic.fontsHeaderCode( pfonts, verbose )    
    
    # convert all bitmaps, generate common bitmaps header code
    ngl_bitmaps = nuic.convertBitmaps( pbitmaps, verbose )
    ngl_bitmaps_header = nuic.bitmapsHeaderCode( pbitmaps, verbose )
    
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
    inform( '-*-*- All works finish! :) --- out code locate in %s' % os.path.abspath(code_dirs['base']) )
    


# ------------------------------------------------------------------------------
# program start here
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())
    
