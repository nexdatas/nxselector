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
## \file PropertiesDlg.py
# label dialog

"""  label dialog """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

#from .ui.ui_edlistdlg import Ui_EdListDlg
from taurus.qt.qtgui.util.ui import UILoadable

from .LDataDlg import LDataDlg

import logging
logger = logging.getLogger(__name__)


class PropertiesDlg(Qt.QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(PropertiesDlg, self).__init__(parent)
        self.widget = PropertiesWg(self)
        self.dirty = False
        self.available_names = None

    def createGUI(self):
        self.widget.available_names = self.available_names
        self.widget.createGUI()
        layout = Qt.QHBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.connect(self.widget.ui.closePushButton,
                     Qt.SIGNAL("clicked()"),
                     self.accept)
        self.widget.ui.closePushButton.show()
        self.connect(self.widget, Qt.SIGNAL("dirty"), self.__setDirty)

    def __setDirty(self):
        self.dirty = True


## main window class
@UILoadable(with_ui='ui')
class PropertiesWg(Qt.QWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(PropertiesWg, self).__init__(parent)
        self.simple = False
        self.paths = {}
        self.shapes = {}
        self.links = {}
        self.types = {}
        self.available_names = None
#        self.ui = Ui_EdListDlg()

    def createGUI(self):
        self.loadUi(filename='EdListWg.ui')
#        self.ui.setupUi(self)
        self.ui.closePushButton = self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close)
        self.ui.addPushButton = self.ui.addEditRemoveButtonBox.addButton(
            "&Add", Qt.QDialogButtonBox.ActionRole)
        self.ui.editPushButton = self.ui.addEditRemoveButtonBox.addButton(
            "&Edit", Qt.QDialogButtonBox.ActionRole)
        self.ui.removePushButton = self.ui.addEditRemoveButtonBox.addButton(
            "&Remove", Qt.QDialogButtonBox.ActionRole)

        names = self.__names()
        if names:
            item = names[0]
        else:
            item = None
        self.__populateTable(item)
        self.connect(self.ui.addPushButton, Qt.SIGNAL("clicked()"),
                     self.__add)
        self.connect(self.ui.editPushButton, Qt.SIGNAL("clicked()"),
                     self.__edit)
        self.connect(self.ui.tableWidget,
                     Qt.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     self.__edit)
        self.connect(self.ui.removePushButton, Qt.SIGNAL("clicked()"),
                     self.__remove)

    def __names(self):
        return sorted(set(self.paths.keys()) |
                       set(self.shapes.keys()) |
                       set(self.links.keys()) |
                       set(self.types.keys()))

    def __populateTable(self, selected=None):
        self.ui.tableWidget.clear()
        sitem = None
        self.ui.tableWidget.setSortingEnabled(False)
        names = self.__names()
        self.ui.tableWidget.setRowCount(len(names))
        headers = ["Name", "Type", "Shape", "Link", "Path"]
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
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

            value = str(self.types[name]) \
                if name in self.types.keys() else ''
            self.ui.tableWidget.setItem(row, 1, Qt.QTableWidgetItem(value))
            value = str(self.shapes[name]) \
                if name in self.shapes.keys() else ''
            self.ui.tableWidget.setItem(row, 2, Qt.QTableWidgetItem(value))
            value = str(self.links[name]) \
                if name in self.links.keys() else ''
            self.ui.tableWidget.setItem(row, 3, Qt.QTableWidgetItem(value))
            value = str(self.paths[name]) \
                if name in self.paths.keys() else ''
            self.ui.tableWidget.setItem(row, 4, Qt.QTableWidgetItem(value))
        self.ui.tableWidget.resizeColumnsToContents()
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
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = self.__names()
        if len(skeys) > row and row >= 0:
            name = skeys[row]
        return name

    @classmethod
    def __updateItem(cls, name, value, dct):
        if not value:
            if name in dct.keys():
                dct.pop(name)
        elif name:
            dct[name] = value

    def __updateTable(self, form):
        if form.label:
            name = form.label

            self.__updateItem(name, form.path, self.paths)
            self.__updateItem(name, form.dtype, self.types)
            self.__updateItem(name, form.shape, self.shapes)

            if form.link is None:
                if name in self.links.keys():
                    self.links.pop(name)
            elif name:
                self.links[name] = form.link

            self.__populateTable()
            self.emit(Qt.SIGNAL("dirty"))

    def __add(self):
        dform = LDataDlg(self)
        dform.available_names = self.available_names
        dform.createGUI()
        if dform.exec_():
            self.__updateTable(dform)

    def __edit(self):
        dform = LDataDlg(self)
        name = self.__currentName()
        dform.label = name
        if name in self.types.keys():
            dform.dtype = self.types[name]
        if name in self.shapes.keys():
            dform.shape = self.shapes[name]
        if name in self.links.keys():
            dform.link = self.links[name]
        if name in self.paths.keys():
            dform.path = self.paths[name]

        dform.available_names = self.available_names
        dform.createGUI()
        if name:
            dform.ui.labelLineEdit.setEnabled(False)
        if dform.exec_():
            self.__updateTable(dform)

    def __remove(self):
        name = self.__currentName()

        if Qt.QMessageBox.question(
            self, "Removing Data", "Would you like  to remove '%s'?" % name,
            Qt.QMessageBox.Yes | Qt.QMessageBox.No,
            Qt.QMessageBox.Yes) == Qt.QMessageBox.No:
            return
        if name in self.types.keys():
            self.types.pop(name)
        if name in self.shapes.keys():
            self.shapes.pop(name)
        if name in self.links.keys():
            self.links.pop(name)
        if name in self.paths.keys():
            self.paths.pop(name)

        self.emit(Qt.SIGNAL("dirty"))
        self.__populateTable()
