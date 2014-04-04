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
from qgis.core import QgsMessageLog
#from logging import warning


class CodeComposer():
    """
    Class for code composition and serializing/deserializing
    """

    _linesep = '\n'
    _header = '# <QGIS FieldPyculator file>'
    _global_separator = '# <Global code>'
    _local_separator = '# <Local code>'

    @staticmethod
    def compose(global_code, local_code):
        content = '{h}{sep}{gs}{nl}{gc}{sep}{ls}{nl}{lc}'.format(h=CodeComposer._header,
                                                         gs=CodeComposer._global_separator,
                                                         gc=global_code,
                                                         ls=CodeComposer._local_separator,
                                                         lc=local_code,
                                                         sep=CodeComposer._linesep*3,
                                                         nl=CodeComposer._linesep)
        return content

    @staticmethod
    def decompose(content):
        global_code = ''
        local_code = ''

        if CodeComposer._header not in content or CodeComposer._global_separator not in content or CodeComposer._local_separator not in content:
            QgsMessageLog.logMessage('FieldPyculator: File does not look like a FieldPyculator code! Try to load as plain code...', level=QgsMessageLog.WARNING)
        content = content.replace(CodeComposer._header, '')

        blocks = content.split(CodeComposer._local_separator, 1)

        if len(blocks) == 1:
            local_code = blocks[0]
        else:
            global_code = blocks[0]
            local_code = blocks[1]

        global_code = global_code.replace(CodeComposer._global_separator, '').strip()
        local_code =  local_code.replace(CodeComposer._local_separator, '').strip()  # overhead

        return global_code, local_code