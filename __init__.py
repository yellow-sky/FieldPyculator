"""
/***************************************************************************
 FieldPyculatorPlugin
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
 This script initializes the plugin, making it known to QGIS.
"""
def name():
    return "Simple field python calculator"
def description():
    return "Use python for "
def version():
    return "Version 0.2.0"
def icon():
    return "icon.png"
def qgisMinimumVersion():
    return "1.7"
def classFactory(iface):
    # load FieldPyculatorPlugin class from file FieldPyculatorPlugin
    from fieldpyculatorplugin import FieldPyculatorPlugin
    return FieldPyculatorPlugin(iface)
