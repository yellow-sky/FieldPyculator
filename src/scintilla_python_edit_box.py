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
Code from geoprocessing/ScriptEdit.py  by Alexander Bruy
"""

import os
from PyQt4.QtCore import SIGNAL, Qt, QSettings
from PyQt4.QtGui import QFont, QShortcut, QColor, QKeySequence
from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from qgis.core import QgsApplication
from base_python_edit_box import BasePythonEditBox


class ScintillaPythonEditBox(QsciScintilla, BasePythonEditBox):

    def __init__(self, parent=None):
        QsciScintilla.__init__(self, parent)

        self.lexer = None
        self.api = None
        self.lexerType = -1

        self.setCommonOptions()
        self.initShortcuts()

    def setCommonOptions(self):
        # Enable non-ASCII characters
        self.setUtf8(True)

        # Default font
        # Load font from Python console settings
        settings = QSettings()
        fontName = settings.value('pythonConsole/fontfamilytext', 'Monospace')
        fontSize = int(settings.value('pythonConsole/fontsize', 10))

        self.defaultFont = QFont(fontName)
        self.defaultFont.setFixedPitch(True)
        self.defaultFont.setPointSize(fontSize)
        self.defaultFont.setStyleHint(QFont.TypeWriter)
        self.defaultFont.setStretch(QFont.SemiCondensed)
        self.defaultFont.setLetterSpacing(QFont.PercentageSpacing, 87.0)
        self.defaultFont.setBold(False)

        self.boldFont = QFont(self.defaultFont)
        self.boldFont.setBold(True)

        self.italicFont = QFont(self.defaultFont)
        self.italicFont.setItalic(True)

        self.setFont(self.defaultFont)
        self.setMarginsFont(self.defaultFont)

        self.setFont(self.defaultFont)
        self.setMarginsFont(self.defaultFont)

        self.initLexer()

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        self.setWrapMode(QsciScintilla.WrapWord)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagByText,
                                QsciScintilla.WrapFlagNone, 4)

        self.setSelectionForegroundColor(QColor('#2e3436'))
        self.setSelectionBackgroundColor(QColor('#babdb6'))

        # Show line numbers
        self.setMarginWidth(1, '000')
        self.setMarginLineNumbers(1, True)
        self.setMarginsForegroundColor(QColor('#2e3436'))
        self.setMarginsBackgroundColor(QColor('#babdb6'))

        # Highlight current line
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor('#d3d7cf'))

        # Mark column 80 with vertical line
        self.setEdgeMode(QsciScintilla.EdgeLine)
        self.setEdgeColumn(80)
        self.setEdgeColor(QColor('#eeeeec'))

        # Indentation
        self.setAutoIndent(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setTabWidth(4)

        # Autocomletion
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)


    def initShortcuts(self):
        (ctrl, shift) = (self.SCMOD_CTRL << 16, self.SCMOD_SHIFT << 16)

        # Disable some shortcuts
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('D') + ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('L') + ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('L') + ctrl
                           + shift)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('T') + ctrl)

        #self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord("Z") + ctrl)
        #self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord("Y") + ctrl)

        # Use Ctrl+Space for autocompletion
        self.shortcutAutocomplete = QShortcut(QKeySequence(Qt.CTRL
                + Qt.Key_Space), self)
        self.shortcutAutocomplete.setContext(Qt.WidgetShortcut)
        self.shortcutAutocomplete.activated.connect(self.autoComplete)

    def autoComplete(self):
        self.autoCompleteFromAll()

    def setLexerType(self, lexerType):
        self.lexerType = lexerType
        self.initLexer()

    def initLexer(self):
        self.lexer = QsciLexerPython()

        colorDefault = QColor('#2e3436')
        colorComment = QColor('#c00')
        colorCommentBlock = QColor('#3465a4')
        colorNumber = QColor('#4e9a06')
        colorType = QColor('#4e9a06')
        colorKeyword = QColor('#204a87')
        colorString = QColor('#ce5c00')

        self.lexer.setDefaultFont(self.defaultFont)
        self.lexer.setDefaultColor(colorDefault)

        self.lexer.setColor(colorComment, 1)
        self.lexer.setColor(colorNumber, 2)
        self.lexer.setColor(colorString, 3)
        self.lexer.setColor(colorString, 4)
        self.lexer.setColor(colorKeyword, 5)
        self.lexer.setColor(colorString, 6)
        self.lexer.setColor(colorString, 7)
        self.lexer.setColor(colorType, 8)
        self.lexer.setColor(colorCommentBlock, 12)
        self.lexer.setColor(colorString, 15)

        self.lexer.setFont(self.italicFont, 1)
        self.lexer.setFont(self.boldFont, 5)
        self.lexer.setFont(self.boldFont, 8)
        self.lexer.setFont(self.italicFont, 12)

        self.api = QsciAPIs(self.lexer)

        settings = QSettings()
        useDefaultAPI = bool(settings.value('pythonConsole/preloadAPI',
                                            True))
        if useDefaultAPI:
            # Load QGIS API shipped with Python console
            self.api.loadPrepared(
                os.path.join(QgsApplication.pkgDataPath(),
                             'python', 'qsci_apis', 'pyqgis.pap'))
        else:
            # Load user-defined API files
            apiPaths = settings.value('pythonConsole/userAPI', [])
            for path in apiPaths:
                self.api.load(path)
            self.api.prepare()
            self.lexer.setAPIs(self.api)

        self.setLexer(self.lexer)

    #impliment base editor
    def insertPlainText(self, text):
        self.insert(text)
        pos = self.getCursorPosition()
        self.setCursorPosition(pos[0], pos[1]+len(text))

    def toPlainText(self):
        return self.text()

    def get_font_size(self):
        return self.font().pointSize()

    def set_font_size(self, new_point_size):
        font = self.font()
        self.setFont(QFont(font.family(), new_point_size))

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.emit(SIGNAL("wheelEvent(QWheelEvent)"), event)
        else:
            super(ScintillaPythonEditBox, self).wheelEvent(event)