#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import pkg_resources


class NCodeService(object):
    """docstring for NCodeService"""

    @staticmethod
    def removeDuplicates(objects):
        objs = set( objects )
        return list(objs)

    @staticmethod
    def iconName(bitmaps, key):
        for bn in bitmaps:
            if key in bitmaps[bn]:
                return os.path.basename(bn).split('.')[0]
        return None

    @staticmethod
    def resourceTemplate(res_name):
        """ get code template from ngl_utils package """
        res_path = pkg_resources.resource_filename( 'ngl_utils', 'templates/%s.ntp' % res_name )

        with open(res_path, 'rt') as f:
            template = f.read()

        return template

    @staticmethod
    def sortClassKeys(objects):
        """ Sort object classes keys for correct
            pointers in NGL_Page typedef struct """

        orderdict = {}
        for classkey in objects:
            orderdict[classkey] = list(objects[classkey].values())[0].__class__.ngl_order

        # sort objects
        objs = sorted(objects, key=lambda classkey: orderdict[classkey])
        return objs

    @staticmethod
    def pageObjectsName(pagename, objname):
        return '{page}_{objs}s'.format(page = pagename.lower(),
                                       objs = objname.lower().replace('ngl_', ''))

    @staticmethod
    def pageObjectsCountName(name):
        return '%s_CNT' % name.upper()

    @staticmethod
    def getDynObjects(objects):
        dobjects = {}

        for key in objects:
            if objects[key].getStatic() is False:
               dobjects[key] = objects[key]

        return dobjects

    @staticmethod
    def getObjectsEvents(objects):
        """ Return all object events from gived page """
        return NCodeService.removeDuplicates(
            [ objects[key].clickEventName for key in objects if objects[key].eventsEnabled ])


