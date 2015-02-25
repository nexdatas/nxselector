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
## \file State.py
# automatic tab

""" automatic tab """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .Element import CPElement
from .ElementModel import ElementModel
from .Views import CheckerView

import logging
logger = logging.getLogger(__name__)


## main window class
class State(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None, userView=CheckerView, rowMax=0):
        self.ui = ui
        self.state = state
        self.userView = userView
        self.rowMax = rowMax
        self.layout = None

        self.agroup = []
        self.aview = None

        self.mgroup = []
        self.mview = None

    def createGUI(self):

        self.ui.state.hide()
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
            self.layout = Qt.QHBoxLayout(self.ui.state)

        mframe = Qt.QFrame(self.ui.state)
        mframe.setFrameShape(Qt.QFrame.StyledPanel)
        mframe.setFrameShadow(Qt.QFrame.Raised)
        layout_groups = Qt.QHBoxLayout(mframe)

        mgroup = Qt.QGroupBox(mframe)
        mgroup.setTitle("Beamline")
        layout_auto = Qt.QGridLayout(mgroup)
        mview = self.userView(mgroup)
        mview.rowMax = self.rowMax
        if hasattr(mview, 'dmapper'):
            mview.dmapper = None

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)

        self.mview = mview
        self.layout.addWidget(mframe)

        mframe = Qt.QFrame(self.ui.state)
        mframe.setFrameShape(Qt.QFrame.StyledPanel)
        mframe.setFrameShadow(Qt.QFrame.Raised)
        layout_groups = Qt.QHBoxLayout(mframe)

        mgroup = Qt.QGroupBox(mframe)
        mgroup.setTitle("Discipline")
        layout_auto = Qt.QGridLayout(mgroup)
        mview = self.userView(mgroup)
        mview.rowMax = self.rowMax
        if hasattr(mview, 'dmapper'):
            mview.dmapper = None

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)

        self.aview = mview
        self.layout.addWidget(mframe)

        self.ui.state.update()
        if self.ui.tabWidget.currentWidget() == self.ui.state:
            self.ui.state.show()

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

    def setModels(self):
        md = ElementModel(self.agroup)
        md.enable = False
        self.aview.setModel(md)
        md.connect(md, Qt.SIGNAL("componentChecked"),
                   self.__componentChecked)

        md = ElementModel(self.mgroup)
        md.enable = False
        self.mview.setModel(md)
        md.connect(md, Qt.SIGNAL("componentChecked"),
                   self.__componentChecked)

    def __componentChecked(self):
        self.ui.state.emit(Qt.SIGNAL("componentChecked"))

    def updateViews(self):
        self.aview.reset()
        self.mview.reset()

    def reset(self):
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
