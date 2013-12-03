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
import sys
import datetime
#import locale

from PyQt4.QtGui import QDialog, QMessageBox, QFont
from PyQt4.QtCore import QObject, SIGNAL, Qt
from qgis.core import QgsFeature, QgsRectangle, QgsMapLayerRegistry
 
from ui_field_pyculator_dialog import Ui_FieldPyculatorDialog
from syntax_highlighter import PythonHighlighter


class FieldPyculatorDialog(QDialog):
    RESULT_VAR_NAME = 'value'

    def __init__(self, iface):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_FieldPyculatorDialog()
        self.ui.setupUi(self)

        active_layer = iface.activeLayer()
        self.iface = iface
        self.active_layer_id = active_layer.id()
        #self.data_provider = self.active_layer.dataProvider()

        #INIT CONTROLS VALUES
        self.ui.lblLayerName.setText(active_layer.name())
        self.ui.cmbUpdateField.addItems(self.get_field_names(active_layer))
        self.ui.lstFields.addItems(self.get_field_names(active_layer))
        self.ui.txtGlobalExp.hide()
        self.ui.txtFieldExp.insertPlainText(self.RESULT_VAR_NAME + ' = ')          

        #setup actions
        self.ui.btnToggleEditing.setDefaultAction(self.iface.actionToggleEditing())

        #setup syntax highlight
        self.highlight_field = PythonHighlighter(self.ui.txtFieldExp.document())
        self.highlight_global = PythonHighlighter(self.ui.txtGlobalExp.document())

        #setup auto focus
        self.ui.lstFields.setFocusProxy(self.ui.txtFieldExp)
        self.ui.lstValues.setFocusProxy(self.ui.txtFieldExp)
        self.ui.btnId.setFocusProxy(self.ui.txtFieldExp)
        self.ui.btnGeom.setFocusProxy(self.ui.txtFieldExp)

        #SIGNALS
        QObject.connect(self.ui.lstFields, SIGNAL("currentItemChanged ( QListWidgetItem * , QListWidgetItem * )"), self.update_field_sample_values)
        QObject.connect(self.ui.lstFields, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.add_field_to_expression)
        QObject.connect(self.ui.lstValues, SIGNAL("itemDoubleClicked(QListWidgetItem *)"), self.add_value_to_expression)
        QObject.connect(self.ui.btnGetAll, SIGNAL(" clicked()"), self.update_field_all_values)
        QObject.connect(self.ui.btnId, SIGNAL("clicked()"), self.add_id_to_expression)
        QObject.connect(self.ui.btnGeom, SIGNAL(" clicked()"), self.add_geom_to_expression)
        QObject.connect(self.ui.btnRun, SIGNAL("clicked()"), self.processing)
        # TODO: add handler for tab replacing in txtFieldExp and txtGlobalExp
        # TODO: add handler for ctrl + scroll as font size selector in txtFieldExp and txtGlobalExp
        #QObject.connect(self.ui.txtFieldExp, SIGNAL("wheelEvent( QWheelEvent * )"), self.wheelEvent2)

    #---------------
    def wheelEvent(self, event):
        delta = event.delta()/100
        ctrl = event.modifiers() == Qt.ControlModifier
        if ctrl:
            font = self.ui.txtFieldExp.font()
            if 5 < (font.pointSize() + delta) < 20:
                new_font = QFont(font.family(), font.pointSize() + delta)
                self.ui.txtFieldExp.setFont(new_font)
                self.ui.txtGlobalExp.setFont(new_font)

    def get_active_layer(self):
        #get and check layer
        active_layer = QgsMapLayerRegistry.instance().mapLayer(self.active_layer_id)
        if not active_layer:
            QMessageBox.critical(self, self.tr("FieldPyculator error"),
                                 self.tr("Layer was not found! It could be removed!"))
            return None
        else:
            return active_layer

    #--------------- Fields handlers ---------------------------
    def update_field_sample_values(self, new_item, old_item):
        field_name = new_item.text()
        self.update_field_values(field_name, 25)

    def update_field_all_values(self):
        if self.ui.lstFields.currentItem():
            field_name = self.ui.lstFields.currentItem().text()
            self.update_field_values(field_name)

    def update_field_values(self, field_name, limit=-1):
        active_layer = self.get_active_layer()
        if not active_layer:
            return
        data_provider = active_layer.dataProvider()

        self.setCursor(Qt.WaitCursor)
        field_ind = data_provider.fieldNameIndex(field_name)
        field_type = data_provider.fields()[field_ind].typeName()
        
        self.ui.lstValues.clear()
        values = data_provider.uniqueValues(field_ind, limit)
        for val in values:
            if field_type == 'String':
                self.ui.lstValues.addItem("'" + unicode(val.toString()) + "'")
            else:
                self.ui.lstValues.addItem(unicode(val.toString()))
        self.unsetCursor()

    def add_field_to_expression(self, item):
        field_name = item.text()
        self.ui.txtFieldExp.insertPlainText(' <'+field_name+'> ')

    def add_value_to_expression(self, item):
        value = item.text()
        self.ui.txtFieldExp.insertPlainText(' '+value+' ')
    
    #------------- Vars handlers  ---------------------------------
    def add_id_to_expression(self):
        self.ui.txtFieldExp.insertPlainText(' $id ')
        
    def add_geom_to_expression(self):
        self.ui.txtFieldExp.insertPlainText(' $geom ')
    #--------------------------------------------------------------

    def processing(self):
        #get and check layer
        active_layer = self.get_active_layer()
        if not active_layer:
            # may be need to disable form?
            return
        data_provider = active_layer.dataProvider()

        #check edit mode
        if not active_layer.isEditable():
            QMessageBox.warning(self, self.tr("FieldPyculator warning"),
                                 self.tr("Layer is not in edit mode! Please start editing the layer!"))
            return    
        
        start = datetime.datetime.now()
        new_ns = {}
        
        #run global code
        if self.ui.grpGlobalExpression.isChecked():
            try:
                code = unicode(self.ui.txtGlobalExp.toPlainText())
                bytecode = compile(code, '<string>', 'exec')
                exec bytecode in new_ns
            except:
                QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            (self.tr("Global code block can't be executed!\n%1: %2"))
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1])))
                return

        code = unicode(self.ui.txtFieldExp.toPlainText())
        
        #TODO: check 'result' existing in text of code???!!!
            
        #replace all fields tags
        field_map = data_provider.fields()
        for num, field in field_map.iteritems():
            field_name = unicode(field.name())
            replval = '__attr[' + str(num) + ']'
            code = code.replace("<"+field_name+">", replval)

        #replace all special vars
        code = code.replace('$id', '__id')
        code = code.replace('$geom', '__geom')
        #is it need: $area, $length, $x, $y????

        #print code #debug

        #search needed vars (hmmm... comments?!)
        need_id = code.find("__id") != -1
        need_geom = code.find("__geom") != -1
        need_attrs = code.find("__attr") != -1

        #compile
        try:
            bytecode = compile(code, '<string>', 'exec')
        except:
            QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                                 self.tr("Field code block can't be executed!\n%1: %2")
                                 .arg(unicode(sys.exc_info()[0].__name__))
                                 .arg(unicode(sys.exc_info()[1])))
            return

        #get num of updating field
        field_num = data_provider.fieldNameIndex(self.ui.cmbUpdateField.currentText())
        
        #setup progress bar       
        self.ui.prgTotal.setValue(0)
        
        #run
        if not self.ui.chkOnlySelected.isChecked():
            #select all features
            features_for_update = data_provider.featureCount()
            if features_for_update > 0:
                self.ui.prgTotal.setMaximum(features_for_update)
            
            feat = QgsFeature()
            if need_attrs:
                attr_ind = data_provider.attributeIndexes()
            else:
                attr_ind = []
            data_provider.select(attr_ind, QgsRectangle(), need_geom)
            
            while data_provider.nextFeature(feat):
                feat_id = feat.id()
                
                #add needed vars
                if need_id:
                    new_ns['__id'] = feat_id

                if need_geom:
                    geom = feat.geometry()
                    new_ns['__geom'] = geom

                if need_attrs:
                    attr_map = feat.attributeMap()
                    attr = []
                    for num, a in attr_map.iteritems():
                        attr.append(self.qvar2py(a))
                    new_ns['__attr'] = attr
                
                #clear old result
                if self.RESULT_VAR_NAME in new_ns:
                    del new_ns[self.RESULT_VAR_NAME]
                
                #exec
                try:
                    exec bytecode in new_ns
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block can't be executed for feature %3!\n%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return
                
                #check result
                if not self.RESULT_VAR_NAME in new_ns:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block does not return '%1' variable! Please declare this variable in your code!")
                            .arg(self.RESULT_VAR_NAME))
                    return
                
                #try assign
                try:
                    active_layer.changeAttributeValue(feat_id, field_num, new_ns[self.RESULT_VAR_NAME])
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Result value can't be assigned to the feature %3!\n%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return

                self.ui.prgTotal.setValue(self.ui.prgTotal.value()+1)

        else:
            #only selected (TODO: NEED REFACTORING - copy-past!!!)
            features_for_update = active_layer.selectedFeatureCount()
            if features_for_update > 0:
                self.ui.prgTotal.setMaximum(features_for_update)

            for feat in active_layer.selectedFeatures():
                feat_id = feat.id()

                #add needed vars
                if need_id:
                    new_ns['__id'] = feat_id

                if need_geom:
                    geom = feat.geometry()
                    new_ns['__geom'] = geom

                if need_attrs:
                    attr_map = feat.attributeMap()
                    attr = []
                    for num, a in attr_map.iteritems():
                        attr.append(self.qvar2py(a))
                    new_ns['__attr'] = attr

                #clear old result
                if new_ns.has_key(self.RESULT_VAR_NAME):
                    del new_ns[self.RESULT_VAR_NAME]

                #exec
                try:
                    exec bytecode in new_ns
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block can't be executed for feature %3!\n%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return

                #check result
                if not self.RESULT_VAR_NAME in new_ns:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block does not return '%1' variable! Please declare this variable in your code!")
                            .arg(self.RESULT_VAR_NAME))
                    return

                #try assign
                try:
                    active_layer.changeAttributeValue(feat_id, field_num, new_ns[self.RESULT_VAR_NAME])
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Result value can't be assigned to the feature %3!\n%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return

                self.ui.prgTotal.setValue(self.ui.prgTotal.value()+1)

        stop = datetime.datetime.now()

        #workaround for python < 2.7
        td = stop - start
        if sys.version_info[:2] < (2, 7):
            total_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        else:
            total_sec = td.total_seconds()

        QMessageBox.information(self, self.tr("FieldPyculator code executed successfully"),
                         self.tr("Updated %1 features for %2 seconds")
                            .arg(unicode(features_for_update))
                            .arg(unicode(total_sec))
                         )

    @staticmethod
    def qvar2py(qv):
        if qv.type() == 2:
            return qv.toInt()[0]
        if qv.type() == 10:
            return unicode(qv.toString())
        if qv.type() == 6:
            return qv.toDouble()[0]
        return None

    @staticmethod
    def get_field_names(layer):
        field_map = layer.dataProvider().fields()
        field_list = []
        for num, field in field_map.iteritems():
            field_list.append(unicode(field.name()))
        return field_list  # sorted( field_list, cmp=locale.strcoll )
