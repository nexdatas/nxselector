#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# editable data dialog

"""  editable data dialog """

import json
import sys

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


if sys.version_info > (3,):
    unicode = str


@UILoadable(with_ui='ui')
class EdDataDlg(Qt.QDialog):
    """ editable data dialog
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        #: (:obj:`bool`) dialog simple version
        self.simple = False
        #: (:obj:`str`) data name
        self.name = ''
        #: (:obj:`str` or `any`) data values
        self.value = ''
        #: (:obj:`bool`) if value is string
        self.isString = True
        #: (:obj:`list` <:obj:`str`> ) table headers
        self.headers = []
        #: (:obj:`list` <:obj:`str`> ) available data names
        self.available_names = None

    def setText(self, text):
        """ sets text into name QComboBox

        :param text: data name
        :type text: :obj:`str`
        """
        if str(text) not in self.available_names:
            self.ui.nameComboBox.addItem(str(text))
        ind = self.ui.nameComboBox.findText(str(text))
        self.ui.nameComboBox.setCurrentIndex(ind)
        self.ui.nameComboBox.setEditText(str(text))

    def createGUI(self):
        """ creates widget GUI
        """
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
                                       (str, unicode))
        self.ui.stringCheckBox.setChecked(self.isString)
        self.setText(str(self.name))
        self.ui.valueTextEdit.setText(str(str(self.value)))

#        if self.available_names:
#            completer = Qt.QCompleter(self.available_names, self)
#            self.ui.nameLineEdit.setCompleter(completer)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    @Qt.pyqtSlot()
    def accept(self):
        """ checks if dialog is filled in correctly and accepts it
        """
        self.name = unicode(self.ui.nameComboBox.currentText())
        self.isString = self.ui.stringCheckBox.isChecked()
        self.value = unicode(self.ui.valueTextEdit.toPlainText())
        if not self.isString and not self.simple:
            try:
                self.value = json.loads(self.value)
            except Exception:
                pass

        if not self.name:
            Qt.QMessageBox.warning(self, "Wrong Data", "Empty data name")
            self.ui.nameComboBox.setFocus()
            return
        Qt.QDialog.accept(self)
