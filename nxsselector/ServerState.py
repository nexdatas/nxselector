#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# state of sardana recorder server

""" state of recorder server """

import PyTango
import json
import time
import subprocess

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt


import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Checker(object):
    """ compare configuation methods
    """

    def __init__(self):
        """ constructor
        """

        #: (:obj:`list`<:obj:`str`>) special keys for sorted json lists
        self.jsortedlists = ['PreselectingDataSources']
        #: (:obj:`list`<:obj:`str`>) special keys for json dicts
        self.jdicts = ['DataSourceSelection']

    def compDict(self, dct, dct2, sort=False):
        """ compare two configuration dictionaries

        :param dct: first configuration dictionary
        :type dct: `dict`<:obj:`any`, :obj:`any`>
        :param dct2: second configuration dictionary
        :type dct2: `dict`<:obj:`any`, :obj:`any`>
        :param sort: if use special keys
        :type sort: :obj:`bool`
        :returns: if configuration are equal
        :rtype: :obj:`bool`
        """

        if not isinstance(dct, dict):
            return False
        if not isinstance(dct2, dict):
            return False
        if len(dct.keys()) != len(dct2.keys()):
            return False
        for k, v in dct.items():
            if k not in dct2.keys():
                return False
            if isinstance(v, dict):
                return self.compDict(v, dct2[k])
            elif sort and k in self.jsortedlists:
                l1 = sorted(json.loads(v))
                l2 = sorted(json.loads(dct2[k]))
                if l1 != l2:
                    return False
            elif sort and k in self.jdicts:
                d1 = json.loads(v)
                d2 = json.loads(dct2[k])
                return self.compDict(d1, d2)
            else:
                if v != dct2[k]:
                    return False
        return True


