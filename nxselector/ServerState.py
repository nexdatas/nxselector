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
import subprocess

import logging
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt


## main window class
class ServerState(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, server=None):

        self.server = None
        self.__db = PyTango.Database()
        self.__dp = None

        self.__timeout = 25000

        self.findServer(server)

        ## tango database
        self.errors = []

        self.scanDir = None
        self.scanFile = []
        self.scanID = 0

        self.cnfFile = "/"

        self.timers = None
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
        self.avmglist = []
        self.vrcpdict = {}

        self.orderedchannels = []

        self.configvars = {}
        self.datarecord = {}
        self.fullnames = {}

        self.labellinks = {}
        self.labelpaths = {}
        self.labelshapes = {}
        self.labeltypes = {}

        try:
            self.setServer()
            if self.server:
                self.__dp.init()
                self.__dp.ping()
        except Exception as e:
            self.server = None
            raise
        logger.debug("DP %s" % type(self.__dp))

    def grepServer(self):
        server = None
        try:
            pipe = subprocess.Popen("ps -ef | grep 'NXSRecSelecto'",
                                    stdout=subprocess.PIPE,
                                    shell=True, bufsize=10000).stdout
            res = pipe.read().split("\n")
            cres = [r for r in res if 'NXSRecSelector' in r]
            mi = 0
            if len(cres) > 0:
                command = cres[0].split()
                for i in range(len(command)):
                    if 'NXSRecSelector' in command[i]:
                        mi = i
                        break
                if len(command) > mi + 1:
                    instance = command[mi + 1]
                    server = self.__db.get_device_class_list(
                        "NXSRecSelector/%s" % instance).value_string[2]
        except:
            pass
        return server

    def findServer(self, server=None):
        if server is None:
            servers = self.__db.get_device_exported_for_class(
                "NXSRecSelector").value_string
            if len(servers):
                if len(servers) > 1:
                    gserver = self.grepServer()
                    if gserver in servers:
                        self.server = str(gserver)
                else:
                    self.server = str(servers[0])
            else:
                self.server = None
        elif not server:
            self.server = None
        else:
            self.server = str(server)

    def fetchSettings(self):
        if not self.__dp:
            self.setServer()
        if not self.server:
            self.__dp.importAllEnv()
        self.dsgroup = self.loadDict("dataSourceGroup")
        self.labels = self.loadDict("labels")
        self.labellinks = self.loadDict("labelLinks")
        self.labelpaths = self.loadDict("labelPaths")
        self.labelshapes = self.loadDict("labelShapes")
        self.labeltypes = self.loadDict("labelTypes")
        self.nodisplay = self.loadList("hiddenElements", True)
        self.orderedchannels = self.loadList("orderedChannels", True)
        self.cpgroup = self.loadDict("componentGroup")
        self.avcplist = self.getList("availableComponents")
        self.avdslist = self.getList("availableDataSources")
        self.avmglist = self.getList("availableMeasurementGroups")
        self.acpgroup = self.loadDict("automaticComponentGroup")
        self.acplist = self.loadList("automaticComponents")

        self.adslist = self.loadList("automaticDataSources", True)
        self.atlist = list(self.loadList("availableTimers"))
        self.mcplist = self.getList("mandatoryComponents")
        self.description = self.loadList("description", True)
        self.vrcpdict = self.loadDict("variableComponents")
        self.fullnames = self.loadDict("fullDeviceNames")
        self.datarecord = self.loadDict("dataRecord")
        self.configvars = self.loadDict("configVariables")

        self.fetchFileData()
        self.fetchEnvData()

    def fetchFileData(self):
        self.timers = self.loadList("timer", True)
        self.mntgrp = self.loadData("mntGrp")
        try:
            self.door = self.loadData("door")
        except:
            self.storeData("door", "")
            self.door = self.loadData("door")

        self.configDevice = self.loadData("configDevice")
        self.writerDevice = self.loadData("writerDevice")

        self.appendEntry = self.loadData("appendEntry")

