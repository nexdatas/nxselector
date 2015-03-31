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
## \file EdDataDlg.py
# editable data dialog

"""  editable data dialog """

import json

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

#from .ui.ui_eddatadlg import Ui_EdDataDlg

import logging
logger = logging.getLogger(__name__)


## main window class
@UILoadable(with_ui='ui')
class EdDataDlg(Qt.QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(EdDataDlg, self).__init__(parent)
        self.loadUi()
        self.simple = False
        self.name = ''
        self.value = ''
        self.isString = True
        self.headers = []
        self.available_names = None

    def setText(self, text):
        if str(text) not in self.available_names:
            self.ui.nameComboBox.addItem(str(text))
        ind = self.ui.nameComboBox.findText(str(text))
        self.ui.nameComboBox.setCurrentIndex(ind)
        self.ui.nameComboBox.setEditText(str(text))


    def createGUI(self):
        if self.available_names:
            self.ui.nameComboBox.clear()
            for an in self.available_names:
                self.ui.nameComboBox.addItem(str(an))
        if len(self.headers) > 0:
            self.ui.nameLabel.setText(str(self.headers[0]))
            if len(self.headers) > 1:
                self.ui.valueLabel.setText(str(self.headers[1]))
        if self.simple:
            self.ui.stringCheckBox.hide()
        else:
            self.isString = isinstance(self.value,
                                       (str, unicode, Qt.QString))
        self.ui.stringCheckBox.setChecked(self.isString)
        self.setText(Qt.QString(self.name))
        self.ui.valueTextEdit.setText(Qt.QString(str(self.value)))

#        if self.available_names:
#            completer = Qt.QCompleter(self.available_names, self)
#            self.ui.nameLineEdit.setCompleter(completer)

        self.connect(self.ui.buttonBox, Qt.SIGNAL("accepted()"),
                     self.accept)
        self.connect(self.ui.buttonBox, Qt.SIGNAL("rejected()"),
                     self.reject)

    def accept(self):
        self.name = unicode(self.ui.nameComboBox.currentText())
        self.isString = self.ui.stringCheckBox.isChecked()
        self.value = unicode(self.ui.valueTextEdit.toPlainText())
        if not self.isString and not self.simple:
            try:
                self.value = json.loads(self.value)
            except:
                pass

        if not self.name:
            Qt.QMessageBox.warning(self, "Wrong Data", "Empty data name")
            self.ui.nameComboBox.setFocus()
            return
        Qt.QDialog.accept(self)
