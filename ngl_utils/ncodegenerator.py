#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pkg_resources

# ------------------------------------------------------------------------------
# NCodeGen
# ------------------------------------------------------------------------------
class NCodeGen(object):
    """ doc for NCodeGen"""

    @staticmethod
    def getResourceTemplate(res_name):
        res_path = pkg_resources.resource_filename( 'ngl_utils', 'templates/%s.ntp' % res_name )
        with open(res_path, 'rt') as f:
            template = f.read()
        return template

    @staticmethod
    def generateButtonsHeader(page):
        # get templates
        header_template = NCodeGen.getResourceTemplate('header')
                
        defineString = '__{0}_BUTTONS_H'.format( page['name'].upper() )

        # Get non duplicate click events in page
        buttonsEvents = NCodeGen._removeDuplicateObjects(
                                [ itm['click'] for itm in page['buttons'] ] )
        eventPrototypes = ''
        for event in buttonsEvents:
            eventPrototypes += 'static void %s(void);\n' % event

        buttonsCode = '';
        for item in page['buttons']:
            buttonsCode += NCodeGen._buttonTemplate( page['name'], item ) + '\n\n'

        return header_template.format(  pageName = page['name'],
                                        prefix = '_buttons',
                                        brief = 'NGL Page Buttons structs',
                                        date = datetime.now(),
                                        define = defineString,
                                        functionPrototypes = eventPrototypes,
                                        varsText = buttonsCode  )

    @staticmethod
    def _buttonTemplate( PageName, button ):
        button_template = NCodeGen.getResourceTemplate('button')

        bitmapName = '(void*)0'
        fontName = '(void*)0'

        bmp_path = button['bitmap']['path']
        if button['bitmap'] != None and bmp_path != '':
            bitmapName = '(NGL_Image*)&%s' % button['bitmap']['name']

        if button['font'] != None and button['font']['family'] != '':
            fontName = NCodeGen._formatFontPointer( button['font'] )

        if 'text' not in button:
            button['text'] = 'nbutton'

        if 'bitmap' in button:
            btnType = 'IconButton'
        else:
            btnType = 'ColorFillButton'

        return button_template.format(
            pageName    = PageName,
            itemName    = button['name'],
            x           = button['x'],
            y           = button['y'],
            width       = button['width'],
            height      = button['height'],
            type        = btnType,
            color       = hex( button['color'] ),
            backColor   = hex( button['background_color'] ),
            colorShift  = 'TRUE',
            bitmapName  = bitmapName,
            fontName    = fontName,
            text_X_shift = '0',
            text_Y_shift = '0',
            textColor   = hex( button['color'] ),
            text        = button['text'],
            visible     = 'TRUE',
            status      = 'ENABLE',
            eventName   = button['click']
        ).replace('True', 'ENABLE').replace('False', 'DISABLE')

    @staticmethod
    def generateLabelsHeader(page):        
        """ generate code for labels header file """
        # get template from resources
        header_template = NCodeGen.getResourceTemplate('header')

        # labels varibles and struct code
        labelsVars = ''
        labelsCode = '';

        for item in page['labels']:
            item['labelVar'] = '%s_text' % item['name']
            labelsVars += 'char {0}[{1}] = "{2}";\n'.format( item['labelVar'], len(item['text']), item['text'] )
            labelsCode += NCodeGen._labelTemplate( page['name'], item )

        return header_template.format(  pageName = page['name'],
                                        prefix = '_labels',
                                        brief = 'NGL Page labels structs',
                                        date = datetime.now(),
                                        define = '__{0}_LABELS_H'.format( page['name'].upper() ),
                                        functionPrototypes = '',
                                        varsText = labelsVars + labelsCode )

    @staticmethod
    def generetePageCode(page):
        # get templates
        page_template = NCodeGen.getResourceTemplate('page')
        func_template = NCodeGen.getResourceTemplate('function')

        # Create page draw function code        
        pageDrawCode = NCodeGen._generatePageDraw( page )

        # Get non duplicate click events in page and create functions code
        btnEvents = [ itm['click'] for itm in page['buttons'] ]
        btnEvents = NCodeGen._removeDuplicateObjects( btnEvents )
        
        eventsCode = ''
        for item in btnEvents:
            event = func_template.format( static='static',
                                          func_name=item,
                                          func_desc='Item/Items click event' )
            eventsCode += event + '\n\n'

        # page includes
        page_includes = ( '#include "{0}_buttons.h"\n'
                          '#include "{0}_labels.h"' )
        page_includes = page_includes.format( page['name'].lower() )

        # Create final page code text
        return page_template.format(
                pageName       = page['name'],
                date           = datetime.now(),
                brief          = 'NGL Page %s sourse' % page['name'],
                include        = page_includes,
                protFunctions  = 'static void %s(void);' % (page['name'] + '_Draw'),                
                rect           = '0, 0, %s, %s' % ( page['width'], page['height'] ),
                clip           = 'DISABLE',
                clip_id        = '0',
                bcolor         = hex( page['background_color'] ),
                start_btn      = '0',
                btn_cnt        = len(page['buttons']),
                sel_indx       = '0',
                old_indx       = '0',
                lbl_cnt        = len(page['labels']),
                btn_pnt        = NCodeGen._generatePointersCode( page['buttons'] ),
                lbl_pnt        = NCodeGen._generatePointersCode( page['labels'] ),                
                functions      = pageDrawCode + '\n\n' + eventsCode )

    @staticmethod
    def _removeDuplicateObjects(objects):
        objs = set( objects )
        return list(objs)

    @staticmethod
    def _formatFontPointer(font):
        """ format pointer to font data for C style """        
        return '(NGL_Font*)&{0}'.format( font['name'] )

    @staticmethod
    def _labelTemplate( pageName, item ):
        # get templates
        label_template = NCodeGen.getResourceTemplate('label')

        if 'text' not in item:
            item['text'] = 'label'

        fontName = NCodeGen._formatFontPointer( item[ 'font' ] )
        code = label_template.format( pageName = pageName,
                                      itemName = item['name'],
                                      x = item['x'],
                                      y = item['y'],
                                      color = hex( item['color'] ),
                                      visible = 'True',
                                      text = '&%s' % item['labelVar'],
                                      fontName = fontName )
        return code.replace('True', 'ENABLE').replace('False', 'DISABLE')

    @staticmethod
    def _lineObjectDrawTemplate(line):
        return "LCD_DrawLine({x0}, {y0}, {x1}, {y1}, {color});\n".format(
                x0 = line['x'],
                y0 =line['y'],
                x1 = int(line['x']) + int(line['width']) - 1,
                y1 = int(line['y']) + int(line['height']) - 1,
                color = hex( line['color'] ) )

    @staticmethod
    def _rectangleObjectDrawTemplate(rectangle):
        fillParamText = "";
        color = rectangle.UIColor.ConvertTo565Color().ToString("X");

        if rectangle.Fill == True:
            fillParamText = '0x{0}, DRAW, 0x{0}'.format( color );

        return '\tLCD_DrawFillRect({0}, {1}, {2}, {3}, {4});\r\n'.format(
            rectangle.p0.X.ToString(),
            rectangle.p0.Y.ToString(),
            (rectangle.p0.X + rectangle.Widht).ToString(),
            (rectangle.p0.Y + rectangle.Height).ToString(),
            fillParamText )

    @staticmethod
    def _labelObjectDrawTemplate(label):
        return '\tLCD_PutColorStrig({0}, {1}, {2}, \"{3}\", 0x{4});\r\n'.format(
            label.p0.X,
            label.p0.Y,
            "1",
            label.Text,
            label.UIColor.ConvertTo565Color().ToString("X") )

    @staticmethod
    def _imageObjectDrawTemplate(bitmap):
        return '\tLCD_DrawImage({0}, {1}, &{2}Info);\r\n'.format(
            bitmap.p0.X,
            bitmap.p0.Y,
            bitmap.BitmapName )

    @staticmethod
    def _generatePageDraw(page):
        # get template
        template = NCodeGen.getResourceTemplate('page_obj_draw')

        graphics_obj_draw = ''

        # Lines
        for line in page['lines']:
            graphics_obj_draw += '\t\t' + NCodeGen._lineObjectDrawTemplate( line )

        # Rectangles
        # for rect in page['rectangles']:
        #     codeText += rectangleObjectDrawTemplate( rect )

        # Bitmaps
        # for img in page['bitmaps']:
        #     codeText += imageObjectDrawTemplate( img )
                                                 # p = ', ResetButton')
        
        return template.format( pageName = page['name'],
                                page_backcolor = hex( page['background_color'] ),
                                graphics_objects = graphics_obj_draw )

    @staticmethod
    def _generatePointersCode(objects):
        text =''
        cnt = 0
        for obj in objects:
            text += ' &%s,' % obj['name']
            if cnt >= 5:
                text += '\r\n' + '\t' * 3
                cnt = 0
            else:
                cnt += 1

        return text

