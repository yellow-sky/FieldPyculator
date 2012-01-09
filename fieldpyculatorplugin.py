"""
/***************************************************************************
 FieldPyculatorPlugin
                                 A QGIS plugin
 Use python for 
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QObject, QCoreApplication, SIGNAL
from PyQt4.QtGui import QIcon, QAction
from qgis.core import QgsMapLayer 

# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from fieldpyculatordialog import FieldPyculatorDialog

class FieldPyculatorPlugin:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/fieldpyculatorplugin/icon.png"), \
            QCoreApplication.translate("FieldPyculator","Field pyculator"), self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(QCoreApplication.translate("FieldPyculator", "&Field pyculator"), self.action)
        
        
        # track layer changing
        QObject.connect(self.iface, SIGNAL("currentLayerChanged( QgsMapLayer* )"), self.layerChanged)
      
        # check already selected layers
        self.layerChanged()
        

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(QCoreApplication.translate("FieldPyculator", "&Field pyculator"),self.action)
        self.iface.removeToolBarIcon(self.action)
        
        # remove layer changing tracking
        QObject.disconnect(self.iface, SIGNAL("currentLayerChanged( QgsMapLayer* )"), self.layerChanged)



    def layerChanged(self):
        layer = self.iface.activeLayer()

        if (layer is None) or (layer.type() != QgsMapLayer.VectorLayer):
            self.action.setEnabled(False)
        else:
            self.action.setEnabled(True)
            

    # run method that performs all the real work
    def run(self):

        # create and show the dialog
        dlg = FieldPyculatorDialog(self.iface)
        # show the dialog
        dlg.show()
        result = dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code
            pass
