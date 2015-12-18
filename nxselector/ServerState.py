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
## \file ServerState.py
# state of sardana recorder server

""" state of recorder server """

import PyTango
import json
import time
import subprocess

import logging
logger = logging.getLogger(__name__)


## main window class
class ServerState(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, server=None):

        self.server = None
        self.__db = PyTango.Database()
        self.__dp = None

        self.__timeout = 25000

        ## server configuration
        self.__conf = {}

        self.findServer(server)

        ## tango database
        self.errors = []

        self.scanDir = None
        self.scanFile = []
        self.scanID = 0

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
        self.properties = {}
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
        self.cpvrdict = {}
        self.idslist = []
        self.admindata = []

        self.orderedchannels = []

        self.configvars = {}
        self.datarecord = {}
        self.fullnames = {}

        self.labellinks = {}
        self.labelpaths = {}
        self.labelshapes = {}
        self.labeltypes = {}

        self.errors = []
        self.notimerresctriction = False

        try:
            self.setServer()
            if self.server:
                self.__dp.ping()
        except Exception:
            self.server = None
            raise
        logger.debug("DP %s" % type(self.__dp))

        self.recorder_names = ['serialno', 'end_time', 'start_time',
                               'point_nb', 'timestamps']
        self.channelprops = ["nexus_path", "link", "shape", "label",
                             "data_type"]

    def __grepServer(self):
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

    ## sets the existing NXSRecSelector server
    ## \param server server name
    def findServer(self, server=None):
        if server is None:
            servers = self.__db.get_device_exported_for_class(
                "NXSRecSelector").value_string
            if len(servers):
                if len(servers) > 1:
                    gserver = self.__grepServer()
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

    def __fetchConfiguration(self):
        if not self.__dp:
            self.setServer()
        if not self.server:
            self.__dp.exportEnvProfile()
        self.__conf = json.loads(self.__dp.profileConfiguration)

    def fetchErrors(self):
        if not self.__dp:
            self.setServer()
        self.errors = self.__loadList("descriptionErrors")
        return self.errors

    def setProperties(self):
        if "label" in self.properties:
            self.labels = self.properties["label"]
        else:
            self.labels = {}
        if "link" in self.properties:
            self.labellinks = self.properties["link"]
        else:
            self.labellinks = {}
        if "nexus_path" in self.properties:
            self.labelpaths = self.properties["nexus_path"]
        else:
            self.labelpaths = {}
        if "shape" in self.properties:
            self.labelshapes = self.properties["shape"]
        else:
            self.labelshapes = {}
        if "data_type" in self.properties:
            self.labeltypes = self.properties["data_type"]
        else:
            self.labeltypes = {}

    def getProperties(self):
        self.properties["label"] = self.labels
        self.properties["link"] = self.labellinks
        self.properties["nexus_path"] = self.labelpaths
        self.properties["shape"] = self.labelshapes
        self.properties["data_type"] = self.labeltypes

    ## fetches configuration setting from server
    def fetchSettings(self):
        self.__fetchConfiguration()

        self.cpgroup = self.__importDict("ComponentSelection")
        self.dsgroup = self.__importDict("DataSourceSelection")
        self.acpgroup = self.__importDict("ComponentPreselection")
        self.properties = self.__importDict("ChannelProperties")
        self.setProperties()
        self.datarecord = self.__importDict("UserData")
        self.configvars = self.__importDict("ConfigVariables")

        self.nodisplay = self.__importList("UnplottedComponents", True)
        self.orderedchannels = self.__importList("OrderedChannels", True)
        self.idslist = self.__importList("InitDataSources", True)

        self.avcplist = self.__getList("availableComponents")
        self.avdslist = self.__getList("availableDataSources")
        self.avmglist = self.__getList("availableMntGrps")
        self.mcplist = self.__getList("mandatoryComponents")

        self.acplist = self.__getList("preselectedComponents")
        self.atlist = self.__getList("availableTimers")
        self.description = self.__getList("componentDescription", True)

        self.vrcpdict = self.__getDict("variableComponents")
        self.fullnames = self.__getDict("fullDeviceNames")
        self.admindata = self.__getList("administratorDataNames")

        self.__fetchFileData()
        self.__fetchEnvData()
        if self.notimerresctriction:
            ## old version to check
            self.atlist = list(set(self.atlist) | set(self.timers))
        else:
            if self.timers:
                self.atlist = list(set(self.atlist) | set([self.timers[0]]))
            self.timers = [tm for tm in self.timers if tm in self.atlist]

        self.cpvrdict = {}
        for vr,cps in self.vrcpdict.items():
            for cp in cps:
                if cp not in self.cpvrdict.keys():
                    self.cpvrdict[cp] = set()
                self.cpvrdict[cp].add(vr)


    def __fetchFileData(self):
        self.timers = self.__importList("Timer", True)
        self.mntgrp = str(self.__importData("MntGrp"))
        try:
            self.door = str(self.__loadData("door"))
        except:
            self.storeData("door", "")
            self.door = str(self.__loadData("door"))

        self.configDevice = str(self.__loadData("configDevice"))
        self.writerDevice = str(self.__importData("WriterDevice"))

        self.appendEntry = self.__importData("AppendEntry")
        self.dynamicLinks = self.__importData("DefaultDynamicLinks")
        self.dynamicPath = str(self.__importData("DefaultDynamicPath"))

    def __fetchEnvData(self):
        params = {"ScanDir": "scanDir",
                  "ScanFile": "scanFile",
                  "ScanID": "scanID"}

        if not self.__dp:
            self.setServer()

        jvalue = self.__command(self.__dp, "scanEnvVariables")
        value = json.loads(jvalue)

        for var, attr in params.items():
            if var in value.keys():
                setattr(self, attr, value[var])
        logger.debug("fetch Env: %s" % (jvalue))

    def __storeEnvData(self):
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
        self.scanID = self.__command(self.__dp, "setScanEnvVariables", jvalue)
        logger.debug("Store Env: %s" % (jvalue))

    def __storeFileData(self):

        self.storeData("configDevice", self.configDevice)
        self.storeData("door", self.door)

        self.__exportData("ConfigDevice", self.configDevice)
        self.__exportData("Door", self.door)
        self.__exportData("MntGrp", self.mntgrp)

        self.__exportData("WriterDevice", self.writerDevice)
        self.__exportList("Timer", self.timers)
        self.__exportData("AppendEntry", self.appendEntry)
        self.__exportData("DynamicComponents", self.dynamicComponents)
        self.__exportData("DefaultDynamicLinks", self.dynamicLinks)
        self.__exportData("DefaultDynamicPath", self.dynamicPath)

    def storeGroups(self):
        if not self.__dp:
            self.setServer()
        self.__exportDict("DataSourceSelection", self.dsgroup)
        self.__exportDict("ComponentSelection", self.cpgroup)
        self.__exportDict("ComponentPreselection", self.acpgroup)
        self.__exportList("InitDataSources", self.idslist)
        self.__storeConfiguration()

    ## stores configuration settings on server
    def storeSettings(self):
        if not self.__dp:
            self.setServer()
        self.__storeEnvData()
        self.__storeFileData()
        self.__exportDict("DataSourceSelection", self.dsgroup)
        self.__exportDict("ComponentSelection", self.cpgroup)
        self.__exportDict("ComponentPreselection", self.acpgroup)
        self.__exportList("InitDataSources", self.idslist)
        self.getProperties()
        self.__exportDict("ChannelProperties", self.properties)
        self.__exportList("UnplottedComponents", self.nodisplay)
        self.__exportList("OrderedChannels", self.orderedchannels)
        self.__exportDict("UserData", self.datarecord)
        self.__exportDict("ConfigVariables", self.configvars)
        if not self.server:
            self.__dp.exportEnvProfile()
        self.__storeConfiguration()

    def __storeConfiguration(self):
        if not self.__dp:
            self.setServer()
        self.__dp.profileConfiguration = str(json.dumps(self.__conf))
        if not self.server:
            self.__dp.exportEnvProfile()

    def fetchMntGrp(self):
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "fetchProfile")

    def switchMntGrp(self):
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "switchProfile")

    ## update measurement group
    def updateMntGrp(self):
        if not self.mntgrp:
            raise Exception("ActiveMntGrp not defined")
        if not self.scanFile:
            raise Exception("ScanFile not defined")
        if not self.scanDir:
            raise Exception("ScanDir not defined")
        self.storeSettings()
        mgconf = self.__command(self.__dp, "updateMntGrp")
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = json.loads(mgconf)
        return conf

    def isMntGrpChanged(self):
        if not self.__dp:
            self.setServer()
        return self.__command(self.__dp, "isMntGrpUpdated")

    def importMntGrp(self):
        if not self.__dp:
            self.setServer()
        return self.__command(self.__dp, "importMntGrp")

    def createConfiguration(self):
        if not self.__dp:
            self.setServer()
        return self.__command(self.__dp, "createWriterConfiguration", [])

    def deleteMntGrp(self, name):
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "deleteProfile", str(name))
        self.avmglist = self.__getList("availableMntGrps")
        if self.avmglist:
            self.mntgrp = self.avmglist[0]
            self.storeData("mntGrp", self.mntgrp)
            self.fetchMntGrp()

    def mntGrpConfiguration(self):
        mgconf = self.__command(self.__dp, "mntGrpConfiguration")
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = json.loads(mgconf)
        return json.dumps(conf)

    def getConfiguration(self):
        self.storeSettings()
        return self.__dp.profileConfiguration

    def setConfiguration(self, conf):
        self.__dp.profileConfiguration = conf
        self.__command(self.__dp, "updateMntGrp")
        self.fetchSettings()

    def resetDescriptions(self):
        if hasattr(self.__dp, "command_inout_asynch"):
