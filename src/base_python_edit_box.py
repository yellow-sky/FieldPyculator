"""
/***************************************************************************
 FieldPyculator
                                 A QGIS plugin
 Use python power for calculate fields of vector layers
                              -------------------
        begin                : 2012-01-07
        copyright            : (C) 2012 by Nikulin Evgeniy
        email                : nikulin.e at gmail
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
#from PyQt4 import Qt
#from PyQt4.QtCore import SIGNAL


class BasePythonEditBox():
    def __init__(self):
        pass

    def get_font_size(self):
        raise NotImplementedError()

    def set_font_size(self, new_point_size):
        raise NotImplementedError()

    def insertPlainText(self, text):
        raise NotImplementedError()

    def toPlainText(self):
        raise NotImplementedError()

    #def wheelEvent(self, event):
        #self.emit(SIGNAL("wheelEvent(QWheelEvent)"), event)
        #raise NotImplementedError()
