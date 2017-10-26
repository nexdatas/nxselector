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
# Element

""" device Model """

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

#: (:obj:`int`) datasource=0, component=1  element types
DS, CP = range(2)


class Element(object):
    """ element class
    """

    def __init__(self, name, eltype, state):
        """ constructor

        :param name: element name
        :type name: :obj:`str`
        :param eltype: element type, i.e. DS=0 or CP=1
        :type eltype: :obj:`int`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        """
        #: (:obj:`str`) element name
        self.name = name
        #: (:obj:`int`) element type, i.e. DS=0 or CP=1
        self.eltype = eltype
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = state

    def __getChecked(self):
        """ getter for checked flag

        :returns: if element is checked
        :rtype: :obj:`bool` or `None`
        """
        return self._getChecked()

    def __setChecked(self, status):
        """ setter for checked flag

        :param status: check status
        :type: :obj:`bool` or `None`
        """
        self._setChecked(status)

    def _getChecked(self):
        """ virtual getter for checked flag

        :returns: if element is checked
        :rtype: :obj:`bool` or `None`
        """
        pass

    def _setChecked(self, _):
        """ virtual setter for checked flag

        :param status: check status
        :type: :obj:`bool` or `None`
        """
        pass

    checked = property(__getChecked, __setChecked,
                       doc='check status')

    def __getEnable(self):
        """ getter for enable flag

        :returns: if element is enable
        :rtype: :obj:`bool`
        """
        return self._getEnable()

    def _getEnable(self):
        """ virtual getter for enable flag

        :returns: if element is enable
        :rtype: :obj:`bool`
        """
        return True

    enable = property(__getEnable, doc='check status')

    def __getDisplay(self):
        """ getter for display flag

        :returns: if element should be displayed
        :rtype: :obj:`bool`
        """
        return self._getDisplay()

    def __setDisplay(self, status):
        """ setter for display flag

        :param status: display status
        :type: :obj:`bool` or `None`
        """
        self._setDisplay(status)

    def _getDisplay(self):
        """ virtual getter for display flag

        :returns: if element should be displayed
        :rtype: :obj:`bool`
        """
        pass

    def _setDisplay(self, _):
        """ virtual setter for display flag

        :param status: display status
        :type: :obj:`bool` or `None`
        """
        pass

    display = property(__getDisplay, __setDisplay,
                       doc='check status')

    def __str__(self):
        return (self.name, self.eltype, self.state)

    def __repr__(self):
        return "(%s,%s)" % (self.name, self.eltype)


class GElement(Element):
    """ group element class
    """

    def __init__(self, name, eltype, state, dct):
        """ constructor

        :param name: element name
        :type name: :obj:`str`
        :param eltype: element type, i.e. DS=0 or CP=1
        :type eltype: :obj:`int`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        :param dct: element selection group
        :type dct: :obj:`dict` <:obj:`str`, :obj:`bool` or `None`>
        """
        super(GElement, self).__init__(name, eltype, state)
        #: (:obj:`dict` <:obj:`str`, :obj:`bool` or `None`> ) \
        #:     element selection group
        self.group = dct

    def _getChecked(self):
        """ getter for checked flag

        :returns: if element is checked
        :rtype: :obj:`bool` or `None`
        """
        if self.name in self.group.keys():
            return self.group[self.name]
        return False

    def _setChecked(self, status):
        """ setter for checked flag

        :param status: check status
        :type: :obj:`bool` or `None`
        """
        logger.debug("Changed: %s to %s" % (self.name, status))
        self.group[self.name] = bool(status)


class DSElement(Element):
    """ datasource element class
    """

    def __init__(self, name, state):
        """ constructor

        :param name: element name
        :type name: :obj:`str`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        """
        super(DSElement, self).__init__(name, DS, state)

    def _getChecked(self):
        """ getter for checked flag

        :returns: if element is checked
        :rtype: :obj:`bool` or `None`
        """
        res = self.state.dsgroup
        timers = self.state.timers or []
        if self.name in timers:
            return True
        if self.name in res.keys():
            return res[self.name]
        return False

    def _setChecked(self, status):
        """ setter for checked flag

        :param status: check status
        :type: :obj:`bool` or `None`
        """
        dc = self.state.dsgroup
        dc[self.name] = status
        self.state.ddsdirty = True
        if not status:
            nd = self.state.nodisplay
            if self.name in nd:
                nd.remove(self.name)

    def _getDisplay(self):
        """ getter for display flag

        :returns: if element should be displayed
        :rtype: :obj:`bool`
        """
        res = self.state.dsgroup
        nd = self.state.nodisplay
        if self.name not in nd:
            if self.name in res.keys():
                return res[self.name]
        return False

    def _setDisplay(self, status):
        """ setter for display flag

        :param status: display status
        :type: :obj:`bool` or `None`
        """
        dc = self.state.dsgroup
        nd = self.state.nodisplay
        timers = self.state.timers or []
        if self.name in dc.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
                    dc[self.name] = True
            else:
                if not status:
                    if self.name in timers:
                        dc[self.name] = False
                    else:
                        nd.append(self.name)
                else:
                    dc[self.name] = True

        else:
            if self.name in nd:
                nd.remove(self.name)


