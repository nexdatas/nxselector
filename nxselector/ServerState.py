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
import time 
import pickle

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

        self.cnfFile = "/"

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
        self.atlist = []
        self.mcplist = []
        self.description = []


    def fetchSettings(self):
        self.dsgroup = self.loadDict("DataSourceGroup") 
        self.dslabels = self.loadDict("DataSourceLabels") 
        self.cpgroup = self.loadDict("ComponentGroup") 
        self.acpgroup = self.loadDict("AutomaticComponentGroup") 
        self.acplist = self.loadList("AutomaticComponents") 
        self.atlist = list(self.loadList("AvailableTimers"))
        self.mcplist = self.getList("MandatoryComponents") 
        self.description = self.loadList("Description", True) 
        self.fetchFileData()
        self.fetchEnvData()

    def fetchEnvData(self):
        params = {"ScanDir":"scanDir",
                  "ScanFile":"scanFile",
                  "ScanID":"scanID",
                  "ActiveMntGrp":"mntgrp"}

        dp = self.openProxy(self.macroServer)
        rec = dp.Environment
        if rec[0] == 'pickle':
            dc = pickle.loads(rec[1])
            if 'new' in dc.keys() :
                for var, attr in params.items():
                    if var in dc['new'].keys():
                        setattr(self, attr, dc['new'][var])
    
#        self.scanDir = self.loadData("ScanDir")
#        self.scanFile = self.loadData("ScanFile")
#        self.scanID = self.loadData("ScanID")
#        self.mntgrp = str(self.loadData("ActiveMntGrp"))

    def fetchFileData(self):
        self.timer = self.loadData("Timer")
        self.macroServer = self.loadData("MacroServer")

        self.configDevice = self.loadData("ConfigDevice")
        self.writerDevice = self.loadData("WriterDevice")
            
        self.appendEntry = self.loadData("AppendEntry")
        self.timeZone = self.loadData("TimeZone")

        self.dynamicComponents = self.loadData("DynamicComponents")
        self.dynamicLinks = self.loadData("DynamicLinks")
        self.dynamicPath = self.loadData("DynamicPath")
        self.cnfFile = self.loadData("ConfigFile")


    def storeEnvData(self):
        params = {"ScanDir":"scanDir",
                  "ScanFile":"scanFile",
#                  "ScanID":"scanID"],
                  "ActiveMntGrp":"mntgrp"}

        s0 = time.time()

        dp = self.openProxy(self.macroServer)
        if not self.__dp:
            self.setServer()
        full = self.__dp.FindMntGrp(self.mntgrp)    
        if not full:
            pn = dp.get_property("PoolNames")["PoolNames"]
            if len(pn)>0:
                pool = self.openProxy(pn[0])
            if not pool and len(pools)> 0 :
                pool = pools[0]
            if pool:
                pool.CreateMeasurementGroup([self.mntgrp, self.timer])

        rec = dp.Environment
        if rec[0] == 'pickle':
            dc = pickle.loads(rec[1])
            if 'new' in dc.keys():
                for var, attr in params.items():
                    dc['new'][var] = getattr(self, attr)
                    pk = pickle.dumps(dc)    
                dp.Environment = ['pickle', pk]


        s1 = time.time()
        
#        self.storeData("ScanDir", self.scanDir)
#        self.storeData("ScanFile", self.scanFile)
#        self.storeData("ScanID", self.scanID)
#        self.storeData("ActiveMntGrp", self.mntgrp)
        s2 = time.time()
#        print  "ESTORING", s1-s0, s2-s1

    def storeFileData(self):

        s4 = time.time()
        self.storeData("Timer", self.timer)
        s5 = time.time()
        self.storeData("MacroServer", self.macroServer)

        s6 = time.time()
        self.storeData("ConfigDevice", self.configDevice)
        s7 = time.time()
        self.storeData("WriterDevice", self.writerDevice)
        s8 = time.time()

        self.storeData("AppendEntry", self.appendEntry)
        s9 = time.time()
        self.storeData("TimeZone", self.timeZone)
        s10 = time.time()
        self.storeData("DynamicComponents", self.dynamicComponents)
        s11 = time.time()
        self.storeData("DynamicLinks", self.dynamicLinks)
        s12 = time.time()
        self.storeData("DynamicPath", self.dynamicPath)
        s13 = time.time()
#        print  "FSTORING", s5-s4,s6-s5,s7-s6,s8-s7,s9-s8,s10-s9,s11-s10,s12-s11,s13-s12


    def storeSettings(self):
        s1 = time.time()
        self.storeDict("DataSourceGroup", self.dsgroup) 
        s2 = time.time()
        self.storeDict("DataSourceLabels", self.dslabels) 
        s3 = time.time()
        self.storeDict("ComponentGroup", self.cpgroup) 
        s4 = time.time()
        self.storeFileData()
        s5 = time.time()
        self.storeEnvData()
        s6 = time.time()
#        print  "STORING", s2-s1, s3-s2, s4-s3, s5-s4, s6-s5

    def updateMntGrp(self):
        s1 = time.time() 
        self.storeSettings()
        s2 = time.time() 
        self.__dp.UpdateMntGrp()
        s3 = time.time() 
#        print "UPDATE: STORE, UPDATEMG", s2-s1,s3-s2
            
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
                self.server = servers[0]                

        self.__dp = self.openProxy(self.server)    

    def openProxy(self, server):
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
