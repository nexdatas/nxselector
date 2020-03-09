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
# editable list of component groups

"""  editable list dialog """

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable
# from taurus.qt.qtgui.panel import TaurusModelChooser
# from taurus.qt.qtgui.panel import TaurusModelSelectorTree
# from taurus.core.taurusbasetypes import TaurusElementType
# import taurus

from .Views import OneTableView
from .Element import GElement, CP, DS
from .ElementModel import ElementModel
from .AddDataSourceDlg import AddDataSourceDlg


import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


@UILoadable(with_ui='ui')
class GroupsDlg(Qt.QDialog):
    """  editable other device list dialog
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        #: (:obj:`bool`) dirty flag
        self.dirty = False
        #: (:obj:`dict` <:obj:`str`, :obj:`bool` or `None`>) \
        #:     component selection
        self.components = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`bool` or `None`>) \
        #:     datasource selection
        self.datasources = {}
        #: (:obj:`list` <:class:`nxsselector.Element.Element`>) \
        #:    list of component elements
        self.dcpgroup = []
        #: (:obj:`list` <:class:`nxsselector.Element.Element`>) \
        #:    list of datasource elements
        self.ddsgroup = []
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = None
        #: (:obj:`str`) group title
        self.title = "Selectable Detector Elements"
        #: (:obj:`dict` <:obj:`str`, :obj:`str``>) \
        #:     datasources to add { name: source }
        self.newdatasources = {}

    def __createViews(self, widget, cpview, dsview):
        """ creates basic views

        :param widget: main detector widget
        :type widget: :class:`taurus.qt.Qt.QWidget`
        :param cpview: component table view
        :type cpview: :class:`taurus.qt.Qt.QTableView`
        :param dsview: datasource table view
        :type dsview: :class:`taurus.qt.Qt.QTableView`
        """
        gridLayout_3 = Qt.QGridLayout(widget)
        gridLayout = Qt.QGridLayout()
        gridLayout.addWidget(cpview, 0, 0, 1, 1)
        gridLayout.addWidget(dsview, 0, 1, 1, 1)
        gridLayout_3.addLayout(gridLayout, 0, 0, 1, 1)

    def createGUI(self):
        """ creates GUI
        """
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

        self.ui.createPushButton = self.ui.closeButtonBox.addButton(
            "", Qt.QDialogButtonBox.ActionRole)
        self.ui.createPushButton.setText("Create DataSources ...")
        self.ui.createPushButton.clicked.connect(
            self.__createDataSources)

    @Qt.pyqtSlot()
    def __dirty(self):
        """ sets dirty to True
        """
        self.dirty = True
        self.setWindowTitle("Component Groups *")
        logger.debug("changed")

    @Qt.pyqtSlot()
    def __createDataSources(self):
        """ selects configuration of new datasources
        """
        dform = AddDataSourceDlg(self)
        dform.createGUI()
        if dform.exec_():
            self.newdatasources[dform.name] = dform.source
            self.datasources[dform.name] = True
            datasources = {dform.name: True}
            self.__populateTable(self.ui.ddsTableView, self.ddsgroup, DS,
                                 datasources, "DataSources:")
            self.dirty = True

    def __populateTable(self, view, group, eltype, dct, header):
        """ populates the group table

        :param view: element table view
        :type view: :class:`taurus.qt.Qt.QTableView`
        :param group: list ofg elements
        :type group: :obj:`list` <:class:`nxsselector.Element.Element`>
        :param eltype: element type, i.e datasource=DS (0) or component=CP (1)
        :type eltype: :obj:`int`
        :param dct: element selection dictionary
        :type dct: :obj:`dict` <:obj:`str`, :obj:`bool` or `None`>
        :param header: table header
        :type header: :obj:`str`
        """

        for el in dct.keys():
            group.append(GElement(el, eltype, self.state, dct))
        md = ElementModel(group)
        md.headers = [header]
        md.autoEnable = False
        view.horizontalHeader().setVisible(True)
        view.setModel(md)
        md.dirty.connect(self.__dirty)
