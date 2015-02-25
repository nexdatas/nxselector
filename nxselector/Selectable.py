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

from .Views import CheckerView

import logging
logger = logging.getLogger(__name__)


## main window class
class Selectable(object):

    ## constructor
    def __init__(self, ui, state=None, userView=CheckerView, rowMax=0):
        self.ui = ui
        self.state = state
        self.userView = userView
        self.rowMax = rowMax
        self.layout = None

        self.frames = None
        self.mgroups = None
        self.groups = {}
        self.views = {}

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
#        for k in self.groups.keys():
#            self.groups[k] = sorted(self.groups[k])

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

    def createGUI(self):

        self.ui.selectable.hide()
        if self.layout:
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, Qt.QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
        else:
            self.layout = Qt.QHBoxLayout(self.ui.selectable)

        self.views = {}
        frames = Frames(self.frames, DS in self.groups, CP in self.groups)
        for frame in frames:
            mframe = Qt.QFrame(self.ui.selectable)
            mframe.setFrameShape(Qt.QFrame.StyledPanel)
            mframe.setFrameShadow(Qt.QFrame.Raised)
            layout_columns = Qt.QHBoxLayout(mframe)

            for column in frame:
                layout_groups = Qt.QVBoxLayout()

                for group in column:
                    mgroup = Qt.QGroupBox(mframe)
                    mgroup.setTitle(group[0])
                    layout_auto = Qt.QGridLayout(mgroup)
                    mview = self.userView(mgroup)
                    mview.rowMax = self.rowMax

                    layout_auto.addWidget(mview, 0, 0, 1, 1)
                    layout_groups.addWidget(mgroup)

                    self.views[group[1]] = mview

                layout_columns.addLayout(layout_groups)

            self.layout.addWidget(mframe)
        self.ui.selectable.update()
        if self.ui.tabWidget.currentWidget() == self.ui.selectable:
            self.ui.selectable.show()

    def setModels(self):
        for k in self.views.keys():
            if k in self.groups.keys():
                md = ElementModel(self.groups[k])
            else:
                md = ElementModel([])

            self.views[k].setModel(md)
            md.connect(md, Qt.SIGNAL("componentChecked"),
                       self.updateViews)
            md.connect(md, Qt.SIGNAL("dirty"),
                       self.dirty)

    def dirty(self):
        self.ui.selectable.emit(Qt.SIGNAL("dirty"))

    def reset(self):
        logger.debug("reset views")
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
        logger.debug("reset views end")

    def updateViews(self):
        logger.debug("update views")
        for vw in self.views.values():
            vw.reset()

        logger.debug("update views end")
