#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

from .Views import OneTableView
from .Element import GElement, CP, DS
from .ElementModel import ElementModel

import logging
logger = logging.getLogger(__name__)


@UILoadable(with_ui='ui')
class GroupsDlg(Qt.QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(GroupsDlg, self).__init__(parent)
        self.loadUi()
        self.dirty = False
        self.components = {}
        self.datasources = {}
        self.dcpchanged = False
        self.ddschanged = False
        self.dcpgroup = []
        self.ddsgroup = []
        self.state = None
        self.title = "Selectable Detector Elements"

    def __createViews(self, widget, cpview, dsview):
        gridLayout_3 = Qt.QGridLayout(widget)
        gridLayout = Qt.QGridLayout()
        gridLayout.addWidget(cpview, 0, 0, 1, 1)
        gridLayout.addWidget(dsview, 0, 1, 1, 1)
        gridLayout_3.addLayout(gridLayout, 0, 0, 1, 1)

    def createGUI(self):
        self.setWindowTitle(self.title)
        self.ui.dcpTableView = OneTableView(self.ui.detector)
        self.ui.ddsTableView = OneTableView(self.ui.detector)

        self.__createViews(self.ui.detector,
                           self.ui.dcpTableView, self.ui.ddsTableView)

        self.__populateTable(self.ui.dcpTableView, self.dcpgroup, CP,
                             self.components, "Components:")
        self.__populateTable(self.ui.ddsTableView, self.ddsgroup, DS,
                             self.datasources, "DataSources:")

        self.ui.dcpTableView.dirty.connect(self.__dirty)
        self.ui.ddsTableView.dirty.connect(self.__dirty)

        self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close).clicked.connect(self.reject)

    @Qt.pyqtSlot()
    def __dirty(self):
        self.dirty = True
        self.setWindowTitle("Component Groups *")
        logger.debug("changed")

    def __populateTable(self, view, group, eltype, dct, header):
        for el, sl in dct.items():
            group.append(GElement(el, eltype, self.state, dct))
        md = ElementModel(group)
        md.headers = [header]
        md.autoEnable = False
        view.horizontalHeader().setVisible(True)
        view.setModel(md)
        md.dirty.connect(self.__dirty)
