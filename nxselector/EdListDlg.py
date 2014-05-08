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
    QHeaderView)

from .ui.ui_edlistdlg import Ui_EdListDlg

from .EdDataDlg import EdDataDlg

import logging
logger = logging.getLogger(__name__)

## main window class
class EdListDlg(QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(EdListDlg, self).__init__(parent)
        self.simple = False
        self.record = {}
        self.dirty = False
        self.ui = Ui_EdListDlg()

    def createGUI(self):
        self.ui.setupUi(self)
        
        if self.record:
            item = sorted(self.record.keys())[0]
        else:
            item = None
        self.__populateTable(item)
        self.connect(self.ui.closePushButton, SIGNAL("clicked()"),
                     self.accept)
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
            value = self.record[name]
#            isString = isinstance(vl, (str, unicode, QString))
            item = QTableWidgetItem(name)
            if selected is not None and selected == name:
                sitem = item
            self.ui.tableWidget.setItem(row, 0, item)
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(value))) 
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)        
        self.ui.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if sitem is not None:
            sitem.setSelected(True)
            self.ui.tableWidget.setCurrentItem(sitem)

    def __currentName(self):
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = sorted(self.record.keys())
        print "row", row, skeys
        if len(skeys) > row:
            name = skeys[row]
        return name

    def __add(self):    
        dform  = EdDataDlg(self)
        dform.simple = self.simple
        dform.createGUI()
        if dform.exec_():
            print "OK" ,dform.name, dform.value
            self.record[dform.name] = dform.value
            self.__populateTable()
            self.dirty = True
        
    def __edit(self):    
        dform  = EdDataDlg(self)
        dform.simple = self.simple
        name = self.__currentName()
        dform.name = name
        dform.value = self.record[name]
        dform.createGUI()
        if dform.exec_():
            print "OK" ,dform.name, dform.value
            self.record[dform.name] = dform.value
            self.__populateTable()
            self.dirty = True

    def __remove(self):
        name = self.__currentName()
        
        if QMessageBox.question(
            self, "Removing Data", "Would you like  to remove '%s'?" % name,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        self.record.pop(name)
        self.dirty = True
        self.__populateTable()
