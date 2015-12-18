#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package nxselector nexdatas
## \file LDataDlg.py
# editable data dialog

"""  editable data dialog """

import json

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .MessageBox import MessageBox


from taurus.qt.qtgui.util.ui import UILoadable
#from .ui.ui_ldatadlg import Ui_LDataDlg

import logging
logger = logging.getLogger(__name__)


## main window class
@UILoadable(with_ui='ui')
class LDataDlg(Qt.QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(LDataDlg, self).__init__(parent)
        self.loadUi()
        self.label = ''
        self.path = ''
        self.shape = None
        self.dtype = ''
        self.link = None
        self.available_names = None
        self.special = ["shape", "data_type", "nexus_path", "link"]
        self.variables = {}
        self.names = {}
        self.widgets = {}

    @classmethod
    def __linkText(cls, value):
        if isinstance(value, bool):
            if value is True:
                return "True"
            if value is False:
                return "False"
        return "Default"

    def createGUI(self):
        self.ui.labelLineEdit.setText(Qt.QString(str(self.label)))
        self.ui.pathLineEdit.setText(Qt.QString(str(self.path)))
        if self.shape is None:
            shape = ''
        else:
            shape = self.shape
        self.ui.shapeLineEdit.setText(
            Qt.QString(str(shape)))
        self.ui.typeLineEdit.setText(Qt.QString(str(self.dtype)))

        cid = self.ui.linkComboBox.findText(
            Qt.QString(self.__linkText(self.link)))
        if cid < 0:
            cid = 0
        self.ui.linkComboBox.setCurrentIndex(cid)

        if self.available_names:
            completer = Qt.QCompleter(self.available_names, self)
            self.ui.labelLineEdit.setCompleter(completer)
        if self.variables:
            self.addGrid()

    def addGrid(self):
        index = 0
        for nm, val in self.variables.items():
            self.names[nm] = Qt.QLabel(self.ui.varFrame)
            self.names[nm].setText(Qt.QString(str(nm)))
            self.ui.varGridLayout.addWidget(self.names[nm], index, 0, 1, 1)
            self.widgets[nm] = Qt.QLineEdit(self.ui.varFrame)
            if val is not None:
                self.widgets[nm].setText(Qt.QString(str(val)))
            self.ui.varGridLayout.addWidget(self.widgets[nm], index, 1, 1, 1)
            index += 1

    def addVariables(self, variables):
        leftchannels = False
        for sp in self.special:
            if sp in variables.keys():
                leftchannels = True
        if not leftchannels:
            self.ui.channelFrame.hide()
        for vr, val in variables.items():
            if vr not in self.special:
                self.variables[vr] = val

    def accept(self):
        link = str(self.ui.linkComboBox.currentText())
        if link == "True":
            self.link = True
        elif link == "False":
            self.link = False
        else:
            self.link = None

        self.label = unicode(self.ui.labelLineEdit.text())
        self.path = unicode(self.ui.pathLineEdit.text())
        self.dtype = unicode(self.ui.typeLineEdit.text())
        tshape = unicode(self.ui.shapeLineEdit.text()).replace("None", "null")
        try:
            if not tshape:
                self.shape = None
            else:
                shape = json.loads(tshape)
                if not isinstance(shape, list):
                    raise Exception("shape is not a list")
                self.shape = shape
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Wrong structure of Shape")
            MessageBox.warning(
                self,
                "NXSSelector: Wrong Data",
                text, str(value))
            self.ui.shapeLineEdit.setFocus()
            return

        for nm, wg in self.widgets.items():
            self.variables[nm] = unicode(wg.text()) or None

        if not self.label:
            Qt.QMessageBox.warning(self, "Wrong Data", "Empty data label")
            self.ui.labelLineEdit.setFocus()
            return

        Qt.QDialog.accept(self)
