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
## \package nxsselector nexdatas
## \file Descriptions.py
# descriptions tab

""" descriptions tab """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .Element import CPElement
from .ElementModel import ElementModel
from .Views import CheckerView
from .DynamicTools import DynamicTools

import logging
logger = logging.getLogger(__name__)

OPTIONAL, MANDATORY, OTHERS = range(3)


## main window class
class Descriptions(Qt.QObject):

    componentChecked = Qt.pyqtSignal()

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None, userView=CheckerView,
                 mandUserView=CheckerView, rowMax=0):
        Qt.QObject.__init__(self)
        self.ui = ui
        self.state = state
        self.userView = userView
        self.mandUserView = mandUserView
        self.rowMax = rowMax

        self.agroup = []
        self.igroup = []
        self.mgroup = []

        self.mframes = []
        self.group_layouts = []
        self.auto_layouts = []
        self.groupboxes = []
        self.views = {}
        self.models = []
        self.__cplayout = None
        self.__dslayout = None
        self.__mainlayout = None

    def updateGroups(self):
        self.agroup = []
        for cp in self.state.acpgroup.keys():
            self.agroup.append(
                CPElement(cp, self.state,
                          group=self.state.acpgroup))

        self.mgroup = []
        mcpgroup = {}
        for cp in self.state.mcplist:
            mcpgroup[cp] = True
        for cp in mcpgroup.keys():
            self.mgroup.append(
                CPElement(cp, self.state, group=mcpgroup))

        self.igroup = []
        for ds in self.state.idsgroup.keys():
            self.igroup.append(
                CPElement(ds, self.state,
                          group=self.state.idsgroup))

    def __clearFrames(self):
        DynamicTools.cleanupObjects(self.models, "model")
        if self.views:
            views = list(self.views.values())
            DynamicTools.cleanupWidgets(views, "views")
            self.views = {}
        DynamicTools.cleanupObjects(self.auto_layouts, "auto")
        DynamicTools.cleanupWidgets(self.groupboxes, "groupbox")
        DynamicTools.cleanupObjects(self.group_layouts, "group")
        DynamicTools.cleanupFrames(self.mframes, "frames")
        DynamicTools.cleanupLayoutWithItems(self.__cplayout)
        DynamicTools.cleanupLayoutWithItems(self.__dslayout)
        DynamicTools.cleanupLayoutWithItems(self.__mainlayout)
        self.__cplayout = None
        self.__dslayout = None

    def createGUI(self):

        self.ui.descriptions.hide()
        if self.__cplayout and self.__dslayout:
            self.__clearFrames()
        self.__mainlayout = Qt.QHBoxLayout(self.ui.descriptions)
        self.__cplayout = Qt.QVBoxLayout()
        self.__dslayout = Qt.QVBoxLayout()
        self.__mainlayout.addLayout(self.__cplayout)
        self.__mainlayout.addLayout(self.__dslayout)
        self.__mainlayout.setStretchFactor(self.__cplayout, 3)
        self.__mainlayout.setStretchFactor(
            self.__dslayout, 1 if self.igroup else 0)

        self.views[OTHERS] = self.__addView(
            "Other Optional", self.userView, self.rowMax,
            self.__dslayout, not self.igroup)

        la = len(self.agroup)
        lm = len(self.mgroup)
        if la + lm:
            la, lm = [float(la) / (la + lm), float(lm) / (la + lm)]

        self.views[OPTIONAL] = self.__addView(
            "Optional", self.userView, max(1, int(la * (self.rowMax - 2))))
        self.views[MANDATORY] = self.__addView(
            "Mandatory", self.mandUserView,
            max(1, int(lm * (self.rowMax - 2))))

        self.ui.descriptions.update()
        if self.ui.tabWidget.currentWidget() == self.ui.descriptions:
            self.ui.descriptions.show()

    def __addView(self, label, view, rowMax, layout=None, hide=False):
        if layout is None:
            layout = self.__cplayout
        mframe = Qt.QFrame(self.ui.descriptions)
        mframe.setFrameShape(Qt.QFrame.StyledPanel)
        mframe.setFrameShadow(Qt.QFrame.Raised)
        self.mframes.append(mframe)
        layout_groups = Qt.QHBoxLayout(mframe)
        self.group_layouts.append(layout_groups)

        mgroup = Qt.QGroupBox(mframe)
        mgroup.setTitle(label)
        self.groupboxes.append(mgroup)
        layout_auto = Qt.QGridLayout(mgroup)
        self.auto_layouts.append(layout_auto)
        mview = view(mgroup)
        mview.rowMax = rowMax
        if hasattr(mview, 'dmapper'):
            mview.dmapper = None

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)

        layout.addWidget(mframe)
        if hide:
            mframe.hide()
        else:
            mframe.show()
        return mview

    def setModels(self):
        md = ElementModel(self.agroup)
#        md.enable = False
        self.models.append(md)
        self.views[OPTIONAL].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

        md = ElementModel(self.mgroup)
        md.enable = False
        self.models.append(md)
        self.views[MANDATORY].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

        md = ElementModel(self.igroup)
#        md.enable = False
        self.models.append(md)
        self.views[OTHERS].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

    @Qt.pyqtSlot()
    def __componentChecked(self):
        self.componentChecked.emit()

    def updateViews(self):
        for vw in self.views.values():
            vw.reset()

    def reset(self):
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