#        self.dynamicComponents = self.loadData("dynamicComponents")
        self.dynamicLinks = self.loadData("dynamicLinks")
        self.dynamicPath = self.loadData("dynamicPath")
        self.cnfFile = self.loadData("configFile")

    def fetchEnvData(self):
        params = {"ScanDir": "scanDir",
                  "ScanFile": "scanFile",
                  "ScanID": "scanID"}

        if not self.__dp:
            self.setServer()

        jvalue = self.__dp.fetchEnvData()
        value = json.loads(jvalue)

        for var, attr in params.items():
            if var in value.keys():
                setattr(self, attr, value[var])
        logger.debug("fetch Env: %s" % (jvalue))

    def storeEnvData(self):
        params = {"ScanDir": "scanDir",
                  "ScanFile": "scanFile",
                  "NeXusSelectorDevice": "server",
#                  "ScanID": "scanID"
                  }

        if not self.__dp:
            self.setServer()

        value = {}
        for var, attr in params.items():
            value[var] = getattr(self, attr)
        jvalue = json.dumps(value)
        self.scanID = self.__dp.storeEnvData(jvalue)
        logger.debug("Store Env: %s" % (jvalue))

    def storeFileData(self):

        self.storeData("configDevice", self.configDevice)
        self.storeData("writerDevice", self.writerDevice)

        self.storeList("timer", self.timers)
        self.storeData("door", self.door)
        self.storeData("mntGrp", self.mntgrp)

        self.storeData("appendEntry", self.appendEntry)
        self.storeData("dynamicComponents", self.dynamicComponents)
        self.storeData("dynamicLinks", self.dynamicLinks)
        self.storeData("dynamicPath", self.dynamicPath)

    def storeGroups(self):
        if not self.__dp:
            self.setServer()
        self.storeDict("dataSourceGroup", self.dsgroup)
        self.storeDict("componentGroup", self.cpgroup)
        self.storeDict("automaticComponentGroup", self.acpgroup)
        self.storeList("automaticDataSources", self.adslist)

    def storeSettings(self):
        if not self.__dp:
            self.setServer()
        self.storeEnvData()
        self.storeFileData()
        self.storeDict("dataSourceGroup", self.dsgroup)
        self.storeDict("labels", self.labels)
        self.storeDict("labelLinks", self.labellinks)
        self.storeDict("labelPaths", self.labelpaths)
        self.storeDict("labelShapes", self.labelshapes)
        self.storeDict("labelTypes", self.labeltypes)
        self.storeList("hiddenElements", self.nodisplay)
        self.storeList("orderedChannels", self.orderedchannels)
        self.storeDict("componentGroup", self.cpgroup)
        self.storeDict("dataRecord", self.datarecord)
        self.storeDict("configVariables", self.configvars)
        if not self.server:
            self.__dp.exportAllEnv()

    def updateMntGrp(self):
        if not self.mntgrp:
            raise Exception("ActiveMntGrp not defined")
        if not self.scanFile:
            raise Exception("ScanFile not defined")
        if not self.scanDir:
            raise Exception("ScanDir not defined")
        self.storeSettings()
        mgconf = self.__dp.updateMntGrp()
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = json.loads(mgconf)
        return conf

    def isMntGrpChanged(self):
        return self.__dp.isMntGrpChanged()

    def importMntGrp(self):
        return self.__dp.importMntGrp()

    def mntGrpConfiguration(self):
        mgconf = self.__dp.mntGrpConfiguration()
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = json.loads(mgconf)
        return json.dumps(conf)

    def getConfiguration(self):
        self.storeSettings()
        return self.__dp.configuration

    def setConfiguration(self, conf):
        self.__dp.configuration = conf
        self.__dp.updateMntGrp()
        self.fetchSettings()

    def updateControllers(self):
        if hasattr(self.__dp, "command_inout_asynch"):
#            aid = self.__dp.command_inout_asynch("updateControllers")
#            self.wait(self.__dp)
            try:
                self.__dp.updateControllers()
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.wait(self.__dp)
                else:
                    raise
        else:
            self.__dp.updateControllers()

    def setServer(self):

        if self.server:
            self.__dp = self.openProxy(self.server)
            self.__dp.set_timeout_millis(self.__timeout)
            logger.debug("set server: %s:%s/%s" % (self.__dp.get_db_host(),
                                                   self.__dp.get_db_port(),
                                                   self.__dp.name()))
        else:
            from nxsrecconfig import Settings
            self.__dp = Settings.Settings()

    @classmethod
    def openProxy(cls, server):
        proxy = PyTango.DeviceProxy(server)
        cls.wait(proxy)
        return proxy

    @classmethod
    def wait(cls, proxy, counter=100):
        found = False
        cnt = 0
        while not found and cnt < counter:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if proxy.state() != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError) as e:
                time.sleep(0.01)
                found = False
                if cnt == counter - 1:
                    raise

            cnt += 1

    def loadDict(self, name):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dsg = self.__dp.read_attribute(name).value
        else:
            dsg = getattr(self.__dp, name)
        res = {}
        if dsg:
            dc = json.loads(dsg)
            if isinstance(dc, dict):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def storeDict(self, name, value):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()

        jvalue = json.dumps(value)
        if self.server:
            try:
                self.__dp.write_attribute(name, jvalue)
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.wait(self.__dp)
                else:
                    raise
        else:
            setattr(self.__dp, name, jvalue)

        logger.debug(" %s = %s" % (name, jvalue))

    def storeList(self, name, value):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()

        jvalue = json.dumps(value)
        if self.server:
            try:
                self.__dp.write_attribute(name, jvalue)
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.wait(self.__dp)
                else:
                    raise
        else:
            setattr(self.__dp, name, jvalue)

        logger.debug(" %s = %s" % (name, jvalue))

    def storeData(self, name, value):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()

        if self.server:
            try:
                self.__dp.write_attribute(name, value)
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.wait(self.__dp)
                else:
                    raise
        else:
            setattr(self.__dp, name, value)
        logger.debug(" %s = %s" % (name, value))

    def loadList(self, name, encoded=False):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.read_attribute(name).value
        else:
            dc = getattr(self.__dp, name)
        logger.debug(dc)
        res = []
        if dc:
            if encoded:
                dc = json.loads(dc)
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def loadData(self, name):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.read_attribute(name).value
        else:
            dc = getattr(self.__dp, name)

        logger.debug(dc)
        return dc

    def getList(self, name):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.command_inout(name)
        else:
            dc = getattr(self.__dp, name)()

        logger.debug(dc)
        res = []
        if dc:
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res))
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
                                    dds[ds] = cp
                                    break
        for timer in self.timers:
            if timer not in dds.keys():
                dds[timer] = ''
        return dds

    def clientRecords(self, selected=False):
        res = self.description
        dds = {}

        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if not selected or cp in self.cplist \
                            or cp in self.mcplist \
                            or cp in self.acplist:
                        for ds, values in dss.items():
                            for vl in values:
                                if len(vl) > 1 and vl[1] == 'CLIENT':
                                    dds[ds] = vl[2]
        return dds

    ## provides disable datasources
    ddsdict = property(disableDataSources,
                       doc='provides disable datasources')

    ## update a list of Components
    def Components(self):
        if isinstance(self.cpgroup, dict):
            return [cp for cp in self.cpgroup.keys() if self.cpgroup[cp]]
        else:
            return []

    ## provides disable datasources
    cplist = property(Components,
                       doc='provides selected components')