class SynchThread(Qt.QThread):
    """ thread with server command
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    scanidchanged = Qt.pyqtSignal()

    #: (:class:`taurus.qt.Qt.pyqtSignal') mg configuration changed
    mgconfchanged = Qt.pyqtSignal()

    def __init__(self, serverstate, server, mutex):
        """constructor
        :param serverstate: ServerState
        :type serverstate: :class:`ServerState`
        :param server: server name
        :type server: :obj:`str`
        """
        Qt.QThread.__init__(self, serverstate)
        #: (:obj:`bool`) server is running
        self.running = True

        #: (:class:`taurus.qt.Qt.QMutex`) thread mutex
        self.mutex = mutex

        #: (:obj:`str`) server name
        self.server = str(serverstate.server) if serverstate.server else None

        #: (:obj:`str`) server name
        self.__serverstate = serverstate

        #: (:obj:`int`) last scan id
        self.__lastscanid = 0
        #: (:obj:`str`) last mntgrp configuration
        self.__lastmg = ""
        #: (:obj:`str`) last profile configuration
        self.__lastprof = ""

        self.__dp = None
        if self.server and self.server != 'module':
            self.__dp = PyTango.DeviceProxy(self.server)
            self.__dp.set_source(PyTango.DevSource.DEV)
            self.__lastscanid = self.__dp.scanID
            self.__lastmg = self.__dp.mntGrpConfiguration()
            self.__lastprof = self.__dp.profileConfiguration

    def restart(self):
        with Qt.QMutexLocker(self.mutex):
            self.server = str(self.__serverstate.server) \
                if self.__serverstate.server else None
        if self.server and self.server != 'module':
            self.__dp = PyTango.DeviceProxy(self.server)
            self.__dp.set_source(PyTango.DevSource.DEV)
            self.__lastscanid = self.__dp.scanID
            self.__lastmg = self.__dp.mntGrpConfiguration()
            self.__lastprof = self.__dp.profileConfiguration
        self.running = True
        self.start()

    def run(self):
        """ runs synch thread
        """
        insynch = True
        checker = Checker()
        while insynch:
            self.sleep(5)
            try:
                if not Qt or not self.__dp:
                    break
                scanid = self.__dp.scanID
                mg = self.__dp.mntGrpConfiguration()
                prof = self.__dp.profileConfiguration
                with Qt.QMutexLocker(self.mutex):
                    if not self.running:
                        insynch = False
                if self.__lastscanid != scanid and insynch:
                    self.scanidchanged.emit()
                    self.__lastscanid = scanid
                if (self.__lastmg != mg or self.__lastprof != prof) \
                   and insynch:
                    m0 = json.loads(self.__lastmg)
                    m1 = json.loads(mg)
                    if not checker.compDict(m0, m1):
                        self.mgconfchanged.emit()
                    else:
                        p0 = json.loads(self.__lastprof)
                        p1 = json.loads(prof)
                        if not checker.compDict(p0, p1, True):
                            self.mgconfchanged.emit()

                    self.__lastmg = mg
                    self.__lastprof = prof
            except Exception:
                """ what is wrong """


class ServerState(Qt.QObject):
    """ state of recorder server """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) server changed signal
    serverChanged = Qt.pyqtSignal()

    def __init__(self, server=None):
        """ constructor

        :param server: selector server name
        :type server: :obj:`str`
        """
        Qt.QObject.__init__(self)

        #: (:obj:`str`) selector server name
        self.server = None

        #: (:class:`taurus.qt.Qt.QMutex`) thread mutex
        self.mutex = Qt.QMutex()

        #: (:class:`PyTango.Database`) tango database instance
        self.__db = PyTango.Database()
        #: (:class:`PyTango.DeviceProxy`) selector server device proxy
        self.__dp = None

        #: (:obj:`int`) timeout
        self.__timeout = 25000

        #: (:obj:`dict` < :obj:`str`, `any`>) \
        #:     profile server configuration
        self.__conf = {}

        self.findServer(server)

        #: (:obj:`list`<:obj:`str`>) tango database
        self.errors = []

        #: (:obj:`str`) scan directory
        self.scanDir = None
        #: (:obj:`list`<:obj:`str`>) scan file names
        self.scanFile = []
        #: (:obj:`int`) scan id
        self.scanID = 0

        #: (:obj:`list`<:obj:`str`>) timers
        self.timers = None
        #: (:obj:`str`) measurement group name
        self.mntgrp = None
        #: (:obj:`str`) door  device name
        self.door = None

        #: (:obj:`str`) configuration device name
        self.configDevice = None
        #: (:obj:`str`) writer device name
        self.writerDevice = None

        #: (:obj:`bool`) append entry in one file
        self.appendEntry = None

        #: (:obj:`bool`) use dynamic components
        self.dynamicComponents = True
        #: (:obj:`bool`) use dynamic links
        self.dynamicLinks = None
        #: (:obj:`str`) default dynamic nexus path
        self.dynamicPath = None

        #: (:obj:`dict` <:obj:`str` , :obj:`bool` or `None`>) \
        #:    datasource selection
        self.dsgroup = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`str`>) device labels
        self.labels = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str` , `any`>>) \
        #:     device properties
        self.properties = {}
        #: (:obj:`list`<:obj:`str`>) list of non-plotted devices
        self.nodisplay = []
        #: (:obj:`dict` <:obj:`str` , :obj:`bool` or `None`>) \
        #:    detector component selection
        self.cpgroup = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`bool` or `None`>) \
        #:    description component selection
        self.acpgroup = {}
        #: (:obj:`list`<:obj:`str`>) selected description components
        self.acplist = []
        #: (:obj:`list`<:obj:`str`>) available timers
        self.atlist = []
        #: (:obj:`list`<:obj:`str`>) mandatory components
        self.mcplist = []
        #: ( [:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, \
        #:        :obj:`list` <(:obj:`str`, :obj:`str`, :obj:`str`, \
        #:        :obj:`str`, :obj:`list` <:obj:`int`>)> > > ] ) \
        #: element description
        self.description = []
        #: (:obj:`list`<:obj:`str`>) available components
        self.avcplist = []
        #: (:obj:`list`<:obj:`str`>) available datasources
        self.avdslist = []
        #: (:obj:`list`<:obj:`str`>) available measurement groups
        self.avmglist = []
        #: (:obj:`dict` <:obj:`str`, :obj:`list` <:obj:`str` >>) \
        #:     variable components
        self.vrcpdict = {}
        #: (:obj:`dict` <:obj:`str`, :obj:`list` <:obj:`str` >>) \
        #:     component variables
        self.cpvrdict = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`bool` or `None`>) \
        #:    init (descriptive) datasource selection
        self.idsgroup = {}
        #: (:obj:`list`<:obj:`str`>) administrator data key names
        self.admindata = []

        #: (:obj:`list`<:obj:`str`>) ordered pool channels
        self.orderedchannels = []

        #: (:obj:`dict` <:obj:`str` , :obj:`str`>) configuration variables
        self.configvars = {}
        #: (:obj:`dict` <:obj:`str` , `any`>) (name, value) \
        #:     user data dictionary
        self.datarecord = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`str`>) full device names
        self.fullnames = {}

        #: (:obj:`dict` <:obj:`str` , :obj:`bool`>) label links
        self.labellinks = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`bool`>) label canfail flags
        self.labelcanfailflags = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`str`>) label nexus paths
        self.labelpaths = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`list`< :obj:`int`> >) \
        #:     label data shapes
        self.labelshapes = {}
        #: (:obj:`dict` <:obj:`str` , :obj:`str`>) label nexus types
        self.labeltypes = {}

        #: (:obj:`list`<:obj:`str`>) error list
        self.errors = []
        #: (:obj:`bool`) no timer restriction flag
        self.notimerresctriction = False

        self.ddsdirty = True
        self.__ddsbackup = {}

        try:
            self.setServer()
            if self.server:
                self.__dp.ping()
        except Exception:
            self.server = None
            raise
        logger.debug("DP %s" % type(self.__dp))

        self.recorder_names = ['serialno', 'end_time', 'start_time',
                               'point_nb', 'timestamps', 'scan_title',
                               'filename'
                               ]
        self.channelprops = ["nexus_path", "link", "shape", "label",
                             "data_type", "canfail"]
        self.extrachannelprops = ["synchronizer", "synchronization"]
        self.synchthread = SynchThread(self, self.server, self.mutex)

    def __grepServer(self):
        """ provides the local selector server device name

        :returns: selector server device name
        :rtype: :obj:`str`
        """
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
        except Exception:
            pass
        return server

    def findServer(self, server=None):
        """  sets the existing NXSRecSelector server

        :param server: selector server device name
        :type server: :obj:`str`
        """
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
        self.updateServerShared()

    def updateServerShared(self):
        with Qt.QMutexLocker(self.mutex):
            if hasattr(self, "synchthread"):
                if self.server != self.synchthread.server:
                    self.serverChanged.emit()

    def __fetchConfiguration(self):
        """ fetches from the server the current profile configuration
        """
        if not self.__dp:
            self.setServer()
        if not self.server:
            self.__dp.exportEnvProfile()
        self.__conf = json.loads(self.__dp.profileConfiguration)

    def createDataSources(self, datasources):
        """ creates new datasources
        :param datasources: datasources to add { name: source }
        :type datasources: :obj:`dict` <:obj:`str`, :obj:`str``>
        """
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "createDataSources",
                       str(json.dumps(datasources)))
        self.__fetchConfiguration()
        self.avdslist = self.__getList("availableDataSources")
        self.dsdescription = self.__getList(
            "dataSourceDescription", argin=self.avdslist)

    def fetchErrors(self):
        """ fetches from the server the description errors
        """
        if not self.__dp:
            self.setServer()

        dc = "Error: Cannot read descriptionErrors"
        if self.server:
            error = True
            maxcount = 10
            while error and maxcount:
                try:
                    dc = self.__dp.read_attribute("descriptionErrors").value
                    error = False
                except Exception as e:
                    logger.warning(str(e))
                maxcount -= 1
        else:
            dc = getattr(self.__dp, "descriptionErrors")
        logger.debug(dc)
        self.errors = []
        if dc:
            if isinstance(dc, (list, tuple)):
                self.errors = dc
        logger.debug(" %s = %s" % ("descriptionErrors", self.errors))
        return self.errors

    def setProperties(self):
        """ sets label properties from properties
        """
        if "label" in self.properties:
            self.labels = self.properties["label"]
        else:
            self.labels = {}
        if "link" in self.properties:
            self.labellinks = self.properties["link"]
        else:
            self.labellinks = {}
        if "canfail" in self.properties:
            self.labelcanfailflags = self.properties["canfail"]
        else:
            self.labelcanfailflags = {}
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
        if "__controllers__" in self.properties:
            self.controllers = self.properties["__controllers__"]
        else:
            self.controllers = {}
        if "__triggergatelist__" in self.properties:
            self.triggergatelist = \
                self.properties["__triggergatelist__"]
        else:
            self.triggergatelist = []

    def getProperties(self):
        """ sets properties from label properties
        """
        self.properties["label"] = self.labels
        self.properties["link"] = self.labellinks
        self.properties["canfail"] = self.labelcanfailflags
        self.properties["nexus_path"] = self.labelpaths
        self.properties["shape"] = self.labelshapes
        self.properties["data_type"] = self.labeltypes

    def fetchSettings(self):
        """ fetches configuration setting from server
        """
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
        self.idsgroup = self.__importDict("DataSourcePreselection")

        self.avcplist = self.__getList("availableComponents")
        self.avdslist = self.__getList("availableDataSources")
        self.dsdescription = self.__getList(
            "dataSourceDescription", argin=self.avdslist)
        self.avmglist = self.__getList("availableMntGrps")
        self.mcplist = self.__getList("mandatoryComponents")

        self.acplist = self.__getList("preselectedComponents")
        self.atlist = self.__getList("availableTimers")
        self.description = self.__getList("componentDescription", True)
        self.ddsdirty = True
        self.mutedChannels = self.__getList("mutedChannels")

        self.vrcpdict = self.__getDict("variableComponents")
        self.fullnames = self.__getDict("fullDeviceNames")
        self.admindata = self.__getList("administratorDataNames")

        self.motors = self.__getList(
            "poolElementNames", argin='MotorList')
        self.acqchannels = self.__getList(
            "poolElementNames", argin='AcqChannelList')
        self.ioregisters = self.__getList(
            "poolElementNames", argin='IORegisterList')

        self.__fetchFileData()
        self.fetchEnvData()
        if self.notimerresctriction:
            # old version to check
            self.atlist = list(set(self.atlist) | set(self.timers))
        else:
            if self.timers:
                self.atlist = list(set(self.atlist) | set([self.timers[0]]))
            self.timers = [tm for tm in self.timers if tm in self.atlist]

        self.cpvrdict = {}
        for vr, cps in self.vrcpdict.items():
            for cp in cps:
                if cp not in self.cpvrdict.keys():
                    self.cpvrdict[cp] = set()
                self.cpvrdict[cp].add(vr)

    def __fetchFileData(self):
        """ fetches file data configuration from the server
        """
        self.timers = self.__importList("Timer", True)
        self.mntgrp = str(self.__importData("MntGrp"))
        try:
            self.door = str(self.__loadData("door"))
        except Exception:
            self.storeData("door", "")
            self.door = str(self.__loadData("door"))

        self.configDevice = str(self.__loadData("configDevice"))
        self.writerDevice = str(self.__importData("WriterDevice"))

        self.appendEntry = self.__importData("AppendEntry")
        self.dynamicLinks = self.__importData("DefaultDynamicLinks")
        self.dynamicPath = str(self.__importData("DefaultDynamicPath"))

    def fetchEnvData(self, params=None):
        """ fetches scan variables from the server
        """
        params = params or {"ScanDir": "scanDir",
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
        """ stores scan variables on the server
        """
        params = {"ScanDir": "scanDir",
                  "ScanFile": "scanFile",
                  "NeXusSelectorDevice": "server",
                  # "ScanID": "scanID"
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
        """ stores file data configuration on the server
        """

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
        """ stores selection group settings on the server"""
        if not self.__dp:
            self.setServer()
        self.__exportDict("DataSourceSelection", self.dsgroup)
        self.__exportDict("ComponentSelection", self.cpgroup)
        self.__exportDict("ComponentPreselection", self.acpgroup)
        self.__exportDict("DataSourcePreselection", self.idsgroup)
        self.__storeConfiguration()

    def storeSettings(self):
        """ stores all settings on the server"""
        if not self.__dp:
            self.setServer()
        self.__storeEnvData()
        self.__storeFileData()
        self.__exportDict("DataSourceSelection", self.dsgroup)
        self.__exportDict("ComponentSelection", self.cpgroup)
        self.__exportDict("ComponentPreselection", self.acpgroup)
        self.__exportDict("DataSourcePreselection", self.idsgroup)
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
        """ stores profile configuration on the server"""
        if not self.__dp:
            self.setServer()
        self.__dp.profileConfiguration = str(json.dumps(self.__conf))
        if not self.server:
            self.__dp.exportEnvProfile()

    def fetchMntGrp(self):
        """ fetches mntgrp and profile from the server
        """
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "fetchProfile")

    def switchMntGrp(self):
        """ switches mntgrp and profile on the server
        """
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "switchProfile")

    def updateMntGrp(self):
        """ updates mntgrp on the macroserver/pool
        """
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
        """ checks if measurement group has changed

        :returns: if measurement group has changed
        :rtype: :obj:`bool`
        """
        if not self.__dp:
            self.setServer()
        mgconf = json.loads(self.__command(self.__dp, "mntGrpConfiguration"))
        locmgconf = self.__importDict("MntGrpConfiguration")
        checker = Checker()
        if checker.compDict(mgconf, locmgconf):
            pconf = json.loads(self.__dp.profileConfiguration)
            locpconf = self.__conf
            return checker.compDict(pconf, locpconf, True)
        return False

    def importMntGrp(self):
        """ imports mntgrp from sardana
        """
        if not self.__dp:
            self.setServer()
        return self.__command(self.__dp, "importMntGrp")

    def createConfiguration(self):
        """ creates the NeXus Writer configuration

        :returns: NeXus writer configuration
        :rtype: :obj:`str`
        """
        if not self.__dp:
            self.setServer()
        return self.__command(self.__dp, "createWriterConfiguration", [])

    def deleteMntGrp(self, name):
        """ deletes the profile and the corresponding measurement group

        :param name: measurement group name
        :type name: :obj:`str`
        """
        if not self.__dp:
            self.setServer()
        self.__command(self.__dp, "deleteProfile", str(name))
        self.avmglist = self.__getList("availableMntGrps")
        if self.avmglist:
            self.mntgrp = self.avmglist[0]
            self.storeData("mntGrp", self.mntgrp)
            self.fetchMntGrp()

    def mntGrpConfiguration(self):
        """ provides measurement group configuration with its name

        :returns: measurement group configuration with its name
        :rtype: :obj:`str`
        """
        mgconf = self.__command(self.__dp, "mntGrpConfiguration")
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = json.loads(mgconf)
        return json.dumps(conf)

    def lastMntGrpConfiguration(self):
        """ provides measurement group configuration with its name

        :returns: measurement group configuration with its name
        :rtype: :obj:`str`
        """
        conf = {}
        conf['MntGrpConfigs'] = {}
        conf['ActiveMntGrp'] = self.mntgrp
        conf['MntGrpConfigs'][self.mntgrp] = \
            self.__importDict("MntGrpConfiguration")
        return json.dumps(conf)

    def getConfiguration(self):
        """ provides profile configuration

        :returns: profile configuration
        :rtype: :obj:`str`
        """
        self.storeSettings()
        return self.__dp.profileConfiguration

    def setConfiguration(self, conf):
        """ sets profile configuration

        :param conf: profile configuration
        :type conf: :obj:`str`
        """
        self.__dp.profileConfiguration = conf
        self.__command(self.__dp, "updateMntGrp")
        self.fetchSettings()

    def resetDescriptions(self):
        """ resets description components to default values
        """
        if hasattr(self.__dp, "command_inout_asynch"):
            # aid = self.__dp.command_inout_asynch("PreselectComponents")
            # self.__wait(self.__dp)
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
        """ update description component selection accoriding
             to its device state
        """
        if hasattr(self.__dp, "command_inout_asynch"):
            # aid = self.__dp.command_inout_asynch("PreselectComponents")
            # self.__wait(self.__dp)
            try:
                self.__command(self.__dp, "PreselectComponents")
            except PyTango.CommunicationFailed as e:
                if e[-1].reason == "API_DeviceTimedOut":
                    self.__wait(self.__dp)
                else:
                    raise
        else:
            self.__command(self.__dp, "preselectComponents")

    def setServer(self):
        """ sets the selector server
        """
        if self.server:
            self.__dp = self.__openProxy(self.server)
            self.__dp.set_source(PyTango.DevSource.DEV)
            self.__dp.set_timeout_millis(self.__timeout)
            logger.debug("set server: %s:%s/%s" % (self.__dp.get_db_host(),
                                                   self.__dp.get_db_port(),
                                                   self.__dp.name()))
        else:
            from nxsrecconfig import Settings
            self.__dp = Settings.Settings()
        if not hasattr(self.__dp, "version") or \
           int(str(self.__dp.version).split(".")[0]) < 2:
            raise Exception("NXSRecSelector (%s) version below 2.0.0" %
                            (self.server or "module"))

    def isDoorFromMacroServer(self, door):
        """ checks if door is of the current MacroServer

        :param door: door name
        :type door: :obj:`str`
        :returns: if door is of the current MacroServer
        :rtype: :obj:`bool`
        """
        if not self.__dp:
            self.setServer()
        if hasattr(self.__dp, "macroServer"):
            ms = str(self.__dp.macroServer)
            if ms:
                if ':' not in ms and hasattr(self.__dp, "get_db_host"):
                    ms = "%s:%s/%s" % (self.__dp.get_db_host(),
                                       self.__dp.get_db_port(),
                                       ms)

                msp = self.__openProxy(ms)
                host = msp.get_db_host()
                port = msp.get_db_port()
                doors = msp.doorList
                if door in doors:
                    return True
                status = False
                for mdoor in doors:
                    if ':' in door and ':' not in mdoor:
                        if door == "%s:%s/%s" % (host, port, mdoor):
                            status = True
                            break
                    elif ':' not in door and ':' in mdoor:
                        if mdoor == "%s:%s/%s" % (host, port, door):
                            status = True
                            break
                return status

    @classmethod
    def __openProxy(cls, server):
        """ creates device proxy

        :param server: server name
        :type server: :obj:`str`
        :returns: server device proxy
        :rtype: :class:`PyTango.DeviceProxy`
        """
        proxy = PyTango.DeviceProxy(server)
        cls.__wait(proxy)
        return proxy

    @classmethod
    def __command(cls, server, command, *var):
        """ executes command on the server

        :param server: server instance
        :type server: :class:`PyTango.DeviceProxy` \
                      or 'nxsrecconfig.Settings.Settings'
        :param command: command name
        :type command: :obj:`str`
        :returns: command result
        :rtype: `any`

        """
        if not hasattr(server, "command_inout"):
            return getattr(server, command)(*var)
        elif var is None:
            return server.command_inout(command)
        else:
            return server.command_inout(command, *var)

    @classmethod
    def __wait(cls, proxy, counter=100):
        """ waits for server until server is not in running state

        :param proxy: server proxy
        :type proxy: :class:`PyTango.DeviceProxy`
        :param counter: maximum waiting timer in 0.01 sec
                        (without command execution)
        :type counter: :obj:`int`
        """
        found = False
        cnt = 0
        while not found and cnt < counter:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if proxy.state() != PyTango.DevState.RUNNING:
                    found = True
            except (PyTango.DevFailed, PyTango.Except, PyTango.DevError):
                time.sleep(0.01)
                found = False
                if cnt == counter - 1:
                    raise
            cnt += 1

    def __importDict(self, name):
        """ imports a dictionary variable from the profile configuration

        :param name: record name
        :type name: :obj:`str`
        :returns: returns dictionary
        :rtype: :obj:`dict` <`any`, `any`>
        """
        dsg = self.__conf[name] if name in self.__conf else None
        res = {}
        if dsg:
            dc = json.loads(dsg)
            if isinstance(dc, dict):
                res = dc
        logger.debug(" %s = %s" % (name, res))
        return res

    def __importList(self, name, encoded=False):
        """ imports a list variable from the profile configuration

        :param name: record name
        :type name: :obj:`str`
        :param encoded: if list should be encoded from JSON
        :type encoded: :obj:`bool`
        :returns: returns configuration list
        :rtype: :obj:`list` <`any`>
        """
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
        """ imports a variable from the profile configuration

        :param name: record name
        :type name: :obj:`str`
        :returns: returns configuration variable
        :rtype: `any`
        """
        dc = self.__conf[name] if name in self.__conf else None
        logger.debug(dc)
        return dc

    def __loadDict(self, name):
        """ reads dictionary variable from the configuration server attribute

        :param name: attribute name
        :type name: :obj:`str`
        :returns: returns dictionary
        :rtype: :obj:`dict` <`any`, `any`>
        """

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
        """ writes a dictionary variable into the profile configuration

        :param name: attribute name
        :type name: :obj:`str`
        :param value: returns dictionary
        :type value: :obj:`dict` <`any`, `any`>
        """
        self.__conf[name] = json.dumps(value)
        logger.debug(" %s = %s" % (name, value))

    def __exportList(self, name, value):
        """ writes a list variable into the profile configuration

        :param name: attribute name
        :type name: :obj:`str`
        :param value: returns dictionary
        :type value: :obj:`list` <`any`>
        """
        self.__conf[name] = json.dumps(value)
        logger.debug(" %s = %s" % (name, value))

    def storeData(self, name, value):
        """ stores data into the configuration server attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param value: attribute value
        :type value: :obj:`list` <`any`>
        """
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
        """ writes a variable into the profile configuration

        :param name: attribute name
        :type name: :obj:`str`
        :param value: returns dictionary
        :type value: `any`
        """
        self.__conf[name] = value
        logger.debug(" %s = %s" % (name, value))

    def __loadList(self, name, encoded=False):
        """ reads a list variable from the configuration server attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param encoded: encoding should be used
        :type encoded: :obj:`bool`
        :returns: returns dictionary
        :rtype: :obj:`list` <`any`>
        """
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
        """ reads a attribute value from the configuration server

        :param name: attribute name
        :type name: :obj:`str`
        :returns: returns an attribute value
        :rtype: `any`
        """
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            dc = self.__dp.read_attribute(name).value
        else:
            dc = getattr(self.__dp, name)

        logger.debug(dc)
        return dc

    def __getList(self, name, encoded=False, argin=None):
        """ returns a result list of the selection server command

        :param name: record name
        :type name: :obj:`str`
        :param encoded: if list should be encoded from JSON
        :type encoded: :obj:`bool`
        :param argin: input command argument
        :type argin: `any`
        :returns: returns the command result list
        :rtype: :obj:`list` <`any`>
        """
        if not self.__dp:
            self.setServer()
        if self.server:
            self.__dp.ping()
            if argin is None:
                dc = self.__dp.command_inout(name)
            else:
                dc = self.__dp.command_inout(name, argin)

        else:
            if argin is None:
                dc = getattr(self.__dp, name)()
            else:
                dc = getattr(self.__dp, name)(argin)

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
        """ returns a result dictionary of the selection server command

        :param name: record name
        :type name: :obj:`str`
        :returns: returns the command result dictionary
        :rtype: :obj:`dict` <`any`, `any`>
        """
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

    def __disableDataSources(self):
        """ provides disable datasources

        :returns: (disable datasources, ds component) dictionary
        :rtype: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        if not self.ddsdirty:
            return dict(self.__ddsbackup)

        res = self.description
        dds = {}
        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if cp in self.cplist \
                       or cp in self.mcplist \
                       or cp in self.dslist \
                       or cp in self.acplist:
                        for ds, values in dss.items():
                            for vl in values:
                                if len(vl) > 0 and vl[0] == 'STEP':
                                    if ds != cp:
                                        dds[ds] = cp
                                        break
        if self.timers:
            for timer in self.timers:
                if timer not in dds.keys():
                    dds[timer] = ''
        self.__ddsbackup = dict(dds)
        self.ddsdirty = False
        return dds

    def clientRecords(self):
        """ provides client recorders

        :returns: list of client recorders
        :rtype: :obj:`list` <:obj:`str`>
        """
        res = self.description
        dds = {}

        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    if cp in self.cplist \
                       or cp in self.mcplist \
                       or cp in self.dslist \
                       or cp in self.acplist:
                        for ds, values in dss.items():
                            for vl in values:
                                if len(vl) > 1 and vl[1] == 'CLIENT':
                                    dds[ds] = vl[2]
        return list(set(dds.values()) - set(self.fullnames.values()) -
                    set(self.recorder_names))

    def stepComponents(self):
        """ provides components with step datasources

        :returns: list of components with step datasources
        :rtype: :obj:`list` <:obj:`str`>
        """
        res = self.description
        cpset = set()
        for cpg in res:
            for cp, dss in cpg.items():
                if isinstance(dss, dict):
                    for values in dss.values():
                        for vl in values:
                            if len(vl) > 0 and vl[0] == 'STEP':
                                cpset.add(cp)
                                break
                        else:
                            continue
                        break
        return list(cpset)

    def clientDataSources(self):
        """ provides client datasources

        :returns: list of client datasources
        :rtype: :obj:`list` <:obj:`str`>
        """
        res = self.dsdescription
        dsset = set()
        for jdsg in res:
            dsg = json.loads(jdsg)
            if isinstance(dsg, dict):
                if dsg['dstype'] == 'CLIENT':
                    dsset.add(dsg['dsname'])
        return list(dsset)

    #: (:obj:`list` <:obj:`str`>) provides disable datasources
    ddsdict = property(__disableDataSources,
                       doc='provides disable datasources')

    def __components(self):
        """ provides selected components

        :returns: list of selected components
        :rtype: :obj:`list` <:obj:`str`>
        """
        if isinstance(self.cpgroup, dict):
            return [cp for cp in self.cpgroup.keys() if self.cpgroup[cp]]
        else:
            return []

    #: (:obj:`list` <:obj:`str`>) provides selected components
    cplist = property(__components,
                      doc='provides selected components')

    def __datasources(self):
        """ provides selected datasources

        :returns: list of selected datasources
        :rtype: :obj:`list` <:obj:`str`>
        """
        if isinstance(self.dsgroup, dict):
            return [cp for cp in self.dsgroup.keys() if self.dsgroup[cp]]
        else:
            return []

    #: (:obj:`list` <:obj:`str`>) provides selected datasources
    dslist = property(__datasources,
                      doc='provides selected datasources')
