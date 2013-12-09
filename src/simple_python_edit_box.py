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
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import QPlainTextEdit, QFont
from syntax_highlighter import PythonHighlighter


class SimplePythonEditBox(QPlainTextEdit):
    def __init__(self, *__args):
        QPlainTextEdit.__init__(self, *__args)
        self.set_tab_size()
        self.highlight = PythonHighlighter(self.document())

    def set_tab_size(self):
        tab_stop = 4
        metrics = self.fontMetrics()
        self.setTabStopWidth(tab_stop * metrics.width(' '))

    def get_font_size(self):
        return self.font().pointSize()

    def set_font_size(self, new_point_size):
        font = self.font()
        self.setFont(QFont(font.family(), new_point_size))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.emit(SIGNAL("wheelEvent(QWheelEvent)"), event)
        else:
            super(SimplePythonEditBox, self).wheelEvent(event)