class CPElement(Element):
    """ datasource element class
    """

    def __init__(self, name, state, group=None):
        """ constructor

        :param name: element name
        :type name: :obj:`str`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        :param group: element selection group
        :type group: :obj:`dict` <:obj:`str`, :obj:`bool` or `None`>
        """
        super(CPElement, self).__init__(name, CP, state)
        self.group = group

    def _getEnable(self):
        """ getter for enable flag

        :returns: if element is enable
        :rtype: :obj:`bool`
        """
        if self.group and self.name in self.group.keys():
            vl = self.group[self.name]
            if vl is None:
                return False
        return True

    def _getChecked(self):
        """ getter for checked flag

        :returns: if element is checked
        :rtype: :obj:`bool` or `None`
        """
        if not self.group:
            res = self.state.cpgroup
            dsres = self.state.dsgroup
        else:
            res = self.group
            dsres = {}
        if self.name in res.keys():
            return res[self.name] is True
        if self.name in dsres.keys():
            return dsres[self.name] is True
        return False

    def _setChecked(self, status):
        """ setter for checked flag

        :param status: check status
        :type: :obj:`bool` or `None`
        """
        self.state.ddsdirty = True
        if not status:
            dds = self.state.ddsdict
        self.state.ddsdirty = True
        if not self.group:
            ds = self.state.dsgroup
            dc = self.state.cpgroup
        else:
            dc = self.group
            ds = {}
        dc[self.name] = status
        self.state.ddsdirty = True
        if self.name in ds.keys():
            ds[self.name] = status
            self.state.ddsdirty = True
        if not status:
            # res = self.state.cpgroup
            nd = self.state.nodisplay
            if self.name in nd:
                nd.remove(self.name)
        else:
            dds = self.state.ddsdict
        for dd, cp in dds.items():
            if cp == self.name:
                if dd in ds:
                    ds[dd] = status
                    self.state.ddsdirty = True
                if dd in dc:
                    dc[dd] = status
                    self.state.ddsdirty = True
                if not status and dd in nd:
                    nd.remove(dd)

    def _getDisplay(self):
        """ getter for display flag

        :returns: if element should be displayed
        :rtype: :obj:`bool`
        """
        cpres = self.state.cpgroup
        dsres = self.state.dsgroup
        nd = self.state.nodisplay
        acpres = self.state.acpgroup
        mcpres = self.state.mcplist
        if self.name not in nd:
            if (self.name in acpres.keys() and acpres[self.name]) or \
               (self.name in cpres.keys() and cpres[self.name]) or \
               (self.name in cpres.keys() and cpres[self.name]) or \
               (self.name in dsres.keys() and dsres[self.name]) or \
               self.name in mcpres:
                return True
        return False

    def _setDisplay(self, status):
        """ setter for display flag

        :param status: display status
        :type: :obj:`bool` or `None`
        """

        dc = self.state.cpgroup
        mc = self.state.mcplist
        ac = self.state.acpgroup
        ds = self.state.dsgroup
        nd = self.state.nodisplay
        dds = self.state.ddsdict
        found = False
        if self.name in ds.keys():
            found = True
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
                else:
                    ds[self.name] = True
        if self.name in dc.keys():
            found = True
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
                else:
                    dc[self.name] = True
        if self.name in ac.keys():
            found = True
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
                else:
                    ac[self.name] = True
        if self.name in mc:
            found = True
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
        if not found:
            if self.name in nd:
                nd.remove(self.name)
        for dd, cp in dds.items():
            if cp == self.name:
                if dd in nd:
                    if status:
                        nd.remove(dd)
                else:
                    if not status:
                        nd.append(dd)
                    else:
                        if dd in dc.keys():
                            dc[dd] = True
                        ds[dd] = True
