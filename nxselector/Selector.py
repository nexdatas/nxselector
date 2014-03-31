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
    QMessageBox, QIcon, QTableView,
    QLabel, QFrame)

from .Frames import Frames
from .Element import Element, DSElement, CPElement, CP, DS
from .ElementModel import ElementModel, ElementDelegate
from .ui.ui_selector import Ui_Selector


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

        self.server = server
        ## device proxy
        self.dp = None
        ## tango database
        self.__db = PyTango.Database()
        
        self.fetchSettings()


        ## user interface
        self.ui = Ui_Selector()

        ## frames/columns/groups
        self.frames =  Frames([
            [[("Counters1", 0), ("Counters2", 2)], [("VCounters", 3)]],
            [[("MCAs", 1), ("SCAs", 4)]],
            [[("Misc", 5) ]]
            ])
        self.frames = Frames([[[("My Controllers", 0)]],[[("My Components", 1)]]])
#        self.frames =  Frames()

        self.groups = {2:[DSElement("ct01", self.dp), DSElement("ct02",self.dp)],
                       5:[CPElement("appscan", self.dp)]}

        self.availableGroups = set()

        self.views = {} 
        self.setServer()
        
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
                    print "ELEM", elem.name
                    if elem.eltype == DS:
                        uds.add(elem.name)
                        print "ELEM2 DS", elem.name
                    elif elem.eltype == CP: 
                        print "ELEM2 CP", elem.name
                        ucp.add(elem.name)
        for ds, flag in self.dsgroup.items():
            if ds not in uds:
                if DS not in self.groups:
                    self.groups[DS] = []
                self.groups[DS].append(DSElement(ds, self.dp))
        for cp, flag in self.cpgroup.items():
            if cp not in ucp and cp not in self.mcplist and cp not in self.acplist:
                if CP not in self.groups:
                    self.groups[CP] = []
                self.groups[CP].append(CPElement(cp, self.dp))

                
                    


    def fetchSettings(self):
        self.dsgroup = self.loadDict("DataSourceGroup") 
        self.dslabels = self.loadDict("DataSourceLabels") 
        self.cpgroup = self.loadDict("ComponentGroup") 
        self.acpgroup = self.loadDict("AutomaticComponentGroup") 
        self.acplist = self.loadList("AutomaticComponents") 
        self.ddslist = self.loadList("DisableDataSources") 
        self.mcplist = self.getList("MandatoryComponents") 

        

    def setServer(self):
        if self.server is None:
            servers = self.__db.get_device_exported_for_class(
                "NXSRecSettings").value_string
            if len(servers):
                self.server = servers[0]                

        found = False
        cnt = 0
        self.dp = PyTango.DeviceProxy(self.server)


        while not found and cnt < 1000:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if self.dp.state() != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError):
                time.sleep(0.01)
                found = False
                if cnt == 999:
                    raise
            cnt += 1



    def loadDict(self, name):    
        if not self.dp:
            self.setServer()
        dsg = self.dp.read_attribute(name).value
        res = {}
        if dsg:
            dc = json.loads(dsg)
            if isinstance(dc, dict):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    def loadList(self, name, encoded = False):    
        if not self.dp:
            self.setServer()
        dc = self.dp.read_attribute(name).value
        logger.debug(dc)
        res = []
        if dc:
            if encoded:
                dc = json.loads(dc)
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    def getList(self, name):    
        if not self.dp:
            self.setServer()
        dc = self.dp.command_inout(name)
        logger.debug(dc)
        res = []
        if dc:
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
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
                    mview = QTableView(mgroup)

                    layout_auto.addWidget(mview, 0, 0, 1, 1)
                    layout_groups.addWidget(mgroup)

                    self.availableGroups.add(group[1])
                    self.views[group[1]] = mview
                    

                layout_columns.addLayout(layout_groups)

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
            
    def updateViews(self):
        for vw in self.views.values():
            vw.reset()

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))

