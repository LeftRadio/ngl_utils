#!/usr/bin/env python3

import os
from datetime import datetime
import pkg_resources


class NCodeGen(object):
    """ doc for NCodeGen"""

    @staticmethod
    def getResourceTemplate(res_name):
        res_path = pkg_resources.resource_filename( 'ngl_utils', 'templates/%s.ntp' % res_name )
        with open(res_path, 'rt') as f:
            template = f.read()
        return template

    @staticmethod
    def generetePageCode(page):
        # get templates
        page_template = NCodeGen.getResourceTemplate('page')
        func_template = NCodeGen.getResourceTemplate('function')

        # Create page draw function code
        pageDrawCode = NCodeGen._generatePageDraw( page )

        # Get non duplicate click events in page and create functions code
        btnEvents = [ key + '_click' for key in page['objects']['NGL_Button'] ]
        btnEvents = NCodeGen._removeDuplicateObjects( btnEvents )

        eventsCode = ''
        for item in btnEvents:
            event = func_template.format( static='static',
                                          func_name=item,
                                          func_desc='Item/Items click event' )
            eventsCode += event + '\n\n'

        # page includes
        page_includes = ('#include "{0}_buttons.h"\n'
                         '#include "{0}_labels.h"').format(page['name'].lower())

        objects = page['objects']

        # Create page final code
        return page_template.format(
                pageName       = page['name'],
                date           = datetime.now(),
                brief          = 'NGL Page %s sourse' % page['name'],
                include        = page_includes,
                protFunctions  = 'static void %s(void);' % (page['name'] + '_Draw'),
                rect           = '0, 0, %s, %s' % (page['width'], page['height']),
                clip           = 'DISABLE',
                clip_id        = '0',
                bcolor         = hex(page['background_color']),
                start_btn      = '0',
                btn_cnt        = len(objects['NGL_Button']),
                sel_indx       = '0',
                old_indx       = '0',
                lbl_cnt        = len(page['objects']['NGL_Label']),
                btn_pnt        = NCodeGen._generatePointersCode(objects['NGL_Button']),
                lbl_pnt        = NCodeGen._generatePointersCode(objects['NGL_Label']),
                functions      = pageDrawCode + '\n\n' + eventsCode
        )

    @staticmethod
    def _generatePageDraw(page):
        # get template
        template = NCodeGen.getResourceTemplate('page_obj_draw')
        objects = page['objects']
        grapcode = ''

        # Lines
        lines = objects['NGL_Line']
        for key in lines:
            code = lines[key].doNGLCode()
            grapcode += '\t\t' + code

        # Rectangles
        rects = objects['NGL_Rect']
        for key in rects:
            code = rects[key].doNGLCode()
            grapcode += '\t\t' + code

        # Bitmaps
        bitmaps = objects['NGL_Bitmap']
        for key in bitmaps:
            code = bitmaps[key].doNGLCode()
            grapcode += '\t\t' + code

        return template.format(pageName = page['name'],
                               page_backcolor = hex(page['background_color']),
                               graphics_objects = grapcode)

    @staticmethod
    def _generatePointersCode(objects):
        text =''
        cnt = 0
        for name in objects:
            text += ' &%s,' % name
            if cnt >= 5:
                text += '\r\n' + '\t' * 3
                cnt = 0
            else:
                cnt += 1

        return text

    @staticmethod
    def _removeDuplicateObjects(objects):
        objs = set( objects )
        return list(objs)

    @staticmethod
    def generateButtonsHeader(page):
        # get templates and buttons
        header_template = NCodeGen.getResourceTemplate('header')
        buttons = page['objects']['NGL_Button']

        # Get non duplicate click events in page
        buttonsEvents = NCodeGen._removeDuplicateObjects(
                                    [ key + '_click' for key in buttons ] )
        eventPrototypes = ''
        for event in buttonsEvents:
            eventPrototypes += 'static void %s(void);\n' % event

        buttonsCode = '';
        for key in buttons:
            iconame = ''
            for bn in page['bitmaps']:
                if key in page['bitmaps'][bn]:
                    iconame = os.path.basename(bn).split('.')[0]

            buttonsCode += buttons[key].doNGLCode(iconame = iconame) + '\n\n'

        # generate out string
        defineString = '__{0}_BUTTONS_H'.format( page['name'].upper() )

        return header_template.format(  pageName = page['name'],
                                        prefix = '_buttons',
                                        brief = 'NGL Page Buttons structs',
                                        date = datetime.now(),
                                        define = defineString,
                                        functionPrototypes = eventPrototypes,
                                        varsText = buttonsCode  )

    @staticmethod
    def generateLabelsHeader(page):
        """ generate code for labels header file """

        # get template and labels
        template = NCodeGen.getResourceTemplate('header')
        labels = page['objects']['NGL_Label']

        # labels varibles and struct code
        labelsVars = ''
        labelsCode = '';

        # generate labels str prototypes and labels sctructs codes
        for name in labels:
            lvar = 'char {0}[{1}] = "{2}";\n'
            labelsVars += lvar.format( '%s_text' % name,
                                       len(labels[name].text),
                                       labels[name].text )

            labelsCode += labels[name].doNGLCode()

        # generate out string
        defineString = '__{0}_LABELS_H'.format(page['name'].upper())

        return template.format(  pageName = page['name'],
                                prefix = '_labels',
                                brief = 'NGL Page labels structs',
                                date = datetime.now(),
                                define = defineString,
                                functionPrototypes = '',
                                varsText = labelsVars + labelsCode )


