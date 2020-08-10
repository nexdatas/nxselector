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
# editable list dialog

"""  editable list dialog """

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

from .EdDataDlg import EdDataDlg

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class EdListDlg(Qt.QDialog):
    """  editable list dialog
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        #: (:class:`nxselector.EdListWg.EdListWg`)  dialog widget
        self.widget = EdListWg(self)
        #: (:obj:`bool`) simple view
        self.simple = False
        #: (:obj:`bool`) dirty flag
        self.dirty = False
        #: (:obj:`list` <:obj:`str`>) available names
        self.available_names = None
        #: (:obj:`list` <:obj:`str`>) table headers
        self.headers = ["Name", "Value"]
        #: (:obj:`list` <:obj:`str`>) disable names
        self.disable = []

    def createGUI(self):
        """ creates widget GUI
        """
        self.widget.simple = self.simple
        self.widget.available_names = self.available_names
        self.widget.headers = self.headers
        self.widget.disable = self.disable
        self.widget.createGUI()
        layout = Qt.QHBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.widget.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close).clicked.connect(self.accept)
        self.widget.ui.closePushButton.show()
        self.widget.dirty.connect(self.__setDirty)

    @Qt.pyqtSlot()
    def __setDirty(self):
        """ set dirty flag """
        self.dirty = True


@UILoadable(with_ui='ui')
class EdListWg(Qt.QWidget):
    """  editable list widget
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QWidget.__init__(self, parent)
        self.loadUi()
        #: (:obj:`bool`) simple view flag
        self.simple = False
        #: (:obj:`dict` <:obj:`str`, `any`>) data (name, value) dictionary
        self.record = {}
        #: (:obj:`list` <:obj:`str`>) available names
        self.available_names = None
        #: (:obj:`list` <:obj:`str`>) table headers
        self.headers = ["Name", "Value"]
        #: (:obj:`list` <:obj:`str`>) disable names
        self.disable = []

    def createGUI(self):
        """ creates widget GUI
        """
        if hasattr(self.ui, "addPushButton"):
            self.ui.addPushButton.clicked.disconnect(self.__add)
            self.ui.editPushButton.clicked.disconnect(self.__edit)
            self.ui.tableWidget.itemDoubleClicked.disconnect(self.__edit)
            self.ui.removePushButton.clicked.disconnect(self.__remove)

        self.ui.closePushButton = self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close)

        self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close).hide()
        if not hasattr(self.ui, "addPushButton"):
            self.ui.addPushButton = self.ui.addEditRemoveButtonBox.addButton(
                "&Add", Qt.QDialogButtonBox.ActionRole)
            self.ui.editPushButton = self.ui.addEditRemoveButtonBox.addButton(
                "&Edit", Qt.QDialogButtonBox.ActionRole)
            self.ui.removePushButton = \
                self.ui.addEditRemoveButtonBox.addButton(
                    "&Remove", Qt.QDialogButtonBox.ActionRole)

        if self.record:
            item = sorted(self.record.keys())[0]
        else:
            item = None
        self.__populateTable(item)
        self.ui.addPushButton.clicked.connect(self.__add)
        self.ui.editPushButton.clicked.connect(self.__edit)
        self.ui.tableWidget.itemDoubleClicked.connect(self.__edit)
        self.ui.removePushButton.clicked.connect(self.__remove)

    def __populateTable(self, selected=None):
        """ populate table records

        :param selected: name of selected item
        :type selected: :obj:`str`
        """
        self.ui.tableWidget.clear()
        sitem = None
        self.ui.tableWidget.setSortingEnabled(False)
        names = sorted(self.record.keys())
        self.ui.tableWidget.setRowCount(len(names))
        self.ui.tableWidget.setColumnCount(len(self.headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(self.headers)
        for row, name in enumerate(names):
            enable = True
            if self.available_names is not None and\
                    name not in self.available_names:
                enable = False
            item = Qt.QTableWidgetItem(name)
            if self.available_names is not None:
                if enable is False:
                    flags = item.flags()
                    flags &= ~Qt.Qt.ItemIsEnabled
                    item.setFlags(flags)
            if selected is not None and selected == name:
                sitem = item
            self.ui.tableWidget.setItem(row, 0, item)
            value = self.record[name]
            item = Qt.QTableWidgetItem(str(value))
            if name in self.disable:
                flags = item.flags()
                flags &= ~Qt.Qt.ItemIsEnabled
                item.setFlags(flags)
            self.ui.tableWidget.setItem(row, 1, item)
        self.ui.tableWidget.resizeColumnToContents(0)
        self.ui.tableWidget.setSelectionBehavior(
            Qt.QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(
            Qt.QAbstractItemView.SingleSelection)
        self.ui.tableWidget.horizontalHeader(
        ).setStretchLastSection(True)
        self.ui.tableWidget.setEditTriggers(
            Qt.QAbstractItemView.NoEditTriggers)
        if sitem is not None:
            sitem.setSelected(True)
            self.ui.tableWidget.setCurrentItem(sitem)

    def __currentName(self):
        """ provides currently selected name

        :returns: currently selected name
        :rtype: :obj:`str`
        """
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = sorted(self.record.keys())
        if len(skeys) > row and row >= 0:
            name = skeys[row]
        return name

    @Qt.pyqtSlot()
    def __add(self):
        """ adds a new record into the table
        """
        dform = EdDataDlg(self)
        dform.simple = self.simple
        dform.headers = self.headers
        dform.available_names = list(
            set(self.available_names) - set(self.disable))
        dform.available_tips = True
        dform.createGUI()
        if dform.exec_():
            if dform.name in self.disable:
                Qt.QMessageBox.information(
                    self, "Selector in Simple/User Mode",
                    "This data cannot be edited")
                return

            self.record[dform.name] = dform.value
            self.__populateTable()
            self.dirty.emit()
        dform.setParent(None)

    @Qt.pyqtSlot()
    def __edit(self):
        """ edits the current record in the table
        """
        name = self.__currentName()
        if name in self.disable:
            Qt.QMessageBox.information(
                self, "Selector in Simple/User Mode",
                "This data cannot be edited")
            return
        dform = EdDataDlg(self)
        dform.simple = self.simple
        dform.available_names = self.available_names
        if name:
            dform.name = name
            dform.value = self.record[name]
        dform.headers = self.headers
        dform.createGUI()
        if name:
            dform.ui.nameComboBox.setEnabled(False)
        if dform.exec_():
            self.record[dform.name] = dform.value
            self.__populateTable()
            self.dirty.emit()
        dform.setParent(None)

    @Qt.pyqtSlot()
    def __remove(self):
        """ removes the current record from the table
        """
        name = self.__currentName()
        if name in self.disable:
            Qt.QMessageBox.information(
                self, "Selector in Simple Mode",
                "This data cannot be removed")
            return
        if name not in self.record:
            return

        if Qt.QMessageBox.question(
                self, "Removing Data",
                "Would you like  to remove '%s'?" % name,
                Qt.QMessageBox.Yes | Qt.QMessageBox.No,
                Qt.QMessageBox.Yes) == Qt.QMessageBox.No:
            return
        self.record.pop(name)
        self.dirty.emit()
        self.__populateTable()
