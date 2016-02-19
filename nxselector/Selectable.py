#!/usr/bin/env python
#   This file is part of nexdatas - Tanog Server for NeXus data writer
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
## \file Selectable.py
# selactable tab

""" selactable tab """

import json
import fnmatch

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .Element import DSElement, CPElement, CP, DS
from .ElementModel import ElementModel
from .Frames import Frames
from .DynamicTools import DynamicTools

from .Views import CheckerView

import logging
logger = logging.getLogger(__name__)


## main window class
class Selectable(Qt.QObject):

    dirty = Qt.pyqtSignal()

    ## constructor
    def __init__(self, ui, state=None, userView=CheckerView, rowMax=0,
                 simpleMode=0):
        Qt.QObject.__init__(self)

        self.ui = ui
        self.state = state
        self.userView = userView
        self.rowMax = rowMax
        self.__simpleMode = simpleMode
        self.glayout = None

        self.frames = None
        self.mgroups = None
        self.groups = {}
        self.views = {}
        self.mframes = []
        self.column_layouts = []
        self.group_layouts = []
        self.auto_layouts = []
        self.groupboxes = []
        self.models = []

    def updateGroups(self):
        self.groups = {}
        ucp = set()
        uds = set()
        try:
            mgroups = json.loads(self.mgroups)
        except:
            mgroups = {}
        for k, gr in mgroups.items():
            if int(k) in self.__availableGroups():
                group = []
                for elem in gr:
                    if isinstance(elem, list) and elem:
                        ielem = elem[0]
                    else:
                        ielem = elem
                    cpfiltered = fnmatch.filter(
                        self.state.cpgroup.keys(),
                        ielem)
                    dsfiltered = fnmatch.filter(
                        self.state.dsgroup.keys(),
                        ielem)
                    filtered = set(cpfiltered)
                    filtered.update(dsfiltered)
                    for felem in filtered:
                        if felem not in self.state.dsgroup.keys() \
                                and felem in self.state.avcplist:
                            group.append(
                                CPElement(felem, self.state))
                            ucp.add(felem)
                        else:
                            group.append(
                                DSElement(felem, self.state))
                            uds.add(felem)
                if group:
                    if int(k) not in self.groups:
                        self.groups[int(k)] = []
                    self.groups[int(k)].extend(group)

        for ds in self.state.dsgroup.keys():
            if ds not in uds and ds not in ucp:
                if DS not in self.groups:
                    self.groups[DS] = []
                self.groups[DS].append(DSElement(ds, self.state))
        for cp in self.state.cpgroup.keys():
            if cp not in ucp and cp not in uds \
                    and cp not in self.state.mcplist \
                    and cp not in self.state.acplist:
                if CP not in self.groups:
                    self.groups[CP] = []
                self.groups[CP].append(CPElement(cp, self.state))

    def __availableGroups(self):
        res = set()
        try:
            frames = Frames(self.frames)
            for frame in frames:
                for column in frame:
                    for group in column:
                        res.add(group[1])
        except:
            pass
        return res

    def __clearFrames(self):
        DynamicTools.cleanupObjects(self.models, "model")
        if self.views:
            views = list(self.views.values())
            DynamicTools.cleanupWidgets(views, "views")
            self.views = {}
        DynamicTools.cleanupObjects(self.auto_layouts, "auto")
        DynamicTools.cleanupWidgets(self.groupboxes, "groupbox")
        DynamicTools.cleanupObjects(self.group_layouts, "group")
        DynamicTools.cleanupObjects(self.column_layouts, "column")
        DynamicTools.cleanupFrames(self.mframes, "frames")
        DynamicTools.cleanupLayoutWithItems(self.glayout)

    def createGUI(self):

        self.__clearFrames()
        self.glayout = Qt.QHBoxLayout(self.ui.selectable)

        frames = Frames(self.frames, DS in self.groups, CP in self.groups)
        for frame in frames:
            mframe = Qt.QFrame(self.ui.selectable)
            self.mframes.append(mframe)
            mframe.setFrameShape(Qt.QFrame.StyledPanel)
            mframe.setFrameShadow(Qt.QFrame.Raised)
            layout_columns = Qt.QHBoxLayout(mframe)
            self.column_layouts.append(layout_columns)

            for column in frame:
                layout_groups = Qt.QVBoxLayout()
                self.group_layouts.append(layout_groups)

                for group in column:
                    hide = False
                    try:
                        ig = int(group[1])
                        if (self.__simpleMode & 1) and ig < 0:
                            hide = True
                    except Exception:
                        pass
                    if not hide:
                        mgroup = Qt.QGroupBox(mframe)
                        self.groupboxes.append(mgroup)
                        mgroup.setTitle(group[0])
                        layout_auto = Qt.QGridLayout(mgroup)
                        self.auto_layouts.append(layout_auto)
                        mview = self.userView(mgroup)
                        mview.rowMax = self.rowMax

                        layout_auto.addWidget(mview, 0, 0, 1, 1)
                        self.views[group[1]] = mview
                        layout_groups.addWidget(mgroup)
                if layout_groups.count():
                    layout_columns.addLayout(layout_groups)
            if layout_columns.count():
                self.glayout.addWidget(mframe)
            else:
                mframe.hide()
        self.ui.selectable.update()
        if self.ui.tabWidget.currentWidget() == self.ui.selectable:
            self.ui.selectable.show()

    def setModels(self):
        for k in self.views.keys():
            if k in self.groups.keys():
                md = ElementModel(self.groups[k])
            else:
                md = ElementModel([])
            self.models.append(md)
            try:
                ig = int(k)
                if (self.__simpleMode & 2) and ig < 0:
                    md.enable = False
                    md.disEnable = False
            except Exception:
                pass
            self.views[k].setModel(md)

            md.componentChecked.connect(self.updateViews)
            md.dirty.connect(self.setDirty)

    @Qt.pyqtSlot()
    def setDirty(self):
        self.dirty.emit()

    def reset(self):
        logger.debug("reset views")
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
        logger.debug("reset views end")

    @Qt.pyqtSlot()
    def updateViews(self):
        logger.debug("update views")
        for vw in self.views.values():
            vw.reset()

        logger.debug("update views end")
