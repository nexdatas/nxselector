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
## \file Views.py
# module with different table views

""" main window application dialog """

import os
import PyTango
import json

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString, QSignalMapper,
    SLOT)
from PyQt4.QtGui import (QTableView, QHeaderView, QWidget, QGridLayout, 
                         QCheckBox, QAbstractScrollArea, QPalette,
                         QAbstractItemView, QLabel, QFrame, QSpacerItem,
                         QRadioButton, QPushButton)



        
class TableView(QTableView):

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)        
        self.horizontalHeader().setVisible(False)        
        self.horizontalHeader().setStretchLastSection(True)        
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)




class CheckerView(QWidget):

    def __init__(self, parent=None):
        super(CheckerView, self).__init__(parent)
        self.model = None
#        self.layout = QtGui.QFormLayout(self)
        self.layout = QGridLayout(self)
        self.widgets = []
        self.mapper = QSignalMapper(self)
        self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                     self.checked)
        self.spacer = None
        self.widget = QCheckBox
        
    def checked(self, widget):
        row = self.widgets.index(widget)
        
        ind = self.model.index(row, 1)
        value = QVariant(self.widgets[row].isChecked())
        self.model.setData(ind, value, Qt.CheckStateRole)
            
    def setModel(self, model):
        self.model = model
        self.connect(self.model,
                     SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.updateState)
        self.connect(self.model,
                     SIGNAL("modelReset()"),
                     self.updateState)
        self.updateState()

    def reset(self):
        self.hide()
        if self.layout:
            self.widgets = []
            self.spacer = None
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QtGui.QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
            self.mapper = QSignalMapper(self)
            self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                         self.checked)
        self.updateState()
        self.show()

    def updateState(self):
        if not self.model is None:
            for row in range(self.model.rowCount()):
                ind = self.model.index(row,1)
                name = self.model.data(ind, role = Qt.DisplayRole)
                status = self.model.data(ind, role = Qt.CheckStateRole)
                flags = self.model.flags(ind)
                if row < len(self.widgets):
                    cb = self.widgets[row]
                else:
                    cb = self.widget()
                    if hasattr(cb, "setCheckable"):
                        cb.setCheckable(True)
                cb.setEnabled(bool(Qt.ItemIsEnabled & flags))
                if name:
                    cb.setText(str(name.toString()))
                if status is not None:    
#                    cb.setCheckState(status)
                    cb.setChecked(bool(status))
                if row >= len(self.widgets):
                    self.layout.addWidget(cb, row, 0, 1, 1)
                    self.widgets.append(cb)
                    self.connect(cb, SIGNAL("clicked()"),
                                 self.mapper, SLOT("map()"))
                    self.mapper.setMapping(cb, cb)
            if not self.spacer:
                self.spacer = QSpacerItem(10, 10, 
                                         QtGui.QSizePolicy.Expanding, 
                                         QtGui.QSizePolicy.Expanding)
                self.layout.addItem(self.spacer)
                
            
        self.update()
        self.updateGeometry()

class RadioView(CheckerView):
#class CheckerView(QAbstractItemView):

    def __init__(self, parent=None):
        super(RadioView, self).__init__(parent)
        self.widget = QRadioButton


class ButtonView(CheckerView):
#class CheckerView(QAbstractItemView):

    def __init__(self, parent=None):
        super(ButtonView, self).__init__(parent)
        self.widget = QPushButton
