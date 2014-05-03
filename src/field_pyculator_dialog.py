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
from os import path

from PyQt4.QtGui import QMainWindow, QMessageBox, QListWidgetItem, QFileDialog
from PyQt4.QtCore import QObject, SIGNAL, Qt, QSettings
from qgis.core import QgsMapLayerRegistry, QgsFeatureRequest, QgsApplication

from ui_field_pyculator_dialog import Ui_FieldPyculatorDialog

from code_composer import CodeComposer


class FieldPyculatorDialog(QMainWindow):
    RESULT_VAR_NAME = 'value'

    _filter = 'Pyculator files (*.pycl);; Python files (*.py);; All files (*)'

    def __init__(self, iface):
        QMainWindow.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_FieldPyculatorDialog()
        self.ui.setupUi(self)

        active_layer = iface.activeLayer()
        self.iface = iface
        self.active_layer_id = active_layer.id()

        self._code_from_file = None
        self._is_dirty = False

        #restore settings
        rest_font_size = self.load_font_size(self.ui.txtFieldExp.get_font_size())
        self.ui.txtFieldExp.set_font_size(rest_font_size)
        self.ui.txtGlobalExp.set_font_size(rest_font_size)

        #INIT CONTROLS VALUES
        self.ui.lblLayerName.setText(active_layer.name())
        self.ui.cmbUpdateField.addItems(self.get_field_names(active_layer))
        self.ui.lstFields.addItems(self.get_field_names(active_layer))
        self.ui.txtGlobalExp.hide()
        self.ui.txtFieldExp.insertPlainText(self.RESULT_VAR_NAME + ' = ')

        #setup auto focus
        self.ui.lstFields.setFocusProxy(self.ui.txtFieldExp)
        self.ui.lstValues.setFocusProxy(self.ui.txtFieldExp)
        self.ui.btnId.setFocusProxy(self.ui.txtFieldExp)
        self.ui.btnGeom.setFocusProxy(self.ui.txtFieldExp)

        #setup icons
        self.init_toolbox()
        self.ui.btnRun.setIcon(QgsApplication.getThemeIcon('console/iconRunScriptConsole.png'))

        #SIGNALS
        QObject.connect(self.ui.lstFields, SIGNAL('currentItemChanged ( QListWidgetItem * , QListWidgetItem * )'),
                        self.update_field_sample_values)
        QObject.connect(self.ui.lstFields, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.add_field_to_expression)
        QObject.connect(self.ui.lstValues, SIGNAL('itemDoubleClicked(QListWidgetItem *)'), self.add_value_to_expression)
        QObject.connect(self.ui.btnGetAll, SIGNAL('clicked()'), self.update_field_all_values)
        QObject.connect(self.ui.btnId, SIGNAL('clicked()'), self.add_id_to_expression)
        QObject.connect(self.ui.btnGeom, SIGNAL('clicked()'), self.add_geom_to_expression)
        QObject.connect(self.ui.btnRun, SIGNAL('clicked()'), self.processing)
        QObject.connect(self.ui.txtFieldExp, SIGNAL('wheelEvent(QWheelEvent)'), self.editorWheelEvent)
        QObject.connect(self.ui.txtGlobalExp, SIGNAL('wheelEvent(QWheelEvent)'), self.editorWheelEvent)
        QObject.connect(self.ui.action_open, SIGNAL('triggered(bool)'), self.action_open_handler)
        QObject.connect(self.ui.action_save, SIGNAL('triggered(bool)'), self.action_save_handler)
        QObject.connect(self.ui.action_save_as, SIGNAL('triggered(bool)'), self.action_save_as_handler)
        QObject.connect(self.ui.txtGlobalExp, SIGNAL('textChanged()'), self.set_dirty_flag)
        QObject.connect(self.ui.txtFieldExp, SIGNAL('textChanged()'), self.set_dirty_flag)

    #-------------- GUI INIT

    def init_toolbox(self):
        icon = QgsApplication.getThemeIcon('console/iconOpenConsole.png') or QgsApplication.getThemeIcon('/mActionFileOpen.svg')
        self.ui.action_open.setIcon(icon)
        icon = QgsApplication.getThemeIcon('console/iconSaveConsole.png') or QgsApplication.getThemeIcon('/mActionFileSave.svg')
        self.ui.action_save.setIcon(icon)
        icon = QgsApplication.getThemeIcon('console/iconSaveAsConsole.png') or QgsApplication.getThemeIcon('/mActionFileSaveAs.svg')
        self.ui.action_save_as.setIcon(icon)
        self.update_btn_status()

    #---------------

    def editorWheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.delta()/100
            font_size = self.ui.txtFieldExp.get_font_size()
            new_font_size = font_size + delta
            if 5 < (new_font_size) < 20:
                self.ui.txtFieldExp.set_font_size(new_font_size)
                self.ui.txtGlobalExp.set_font_size(new_font_size)
                self.save_font_size(new_font_size)

    def save_font_size(self, new_font_size):
        sett = QSettings()
        sett.setValue('field_pyculator/font_size', new_font_size)

    def load_font_size(self, def_value):
        sett = QSettings()
        return sett.value('field_pyculator/font_size', def_value, type=int)

    def get_active_layer(self):
        #get and check layer
        active_layer = QgsMapLayerRegistry.instance().mapLayer(self.active_layer_id)
        if not active_layer:
            QMessageBox.critical(self, self.tr('FieldPyculator error'),
                                 self.tr('Layer was not found! It could be removed!'))
            return None
        else:
            return active_layer

    #--------------- Open/Save handlers -----------------------
    def action_open_handler(self):
        #TODO: Add _is_dirty flag check
        file_name = QFileDialog.getOpenFileName(self, self.tr('Open file with code...'), filter=self._filter)
        if file_name:
            if path.exists(file_name):
                with open(file_name) as content_file:
                    content = content_file.read()
                glob_code, local_code = CodeComposer.decompose(content)
                self.ui.txtGlobalExp.setText(glob_code)
                self.ui.txtFieldExp.setText(local_code)
                if glob_code:
                    self.ui.grpGlobalExpression.setChecked(True)
                else:
                    self.ui.grpGlobalExpression.setChecked(False)
                self._code_from_file = file_name
                self._is_dirty = False
                self.update_btn_status()
            else:
                QMessageBox.warning(self, self.tr('FieldPyculator warning'), self.tr('No such file: ') + file_name)

    def action_save_handler(self):
        if self._code_from_file and self._is_dirty:
            content = CodeComposer.compose(self.ui.txtGlobalExp.toPlainText(), self.ui.txtFieldExp.toPlainText())
            with open(self._code_from_file, 'w') as content_file:
                content_file.write(content)
            self._is_dirty = False
            self.update_btn_status()

    def action_save_as_handler(self):
        file_name = QFileDialog.getSaveFileName(self, self.tr('Save code to file...'), filter=self._filter)
        if file_name:
            content = CodeComposer.compose(self.ui.txtGlobalExp.toPlainText(), self.ui.txtFieldExp.toPlainText())
            with open(file_name, 'w') as content_file:
                content_file.write(content)
                self._code_from_file = file_name
                self._is_dirty = False
                self.update_btn_status()

    def update_btn_status(self):
        self.ui.action_save.setEnabled(self._code_from_file is not None and self._is_dirty)

    def set_dirty_flag(self):
        self._is_dirty = True
        self.update_btn_status()

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
            new_item = QListWidgetItem()
            if field_type in ('String', 'Date'):
                new_item.setText("'" + unicode(val) + "'")
                new_item.setData(Qt.UserRole, "u'" + unicode(val) + "'")
            else:
                #TODO: is too long!!!
                new_item.setText(unicode(val))
                new_item.setData(Qt.UserRole, unicode(val))
            self.ui.lstValues.addItem(new_item)
        self.unsetCursor()

    def add_field_to_expression(self, item):
        field_name = item.text()
        self.ui.txtFieldExp.insertPlainText(' <'+field_name+'> ')

    def add_value_to_expression(self, item):
        value = item.data(Qt.UserRole)
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
            QMessageBox.warning(self, self.tr('FieldPyculator warning'),
                                self.tr('Layer is not in edit mode! Please start editing the layer!'))
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
                QMessageBox.critical(self, self.tr('FieldPyculator code execute error'),
                                    (self.tr('Global code block can\'t be executed!\n{0}: {1}'))
                                    .format(unicode(sys.exc_info()[0].__name__), unicode(sys.exc_info()[1])))
                return

        code = unicode(self.ui.txtFieldExp.toPlainText())

        #TODO: check 'result' existing in text of code???!!!

        #replace all fields tags
        field_map = data_provider.fields()
        for field in field_map:
            field_name = unicode(field.name())
            replval = '__attr[\'' + field_name + '\']'
            code = code.replace('<' + field_name + '>', replval)

        #replace all special vars
        code = code.replace('$id', '__id')
        code = code.replace('$geom', '__geom')
        #is it need: $area, $length, $x, $y????

        #print code #debug

        #search needed vars (hmmm... comments?!)
        need_id = code.find('__id') != -1
        need_geom = code.find('__geom') != -1
        need_attrs = code.find('__attr') != -1

        #compile
        try:
            bytecode = compile(code, '<string>', 'exec')
        except:
            QMessageBox.critical(self, self.tr('FieldPyculator code execute error'),
                                (self.tr('Field code block can\'t be executed!\n{0}: {1}'))
                                .format(unicode(sys.exc_info()[0].__name__), unicode(sys.exc_info()[1])))
            return

        #get num of updating field
        field_num = data_provider.fieldNameIndex(self.ui.cmbUpdateField.currentText())

        #setup progress bar       
        self.ui.prgTotal.setValue(0)

        #run
        if not self.ui.chkOnlySelected.isChecked():
            features_for_update = data_provider.featureCount()
            request = QgsFeatureRequest()
            if not need_geom:
                request.setFlags(QgsFeatureRequest.NoGeometry)
            if need_attrs:
                request.setSubsetOfAttributes(data_provider.attributeIndexes())
            else:
                request.setSubsetOfAttributes([])
            features = active_layer.getFeatures(request)
        else:
            features_for_update = active_layer.selectedFeatureCount()
            features = active_layer.selectedFeatures()

        if features_for_update > 0:
            self.ui.prgTotal.setMaximum(features_for_update)

        for feat in features:
            feat_id = feat.id()
            #add needed vars
            if need_id:
                new_ns['__id'] = feat_id
            if need_geom:
                geom = feat.geometry()
                new_ns['__geom'] = geom
            if need_attrs:
                fields = feat.fields()
                attr = {}
                for a in fields:
                    attr[a.name()] = feat[a.name()]
                new_ns['__attr'] = attr

            #clear old result
            if self.RESULT_VAR_NAME in new_ns:
                del new_ns[self.RESULT_VAR_NAME]

            #exec
            try:
                exec bytecode in new_ns
            except:
                QMessageBox.critical(self, self.tr('FieldPyculator code execute error'),
                                     self.tr('Field code block can\'t be executed for feature {2}!\n{0}: {1}')
                                     .format(unicode(sys.exc_info()[0].__name__),
                                             unicode(sys.exc_info()[1]),
                                             unicode(feat_id)))
                return

            #check result
            if not self.RESULT_VAR_NAME in new_ns:
                QMessageBox.critical(self, self.tr('FieldPyculator code execute error'),
                        self.tr('Field code block does not return \'{0}\' variable! Please declare this variable in your code!')
                        .format(self.RESULT_VAR_NAME))
                return

            #try assign
            try:
                active_layer.changeAttributeValue(feat_id, field_num, new_ns[self.RESULT_VAR_NAME])
            except:
                QMessageBox.critical(self, self.tr('FieldPyculator code execute error'),
                                     self.tr('Result value can\'t be assigned to the feature {2}!\n{0}: {1}')
                                     .format(unicode(sys.exc_info()[0].__name__),
                                             unicode(sys.exc_info()[1]),
                                             unicode(feat_id)))
                return

            self.ui.prgTotal.setValue(self.ui.prgTotal.value()+1)

        stop = datetime.datetime.now()
        #workaround for python < 2.7
        td = stop - start
        if sys.version_info[:2] < (2, 7):
            total_sec = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
        else:
            total_sec = td.total_seconds()

        QMessageBox.information(self, self.tr('FieldPyculator code executed successfully'),
                                (self.tr('Updated {0} features for {1} seconds'))
                                .format(unicode(features_for_update), unicode(total_sec)))

    @staticmethod
    def get_field_names(layer):
        field_map = layer.dataProvider().fields()
        field_list = []
        for field in field_map:
            field_list.append(unicode(field.name()))
        return field_list  # sorted( field_list, cmp=locale.strcoll )
