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

#from PyQt4.QtGui import (
#    QCheckBox,
#    QItemDelegate, QStyledItemDelegate)
#from PyQt4.QtCore import (
#    SIGNAL, Qt, QVariant, QAbstractTableModel,
#    QModelIndex, QString)

from taurus.qt import Qt

from .Element import DS, CP

import logging
logger = logging.getLogger(__name__)


NAME = range(1)

## main window class
class ElementModel(Qt.QAbstractTableModel):

    ## constructor
    # \param parent parent widget
    def __init__(self, group = None):
        super(ElementModel, self).__init__()
        self.enable = True
        self.group = []

        if group:
            self.group = sorted(group, key=lambda x: x.name, reverse=False)

    def rowCount(self, _=Qt.QModelIndex()):
        return len(self.group)
        

    def columnCount(self, _=Qt.QModelIndex()):
        return 5

    def index(self, row, column, _=Qt.QModelIndex()):
        return self.createIndex(row, column)

    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self.group)):
            return
        device = self.group[index.row()]
        column = index.column()
        if column == 0:
            if role == Qt.Qt.DisplayRole:
                return Qt.QVariant(device.name)
            if role == Qt.Qt.CheckStateRole: 
                if (not (self.flags(index) & Qt.Qt.ItemIsEnabled) \
                        and self.enable) \
                        or device.checked:
                    return Qt.Qt.Checked
                else:
                    return Qt.Qt.Unchecked
        elif column == 1:
            if role == Qt.Qt.CheckStateRole: 
                return
            if device.name in device.state.labels.keys():
                return Qt.QVariant(device.state.labels[device.name])
        elif column == 2:
            if role == Qt.Qt.CheckStateRole: 
                if (not (self.flags(index) & Qt.Qt.ItemIsEnabled) \
                        and self.enable) \
                        or device.checked:
                    if device.eltype == DS:
                        dds = device.state.ddsdict
                        if device.name in dds.keys():
                            nd = device.state.nodisplay
                            if dds[device.name] in nd:
                                return Qt.Qt.Unchecked
                            else:
                                return Qt.Qt.Checked
                            
                    if device.display:
                        return Qt.Qt.Checked
                    else:
                        return Qt.Qt.Unchecked
                else:
                    return Qt.Qt.Unchecked
        elif column == 3:
            if role == Qt.Qt.CheckStateRole: 
                return
            desc = device.state.description       
            contains = set()
            for cpg in desc:
                for cp, dss in cpg.items():
                    if cp == device.name:
                        if isinstance(dss, dict):
                            for ds, values in dss.items():
                                for vl in values:
                                    if len(vl) > 0 and vl[0] == 'STEP':
                                        contains.add(ds)
                                        break
            if contains:    
                return Qt.QVariant(Qt.QString(
                        " ".join([str(c) for c in sorted(contains)])))
        elif column == 4:
            if role == Qt.Qt.CheckStateRole: 
                return
            desc = device.state.description       
            contains = set()
            for cpg in desc:
                for cp, dss in cpg.items():
                    if cp == device.name:
                        if isinstance(dss, dict):
                            for ds, values in dss.items():
                                for vl in values:
                                    if len(vl) == 0 or vl[0] != 'STEP':
                                        contains.add(ds)
                                        break
            if contains:    
                return Qt.QVariant(Qt.QString(
                        " ".join([str(c) for c in sorted(contains)])))
             


        return Qt.QVariant()

    def headerData(self, section, _, role=Qt.Qt.DisplayRole):
        if role != Qt.Qt.DisplayRole:
            return Qt.QVariant()
        if section == 0:
            return Qt.QVariant("Element")
        elif section == 1:
            return Qt.QVariant("Label")
        elif section == 2:
            return Qt.QVariant("Display")
        elif section == 3:
            return Qt.QVariant("Scans")
        elif section == 4:
            return Qt.QVariant("Contains")
            
        return Qt.QVariant(int(section + 1))

    def flags(self, index):
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled

        enable2 = self.enable
        enable = True
        device = self.group[index.row()]
        flag = Qt.QAbstractTableModel.flags(self, index)
        column = index.column()
        if device.eltype == DS:
            dds = device.state.ddsdict
            if device.name in dds.keys():
                enable = False
                flag &= ~Qt.Qt.ItemIsEnabled
        elif device.eltype == CP:
            mcp = device.state.mcplist
            acp = device.state.acplist
            if device.name in mcp or device.name in acp:
                enable2 = False
                
                flag &= ~Qt.Qt.ItemIsEnabled
        if column == 0:
            if enable and enable2:        
                return Qt.Qt.ItemFlags(flag | 
                                    Qt.Qt.ItemIsEnabled  | 
                                    Qt.Qt.ItemIsUserCheckable 
                                    )
            else:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(flag | 
                                    Qt.Qt.ItemIsUserCheckable 
                                    )
        elif column == 1:
            flag &= ~Qt.Qt.ItemIsUserCheckable
            if not enable or not enable2:
                flag &= ~Qt.Qt.ItemIsEnabled
            return Qt.Qt.ItemFlags(flag | 
                                Qt.Qt.ItemIsEditable 
                                )
        if column == 2:
            if enable:        
                return Qt.Qt.ItemFlags(flag | 
                                    Qt.Qt.ItemIsEnabled  | 
                                    Qt.Qt.ItemIsUserCheckable 
                                    )
            else:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(flag | Qt.Qt.ItemIsUserCheckable)
        elif column == 3:
            if enable and enable2:        
                return Qt.Qt.ItemFlags(flag | Qt.Qt.ItemIsEnabled)
            else:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(flag)
        elif column == 4:
            if enable and enable2:        
                return Qt.Qt.ItemFlags(flag | Qt.Qt.ItemIsEnabled)
            else:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(flag)


    def setData(self, index, value, role=Qt.Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.group):
            device = self.group[index.row()]
            column = index.column()
            if column == 0:
                if role == Qt.Qt.CheckStateRole: 
                    index3 = self.index(index.row(), 2) 
                    device.checked = value.toBool()

                    self.emit(Qt.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index3)
                    if device.eltype == CP:
                        self.emit(Qt.SIGNAL("componentChecked"))
                    self.emit(Qt.SIGNAL("dirty"))
                return True
            elif column == 1:
                if role == Qt.Qt.EditRole: 
                    label = value.toString()
                    device.state.labels[device.name] = str(label)
                    self.emit(Qt.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index)
                    self.emit(Qt.SIGNAL("dirty"))
                    return True
            elif column == 2:
                if role == Qt.Qt.CheckStateRole: 
                    index3 = self.index(index.row(), 2) 
                    device.display = value.toBool()
                    
                    self.emit(Qt.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), 
                              index, index3)
                    if device.eltype == CP:
                        self.emit(Qt.SIGNAL("componentChecked"))
                    self.emit(Qt.SIGNAL("dirty"))
                    return True
        return False


class ElementDelegate(Qt.QStyledItemDelegate):
                
    def __init__(self, parent=None):
        super(ElementDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = Qt.QCheckBox(parent)
            return editor
        else:
            return Qt.QItemDelegate.createEditor(self, parent, option, index)
        
            
