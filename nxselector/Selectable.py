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
## \file Selectable.py
# selactable tab

""" selactable tab """

import os
import PyTango
import json



from PyQt4 import QtCore, QtGui

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView, QDialogButtonBox,
    QLabel, QFrame, QHeaderView)

from .Element import Element, DSElement, CPElement, CP, DS
from .ElementModel import ElementModel, ElementDelegate

from .Views import TableView, CheckerView, RadioView
from .Frames import Frames

import logging
logger = logging.getLogger(__name__)

## main window class
class Selectable(object):

    ## constructor
    def __init__(self, ui, state = None, userView = CheckerView):
        self.ui = ui
        self.state = state
        self.userView = userView

        self.layout = None


        ## frames/columns/groups
        self.mframes = []
        self.mframes.append(Frames(
                '[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'))
        self.mframes.append(Frames(
                '[[[["My Controllers", 0]]],[[["My Components", 1]]]]'))
        self.mframes.append(Frames())
        self.cframe = 1
        self.frames = self.mframes[self.cframe]

        self.mgroups = None
        self.groups = {}
        self.availableGroups = set()
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
            if int(k) in self.availableGroups:
                self.groups[int(k)] = []
                for elem in gr:
                    if elem[1] == DS:
                        self.groups[int(k)].append(
                            DSElement(elem[0], self.state))
                        uds.add(elem[0])
                    elif elem[1] == CP: 
                        self.groups[int(k)].append(
                            CPElement(elem[0], self.state))
                        ucp.add(elem[0])
        
        for ds, flag in self.state.dsgroup.items():
            if ds not in uds:
                if DS not in self.groups:
                    self.groups[DS] = []
                self.groups[DS].append(DSElement(ds, self.state))
        for cp, flag in self.state.cpgroup.items():
            if cp not in ucp and cp not in self.state.mcplist \
                    and cp not in self.state.acplist:
                if CP not in self.groups:
                    self.groups[CP] = []
                self.groups[CP].append(CPElement(cp, self.state))
#        for k in self.groups.keys():
#            self.groups[k] = sorted(self.groups[k])
            


    def createGUI(self):
        
        self.ui.selectable.hide()
        if self.layout:
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QtGui.QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
        else:
            self.layout = QHBoxLayout(self.ui.selectable)
            
        self.views = {} 

        for frame in self.frames:
            mframe = QFrame(self.ui.selectable)
            mframe.setFrameShape(QFrame.StyledPanel)
            mframe.setFrameShadow(QFrame.Raised)
            layout_columns = QHBoxLayout(mframe)

            for column in frame: 
                layout_groups = QVBoxLayout()

                for group in column:
                    mgroup = QGroupBox(mframe)
                    mgroup.setTitle(group[0])
                    layout_auto = QGridLayout(mgroup)
                    mview = self.userView(mgroup)

                    layout_auto.addWidget(mview, 0, 0, 1, 1)
                    layout_groups.addWidget(mgroup)

                    self.availableGroups.add(group[1])
                    self.views[group[1]] = mview

                layout_columns.addLayout(layout_groups)

            self.layout.addWidget(mframe)
        self.ui.selectable.update()
        if self.ui.tabWidget.currentWidget() == self.ui.selectable:
            self.ui.selectable.show()


    def setModels(self):
        for k, vw in self.views.items():
            if k in self.groups.keys():
                md = ElementModel(self.groups[k])
            else:
                md = ElementModel([])
                
            self.views[k].setModel(md)
            md.connect(md, SIGNAL("componentChecked"), 
                       self.updateViews)
#            self.views[k].setItemDelegate(ElementDelegate(self))

    def reset(self):
        self.createGUI()
        self.updateGroups()
        self.setModels()
        self.updateViews()

    def updateViews(self):
        logger.debug("update views")
        for vw in self.views.values():
            vw.reset()