class NFontCodeGen(object):
    """docstring for NFontCodeGen"""

    @staticmethod
    def font(font):
        codes = {
        '{name}':               font.name,
        '{bitmaps_data}':       NFontCodeGen._nchars_code( font ),
        '{descriptors_data}':   NFontCodeGen._nchars_desc( font ),
        '{font_start_char}':    font.get_chars_list()[0]['char'],
        '{font_end_char}':      font.get_chars_list()[-1]['char'],
        '{space_width}':        '2',
        }

        # get template
        template = NCodeGen.getResourceTemplate('font')

        for key in codes.keys():
            template = template.replace( key, codes[key] )

        return template

    @staticmethod
    def _nchars_code(font):
        """ generate all chars code """
        return '\n'.join( NFontCodeGen._nchar_code(nc) for nc in font.get_chars_list() )

    @staticmethod
    def _nchar_code(nchar):
        char_str_out = '\t/* o@{offset}|l@{len} \'{char}\' ({wide} bits wide) */\n'.format(
                offset = nchar['offset'],
                len = len(nchar['code']),
                char = nchar['char'],
                wide = nchar['bitmap'].width() )

        for y in nchar['code']:
            ch_str = '\t'
            ch_str_vs = '\t\t// '

            for x in y:
                # code
                ch_str += hex(x) + ','
                # visualization
                bit = 7
                while bit >= 0:
                    if x & (1 << bit):
                        ch_str_vs += '*'
                    else:
                        ch_str_vs += ' '
                    bit -= 1

            char_str_out += ch_str + ch_str_vs + '\n'

        return char_str_out

    @staticmethod
    def _nchars_desc(font):
        ch_str = ''
        for ch in font.get_chars_list():
            ch_str += '\t{%d, %d, %d},\t\t/* %s */\n' % (
                    ch['bitmap'].width(),
                    ch['bitmap'].height(),
                    ch['offset'],
                    ch['char'] )
        return ch_str

    @staticmethod
    def generateFontsHeader(fonts):
        """ generate code for fonts header file """
        # get template from resources
        header_template = NCodeGen.getResourceTemplate('header')

        fonts_code = ''
        for font in fonts:
            fonts_code += 'extern NGL_Font %s;\n' % font.name

        return header_template.format(  pageName = '',
                                        prefix = 'fonts',
                                        brief = 'NGL Fonts common header',
                                        date = datetime.now(),
                                        define = '__NGL_FONTS_H',
                                        functionPrototypes = '',
                                        varsText = fonts_code )


class NBitmapCodeGen(object):
    """docstring for NBitmapCodeGen"""

    @staticmethod
    def bitmap(bitmap):
        # get template
        template = NCodeGen.getResourceTemplate('bitmap')
        # format template with bitmap object params
        return template.format(
            name = bitmap.name,
            width = bitmap.width,
            height = bitmap.height,
            compressed = bitmap.compressed,
            color_bit = bitmap.color_bit,
            data_word_size = bitmap.data_word_size,
            data_len_in_words = bitmap.data_len_in_words,
            data_len_in_bytes = bitmap.data_len_in_bytes,
            datatype = bitmap.datatype,
            data = bitmap.formatedData())

    @staticmethod
    def generateBitmapsHeader(bitmaps):
        """ generate code for bitmaps header file """
        # get template from resources
        header_template = NCodeGen.getResourceTemplate('header')

        bitmaps_code = ''
        for bmp in bitmaps:
            bitmaps_code += 'extern NGL_Bitmap %s;\n' % bmp.name

        return header_template.format(  pageName = '',
                                        prefix = 'bitmaps',
                                        brief = 'NGL Bitmaps common header',
                                        date = datetime.now(),
                                        define = '__NGL_BITMAPS_H',
                                        functionPrototypes = '',
                                        varsText = bitmaps_code )
