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
# Class with frames

""" main window application dialog """

import json

import logging
from .Element import CP, DS

#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Frames(object):
    """ element group frames
    """

    def __init__(self, settings=None, ds=False, cp=False):
        """ constructor

        :param settings: frame settings
        :type settings: :obj:`list` < :obj:`list` < :obj:`list` \
                         [:obj:`str`, :obj:`int`] > > >
        :param ds: if datasource default frame
        :type ds: :obj:`bool`
        :param cp: if component default frame
        :type cp: :obj:`bool`
        """
        #: (:obj:`int`) datasource frame id
        self.dsid = None
        #: (:obj:`int`) component frame id
        self.cpid = None
        #: (:obj:`dict` <:obj:`int`, :obj:`str`>) (id, label) group dictionary
        self.__dct = None
        self.__settings = None
        #: ([[[:obj:`str`, :obj:`int`]]]) default datasource frame config
        self.defaultds = [[["Channels", 0]]]
        #: ([[[:obj:`str`, :obj:`int]`]]) default component frame config
        self.defaultcp = [[["Components", 1]]]
        self.set(settings, ds, cp)

    def set(self, settings, ds=False, cp=False):
        """ sets frame

        :param settings: frame settings
        :type settings: frame settings
        :param ds: if datasource frame
        :type ds: :obj:`bool`
        :param cp: if component frame
        :type cp: :obj:`bool`
        """
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

        except Exception:
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
        """ create group dictionary
        """
        for frame in self.__settings:
            for column in frame:
                for group in column:
                    if group[1] in self.__dct.keys():
                        raise Exception("Duplicated Frame ID")
                    self.__dct[group[1]] = (group[0])

    def __iter__(self):
        """ provides frame iterator

        :returns: frame iterator
        :rtype: listiterator
        """
        return iter(self.__settings)

    def name(self, fid):
        """ provides frame label from id

        :param fid: frame id
        :type fid: :obj:`int`
        :returns: frame label
        :rtype: :obj:`str`
        """
        if fid in self.__dct.keys():
            return self.__dct[fid][0]

    def ids(self, name=None):
        """ provides frame id from label

        :parama name: frame label
        :type name: :obj:`str`
        :returns: frame id
        :rtype: :obj:`int`
        """
        if not name:
            return self.__dct.keys()
        res = set()
        for mid in self.__dct.keys():
            if name == self.__dct[mid]:
                res.add(mid)
        return res
