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


        self.__populateCPTable(self.ui.dcpTableView, self.dcpgroup,
                             self.det_components, "Components:")
        self.__populateDSTable(self.ui.ddsTableView, self.ddsgroup,
                             self.det_datasources, "DataSources:")
        self.__populateCPTable(self.ui.bcpTableView, self.bcpgroup,
                             self.beam_components, "Components:")
        self.__populateDSTable(self.ui.bdsTableView, self.bdsgroup,
                             self.beam_datasources, "DataSources:")

        self.connect(self.ui.dcpTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.ddsTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.bcpTableView, Qt.SIGNAL("dirty"), self.__dirty)
        self.connect(self.ui.bdsTableView, Qt.SIGNAL("dirty"), self.__dirty)

        self.connect(self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close),
                     Qt.SIGNAL("clicked()"),
                     self.reject)
#        self.connect(self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Apply),
#                     Qt.SIGNAL("clicked()"),
#                     self.__apply)


    def __dirty(self):
        self.dirty = True
        self.setWindowTitle("Component Groups *")
        
        logger.debug("changed")

    def __populateCPTable(self, view, group, dct, header):
        for el, sl in dct.items():
            group.append(GElement(el, CP, self.state, dct))
        md = ElementModel(group)
        view.setModel(md)
        md.connect(md, Qt.SIGNAL("dirty"),
                   self.__dirty)

#            md.connect(md, Qt.SIGNAL("componentChecked"),
#                       self.updateViews)

    def __populateDSTable(self, view, group, dct, header):
        for el, sl in dct.items():
            group.append(GElement(el, DS, self.state, dct))
        md = ElementModel(group)
        md.autoEnable = False
        view.setModel(md)
        md.connect(md, Qt.SIGNAL("dirty"),
                   self.__dirty)
#        widget.clear()
#        widget.setSortingEnabled(False)
#        names = sorted(dct.keys())
#        widget.setRowCount(len(names))
#        widget.setColumnCount(1)
#        widget.setHorizontalHeaderLabels([header])
#        for row, name in enumerate(names):
#            enable = True

#            item = Qt.QTableWidgetItem(name)
#            item.setCheckState(int(dct[name]) * 2)
#            widget.setItem(row, 0, item)
#        widget.resizeColumnsToContents()
#        widget.horizontalHeader().setStretchLastSection(True)
#        widget.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)