class NCodeGen(object):
    """ doc for NCodeGen"""

    @staticmethod
    def generetePageCode(page):

        objects = page['objects']

        # get templates
        page_template = NCodeService.resourceTemplate('page')
        func_template = NCodeService.resourceTemplate('function')

        # page includes and objects pointers
        page_includes = NCodeGen._generatePageIncludes(page)
        objects_pnt = NCodeGen._generatePageObjPointers(page)

        # page func prototypes
        protFunctions  = ('static void {page}_Draw(void);\n'
                          'static void {page}_Click(void);').format(page = page['name'])

        # create page draw function code
        drawCode = NCodeGen._generatePageDraw(page)

        # create page click function code
        clickCode = NCodeGen._generatePageClick(page)

        # objects events
        eventsCode = NCodeGen._generatePageObjectsEvents(page)

        # preapere all functions code
        functionsCode = (drawCode + '\n\n' + \
                         clickCode + '\n\n' + \
                         eventsCode + '\n\n')

        # create final code
        return page_template.format(
                pageName       = page['name'],
                date           = datetime.now(),
                brief          = 'NGL Page %s sourse' % page['name'],
                include        = ''.join(page_includes),
                protFunctions  = protFunctions,
                rect           = '0, 0, %s, %s' % (page['width'], page['height']),
                id             = '0',
                bcolor         = hex(page['background_color']),
                objects_pnt    = ''.join(objects_pnt),
                functions      = functionsCode)

    @staticmethod
    def _generatePageIncludes(page):
        """ generate page objects headers includes code
        """
        objects = page['objects']
        page_includes = []

        # iter sorted class keys
        for classkey in objects:

            # get all dyn object in NGL class
            dobjects = NCodeService.getDynObjects(objects[classkey])

            # Add includes to page
            if len(dobjects):
                nm = NCodeService.pageObjectsName(page['name'], classkey)
                page_includes.append('#include "%s.h"\n' % nm)

        return page_includes

    @staticmethod
    def _generatePageObjPointers(page):
        """ generate page objects pointers code
        """
        objects = page['objects']
        objects_pnt = []

        # iter sorted class keys
        for classkey in NCodeService.sortClassKeys(objects):

            # get all dyn object in NGL class
            dobjects = NCodeService.getDynObjects(objects[classkey])

            # Add respect include to page and object array pointer
            # to NGL_Page struct init code
            if len(dobjects):
                nm = NCodeService.pageObjectsName(page['name'], classkey)
                objects_pnt.append('%s,\n%s' % (nm, '\t'*4))

        return objects_pnt

    @staticmethod
    def _generatePageDraw(page):

        # get templates
        template = NCodeService.resourceTemplate('function')
        objdraw_template = NCodeService.resourceTemplate('page_obj_draw')
        dobj_template = NCodeService.resourceTemplate('page_dobj_draw')

        # primitives = [obj for obj in page['objects'] if obj.static is True]
        # primitives = page['objects']
        primitives_code = ''
        dobjects_code = ''

        primitives = {}

        # get all objects to common collection and sort by orderIndex
        for classkey in page['objects']:
            for key in page['objects'][classkey]:
                primitives[key] = page['objects'][classkey][key]

        sprmitives = sorted(primitives, key=lambda x: primitives[x].orderIndex)

        # static objects
        for key in sprmitives:
            if primitives[key].getStatic() is True:
                iconame = NCodeService.iconName(page['bitmaps'], key)
                code = primitives[key].doNGLCode(iconame=iconame)
                primitives_code += code + '\n\t\t'

        # dyn objects
        for classkey in NCodeService.sortClassKeys(page['objects']):

            dobjects = NCodeService.getDynObjects(page['objects'][classkey])

            if len(dobjects):
                nm = NCodeService.pageObjectsName(page['name'], classkey)
                obj_cnt_def = NCodeService.pageObjectsCountName(nm)

                # drawfunc = primitives[key].doNGLCode(iconame=iconame)
                obj_class = list(dobjects.values())[0].__class__
                drawfunc = obj_class.ngl_draw(name = nm, index = 'cnt')

                dobjects_code += dobj_template.format(objname = classkey,
                                                      objcnt = obj_cnt_def,
                                                      drawfunc = drawfunc)

        # page all objects draw template format
        _backcolor = hex(page['background_color'])

        func_code = objdraw_template.format(primitives = primitives_code,
                                            dobjects = dobjects_code,
                                            page_backcolor = _backcolor,
                                            pageName = page['name'])

        # final format code and return
        return template.format(func_name = page['name']+ '_Draw',
                               func_desc = 'Draw page objects function',
                               static = 'static',
                               func_code = func_code)

    @staticmethod
    def _generatePageClick(page):
        # get template
        template = NCodeService.resourceTemplate('function')

        # final format code and return
        return template.format(
            func_name = page['name']+ '_Click',
            func_desc = 'Common click page objects',
            static = 'static',
            func_code = '')

    @staticmethod
    def _generatePageObjectsEvents(page):
        """ Get non duplicate click events in page
            and create functions code """

        # get template
        func_template = NCodeService.resourceTemplate('function')

        out_code = ''

        for classkey in page['objects']:
            classobjects = page['objects'][classkey]

            for item in NCodeService.getObjectsEvents(classobjects):
                event = func_template.format( static='static',
                                              func_name=item,
                                              func_desc='Item/Items click event',
                                              func_code='' )
                out_code += event + '\n\n'

        return out_code

    @staticmethod
    def generateObjectsHeader(page):
        """ generate objects headers """

        primitives = ['NGL_Line', 'NGL_Rect', 'NGL_Bitmap']

        objects = page['objects']
        headers = {}

        for classkey in objects:
            # not generate header if object is primitive or bitmap
            if classkey not in primitives and len(objects[classkey]):
                headers[classkey] = NCodeGen._hheader(page, classkey)

        return headers

    @staticmethod
    def _hheader(page, objclass):

        # get templates and objects
        header_template = NCodeService.resourceTemplate('header')
        objects = page['objects'][objclass]

        # code vars
        int_vars = ''
        functionPrototypes = ''
        code = ''
        pointers = []

        # event prototypes
        events = NCodeService.getObjectsEvents(objects)
        functionPrototypes = ''.join(['static void %s(void);\n' % ev for ev in events])

        # generate code for non static objects
        dobjects = NCodeService.getDynObjects(objects)
        for key in dobjects:
            iconame = NCodeService.iconName(page['bitmaps'], key)
            code += dobjects[key].doNGLCode(iconame=iconame) + '\n\n'
            pointers.append('&%s, ' % key)

        # preformat
        nm = NCodeService.pageObjectsName(page['name'], objclass)
        obj_cnt_def = NCodeService.pageObjectsCountName(nm)
        obj_defines = '#define %s\t\t%s\n' % (obj_cnt_def, len(pointers))

        pointers_code = 'static const %s* %s[%s] = {%s};' % (objclass,
                                                             nm,
                                                             obj_cnt_def,
                                                             ''.join(pointers))
        varsText = '%s\n%s\n' % (code, pointers_code)

        # final format header and return result
        return header_template.format(
            pageName = page['name'],
            prefix = '123',
            brief = '123',
            date = datetime.now(),
            header_define = '__%s_H' % nm.upper(),
            defines = obj_defines,
            macros = '',
            typedefs = '',
            functionPrototypes = functionPrototypes,
            int_vars = '',
            varsText = varsText
        ).replace('True', 'ENABLE').replace('False', 'DISABLE')

    @staticmethod
    def pagesHeader(page):
        """ generate page header """
        return NCodeGen._pheader(page)

    @staticmethod
    def _pheader(page):
        """ """
        header_template = NCodeService.resourceTemplate('header')

        # final format header and return result
        return header_template.format(
            pageName = page['name'],
            prefix = '123',
            brief = '123',
            date = datetime.now(),
            header_define = '__PAGES_H',
            defines = '',
            macros = '',
            typedefs = '',
            functionPrototypes = '',
            int_vars = '',
            varsText = 'extern NGL_Page %s;' % page['name']
        )



