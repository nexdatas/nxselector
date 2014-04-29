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

from PyQt4.QtCore import (
    SIGNAL, Qt, QVariant, QAbstractTableModel,
    QModelIndex)
from PyQt4.QtGui import (
    QCheckBox,
    QItemDelegate, QStyledItemDelegate)

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
            self.group = sorted(group, key=lambda x: x.name, reverse=False)

    def rowCount(self, _=QModelIndex()):
        return len(self.group)
        

    def columnCount(self, _=QModelIndex()):
        return 3

    def index(self, row, column, _=QModelIndex()):
        return self.createIndex(row, column)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self.group)):
            return
        device = self.group[index.row()]
        column = index.column()
        if column == 0:
            if role == Qt.DisplayRole:
                return QVariant(device.name)
            if role == Qt.CheckStateRole: 
                if (not (self.flags(index) & Qt.ItemIsEnabled) \
                        and self.enable) \
                        or device.checked:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
        elif column == 1:
            if role == Qt.CheckStateRole: 
                return
            if device.eltype == DS:
                if device.name in device.state.dslabels.keys():
                    return QVariant(device.state.dslabels[device.name])
            elif device.eltype == CP:    
                return 
        elif column == 2:
            if role == Qt.CheckStateRole: 
                if (not (self.flags(index) & Qt.ItemIsEnabled) \
                        and self.enable) \
                        or device.checked:
                    if device.eltype == DS:
                        dds = device.state.ddsdict
                        if device.name in dds.keys():
                            nd = device.state.nodisplay
                            if dds[device.name] in nd:
                                return Qt.Unchecked
                            else:
                                return Qt.Checked
                    if device.display:
                        return Qt.Checked
                    else:
                        return Qt.Unchecked
                else:
                    return Qt.Unchecked
             


        return QVariant()

    def headerData(self, section, _, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()
        if section == 0:
            return QVariant("Element")
        elif section == 1:
            return QVariant("Label")
        elif section == 2:
            return QVariant("Display")
            
        return QVariant(int(section + 1))

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled

        enable = self.enable
        device = self.group[index.row()]
        flag = QAbstractTableModel.flags(self, index)
        column = index.column()
        if device.eltype == DS:
            dds = device.state.ddsdict
            if device.name in dds.keys():
                enable = False
                flag &= ~Qt.ItemIsEnabled
                        
        elif device.eltype == CP:
            mcp = device.state.mcplist
            acp = device.state.acplist
            if device.name in mcp or device.name in acp:
                enable = False
                flag &= ~Qt.ItemIsEnabled
        if column == 0:
            if enable:        
                return Qt.ItemFlags( flag | 
                                     Qt.ItemIsEnabled  | 
                                     Qt.ItemIsUserCheckable 
                                     )
            else:
                flag &= ~Qt.ItemIsEnabled
                return Qt.ItemFlags( flag | 
                                     Qt.ItemIsUserCheckable 
                                     )
        elif column == 1:
            flag &= ~Qt.ItemIsUserCheckable
            if not enable:
                flag &= ~Qt.ItemIsEnabled
            return Qt.ItemFlags( flag | 
                                 Qt.ItemIsEditable 
                                 )
        if column == 2:
            if enable:        
                return Qt.ItemFlags( flag | 
                                     Qt.ItemIsEnabled  | 
                                     Qt.ItemIsUserCheckable 
                                     )
            else:
                flag &= ~Qt.ItemIsEnabled
                return Qt.ItemFlags( flag | 
                                     Qt.ItemIsUserCheckable 
                                     )
#            flag &= ~Qt.ItemIsUserCheckable 
#            print "row/col", index.row(), column, device.name
#            return Qt.ItemFlags( flag | Qt.ItemIsEnabled)


    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.group):
            device = self.group[index.row()]
            column = index.column()
            if column == 0:
                if role == Qt.CheckStateRole: 
                    index3 = self.index(index.row(),3) 
                    device.checked = value.toBool()

                    self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index3)
                    if device.eltype == CP:
                        self.emit(SIGNAL("componentChecked"))
                    self.emit(SIGNAL("dirty"))
                return True
            elif column == 1:
                if role == Qt.EditRole: 
                    label = value.toString()
                    device.state.dslabels[device.name] = str(label)
                    self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index)
                    self.emit(SIGNAL("dirty"))
                    return True
            elif column == 2:
                if role == Qt.CheckStateRole: 
                    device.display = value.toBool()
                    
                    self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index)
                    if device.eltype == CP:
                        self.emit(SIGNAL("componentChecked"))
                    self.emit(SIGNAL("dirty"))
                    return True
        return False


class ElementDelegate(QStyledItemDelegate):
                
    def __init__(self, parent=None):
        super(ElementDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = QCheckBox(parent)
            return editor
        else:
            return QItemDelegate.createEditor(self, parent, option, index)
        
            
