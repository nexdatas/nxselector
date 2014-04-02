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
## \package nxselecto nexdatas
## \file Selector.py
# Main window of the application

""" main window application dialog """

import os
import PyTango
import json

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView, QDialogButtonBox,
    QLabel, QFrame, QHeaderView)

from .Frames import Frames
from .Element import Element, DSElement, CPElement, CP, DS
from .ElementModel import ElementModel, ElementDelegate
from .ServerState import ServerState
from .ui.ui_selector import Ui_Selector

from .Views import TableView, CheckerView

import logging
logger = logging.getLogger(__name__)

    

## main window class
class Selector(QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, parent=None):
        super(Selector, self).__init__(parent)
        logger.debug("PARAMETERS: %s %s", 
                     server, parent)

        
        self.state = ServerState(server)
        self.state.fetchSettings()


        ## user interface
        self.ui = Ui_Selector()

        ## frames/columns/groups
        self.frames =  Frames([
            [[("Counters1", 0), ("Counters2", 2)], [("VCounters", 3)]],
            [[("MCAs", 1), ("SCAs", 4)]],
            [[("Misc", 5) ]]
            ])

#        self.frames = Frames([[[("My Controllers", 0)]],[[("My Components", 1)]]])
#        self.frames =  Frames()

        self.groups = {2:[DSElement("ct01", self.state), DSElement("ct02",self.state)],
                       5:[CPElement("appscan", self.state)]}

        self.userView = TableView
        self.userView = CheckerView

        self.agroup = []

        self.mgroup = []

        self.availableGroups = set()

        self.views = {} 
        
        logger.debug("GROUPS: %s " % self.groups)

        self.createGUI()            
        self.updateGroups()
        self.setModels()
        
        settings = QSettings()
        self.restoreGeometry(
            settings.value("Selector/Geometry").toByteArray())

    def updateGroups(self):
        ucp = set()
        uds = set()
        for k, gr in self.groups.items():
            if k in self.availableGroups:
                for elem in gr:
                    if elem.eltype == DS:
                        uds.add(elem.name)
                    elif elem.eltype == CP: 
                        ucp.add(elem.name)
        for ds, flag in self.state.dsgroup.items():
            if ds not in uds:
                if DS not in self.groups:
                    self.groups[DS] = []
                self.groups[DS].append(DSElement(ds, self.state))
        for cp, flag in self.state.cpgroup.items():
            if cp not in ucp and cp not in self.state.mcplist and cp not in self.state.acplist:
                if CP not in self.groups:
                    self.groups[CP] = []
                self.groups[CP].append(CPElement(cp, self.state))

        self.agroup =[]
        for cp, flag in self.state.acpgroup.items():
                self.agroup.append(CPElement(cp, self.state, group = self.state.acpgroup))
                
        self.mgroup =[]
        mcpgroup = {}
        for cp in self.state.mcplist:
            mcpgroup[cp] = True
        for cp, flag in mcpgroup.items():
                self.mgroup.append(CPElement(cp, self.state, group = mcpgroup))

                
                    



        



    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
        self.createSelectableGUI()
        self.createAutomaticGUI()
        self.createMandatoryGUI()

        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Apply), 
                     SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Reset), 
                     SIGNAL("clicked()"), self.reset)


    def createSelectableGUI(self):
        layout = QHBoxLayout(self.ui.selectable)

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

            layout.addWidget(mframe)


    def createAutomaticGUI(self):
        layout = QHBoxLayout(self.ui.automatic)


        mframe = QFrame(self.ui.automatic)
        mframe.setFrameShape(QFrame.StyledPanel)
        mframe.setFrameShadow(QFrame.Raised)
        layout_groups = QHBoxLayout(mframe)

        mgroup = QGroupBox(mframe)
        mgroup.setTitle("Automatic")
        layout_auto = QGridLayout(mgroup)
        mview = self.userView(mgroup)

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)
            
        self.aview = mview
        layout.addWidget(mframe)


    def createMandatoryGUI(self):
        layout = QHBoxLayout(self.ui.mandatory)


        mframe = QFrame(self.ui.mandatory)
        mframe.setFrameShape(QFrame.StyledPanel)
        mframe.setFrameShadow(QFrame.Raised)
        layout_groups = QHBoxLayout(mframe)

        mgroup = QGroupBox(mframe)
        mgroup.setTitle("Mandatory")
        layout_auto = QGridLayout(mgroup)
        mview = self.userView(mgroup)

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)
            
        self.mview = mview
        layout.addWidget(mframe)


            
    def setModels(self):
        for k, vw in self.views.items():
            if k in self.groups.keys():
                md = ElementModel(self.groups[k])
            else:
                md = ElementModel([])
                
            self.views[k].setModel(md)
            md.connect(md, SIGNAL("componentChecked"), self.updateViews)
#            self.views[k].setItemDelegate(ElementDelegate(self))
#            self.views[k].resizeColumnsToContents()
        md = ElementModel(self.agroup)
        md.enable = False
        self.aview.setModel(md)    

        md = ElementModel(self.mgroup)
        md.enable = False
        self.mview.setModel(md)    
        
            
    def updateViews(self):
        logger.debug("update views")
        for vw in self.views.values():
            vw.reset()
#            vw.resizeColumnsToContents()

    def __saveSettings(self):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))
        
            
    def closeEvent(self, event):
        self.__saveSettings()

    def reset(self):
        self.state.fetchSettings()
        self.updateViews()

    def apply(self):
        self.state.updateMntGrp()
