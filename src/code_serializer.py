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
    _header = '#<QGIS FieldPyculator file>'
    _global_separator = '# <Global code>'
    _local_separator = '# <Local code>'

    @staticmethod
    def compose(self, global_code, local_code):
        content = '{h}{sep}{gs}{gc}{sep}{ls}{lc}'.format(h=self._header,
                                                         gs=self._global_separator,
                                                         gc=global_code,
                                                         ls=self._local_separator,
                                                         lc=local_code,
                                                         sep=self._linesep*3)
        return content

    @staticmethod
    def decompose(self, content):
        global_code = ''
        local_code = ''

        if self._header not in content or self._global_separator not in content or self._local_separator not in content:
            QgsMessageLog.logMessage('FieldPyculator: File does not look like a FieldPyculator code! Try to load as plain code...', QgsMessageLog.WARNING)
        content.replace(self._header, '')

        blocks = str.split(self._local_separator, maxsplit=1)

        if len(blocks) == 1:
            local_code = blocks[0]
        else:
            global_code = blocks[0]
            local_code = blocks[1]

        global_code.replace(self._global_separator, '')
        local_code.replace(self._local_separator, '')  # overhead

        return global_code, local_code