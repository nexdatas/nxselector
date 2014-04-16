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
## \file Automatic.py
# automatic tab

""" automatic tab """


from PyQt4.QtGui import (QHBoxLayout,
    QGroupBox, QGridLayout, QFrame, QWidgetItem)

from .Element import CPElement
from .ElementModel import ElementModel
from .Views import CheckerView

import logging
logger = logging.getLogger(__name__)


## main window class
class Automatic(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None, userView = CheckerView,
                 rowMax = 0):
        self.ui = ui
        self.state = state
        self.userView = userView
        self.rowMax = rowMax

        self.agroup = []
        self.aview = None
        self.layout = None

    def createGUI(self):

        self.ui.automatic.hide()
        if self.layout:
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
        else: 
            self.layout = QHBoxLayout(self.ui.automatic)


        mframe = QFrame(self.ui.automatic)
        mframe.setFrameShape(QFrame.StyledPanel)
        mframe.setFrameShadow(QFrame.Raised)
        layout_groups = QHBoxLayout(mframe)

        mgroup = QGroupBox(mframe)
        mgroup.setTitle("Automatic")
        layout_auto = QGridLayout(mgroup)
        mview = self.userView(mgroup)
        mview.rowMax = self.rowMax

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)
            
        self.aview = mview
        self.layout.addWidget(mframe)
        self.ui.automatic.update()
        if self.ui.tabWidget.currentWidget() == self.ui.automatic:
            self.ui.automatic.show()

    def updateGroups(self):
        self.agroup = []
        for cp in self.state.acpgroup.keys():
            self.agroup.append(
                CPElement(cp, self.state, 
                          group = self.state.acpgroup))


    def setModels(self):
        md = ElementModel(self.agroup)
        md.enable = False
        self.aview.setModel(md)    

    def updateViews(self):
        self.aview.reset()

    def reset(self):
        self.createGUI()
        self.updateGroups()
        self.setModels()
        self.updateViews()
        
