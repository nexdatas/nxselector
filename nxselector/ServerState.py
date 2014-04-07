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
## \file ServerState.py
# state of sardana recorder server

""" state of recorder server """

import os
import PyTango
import json

import logging
logger = logging.getLogger(__name__)


## main window class
class ServerState(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, server=None):
        self.server = server
        self.__dp = None
        ## tango database
        self.__db = PyTango.Database()
        self.setServer()
        self.fetchSettings()

        self.scanDir = None
        self.scanFile = []
        self.scanID = 0

        self.timer = None
        self.mntgrp = None
        self.macroServer = None 

        self.configDevice = None
        self.writerDevice = None

        self.appendEntry = None
        self.timeZone = None

        self.dynamicComponents = None
        self.dynamicLinks = None
        self.dynamicPath = None


        self.dsgroup = {}
        self.dslabels = {}
        self.cpgroup = {}
        self.acpgroup = {}
        self.acplist = []
        self.mcplist = []
        self.description = []


    def fetchSettings(self):
        self.dsgroup = self.loadDict("DataSourceGroup") 
        self.dslabels = self.loadDict("DataSourceLabels") 
        self.cpgroup = self.loadDict("ComponentGroup") 
        self.acpgroup = self.loadDict("AutomaticComponentGroup") 
        self.acplist = self.loadList("AutomaticComponents") 
        self.mcplist = self.getList("MandatoryComponents") 
        self.description = self.loadList("Description", True) 
        self.fetchFileData()

    def fetchFileData(self):
        self.scanDir = self.loadData("ScanDir")
        self.scanFile = self.loadData("ScanFile")
        self.scanID = self.loadData("ScanID")

        self.timer = self.loadData("Timer")
        self.mntgrp = self.loadData("ActiveMntGrp")
        self.macroServer = self.loadData("MacroServer")

        self.configDevice = self.loadData("ConfigDevice")
        self.writerDevice = self.loadData("WriterDevice")
            
        self.appendEntry = self.loadData("AppendEntry")
        self.timeZone = self.loadData("TimeZone")

        self.dynamicComponents = self.loadData("DynamicComponents")
        self.dynamicLinks = self.loadData("DynamicLinks")
        self.dynamicPath = self.loadData("DynamicPath")

    def storeFileData(self):
        self.storeData("ScanDir", self.scanDir)
        self.storeData("ScanFile", self.scanFile)
#        self.storeData("ScanID", self.scanID)

        self.storeData("Timer", self.timer)
        self.storeData("ActiveMntGrp", self.mntgrp)
        self.storeData("MacroServer", self.macroServer)

        self.storeData("ConfigDevice", self.configDevice)
        self.storeData("WriterDevice", self.writerDevice)

        self.storeData("AppendEntry", self.appendEntry)
        self.storeData("TimeZone", self.timeZone)

        self.storeData("DynamicComponents", self.dynamicComponents)
        self.storeData("DynamicLinks", self.dynamicLinks)
        self.storeData("DynamicPath", self.dynamicPath)


    def storeSettings(self):
        self.storeDict("DataSourceGroup", self.dsgroup) 
        self.storeDict("ComponentGroup", self.cpgroup) 
        self.storeFileData()

    def updateMntGrp(self):
        self.storeSettings()
        self.__dp.UpdateMntGrp()

    def setServer(self):
        if not self.server:
            servers = self.__db.get_device_exported_for_class(
                "NXSRecSelector").value_string
            if len(servers):
                self.server = servers[0]                

        found = False
        cnt = 0
        self.__dp = PyTango.DeviceProxy(self.server)


        while not found and cnt < 1000:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if self.__dp.state() != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError):
                time.sleep(0.01)
                found = False
                if cnt == 999:
                    raise
            cnt += 1




    def loadDict(self, name):    
        if not self.__dp:
            self.setServer()
        dsg = self.__dp.read_attribute(name).value
        res = {}
        if dsg:
            dc = json.loads(dsg)
            if isinstance(dc, dict):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    def storeDict(self, name, value):    
        if not self.__dp:
            self.setServer()

        jvalue = json.dumps(value)    
        self.__dp.write_attribute(name, jvalue)
        logger.debug(" %s = %s" % (name, jvalue) )


    def storeData(self, name, value):    
        if not self.__dp:
            self.setServer()

        self.__dp.write_attribute(name, value)
        logger.debug(" %s = %s" % (name, value) )


    def loadList(self, name, encoded = False):    
        if not self.__dp:
            self.setServer()
        dc = self.__dp.read_attribute(name).value
        logger.debug(dc)
        res = []
        if dc:
            if encoded:
                dc = json.loads(dc)
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    def loadData(self, name):    
        if not self.__dp:
            self.setServer()
        dc = self.__dp.read_attribute(name).value
        logger.debug(dc)
        return dc


    def getList(self, name):    
        if not self.__dp:
            self.setServer()
        dc = self.__dp.command_inout(name)
        logger.debug(dc)
        res = []
        if dc:
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res) )
        return res


    ## update a list of Disable DataSources
    def disableDataSources(self):
        res = self.description
        dds = set()

        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if cp in self.cplist or cp in self.mcplist or cp in self.acplist:
                        for ds in dss.keys():
                            dds.add(ds)
        return list(dds)


    ## provides disable datasources
    ddslist = property(disableDataSources,
                       doc = 'provides disable datasources')


    ## update a list of Components
    def Components(self):
        if isinstance(self.cpgroup, dict):
            return [cp for cp in self.cpgroup.keys() if self.cpgroup[cp]]
        else:
            return []

    ## provides disable datasources
    cplist = property(Components,
                       doc = 'provides selected components')
