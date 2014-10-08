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
## \file GroupsDlg.py
# editable list of component groups

"""  editable list dialog """



#from PyQt4.QtCore import (SIGNAL, Qt)
#from PyQt4.QtGui import (
#    QDialog, QTableWidgetItem, QMessageBox, QAbstractItemView,
#    QWidget, QHBoxLayout)

from taurus.external.qt import Qt

from .ui.ui_cpgroupsdlg import Ui_CpGroupsDlg

import logging
logger = logging.getLogger(__name__)

class GroupsDlg(Qt.QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(GroupsDlg, self).__init__(parent)
        self.ui = Ui_CpGroupsDlg()
        self.dirty = False
        self.det_components = {}
        self.det_datasources = {}
        self.beam_components = {}
        self.beam_datasources = {}
        self.dcpchanged = False
        self.ddschanged = False
        self.bcpchanged = False
        self.bdschanged = False


    def createGUI(self):
        self.ui.setupUi(self)
        self.setWindowTitle("Component Groups")

        self.__populateTable(self.ui.dcpTableWidget,
                             self.det_components, "Components:")
        self.__populateTable(self.ui.ddsTableWidget,
                             self.det_datasources, "DataSources:")
        self.__populateTable(self.ui.bcpTableWidget,
                             self.beam_components, "Components:")
        self.__populateTable(self.ui.bdsTableWidget,
                             self.beam_datasources, "DataSources:")

        self.connect(self.ui.dcpTableWidget,
                     Qt.SIGNAL("cellChanged(int, int)"),
                     self.__dirty)
        self.connect(self.ui.ddsTableWidget,
                     Qt.SIGNAL("cellChanged(int, int)"),
                     self.__dirty)
        self.connect(self.ui.bcpTableWidget,
                     Qt.SIGNAL("cellChanged(int, int)"),
                     self.__dirty)
        self.connect(self.ui.bdsTableWidget,
                     Qt.SIGNAL("cellChanged(int, int)"),
                     self.__dirty)

        self.connect(self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close),
                     Qt.SIGNAL("clicked()"),
                     self.reject)
        self.connect(self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Apply),
                     Qt.SIGNAL("clicked()"),
                     self.__apply)

    def __updateDict(self, table, dct):
        changed = False
        for i in range(table.rowCount()):
            item = table.item(i, 0)
            status = bool((item.checkState())/2)
            name = str(item.data(Qt.Qt.DisplayRole))

            if dct[name] != status:
                dct[name] = status
                changed = True
                self.dirty = True
        return changed

    def __apply(self):
        if self.__updateDict(
            self.ui.dcpTableWidget, self.det_components):
            self.dcpchanged = True
        if self.__updateDict(
            self.ui.ddsTableWidget, self.det_datasources):
            self.ddschanged = True
        if self.__updateDict(
            self.ui.bcpTableWidget, self.beam_components):
            self.bcpchanged =  True
        if self.__updateDict(
            self.ui.bdsTableWidget, self.beam_datasources):
            self.bdschanged = True
        logger.debug("APPLY")

    def __dirty(self):
        self.setWindowTitle("Component Groups *")
        logger.debug("changed")

    def __populateTable(self, widget, dct, header):
        widget.clear()
        widget.setSortingEnabled(False)
        names = sorted(dct.keys())
        widget.setRowCount(len(names))
        widget.setColumnCount(1)
        widget.setHorizontalHeaderLabels([header])
        for row, name in enumerate(names):
            enable = True

            item = Qt.QTableWidgetItem(name)
            item.setCheckState(int(dct[name])*2)
            widget.setItem(row, 0, item)
        widget.resizeColumnsToContents()
        widget.horizontalHeader().setStretchLastSection(True)
        widget.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)
