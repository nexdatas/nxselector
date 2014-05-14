#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file EdListDlg.py
# editable list dialog

"""  editable list dialog """



from PyQt4.QtCore import (SIGNAL, QString, Qt)
from PyQt4.QtGui import (
    QDialog, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QHeaderView, QWidget, QHBoxLayout)

from .ui.ui_edlistdlg import Ui_EdListDlg

from .EdDataDlg import EdDataDlg

import logging
logger = logging.getLogger(__name__)

class EdListDlg(QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(EdListDlg, self).__init__(parent)
        self.widget = EdListWg(self)
        self.simple = False
        self.dirty = False
        self.available_names = None
        self.available_values = None
        
    def createGUI(self):
        self.widget.simple = self.simple
        self.widget.available_names = self.available_names
        self.widget.available_values = self.available_values
        self.widget.createGUI()
        layout = QHBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.connect(self.widget.ui.closePushButton, 
                     SIGNAL("clicked()"),
                     self.accept)
        self.widget.ui.closePushButton.show()
        self.connect(self.widget, SIGNAL("dirty"),self.__setDirty)

    def __setDirty(self):
        self.dirty = True
        
        

## main window class
class EdListWg(QWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(EdListWg, self).__init__(parent)
        self.simple = False
        self.record = {}
        self.available_names = None
        self.available_values = None
        self.ui = Ui_EdListDlg()

    def createGUI(self):
        self.ui.setupUi(self)
        self.ui.closePushButton.hide()
        
        if self.record:
            item = sorted(self.record.keys())[0]
        else:
            item = None
        self.__populateTable(item)
        self.connect(self.ui.addPushButton, SIGNAL("clicked()"),
                     self.__add)
        self.connect(self.ui.editPushButton, SIGNAL("clicked()"),
                     self.__edit)
        self.connect(self.ui.tableWidget, 
                     SIGNAL("itemDoubleClicked(QTableWidgetItem*)"),
                     self.__edit)
        self.connect(self.ui.removePushButton, SIGNAL("clicked()"),
                     self.__remove)

    def __populateTable(self, selected = None):
        self.ui.tableWidget.clear()
        sitem = None
        self.ui.tableWidget.setSortingEnabled(False)
        names = sorted(self.record.keys())
        self.ui.tableWidget.setRowCount(len(names))
        headers = ["Name", "Value"]
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        for row, name in enumerate(names):
            enable = True
            if self.available_names is not None and\
                    name not in self.available_names:
                enable = False
            item = QTableWidgetItem(name)
            if self.available_names is not None:
                if enable is False:
                    flags = item.flags()
                    flags &= ~Qt.ItemIsEnabled
                    item.setFlags(flags)
            if selected is not None and selected == name:
                sitem = item
            self.ui.tableWidget.setItem(row, 0, item)

            value = self.record[name]
            venable = True
            if self.available_values is not None and\
                    str(value).strip() not in self.available_values:
                venable = False

            item = QTableWidgetItem(str(value))
            if self.available_values is not None:
                if venable is False:
                    flags = item.flags()
                    flags &= ~Qt.ItemIsEnabled
                    item.setFlags(flags)
            self.ui.tableWidget.setItem(row, 1, item)
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)        
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if sitem is not None:
            sitem.setSelected(True)
            self.ui.tableWidget.setCurrentItem(sitem)

    def __currentName(self):
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = sorted(self.record.keys())
        if len(skeys) > row and row >= 0:
            name = skeys[row]
        return name

    def __add(self):    
        dform  = EdDataDlg(self)
        dform.simple = self.simple
        dform.createGUI()
        if dform.exec_():
            self.record[dform.name] = dform.value
            self.__populateTable()
            self.emit(SIGNAL("dirty"))
        
    def __edit(self):    
        dform  = EdDataDlg(self)
        dform.simple = self.simple
        name = self.__currentName()
        if name:
            dform.name = name
            dform.value = self.record[name]
        dform.createGUI()
        if name:
            dform.ui.nameLineEdit.setEnabled(False)
        if dform.exec_():
            self.record[dform.name] = dform.value
            self.__populateTable()
            self.emit(SIGNAL("dirty"))

    def __remove(self):
        name = self.__currentName()
        
        if QMessageBox.question(
            self, "Removing Data", "Would you like  to remove '%s'?" % name,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        self.record.pop(name)
        self.emit(SIGNAL("dirty"))
        self.__populateTable()

        
