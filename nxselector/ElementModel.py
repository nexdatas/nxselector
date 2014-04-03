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
## \package nxselecto nexdatas
## \file ElementModel.py
# Element Model

""" device Model """

import os
import PyTango
import json

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, QAbstractTableModel,
    QModelIndex)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView, QCheckBox,
    QLabel, QFrame,QStyledItemDelegate)

from .Frames import Frames
from .Element import DS, CP

import logging
logger = logging.getLogger(__name__)


NAME = range(1)

## main window class
class ElementModel(QAbstractTableModel):

    ## constructor
    # \param parent parent widget
    def __init__(self, group = None):
        super(ElementModel, self).__init__()
        self.enable = True
        self.group = []

        if group:
            self.group = group
        pass

    def rowCount(self, index=QModelIndex()):
        return len(self.group)
        

    def columnCount(self, index=QModelIndex()):
        return 1

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self.group)):
            return
        device = self.group[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            return QVariant(device.name)
        if role == Qt.CheckStateRole: 
            if not (self.flags(index) & Qt.ItemIsEnabled) or device.checked:
                return Qt.Checked
            else:
                return Qt.Unchecked


        return QVariant()

#    def headerData(self, section, orientation, role=Qt.DisplayRole):
#        if role != Qt.DisplayRole:
#            return QVariant()
#        if section == NAME:
#            return QVariant("Element")
#        return QVariant(int(section + 1))


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        enable = self.enable
        device = self.group[index.row()]
        flag = QAbstractTableModel.flags(self, index)
        if device.eltype == DS:
            dds = device.state.ddslist
            if device.name in dds:
                enable = False
                flag &= ~Qt.ItemIsEnabled
        elif device.eltype == CP:
            mcp = device.state.mcplist
            acp = device.state.acplist
            if device.name in mcp or device.name in acp:
                enable = False
                flag &= ~Qt.ItemIsEnabled
        if enable:        
            return Qt.ItemFlags( flag | 
                                 Qt.ItemIsEnabled  | 
                                 Qt.ItemIsUserCheckable 
                                 )
        else:
            return Qt.ItemFlags( flag | 
                                 Qt.ItemIsUserCheckable 
                                 )


    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.group):
            device = self.group[index.row()]
            column = index.column()
            if role == Qt.CheckStateRole: 
                device.checked = value.toBool()
                self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                          index, index)
                if device.eltype == CP:
                    self.emit(SIGNAL("componentChecked"))
                
            return True
        return False


class ElementDelegate(QStyledItemDelegate):
                
    def __init__(self, parent=None):
        super(ElementDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == CHECKED:
            editor = QCheckBox(parent)
            return editor
        else:
            return QItemDelegate.createEditor(self, parent, option, index)
        
            
