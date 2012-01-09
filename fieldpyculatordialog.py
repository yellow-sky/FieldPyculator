"""
/***************************************************************************
 FieldPyculatorPluginDialog
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
import sys
import datetime
#import locale

from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QObject, SIGNAL, Qt
from qgis.core import QgsFeature, QgsRectangle
 
from ui_fieldpyculatordialog import Ui_FieldPyculatorDialog
from syntax_highlighter import PythonHighlighter

class FieldPyculatorDialog(QDialog):
    RESULT_VAR_NAME = 'result'
        
    def __init__(self, iface):
        QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_FieldPyculatorDialog()
        self.ui.setupUi(self)
        
        self.iface = iface
        self.active_layer = self.iface.activeLayer()
        self.data_provider =  self.active_layer.dataProvider()
        
        #INIT CONTROLS VALUES
        self.ui.lblLayerName.setText(self.active_layer.name())
        self.ui.cmbUpdateField.addItems(self.GetFieldNames(self.active_layer))
        self.ui.lstFields.addItems(self.GetFieldNames(self.active_layer))
        self.ui.txtFieldExp.setPlainText(self.RESULT_VAR_NAME + ' = ')                                        
        
        #setup syntax highlight
        self.highlight_field = PythonHighlighter(self.ui.txtFieldExp.document())
        self.highlight_global = PythonHighlighter(self.ui.txtGlobalExp.document())
        
        #setup auto focus
        self.ui.lstFields.setFocusProxy(self.ui.txtFieldExp)
        self.ui.lstValues.setFocusProxy(self.ui.txtFieldExp)

        #SIGNALS
        QObject.connect( self.ui.lstFields, SIGNAL( "currentItemChanged ( QListWidgetItem * , QListWidgetItem * )" ), self.UpdateFieldSampleValues)
        QObject.connect( self.ui.lstFields, SIGNAL( "itemDoubleClicked(QListWidgetItem *)" ), self.AddFieldToExpression)
        QObject.connect( self.ui.lstValues, SIGNAL( "itemDoubleClicked(QListWidgetItem *)" ), self.AddValueToExpression)
        QObject.connect( self.ui.btnGetAll, SIGNAL( " clicked()" ), self.UpdateFieldAllValues)
        QObject.connect( self.ui.btnRun, SIGNAL( " clicked()" ), self.Processing)
        
        # TODO: add handler for tab replacing in txtFieldExp and txtGlobalExp
        # TODO: add handler for ctrl + scroll as font size selector in txtFieldExp and txtGlobalExp
        
    
    #--------------- Fields handlers ---------------------------
        
    def UpdateFieldSampleValues(self, new_item, old_item):
        field_name = new_item.text()
        self.UpdateFieldValues(field_name, 25)
            
    def UpdateFieldAllValues(self):
        field_name = self.ui.lstFields.currentItem().text()
        self.UpdateFieldValues(field_name)
                
    def UpdateFieldValues(self, field_name, limit = -1):
        self.setCursor(Qt.WaitCursor)
        field_ind = self.data_provider.fieldNameIndex(field_name)
        field_type = self.data_provider.fields()[field_ind].typeName()
        
        self.ui.lstValues.clear()
        values = self.data_provider.uniqueValues(field_ind, limit)
        for val in values:
            if field_type == 'String':
                self.ui.lstValues.addItem("'" + unicode(val.toString()) + "'")
            else:
                self.ui.lstValues.addItem(unicode(val.toString()))
        self.unsetCursor()

    def AddFieldToExpression(self, item):
        field_name = item.text()
        self.ui.txtFieldExp.insertPlainText('<'+field_name+'>')
        
    def AddValueToExpression(self, item):
        value = item.text()
        self.ui.txtFieldExp.insertPlainText(value)
    
    #---------------------------------------------------------------
    
    def Processing(self):
        #check edit mode
        if not self.active_layer.isEditable():
            QMessageBox.warning(self, self.tr("FieldPyculator warning"),
                                 self.tr("Layer is not in edit mode! Please start editing the layer!"))
            return    
        
        start =  datetime.datetime.now()
        new_ns = {}
        
        #run global code
        if self.ui.grpAdvMode.isChecked():
            try:
                code = unicode(self.ui.txtGlobalExp.toPlainText())
                bytecode = compile(code, '<string>', 'exec')
                exec bytecode in new_ns
            except:
                QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Global code block can't be executed!\r%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1])))
                return
            
        
        code = unicode(self.ui.txtFieldExp.toPlainText())
        
        #TODO: check 'result' existing in text of code???!!!
            
        #replace all fields tags
        field_map = self.data_provider.fields()
        for num, field in field_map.iteritems():
            field_name = unicode(field.name())
            replval = '__attr[' + str(num) + ']'
            code = code.replace("<"+field_name+">",replval)
        
        #replace all special vars
        code = code.replace('$id','__id')
        code = code.replace('$geom','__geom')
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
                                 self.tr("Field code block can't be executed!\r%1: %2")
                                 .arg(unicode(sys.exc_info()[0].__name__))
                                 .arg(unicode(sys.exc_info()[1])))
            return
        
        
        #get num of updating field
        field_num = self.data_provider.fieldNameIndex(self.ui.cmbUpdateField.currentText())
        
        #setup progress bar       
        self.ui.prgTotal.setValue(0)
        
        #run
        if not self.ui.chkOnlySelected.isChecked():
            
            #select all features
            self.ui.prgTotal.setMaximum(self.data_provider.featureCount())
            
            feat = QgsFeature()
            if need_attrs:
                attr_ind = self.data_provider.attributeIndexes()
            else:
                attr_ind = []
            self.data_provider.select(attr_ind, QgsRectangle(), need_geom)
            
            while self.data_provider.nextFeature( feat ):
                feat_id = feat.id()
                
                #add needed vars
                if need_id:
                    new_ns['__id'] = feat_id

                if need_geom:
                    geom = feat.geometry()
                    new_ns['__geom'] = geom

                if need_attrs:
                    attrMap = feat.attributeMap()
                    attr = []
                    for num,a in attrMap.iteritems():
                        attr.append(self.Qvar2py(a))
                    new_ns['__attr'] = attr
                
                #clear old result
                if new_ns.has_key(self.RESULT_VAR_NAME):
                    del new_ns[self.RESULT_VAR_NAME]
                
                #exec
                try:
                    exec bytecode in new_ns
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block can't be executed for feature %3!\r%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return
                
                #check result
                if not new_ns.has_key(self.RESULT_VAR_NAME):
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block does not return '%1' variable! Please declare this variable in your code!")
                            .arg(self.RESULT_VAR_NAME))
                    return
                
                #try assign
                try:
                    self.active_layer.changeAttributeValue(feat_id, field_num, new_ns[self.RESULT_VAR_NAME])
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Result value can't be assigned to the feature %3!\r%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return
                
                self.ui.prgTotal.setValue(self.ui.prgTotal.value()+1)
            
        else:
            #only selected (TODO: NEED REFACTORING - copy-past!!!)
            self.ui.prgTotal.setMaximum(self.active_layer.selectedFeatureCount() )
            
            for feat in self.active_layer.selectedFeatures():
                feat_id = feat.id()
                
                #add needed vars
                if need_id:
                    new_ns['__id'] = feat_id

                if need_geom:
                    geom = feat.geometry()
                    new_ns['__geom'] = geom

                if need_attrs:
                    attrMap = feat.attributeMap()
                    attr = []
                    for num,a in attrMap.iteritems():
                        attr.append(self.Qvar2py(a))
                    new_ns['__attr'] = attr
                
                #clear old result
                if new_ns.has_key(self.RESULT_VAR_NAME):
                    del new_ns[self.RESULT_VAR_NAME]
                
                #exec
                try:
                    exec bytecode in new_ns
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block can't be executed for feature %3!\r%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return
                
                #check result
                if not new_ns.has_key(self.RESULT_VAR_NAME):
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Field code block does not return '%1' variable! Please declare this variable in your code!")
                            .arg(self.RESULT_VAR_NAME))
                    return
                
                #try assign
                try:
                    self.active_layer.changeAttributeValue(feat_id, field_num, new_ns[self.RESULT_VAR_NAME])
                except:
                    QMessageBox.critical(self, self.tr("FieldPyculator code execute error"),
                            self.tr("Result value can't be assigned to the feature %3!\r%1: %2")
                            .arg(unicode(sys.exc_info()[0].__name__))
                            .arg(unicode(sys.exc_info()[1]))
                            .arg(unicode(feat_id)))
                    return
                
                self.ui.prgTotal.setValue(self.ui.prgTotal.value()+1)
                
                
        
        stop = datetime.datetime.now()
        QMessageBox.information(self, self.tr("FieldPyculator code executed successfully"),
                         self.tr("Updated %1 features for %2 seconds")
                            .arg(unicode(self.ui.prgTotal.maximum()))
                            .arg(unicode((stop-start).total_seconds()))
                         )
    
    
    
    def Qvar2py(self,qv):
        if qv.type() == 2:
            return qv.toInt()[0]
        if qv.type() == 10:
            return unicode(qv.toString())
        if qv.type() == 6:
            return qv.toDouble()[0]
        return None
    
    
    def GetFieldNames(self, layer):
        field_map = layer.dataProvider().fields()
        field_list = []
        for num, field in field_map.iteritems():
            field_list.append( unicode( field.name() ) )
        return field_list # sorted( field_list, cmp=locale.strcoll )  
        