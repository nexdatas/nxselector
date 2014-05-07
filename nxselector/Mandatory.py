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
## \file Mandatory.py
# mandatory tab

""" mandatory tab """


from PyQt4.QtGui import (QHBoxLayout,
    QGroupBox, QGridLayout,
    QFrame, QWidgetItem)

from .Element import CPElement
from .ElementModel import ElementModel

from .Views import CheckerView

import logging
logger = logging.getLogger(__name__)

## main window class
class Mandatory(object):

    ## constructor
    def __init__(self, ui, state = None, userView = CheckerView, 
                 rowMax=0):
        self.ui = ui
        self.state = state
        self.userView = userView
        self.rowMax = rowMax
        self.layout = None
        
        self.mgroup = []
        self.mview = None

    def updateGroups(self):
        self.mgroup = []
        mcpgroup = {}
        for cp in self.state.mcplist:
            mcpgroup[cp] = True
        for cp in mcpgroup.keys():
            self.mgroup.append(
                CPElement(cp, self.state, group = mcpgroup))


    def createGUI(self):

        self.ui.mandatory.hide()
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
            self.layout = QHBoxLayout(self.ui.mandatory)
            

        mframe = QFrame(self.ui.mandatory)
        mframe.setFrameShape(QFrame.StyledPanel)
        mframe.setFrameShadow(QFrame.Raised)
        layout_groups = QHBoxLayout(mframe)

        mgroup = QGroupBox(mframe)
        mgroup.setTitle("")
        layout_auto = QGridLayout(mgroup)
        mview = self.userView(mgroup)
        mview.rowMax = self.rowMax

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)
            
        self.mview = mview
        self.layout.addWidget(mframe)
        self.ui.mandatory.update()
        if self.ui.tabWidget.currentWidget() == self.ui.mandatory:
            self.ui.mandatory.show()


    def setModels(self):
        md = ElementModel(self.mgroup)
        md.enable = False
        self.mview.setModel(md)    


    def updateViews(self):
        self.mview.reset()

    def reset(self):
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
        
