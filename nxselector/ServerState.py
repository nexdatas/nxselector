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

import PyTango
import json
import time 

import logging
logger = logging.getLogger(__name__)


## main window class
class ServerState(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, server=None):
        
        self.server = str(server) if server else None
        self.__dp = None
        ## tango database
        self.__db = PyTango.Database()
        self.setServer()
        self.fetchSettings()
            

        self.scanDir = None
        self.scanFile = []
        self.scanID = 0

        self.cnfFile = "/"

        self.timer = None
        self.mntgrp = None
        self.door = None 

        self.configDevice = None
        self.writerDevice = None

        self.appendEntry = None

        self.dynamicComponents = True
        self.dynamicLinks = None
        self.dynamicPath = None


        self.dsgroup = {}
        self.labels = {}
        self.nodisplay = []
        self.cpgroup = {}
        self.acpgroup = {}
        self.acplist = []
        self.atlist = []
        self.mcplist = []
        self.description = []
        self.avcplist = []
        self.avdslist = []
        self.vrcpdict = {}

        self.configvars = {}
        self.datarecord = {}

        self.labellinks = {}
        self.labelpaths = {}
        self.labelshapes = {}
        self.labeltypes = {}

    def fetchSettings(self):
        self.dsgroup = self.loadDict("DataSourceGroup") 
        self.labels = self.loadDict("Labels") 
        self.labellinks = self.loadDict("LabelLinks") 
        self.labelpaths = self.loadDict("LabelPaths") 
        self.labelshapes = self.loadDict("LabelShapes") 
        self.labeltypes = self.loadDict("LabelTypes") 
        self.nodisplay = self.loadList("HiddenElements", True) 
        self.cpgroup = self.loadDict("ComponentGroup") 
        self.avcplist = self.getList("AvailableComponents") 
        self.avdslist = self.getList("AvailableDataSources") 
        self.acpgroup = self.loadDict("AutomaticComponentGroup") 
        self.acplist = self.loadList("AutomaticComponents") 
        self.atlist = list(self.loadList("AvailableTimers"))
        self.mcplist = self.getList("MandatoryComponents") 
        self.description = self.loadList("Description", True) 
        self.vrcpdict = self.loadDict("VariableComponents") 
        self.fullnames = self.loadDict("FullDeviceNames") 
        self.datarecord = self.loadDict("DataRecord") 
        self.configvars = self.loadDict("ConfigVariables") 
        self.fetchFileData()
        self.fetchEnvData()

    def fetchFileData(self):
        self.timer = self.loadData("Timer")
        self.mntgrp = self.loadData("MntGrp")
        self.door = self.loadData("Door")

        self.configDevice = self.loadData("ConfigDevice")
        self.writerDevice = self.loadData("WriterDevice")
            
        self.appendEntry = self.loadData("AppendEntry")

#        self.dynamicComponents = self.loadData("DynamicComponents")
        self.dynamicLinks = self.loadData("DynamicLinks")
        self.dynamicPath = self.loadData("DynamicPath")
        self.cnfFile = self.loadData("ConfigFile")

    def fetchEnvData(self):
        params = {"ScanDir":"scanDir",
                  "ScanFile":"scanFile",
                  "ScanID":"scanID"}


        if not self.__dp:
            self.setServer()

        jvalue = self.__dp.FetchEnvData()
        value = json.loads(jvalue)    
 
        for var, attr in params.items():
            if var in value.keys():
                setattr(self, attr, value[var])
        logger.debug("fetch Env: %s" % ( jvalue) )




    def storeEnvData(self):
        params = {"ScanDir":"scanDir",
                  "ScanFile":"scanFile",
                  "NeXusSelectorDevice":"server",
#                  "ScanID":"scanID"
                  }

        if not self.__dp:
            self.setServer()

        value = {}    
        for var, attr in params.items():
            value[var] = getattr(self, attr)
        jvalue = json.dumps(value)    
        self.scanID = self.__dp.StoreEnvData(jvalue)
        logger.debug("Store Env: %s" % ( jvalue) )

    def storeFileData(self):

        self.storeData("Timer", self.timer)
        self.storeData("Door", self.door)
        self.storeData("MntGrp", self.mntgrp)

        self.storeData("ConfigDevice", self.configDevice)
        self.storeData("WriterDevice", self.writerDevice)

        self.storeData("AppendEntry", self.appendEntry)
        self.storeData("DynamicComponents", self.dynamicComponents)
        self.storeData("DynamicLinks", self.dynamicLinks)
        self.storeData("DynamicPath", self.dynamicPath)


    def storeSettings(self):
        self.storeDict("DataSourceGroup", self.dsgroup) 
        self.storeDict("Labels", self.labels) 
        self.storeDict("LabelLinks", self.labellinks) 
        self.storeDict("LabelPaths", self.labelpaths) 
        self.storeDict("LabelShapes", self.labelshapes) 
        self.storeDict("LabelTypes", self.labeltypes) 
        self.storeList("HiddenElements", self.nodisplay) 
        self.storeDict("ComponentGroup", self.cpgroup) 
        self.storeDict("DataRecord", self.datarecord) 
        self.storeDict("ConfigVariables", self.configvars) 
        self.storeFileData()
        self.storeEnvData()

    def updateMntGrp(self):
        if not self.mntgrp:
            raise Exception("ActiveMntGrp not defined")
        if not self.scanFile:
            raise Exception("ScanFile not defined")
        if not self.scanDir:
            raise Exception("ScanDir not defined")
        self.storeSettings()
        self.__dp.UpdateMntGrp()
            
    def save(self, filename):
        self.storeSettings()
        self.storeData("ConfigFile", filename)
        self.__dp.SaveConfiguration()

    def load(self, filename):
        self.storeData("ConfigFile", filename)
        self.__dp.LoadConfiguration()
        self.fetchSettings()

    def updateControllers(self):
        self.__dp.UpdateControllers()

    def setServer(self):
        if not self.server:
            servers = self.__db.get_device_exported_for_class(
                "NXSRecSelector").value_string
            if len(servers):
                self.server = str(servers[0])

        self.__dp = self.openProxy(self.server)    

    @classmethod
    def openProxy(cls, server):
        found = False
        cnt = 0
        proxy = PyTango.DeviceProxy(server)

        while not found and cnt < 100:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if proxy.state() != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError):
                time.sleep(0.01)
                found = False
                if cnt == 99:
                    raise
            cnt += 1
        return proxy


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




    def storeList(self, name, value):    
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
        dds = {}

        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if cp in self.cplist or cp in self.mcplist \
                            or cp in self.acplist:
                        for ds, values in dss.items():
                            for vl in values:
                                if len(vl) > 0 and vl[0] == 'STEP':
                                    dds[ds]  = cp
                                    break
        if self.timer not in dds.keys():
            dds[self.timer] = ''
        return dds

    def clientRecords(self):
        res = self.description
        dds = {}

        for cpg in res:
            for dss in cpg.values():
                if isinstance(dss, dict):
                    for ds, values in dss.items():
                        for vl in values:
                            if len(vl) > 1 and vl[1] == 'CLIENT':
                                dds[ds]  = vl[2]
        return dds                       
                                
    ## provides disable datasources
    ddsdict = property(disableDataSources,
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
