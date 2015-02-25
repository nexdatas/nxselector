#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

from .ui.ui_cpgroupsdlg import Ui_CpGroupsDlg
from .Views import OneTableView
from .Element import GElement, CP, DS
from .ElementModel import ElementModel

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
        self.dcpgroup = []
        self.ddsgroup = []
        self.bcpgroup = []
        self.bdsgroup = []
        self.state = None

    def __createViews(self, widget, cpview, dsview):
        gridLayout_3 = Qt.QGridLayout(widget)
        gridLayout = Qt.QGridLayout()
        gridLayout.addWidget(cpview, 0, 0, 1, 1)
        gridLayout.addWidget(dsview, 0, 1, 1, 1)
        gridLayout_3.addLayout(gridLayout, 0, 0, 1, 1)

    def createGUI(self):
        self.ui.setupUi(self)
        self.setWindowTitle("Component Groups")
        self.ui.dcpTableView = OneTableView(self.ui.detector)
        self.ui.ddsTableView = OneTableView(self.ui.detector)
        self.ui.bcpTableView = OneTableView(self.ui.beamline)
        self.ui.bdsTableView = OneTableView(self.ui.beamline)

        self.__createViews(self.ui.detector,
                           self.ui.dcpTableView, self.ui.ddsTableView)
        self.__createViews(self.ui.beamline,
                           self.ui.bcpTableView, self.ui.bdsTableView)

        self.__populateTable(self.ui.dcpTableView, self.dcpgroup, CP,
                             self.det_components, "Selectable Components:")
        self.__populateTable(self.ui.ddsTableView, self.ddsgroup, DS,
                             self.det_datasources, "Selectable DataSources:")
        self.__populateTable(self.ui.bcpTableView, self.bcpgroup, CP,
                             self.beam_components,
                             "Preselectable Components:")
        self.__populateTable(self.ui.bdsTableView, self.bdsgroup, DS,
                             self.beam_datasources,
                             "Preselecting DataSources:")

        self.connect(self.ui.dcpTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.ddsTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.bcpTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.bdsTableView, Qt.SIGNAL("dirty"), self.__dirty)

        self.connect(self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close),
                     Qt.SIGNAL("clicked()"),
                     self.reject)

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
        md.connect(md, Qt.SIGNAL("dirty"),
                   self.__dirty)
