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

try:
    from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
    from scintilla_python_edit_box import ScintillaPythonEditBox
    PythonEditBox = ScintillaPythonEditBox
except:
    from simple_python_edit_box import SimplePythonEditBox
    PythonEditBox = SimplePythonEditBox