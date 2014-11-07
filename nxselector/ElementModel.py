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

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .Element import DS, CP

import logging
logger = logging.getLogger(__name__)

NAME = range(1)


## main window class
class ElementModel(Qt.QAbstractTableModel):

    ## constructor
    # \param parent parent widget
    def __init__(self, group=None):
        super(ElementModel, self).__init__()
        ## if enable selection for user
        self.enable = True
        ## if auto enable
        self.autoEnable = True
        ## list of device elements
        self.group = []
        ## headers
        self.headers = ["Element", "Label", "Display", "Scans", "Contains"]

        if group:
            self.group = sorted(group, key=lambda x: x.name, reverse=False)

    def rowCount(self, _=Qt.QModelIndex()):
        return len(self.group)

    def columnCount(self, _=Qt.QModelIndex()):
        return 5

    def index(self, row, column, _=Qt.QModelIndex()):
        return self.createIndex(row, column)

    def __elementCheck(self, device, index):
        if (not (self.flags(index) & Qt.Qt.ItemIsEnabled)
            and self.enable) or device.checked:
            return Qt.Qt.Checked
        else:
            return Qt.Qt.Unchecked

    def __displayCheck(self, device, index):
        if (not (self.flags(index) & Qt.Qt.ItemIsEnabled)
            and self.enable) or device.checked:
            if device.eltype == DS:
                dds = device.state.ddsdict
                if device.name in dds.keys():
                    nd = device.state.nodisplay
                    if not dds[device.name] in nd \
                            and dds[device.name]:
                        return Qt.Qt.Checked

            if device.display:
                return Qt.Qt.Checked
            else:
                return Qt.Qt.Unchecked
        else:
            return Qt.Qt.Unchecked

    def __scanSources(self, device):
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
            return " ".join([str(c) for c in sorted(contains)])

    def __descSources(self, device):
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
            return " ".join([str(c) for c in sorted(contains)])

    @classmethod
    def __createList(cls, text, words=7):
        lst = str(text).split() if text else ''
        cnt = 0
        st = ""
        for sl in lst[:-1]:
            st += sl
            cnt += 1
            if cnt % words:
                st += ', '
            else:
                st += ',\n'

        if len(lst):
            st += lst[-1]
        return st

    def __createTips(self, device, index):
        scans = self.__scanSources(device)
        depends = self.__descSources(device)
        tscans = self.__createList(scans)
        tdepends = self.__createList(depends)
        text = tscans if tscans else ""
        if tdepends:
            text = "%s\n[%s]" % (text, tdepends)

        if text.strip():
            return text

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
                return self.__elementCheck(device, index)
            if role == Qt.Qt.ToolTipRole:
                tips = self.__createTips(device, index)
                if tips:
                    return Qt.QVariant(Qt.QString(tips))
        elif column == 1:
            if role == Qt.Qt.CheckStateRole:
                return
            if device.name in device.state.labels.keys():
                return Qt.QVariant(device.state.labels[device.name])
        elif column == 2:
            if role == Qt.Qt.CheckStateRole:
                return self.__displayCheck(device, index)
        elif column == 3:
            if role == Qt.Qt.CheckStateRole:
                return
            return Qt.QVariant(Qt.QString(self.__scanSources(device)))
        elif column == 4:
            if role == Qt.Qt.CheckStateRole:
                return
            return Qt.QVariant(Qt.QString(self.__descSources(device)))
        return Qt.QVariant()

    def headerData(self, section, _, role=Qt.Qt.DisplayRole):
        if role != Qt.Qt.DisplayRole:
            return Qt.QVariant()
        if section >= 0 and section < len(self.headers):
            return Qt.QVariant(self.headers[section])
        return Qt.QVariant(int(section + 1))

    def flags(self, index):
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled

        enable2 = self.enable
        enable = True
        comp = None
        device = self.group[index.row()]
        flag = Qt.QAbstractTableModel.flags(self, index)
        column = index.column()
        if device.eltype == DS:
            dds = device.state.ddsdict
            if device.name in dds.keys() and self.autoEnable:
                enable = False
                flag &= ~Qt.Qt.ItemIsEnabled
                comp = dds[device.name]
        elif device.eltype == CP:
            mcp = device.state.mcplist
            acp = device.state.acplist
            if (device.name in mcp or device.name in acp) and self.autoEnable:
                enable2 = False
                flag &= ~Qt.Qt.ItemIsEnabled
        if column == 0:
            if enable and enable2:
                return Qt.Qt.ItemFlags(flag |
                                    Qt.Qt.ItemIsEnabled |
                                    Qt.Qt.ItemIsUserCheckable)
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
            cpncheck = False
            if comp:
                if comp in device.state.mcplist:
                    cpncheck = False
                    if not cpncheck and comp in device.state.nodisplay:
                        cpncheck = True
                elif comp in device.state.acpgroup:
                    cpncheck = not device.state.acpgroup[comp]
                    if not cpncheck and comp in device.state.nodisplay:
                        cpncheck = True
                elif comp in device.state.cpgroup:
                    cpncheck = not device.state.cpgroup[comp]
                    if not cpncheck and comp in device.state.nodisplay:
                        cpncheck = True
            elif comp is not None:
                cpncheck = True
            if enable or cpncheck:
                return Qt.Qt.ItemFlags(flag |
                                       Qt.Qt.ItemIsEnabled |
                                       Qt.Qt.ItemIsUserCheckable)
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
                    device.checked = value

                    self.emit(
                        Qt.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                              index, index3)
#                    self.emit(Qt.SIGNAL("componentChecked"))
                    if device.eltype == CP:
                        self.emit(Qt.SIGNAL("componentChecked"))
                    self.emit(Qt.SIGNAL("dirty"))
                return True
            elif column == 1:
                if role == Qt.Qt.EditRole:
                    label = value.toString()
                    device.state.labels[device.name] = str(label)
                    self.emit(
                        Qt.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                              index, index)
                    self.emit(Qt.SIGNAL("dirty"))
                    return True
            elif column == 2:
                if role == Qt.Qt.CheckStateRole:
                    index3 = self.index(index.row(), 2)
                    device.display = value
                    print "Component checked", device.name, value

                    self.emit(Qt.SIGNAL(
                            "dataChanged(QModelIndex, QModelIndex)"),
                              index, index3)
                    if device.eltype == CP:
                        print "Component checked"
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
