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
from os import path
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, SIGNAL, QCoreApplication,  QSettings, QLocale, QTranslator
from PyQt4.QtGui import QIcon, QAction
from qgis.core import QgsMapLayer
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from field_pyculator_dialog import FieldPyculatorDialog

currentPath = path.abspath(path.dirname(__file__))


class FieldPyculatorPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # i18n support
        override_locale = QSettings().value('locale/overrideFlag', False, type=bool)
        if not override_locale:
            locale_full_name = QLocale.system().name()
        else:
            locale_full_name = QSettings().value('locale/userLocale', '', type=unicode)

        self.locale_path = currentPath + '/i18n/field_pyculator_' + locale_full_name[0:2] + '.qm'
        if path.exists(self.locale_path):
            self.translator = QTranslator()
            self.translator.load(self.locale_path)
            QCoreApplication.installTranslator(self.translator)

    def tr(self, text):
        return QCoreApplication.translate('FieldPyculatorPlugin', text)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(':/plugins/fieldpyculatorplugin/icon.png'),
                              self.tr('FieldPyculator'), self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL('triggered()'), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr('&FieldPyculator'), self.action)

        # track layer changing
        QObject.connect(self.iface, SIGNAL('currentLayerChanged( QgsMapLayer* )'), self.layer_changed)

        # check already selected layers
        self.layer_changed()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(self.tr('&FieldPyculator'), self.action)
        self.iface.removeToolBarIcon(self.action)
        # Remove layer changing tracking
        QObject.disconnect(self.iface, SIGNAL('currentLayerChanged( QgsMapLayer* )'), self.layer_changed)

    def layer_changed(self):
        layer = self.iface.activeLayer()
        if (layer is None) or (layer.type() != QgsMapLayer.VectorLayer):
            self.action.setEnabled(False)
        else:
            self.action.setEnabled(True)

    def run(self):
        # create and show the dialog
        dlg = FieldPyculatorDialog(self.iface)
        # show the dialog
        dlg.show()
        result = dlg.exec_()
