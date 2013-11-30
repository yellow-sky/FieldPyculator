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
#There is some of QGIS console code

from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
from PyQt4.QtCore import QSettings, Qt, SIGNAL, QByteArray
from PyQt4.QtGui import QFont, QShortcut, QKeySequence
from qgis.core import QgsApplication

class SciEditor(QsciScintilla):
    def __init__(self, parent=None):
        super(SciEditor,self).__init__(parent)
        self.setUtf8(True)
        self.new_input_line = True 
        
        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        #self.moveToMatchingBrace()
        #self.selectToMatchingBrace()
        
        # Current line visible with special background color
        #self.setCaretLineVisible(True)
        #self.setCaretLineBackgroundColor(QColor("#ffe4e4"))
        self.setCaretWidth(2)
    
        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        self.setLexers()
        
        self.setAutoCompletionThreshold(0)
        self.setAutoCompletionSource(self.AcsAll)
        
        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)

    
        # not too small
        #self.setMinimumSize(500, 300)
        self.setMinimumHeight(32)
        
        self.SendScintilla(QsciScintilla.SCI_SETWRAPMODE, 2)
        self.SendScintilla(QsciScintilla.SCI_EMPTYUNDOBUFFER)
        
        ## Disable command key
        ctrl, shift = self.SCMOD_CTRL<<16, self.SCMOD_SHIFT<<16
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('L')+ ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('T')+ ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('D')+ ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('Z')+ ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('Y')+ ctrl)
        self.SendScintilla(QsciScintilla.SCI_CLEARCMDKEY, ord('L')+ ctrl+shift)
        
        ## New QShortcut = ctrl+space/ctrl+alt+space for Autocomplete
        self.newShortcutCS = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Space), self)
        self.newShortcutCS.activated.connect(self.autoComplete)
        self.connect(self, SIGNAL('userListActivated(int, const QString)'),
                     self.completion_list_selected)
                     
    def autoComplete(self):
        self.autoCompleteFromAll()
        
    def setLexers(self):
        self.lexer = QsciLexerPython()
        settings = QSettings()
        
        
        loadFont = settings.value("pythonConsole/fontfamilytext", "Monospace").toString()
        fontSize = settings.value("pythonConsole/fontsize", 10).toInt()[0]
        
        font = QFont(loadFont)
        font.setFixedPitch(True)
        font.setPointSize(fontSize)
        font.setStyleHint(QFont.TypeWriter)
        font.setStretch(QFont.SemiCondensed)
        font.setLetterSpacing(QFont.PercentageSpacing, 87.0)
        font.setBold(False)
        
        self.lexer.setDefaultFont(font)
        self.lexer.setColor(Qt.red, 1)
        self.lexer.setColor(Qt.darkGreen, 5)
        self.lexer.setColor(Qt.darkBlue, 15)
        self.lexer.setFont(font, 1)
        self.lexer.setFont(font, 3)
        self.lexer.setFont(font, 4)
        
        self.api = QsciAPIs(self.lexer)
        chekBoxAPI = settings.value( "pythonConsole/preloadAPI" ).toBool()
        if chekBoxAPI:
            self.api.loadPrepared( QgsApplication.pkgDataPath() + "/python/qsci_apis/pyqgis_master.pap" )
        else:
            apiPath = settings.value("pythonConsole/userAPI").toStringList()
            for i in range(0, len(apiPath)):
                self.api.load(QString(unicode(apiPath[i])))
            self.api.load("/usr/lib64/qt4/qsci/api/python/Python-2.7.api")
            self.api.prepare()
            self.lexer.setAPIs(self.api)

        self.setLexer(self.lexer)
            
    ## TODO: show completion list for file and directory
    
    def completion_list_selected(self, id, txt):
        if id == 1:
            txt = unicode(txt)
            # get current cursor position 
            line, pos = self.getCursorPosition()
            selCmdLength = self.text(line).length()
            # select typed text
            self.setSelection(line, 4, line, selCmdLength)
            self.removeSelectedText()
            self.insert(txt)

    def getText(self):
        """ Get the text as a unicode string. """
        value = self.getBytes().decode('utf-8')
        # print (value) printing can give an error because the console font
        # may not have all unicode characters
        return value

    def getBytes(self):
        """ Get the text as bytes (utf-8 encoded). This is how
        the data is stored internally. """
        len = self.SendScintilla(self.SCI_GETLENGTH)+1
        bb = QByteArray(len,'0')
        N = self.SendScintilla(self.SCI_GETTEXT, len, bb)
        return bytes(bb)[:-1]

    def getTextLength(self):
        return self.SendScintilla(QsciScintilla.SCI_GETLENGTH)

        
    def refreshLexerProperties(self):
        self.setLexers()
   

    #imitation plain text editor
    def toPlainText(self):
        return self.getText()
        
    def insertPlainText(self, text):
        self.insert(text)
        
    

    
    
