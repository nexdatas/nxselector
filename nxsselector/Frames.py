#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsselector nexdatas
## \file Frames.py
# Class with frames

""" main window application dialog """

import json

import logging
logger = logging.getLogger(__name__)

from .Element import CP, DS


## main window class
class Frames(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, settings=None, ds=False, cp=False):

        self.dsid = None
        self.cpid = None
        self.__dct = None
        self.__settings = None
        self.defaultds = [[["Channels", 0]]]
        self.defaultcp = [[["Components", 1]]]
        self.set(settings, ds, cp)

    def set(self, settings, ds=False, cp=False):
        if settings:
            mysettings = json.loads(settings)
        else:
            mysettings = None
        self.__dct = {}
        self.__settings = [self.defaultds, self.defaultcp]
        try:
            if mysettings is not None:
                groups = set()
                if ds or cp:
                    for frame in mysettings:
                        for column in frame:
                            for group in column:
                                groups.add(group[1])
                if cp and CP not in groups:
                    mysettings.insert(0, self.defaultcp)
                if ds and DS not in groups:
                    mysettings.insert(0, self.defaultds)
                self.__settings = list(mysettings)
            self.__makedict()

            ids = set(self.ids())
            if len(ids) < 1:
                self.__settings = [self.defaultds]
                self.__makedict()

        except:
            self.__settings = [self.defaultds, self.defaultcp]
            self.__makedict()

        ids = list(set(self.ids()))
        self.dsid = ids[0]
        if len(ids) > 1:
            self.cpid = ids[1]
        else:
            self.cpid = ids[0]
        logger.debug("DSid = %s, CPid = %s " % (self.dsid, self.cpid))
        logger.debug(self.__dct)
        logger.debug(self.ids())

    def __makedict(self):
        for frame in self.__settings:
            for column in frame:
                for group in column:
                    if group[1] in self.__dct.keys():
                        raise Exception("Duplicated Frame ID")
                    self.__dct[group[1]] = (group[0])

    def __iter__(self):
        return iter(self.__settings)

    def name(self, fid):
        if fid in self.__dct.keys():
            return self.__dct[fid][0]

    def ids(self, name=None):
        if not name:
            return self.__dct.keys()
        res = set()
        for mid in self.__dct.keys():
            if name == self.__dct[mid]:
                res.add(mid)
        return res