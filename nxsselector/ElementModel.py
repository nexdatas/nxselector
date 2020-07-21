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
# Element Model

""" device Model """

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from .Element import DS, CP

import json
import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

#: (:obj:) name=0
NAME = range(1)

#: (:obj:`list` <:obj:`str` > ) synchronization text labels
PROPTEXT = {"synchronization": ["Trigger", "Gate", "Start"]}


class ElementModel(Qt.QAbstractTableModel):
    """ element model
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) component checked signal
    componentChecked = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) datachanged  signal
    datachanged = Qt.pyqtSignal(Qt.QModelIndex, Qt.QModelIndex)

    def __init__(self, group=None):
        """ consturctor

        :param group: list of device elements
        :type group: :obj:`list` <:class:`nxsselector.Element.Element`>
        """
        Qt.QAbstractTableModel.__init__(self)
        #: (:obj:`bool`) if enable selection for user
        self.enable = True
        #: (:obj:`bool`) if display enable selection for user
        self.disEnable = True
        #: (:obj:`bool`) if  enable (group widget)
        self.autoEnable = True
        #: (:obj:`list` <:class:`nxsselector.Element.Element`>) \
        #:    list of device elements
        self.group = []
        #: (:obj:`list` <:obj:`str`>) headers
        self.headers = ["Element", "Label", "Display",
                        "Scans", "Contains", "Properties"]

        if group:
            self.group = sorted(group, key=lambda x: x.name, reverse=False)

    def rowCount(self, _=Qt.QModelIndex()):
        """ provides number of model rows

        :returns: number of model rows
        :rtype: :obj:`int`
        """
        return len(self.group)

    def columnCount(self, _=Qt.QModelIndex()):
        """ provides number of model columns

        :returns: number of model columns
        :rtype: :obj:`int`
        """
        return len(self.headers)

    def index(self, row, column, _=Qt.QModelIndex()):
        """ creates a new index from the given parameters

        :param row: element row
        :type row: :obj:`int`
        :param column: element column
        :type column: :obj:`int`
        :returns: created index
        :rtype: :class:`taurus.qt.Qt.QModelIndex`
        """

        return self.createIndex(row, column)

    def __elementCheck(self, device, index):
        """ provides device check status

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :returns: check status
        :rtype: :class:`taurus.qt.Qt.Qt.CheckState`
        """
        if (not (self.flags(index) & Qt.Qt.ItemIsEnabled)
            and self.enable and device.enable) \
           or device.checked:
            return Qt.Qt.Checked
        else:
            return Qt.Qt.Unchecked

    def __displayCheck(self, device, index):
        """ provides device display status

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :returns: display status
        :rtype: :class:`taurus.qt.Qt.Qt.CheckState`
        """
        if (not (self.flags(index) & Qt.Qt.ItemIsEnabled)
            and self.enable and device.enable) \
           or device.checked:
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

    def __setProperties(self, device, variables):
        """ sets device properties

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :param variables: (name, value) json dictionary with properties
        :type variables: :obj:`str`
        """
        props = device.state.properties
        dname = device.name
        cpvrs = device.state.cpvrdict
        cvars = device.state.configvars
        prs = json.loads(variables)
        for nm, val in prs.items():
            if not nm.startswith("__"):
                if dname in cpvrs.keys() and nm in cpvrs[dname]:
                    if val is not None:
                        cvars[nm] = val
                    elif nm in cvars:
                        cvars.pop(nm)
                else:
                    if nm not in props.keys():
                        props[nm] = {}
                    if val is not None:
                        props[nm][dname] = val
                    elif dname in props[nm].keys():
                        props[nm].pop(dname)
        device.state.setProperties()

    def __properties(self, device):
        """ provides device properties

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :returns: (name, value) json dictionary with properties
        :rtype: :obj:`str`
        """
        cpvrs = device.state.cpvrdict
        cvars = device.state.configvars
        props = device.state.properties
        ochs = device.state.orderedchannels
        chps = device.state.channelprops
        echps = device.state.extrachannelprops
        admindata = device.state.admindata
        tglist = device.state.triggergatelist
        dname = device.name
        contains = dict()
        if dname in cpvrs.keys():
            for vr in cpvrs[dname]:
                if vr not in admindata:
                    contains[vr] = cvars[vr] if vr in cvars.keys() else None

        if dname in ochs:
            for pr in chps:
                if props and pr in props.keys() and \
                   props[pr] and dname in props[pr].keys():
                    contains[pr] = props[pr][dname]
                else:
                    contains[pr] = None
            for pr in echps:
                if props and pr in props.keys() and \
                   props[pr] and dname in props[pr].keys():
                    contains[pr] = props[pr][dname]
                else:
                    contains[pr] = None
        contains["__triggergatelist__"] = tglist
        return json.dumps(contains)

    def __scanSources(self, device):
        """ provides device scan datasources

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :returns: string list of scan datasources separated by spaces
        :rtype: :obj:`str`
        """
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
        """ provides device description datasources

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :returns: string list of datasources datasources separated by spaces
        :rtype: :obj:`str`
        """
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
        """ creates a comma separated list from the text

        :param text: the given text
        :type device: :obj:`str`
        :returns: comma separated list from the text
        :rtype: :obj:`str`
        """
        lst = str(text).split() if text else []
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
        """ creates device tips

        :param device: device element
        :type device: :class:`nxsselector.Element.Element`
        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :returns: device tips
        :rtype: :obj:`str`
        """
        scans = self.__scanSources(device)
        depends = self.__descSources(device)
        prs = self.__properties(device)
        tscans = self.__createList(scans)
        tdepends = self.__createList(depends)
        text = tscans if tscans else ""
        dds = device.state.ddsdict
        if tdepends:
            text = "%s\n[%s]" % (text, tdepends)

        if device.name in dds:
            sld = dds[device.name]
            if sld:
                text = "%s\n * selected by %s *" % (text, sld)
            else:
                text = "%s\n * timer *" % text

        if prs:
            prs = json.loads(prs)
            tt = " ".join("%s=\"%s\"" % (
                k, (v if k not in PROPTEXT.keys() else PROPTEXT[k][int(v)]))
                for (k, v) in prs.items() if v)
            if tt.strip():
                text = "%s\n(%s)" % (text, tt.strip())

        if text.strip():
            return text

    def data(self, index, role=Qt.Qt.DisplayRole):
        """ provides model data

        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :param role: data model role
        :type role: :class:`taurus.qt.Qt.Qt.ItemDataRole`
        :returns: model data
        :rtype: `str:class:`taurus.qt.Qt.`
        """
        if not index.isValid() or \
                not 0 <= index.row() < len(self.group):
            return
        device = self.group[index.row()]
        column = index.column()
        if column == 0:
            if role == Qt.Qt.DisplayRole:
                return (device.name)
            if role == Qt.Qt.CheckStateRole:
                return self.__elementCheck(device, index)
            if role == Qt.Qt.ToolTipRole:
                tips = self.__createTips(device, index)
                if tips:
                    return (str(tips))
        elif column == 1:
            if role == Qt.Qt.CheckStateRole:
                return
            if device.name in device.state.labels.keys():
                return (device.state.labels[device.name])
        elif column == 2:
            if role == Qt.Qt.CheckStateRole:
                return self.__displayCheck(device, index)
        elif column == 3:
            if role == Qt.Qt.CheckStateRole:
                return
            return (str(self.__scanSources(device)))
        elif column == 4:
            if role == Qt.Qt.CheckStateRole:
                return
            return (str(self.__descSources(device)))
        elif column == 5:
            if role == Qt.Qt.CheckStateRole:
                return
            return (str(self.__properties(device)))
        return ()

    def headerData(self, section, _, role=Qt.Qt.DisplayRole):
        """ provides model data header

        :param section: section number
        :type section: :obj:`int`
        :param role: data model role
        :type role: :class:`taurus.qt.Qt.Qt.ItemDataRole`
        :returns: model data header
        :rtype: `str:class:`taurus.qt.Qt.`
        """
        if role != Qt.Qt.DisplayRole:
            return ()
        if section >= 0 and section < len(self.headers):
            return (self.headers[section])
        return (int(section + 1))

    def flags(self, index):
        """ provides model data flag

        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :returns: model data flag
        :rtype: `str:class:`taurus.qt.Qt.Qt.ItemFlag`
        """
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled

        enable = True
        comp = None
        device = self.group[index.row()]
        enable2 = self.enable and device.enable
        flag = Qt.QAbstractTableModel.flags(self, index)
        column = index.column()
        dds = device.state.ddsdict
        if device.eltype == DS:
            if device.name in dds.keys() and self.autoEnable:
                enable = False
                flag &= ~Qt.Qt.ItemIsEnabled
                comp = dds[device.name]
        elif device.eltype == CP:
            mcp = device.state.mcplist
            # acp = device.state.acplist
            if (self.autoEnable and device.name in mcp) \
               or device.name in dds.keys():
                enable2 = False
                flag &= ~Qt.Qt.ItemIsEnabled
                if device.name in dds.keys():
                    enable = False
                    comp = dds[device.name]
        if column == 0:
            if enable and enable2:
                return Qt.Qt.ItemFlags(flag |
                                       Qt.Qt.ItemIsEnabled |
                                       Qt.Qt.ItemIsUserCheckable)
            else:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(
                    flag |
                    Qt.Qt.ItemIsUserCheckable
                )
        elif column == 1:
            flag &= ~Qt.Qt.ItemIsUserCheckable
            if not enable or not enable2:
                flag &= ~Qt.Qt.ItemIsEnabled
            return Qt.Qt.ItemFlags(
                flag |
                Qt.Qt.ItemIsEditable
            )
        if column == 2:
            if not self.disEnable:
                flag &= ~Qt.Qt.ItemIsEnabled
                return Qt.Qt.ItemFlags(flag | Qt.Qt.ItemIsUserCheckable)
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
                if comp in device.state.dsgroup:
                    cpncheck = not device.state.dsgroup[comp]
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
        elif column == 5:
            return Qt.Qt.ItemFlags(flag | Qt.Qt.ItemIsEnabled)

    def setData(self, index, value, role=Qt.Qt.EditRole):
        """ sets model data

        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :param value: element value
        :type value: :class:`taurus.qt.Qt.`
        :param role: data model role
        :type role: :class:`taurus.qt.Qt.Qt.ItemDataRole`
        :returns: if data fas set
        :rtype: :obj:`str`
        """
        if index.isValid() and 0 <= index.row() < len(self.group):
            device = self.group[index.row()]
            column = index.column()
            if column == 0:
                if role == Qt.Qt.CheckStateRole:
                    index3 = self.index(index.row(), 2)
                    device.state.ddsdirty = True
                    device.checked = value
                    self.datachanged.emit(index, index3)
                    self.componentChecked.emit()
                    self.dirty.emit()
                return True
            elif column == 1:
                if role == Qt.Qt.EditRole:
                    label = value.toString()
                    device.state.labels[device.name] = str(label)
                    self.datachanged.emit(index, index)
                    self.dirty.emit()
                    return True
            elif column == 2:
                if role == Qt.Qt.CheckStateRole:
                    index3 = self.index(index.row(), 2)
                    device.display = value
                    self.datachanged.emit(index, index3)
                    self.componentChecked.emit()
                    self.dirty.emit()
                    return True
            elif column == 5:
                if role == Qt.Qt.EditRole:
                    if hasattr(value, "toString"):
                        value = value.toString()
                    self.__setProperties(device, str(value))
                    index5 = self.index(index.row(), 5)
                    self.datachanged.emit(index, index5)
                    self.dirty.emit()
                    return True
        return False


class ElementDelegate(Qt.QStyledItemDelegate):
    """ element delegate
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """ created editor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        :param option: editor option
        :type option: :class:`taurus.qt.Qt.QStyleOptionViewItem`
        :param index: element index
        :type index: :class:`taurus.qt.Qt.QModelIndex`
        :returns: created editor
        :rtype: :class:`taurus.qt.Qt.QWidget`
        """
        if index.column() == 0:
            editor = Qt.QCheckBox(parent)
            return editor
        else:
            return Qt.QItemDelegate.createEditor(self, parent, option, index)