# ------------------------------------------------------------------------------
# NFontCodeGen
# ------------------------------------------------------------------------------
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
                len = len( nchar['code'] ),
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
            fonts_code += 'extern NGL_Font %s;\n' % font['name']

        return header_template.format(  pageName = '',
                                        prefix = 'fonts',
                                        brief = 'NGL Fonts common header',
                                        date = datetime.now(),
                                        define = '__NGL_FONTS_H',
                                        functionPrototypes = '',
                                        varsText = fonts_code )

# ------------------------------------------------------------------------------
# NBitmapCodeGen
# ------------------------------------------------------------------------------
class NBitmapCodeGen(object):
    """docstring for NBitmapCodeGen"""
    
    @staticmethod
    def bitmap(bitmap):
        codes = {
        '{name}':               bitmap.name,
        '{width}':              bitmap.width,
        '{height}':             bitmap.height,
        '{compressed}':         bitmap.compressed,
        '{color_bit}':          bitmap.color_bit,
        '{data_word_size}':     bitmap.data_word_size,
        '{data_len_in_words}':  bitmap.data_len_in_words,
        '{data_len_in_bytes}':  bitmap.data_len_in_bytes,
        '{datatype}':           bitmap.datatype,
        '{data}':               bitmap.formatedData(),
        }

        # get template
        template = NCodeGen.getResourceTemplate('bitmap')

        for key in codes.keys():
            template = template.replace( key, str(codes[key]) )
       
        return template
    
    @staticmethod
    def generateBitmapsHeader(bitmaps):
        """ generate code for bitmaps header file """
        # get template from resources
        header_template = NCodeGen.getResourceTemplate('header')

        bitmaps_code = ''
        for bmp in bitmaps:            
            bitmaps_code += 'extern NGL_Bitmap %s;\n' % bmp['name']

        return header_template.format(  pageName = '',
                                        prefix = 'bitmaps',
                                        brief = 'NGL Bitmaps common header',
                                        date = datetime.now(),
                                        define = '__NGL_BITMAPS_H',
                                        functionPrototypes = '',
                                        varsText = bitmaps_code )

    # @staticmethod
    # def bitmapName(bitmap):       
    #     return bitmap.name