#            aid = self.__dp.command_inout_asynch("PreselectComponents")
#            self.__wait(self.__dp)
            try:
                self.__command(self.__dp, "resetPreselectedComponents")
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.__wait(self.__dp)
                else:
                    raise
        else:
            self.__command(self.__dp, "resetPreselectedComponents")

    def updateControllers(self):
        if hasattr(self.__dp, "command_inout_asynch"):
#            aid = self.__dp.command_inout_asynch("PreselectComponents")
#            self.__wait(self.__dp)
            try:
                self.__command(self.__dp, "PreselectComponents")
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.__wait(self.__dp)
                else:
                    raise
        else:
            self.__command(self.__dp, "PreselectComponents")

    def setServer(self):

        if self.server:
            self.__dp = self.__openProxy(self.server)
            self.__dp.set_timeout_millis(self.__timeout)
            logger.debug("set server: %s:%s/%s" % (self.__dp.get_db_host(),
                                                   self.__dp.get_db_port(),
                                                   self.__dp.name()))
        else:
            from nxsrecconfig import Settings
            self.__dp = Settings.Settings()

    @classmethod
    def __openProxy(cls, server):
        proxy = PyTango.DeviceProxy(server)
        cls.__wait(proxy)
        return proxy

    @classmethod
    def __command(cls, server, command, *var):
        if not hasattr(server, "command_inout"):
            return getattr(server, command)(*var)
        elif var is None:
            return server.command_inout(command)
        else:
            return server.command_inout(command, *var)

    @classmethod
    def __wait(cls, proxy, counter=100):
        found = False
        cnt = 0
        while not found and cnt < counter:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if cls.__command(proxy, "State") != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError):
                time.sleep(0.01)
                found = False
                if cnt == counter - 1:
                    raise
            cnt += 1

    def __importDict(self, name):
        dsg = self.__conf[name] if name in self.__conf else None
        res = {}
        if dsg:
            dc = json.loads(dsg)
            if isinstance(dc, dict):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def __importList(self, name, encoded=False):
        dc = self.__conf[name] if name in self.__conf else None
        logger.debug(dc)
        res = []
        if dc:
            if encoded:
                dc = json.loads(dc)
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def __importData(self, name):
        dc = self.__conf[name] if name in self.__conf else None
        logger.debug(dc)
        return dc

    def __loadDict(self, name):
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

    def __exportDict(self, name, value):
        self.__conf[name] = json.dumps(value)
        logger.debug(" %s = %s" % (name, value))

    def __exportList(self, name, value):
        self.__conf[name] = json.dumps(value)
        logger.debug(" %s = %s" % (name, value))

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
                    self.__wait(self.__dp)
                else:
                    raise
        else:
            setattr(self.__dp, name, value)
        logger.debug(" %s = %s" % (name, value))

    def __exportData(self, name, value):
        self.__conf[name] = value
        logger.debug(" %s = %s" % (name, value))

    def __loadList(self, name, encoded=False):
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

    def __loadData(self, name):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.read_attribute(name).value
        else:
            dc = getattr(self.__dp, name)

        logger.debug(dc)
        return dc

    def __getList(self, name, encoded=False):
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
            if encoded:
                dc = json.loads(dc)
            if isinstance(dc, (list, tuple)):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def __getDict(self, name):
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.command_inout(name)
        else:
            dc = getattr(self.__dp, name)()

        logger.debug(dc)
        res = {}
        if dc:
            dc = json.loads(dc)
            if isinstance(dc, (dict)):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    ## update a list of Disable DataSources
    def __disableDataSources(self):
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

    def clientRecords(self):
        res = self.description
        dds = {}

        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if cp in self.cplist \
                            or cp in self.mcplist \
                            or cp in self.acplist:
                        for ds, values in dss.items():
                            for vl in values:
                                if len(vl) > 1 and vl[1] == 'CLIENT':
                                    dds[ds] = vl[2]
        return list(set(dds.values()) - set(self.fullnames.values()) -
                    set(self.recorder_names))

    ## provides disable datasources
    ddsdict = property(__disableDataSources,
                       doc='provides disable datasources')

    ## update a list of components
    def __components(self):
        if isinstance(self.cpgroup, dict):
            return [cp for cp in self.cpgroup.keys() if self.cpgroup[cp]]
        else:
            return []

    ## provides disable datasources
    cplist = property(__components,
                       doc='provides selected components')
