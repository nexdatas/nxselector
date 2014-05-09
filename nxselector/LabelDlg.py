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
## \file LabelDlg.py
# label dialog

"""  label dialog """


from PyQt4.QtCore import (SIGNAL, QString, Qt)
from PyQt4.QtGui import (
    QDialog, QTableWidgetItem, QMessageBox, QAbstractItemView,
    QHeaderView, QWidget, QHBoxLayout)

from .ui.ui_edlistdlg import Ui_EdListDlg

from .LDataDlg import LDataDlg

import logging
logger = logging.getLogger(__name__)

class LabelDlg(QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(LabelDlg, self).__init__(parent)
        self.widget = LabelWg(self)
        self.dirty = False
        
    def createGUI(self):
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
class LabelWg(QWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(LabelWg, self).__init__(parent)
        self.simple = False
        self.paths = {}
        self.shapes = {}
        self.links = {}
        self.types = {}
        self.ui = Ui_EdListDlg()

    def createGUI(self):
        self.ui.setupUi(self)
        self.ui.closePushButton.hide()

        names = self.__names()
        if names:
            item = names[0]
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


    def __names(self):
        return sorted(set(self.paths.keys()) |
                       set(self.shapes.keys()) | 
                       set(self.links.keys()) |
                       set(self.types.keys()))
    

    def __populateTable(self, selected = None):
        self.ui.tableWidget.clear()
        sitem = None
        self.ui.tableWidget.setSortingEnabled(False)
        names = self.__names()
        self.ui.tableWidget.setRowCount(len(names))
        headers = ["Name", "Type", "Shape", "Link", "Path"]
        self.ui.tableWidget.setColumnCount(len(headers))
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)
        for row, name in enumerate(names):
            item = QTableWidgetItem(name)
            if selected is not None and selected == name:
                sitem = item
            self.ui.tableWidget.setItem(row, 0, item)

            
            value = str(self.types[name]) \
                if name in self.types.keys() else ''
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(value)) 
            value = str(self.shapes[name]) \
                if name in self.shapes.keys() else ''
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(value)) 
            value = str(self.links[name]) \
                if name in self.links.keys() else ''
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(value))
            value = str(self.paths[name]) \
                if name in self.paths.keys() else ''
            self.ui.tableWidget.setItem(row, 4, QTableWidgetItem(value))
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
#        self.ui.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ui.tableWidget.horizontalHeader().setStretchLastSection(True)        
#        self.ui.tableWidget.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if sitem is not None:
            sitem.setSelected(True)
            self.ui.tableWidget.setCurrentItem(sitem)

    def __currentName(self):
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = self.__names()
        if len(skeys) > row:
            name = skeys[row]
        return name

    def __updateItem(self, name, value, dct):
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
            print name , form.link
                
            self.__populateTable()
            self.emit(SIGNAL("dirty"))

    def __add(self):    
        dform  = LDataDlg(self)
        dform.createGUI()
        if dform.exec_():
            self.__updateTable(dform)
        
    def __edit(self):    
        dform  = LDataDlg(self)
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
                
        dform.createGUI()
        dform.ui.labelLineEdit.setEnabled(False)
        if dform.exec_():
            self.__updateTable(dform)

    def __remove(self):
        name = self.__currentName()
        
        if QMessageBox.question(
            self, "Removing Data", "Would you like  to remove '%s'?" % name,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return
        self.labels.pop(name)
        self.emit(SIGNAL("dirty"))
        self.__populateTable()

        