class NFontCodeGen(object):
    """docstring for NFontCodeGen"""

    @staticmethod
    def font(font):
        # get template, format and return result
        return NCodeService.resourceTemplate('font').format(
                font_max_height = font.max_height(),
                name = font.name,
                bitmaps_data = NFontCodeGen._nchars_code( font ),
                descriptors_data = NFontCodeGen._nchars_desc( font ),
                font_start_char = font.get_chars_list()[0]['char'],
                font_end_char = font.get_chars_list()[-1]['char'],
                space_width = '2')

    @staticmethod
    def _nchars_code(font):
        """ Generate code for all chars in font char list
        """
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
        """ generate code for fonts header file
        """
        # get template from resources
        header_template = NCodeService.resourceTemplate('header')

        fonts_code = ''
        for font in fonts:
            fonts_code += 'extern NGL_Font %s;\n' % font.name

        return header_template.format(
            pageName = '',
            prefix = 'fonts',
            brief = 'NGL Fonts common header',
            date = datetime.now(),
            header_define = '__NGL_FONTS_H',
            defines = '',
            macros = '',
            typedefs = '',
            functionPrototypes = '',
            int_vars = '',
            varsText = fonts_code)


class NBitmapCodeGen(object):
    """docstring for NBitmapCodeGen"""

    @staticmethod
    def bitmap(bitmap):
        # get template
        template = NCodeService.resourceTemplate('bitmap')

        # format template with bitmap object params
        return template.format(
            name = bitmap.name,
            width = bitmap.width-1,
            height = bitmap.height-1,
            compressed = bitmap.compressed,
            color_bit = bitmap.color_bit,
            data_word_size = bitmap.data_word_size,
            data_len_in_words = bitmap.data_len_in_words,
            data_len_in_bytes = bitmap.data_len_in_bytes,
            datatype = bitmap.datatype,
            data = bitmap.formatedData()
        ).replace('None', '0').replace('RLE', '1').replace('JPG', '2')

    @staticmethod
    def generateBitmapsHeader(bitmaps):
        """ generate code for bitmaps header file
        """
        # get template from resources
        header_template = NCodeService.resourceTemplate('header')

        bitmaps_code = ''
        for bmp in bitmaps:
            bitmaps_code += 'extern NGL_Bitmap %s;\n' % bmp.name

        return header_template.format(
            pageName = '',
            prefix = 'bitmaps',
            brief = 'NGL Bitmaps common header',
            date = datetime.now(),
            header_define = '__NGL_BITMAPS_H',
            defines = '',
            macros = '',
            typedefs = '',
            functionPrototypes = '',
            int_vars = '',
            varsText = bitmaps_code )
