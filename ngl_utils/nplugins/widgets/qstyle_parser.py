#!/usr/bin/env python

from PyQt5.QtGui import QColor


class QStyleParser(object):

    @staticmethod
    def getColor(styleSheet, cid):

        # cid = 'color: rgb'

        for line in styleSheet.splitlines():
            if line.find(cid) == 0:
                start = line.find('(') + 1
                end = line.rfind(')')
                r, g, b = line[start:end].replace(' ', '').split(',')
                return QColor( int(r), int(g), int(b) )

        return QColor(0, 0, 0)

    @staticmethod
    def getColorStyleSheet(qcolor, name):
        return '{NAME}: rgb({R}, {G}, {B});'.format( NAME = name,
                                                     R = qcolor.red(),
                                                     G = qcolor.green(),
                                                     B = qcolor.blue()  )
