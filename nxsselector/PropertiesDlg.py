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
# properties dialog

"""  properties dialog """


try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

from .LDataDlg import LDataDlg

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class PropertiesDlg(Qt.QDialog):
    """  properties dialog """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        #: (:class:`nxselector.PropertiesWg.PropertiesWg`) properties widget
        self.widget = PropertiesWg(self)
        #: (:obj:`bool`) dirty flag
        self.dirty = False
        #: (:obj:`list` <:obj:`str`>) available names
        self.available_names = None

    def createGUI(self):
        """ creates widget GUI
        """
        self.widget.available_names = self.available_names
        self.widget.createGUI()
        layout = Qt.QHBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

        self.widget.ui.closePushButton.clicked.connect(self.accept)
        self.widget.ui.closePushButton.show()
        self.widget.dirty.connect(self.__setDirty)

    def __setDirty(self):
        """ set dirty flag """
        self.dirty = True


@UILoadable(with_ui='ui')
class PropertiesWg(Qt.QWidget):
    """  properties widget """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QWidget.__init__(self, parent)
        self.loadUi(filename='EdListWg.ui')
        #: (:obj:`bool`) simple view flag
        self.simple = False
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:    property (name, path) dictionary
        self.paths = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:    property (name, JSON list with shape) dictionary
        self.shapes = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`bool`>) \
        #:    property (name, link) dictionary
        self.links = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`bool`>) \
        #:    property (name, canfailflag) dictionary
        self.canfailflags = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:    property (name, nexus type) dictionary
        self.types = {}
        #: (:obj:`list` <:obj:`str`>) available names
        self.available_names = None

    def createGUI(self):
        """ creates widget GUI
        """
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
        self.ui.addPushButton.clicked.connect(self.__add)
        self.ui.editPushButton.clicked.connect(self.__edit)
        self.ui.tableWidget.itemDoubleClicked.connect(self.__edit)
        self.ui.removePushButton.clicked.connect(self.__remove)

    def __names(self):
        """ provides property names

        :returns:  property names
        :rtype: :obj:`list` <:obj:`str`> >
        """
        return sorted(set(self.paths.keys()) |
                      set(self.shapes.keys()) |
                      set(self.links.keys()) |
                      set(self.canfailflags.keys()) |
                      set(self.types.keys()))

    def __populateTable(self, selected=None):
        """ populates the group table

        :param selected: selected property
        :type selected: :obj:`str`
        """
        self.ui.tableWidget.clear()
        sitem = None
        self.ui.tableWidget.setSortingEnabled(False)
        names = self.__names()
        self.ui.tableWidget.setRowCount(len(names))
        headers = ["Name", "Type", "Shape", "Link", "CanFail", "Path"]
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
            value = str(self.canfailflags[name]) \
                if name in self.canfailflags.keys() else ''
            self.ui.tableWidget.setItem(row, 4, Qt.QTableWidgetItem(value))
            value = str(self.paths[name]) \
                if name in self.paths.keys() else ''
            self.ui.tableWidget.setItem(row, 5, Qt.QTableWidgetItem(value))
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
        """ provides a name of the currently selected channel

        :returns: name of the currently selected channel
        :rtype: :obj:`str`
        """
        name = None
        row = self.ui.tableWidget.currentRow()
        skeys = self.__names()
        if len(skeys) > row and row >= 0:
            name = skeys[row]
        return name

    @classmethod
    def __updateItem(cls, name, value, dct):
        """ updates property items in the given dictionary

        :param name: property name
        :type name: :obj:`str`
        :param value: property value
        :type value: `any`
        :param dct: (name, value) dictionary to be updated
        :type dct: :obj:`dict` < :obj:`str`, `any`>
`
        """
        if not value:
            if name in dct.keys():
                dct.pop(name)
        elif name:
            dct[name] = value

    def __updateTable(self, form):
        """ updates table acdcording to the given form

        :param form: LDataDlg form with properties
        :type form: :class:`nxselector.LDataDlg.LDataDlg`
        """
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

            if form.canfail is None:
                if name in self.canfailflags.keys():
                    self.canfailflags.pop(name)
            elif name:
                self.canfailflags[name] = form.canfail

            self.__populateTable()
            self.dirty.emit()

    @Qt.pyqtSlot()
    def __add(self):
        """ adds a new property """
        dform = LDataDlg(self)
        dform.available_names = self.available_names
        dform.createGUI()
        if dform.exec_():
            self.__updateTable(dform)

    @Qt.pyqtSlot()
    def __edit(self):
        """ change a value of the current property """
        dform = LDataDlg(self)
        name = self.__currentName()
        dform.label = name
        if name in self.types.keys():
            dform.dtype = self.types[name]
        if name in self.shapes.keys():
            dform.shape = self.shapes[name]
        if name in self.links.keys():
            dform.link = self.links[name]
        if name in self.canfailflags.keys():
            dform.canfail = self.canfailflags[name]
        if name in self.paths.keys():
            dform.path = self.paths[name]

        dform.available_names = self.available_names
        dform.createGUI()
        if name:
            dform.ui.labelLineEdit.setEnabled(False)
        if dform.exec_():
            self.__updateTable(dform)

    @Qt.pyqtSlot()
    def __remove(self):
        """ remmoves the current property """
        name = self.__currentName()

        if Qt.QMessageBox.question(
                self, "Removing Data",
                "Would you like  to remove '%s'?" % name,
                Qt.QMessageBox.Yes | Qt.QMessageBox.No,
                Qt.QMessageBox.Yes) == Qt.QMessageBox.No:
            return
        if name in self.types.keys():
            self.types.pop(name)
        if name in self.shapes.keys():
            self.shapes.pop(name)
        if name in self.links.keys():
            self.links.pop(name)
        if name in self.canfailflags.keys():
            self.canfailflags.pop(name)
        if name in self.paths.keys():
            self.paths.pop(name)

        self.dirty.emit()
        self.__populateTable()
