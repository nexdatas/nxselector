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
## \file Element.py
# Element

""" device Model """

import logging
logger = logging.getLogger(__name__)

DS, CP = range(2)


## element class
class Element(object):

    ## constructor
    # \param name element name
    # \param eltype element type, i.e. DS or CP
    # \param state recorder settings state
    def __init__(self, name, eltype, state):
        self.name = name
        self.eltype = eltype
        self.state = state

    def __getChecked(self):
        return self._getChecked()

    def __setChecked(self, status):
        self._setChecked(status)

    def _getChecked(self):
        pass

    def _setChecked(self, _):
        pass

    checked = property(__getChecked, __setChecked,
                       doc='check status')

    def __getEnable(self):
        return self._getEnable()

    def _getEnable(self):
        return True

    enable = property(__getEnable, doc='check status')

    def __getDisplay(self):
        return self._getDisplay()

    def __setDisplay(self, status):
        self._setDisplay(status)

    def _getDisplay(self):
        pass

    def _setDisplay(self, _):
        pass

    display = property(__getDisplay, __setDisplay,
                       doc='check status')

    def __str__(self):
        return (self.name, self.eltype, self.state)

    def __repr__(self):
        return "(%s,%s)" % (self.name, self.eltype)


## group element class
class GElement(Element):

    ## constructor
    # \param parent parent widget
    # \param eltype element type, i.e. DS or CP
    # \param state recorder settings state
    def __init__(self, name, eltype, state, dct):
        super(GElement, self).__init__(name, eltype, state)
        self.group = dct

    def _getChecked(self):
        if self.name in self.group.keys():
            return self.group[self.name]
        return False

    def _setChecked(self, status):
        logger.debug("Changed: %s to %s" % (self.name, status))
        self.group[self.name] = bool(status)


## datasource element class
class DSElement(Element):

    ## constructor
    # \param parent parent widget
    # \param state recorder settings state
    def __init__(self, name, state):
        super(DSElement, self).__init__(name, DS, state)

    def _getChecked(self):
        res = self.state.dsgroup
        timers = self.state.timers or []
        if self.name in timers:
            return True
        if self.name in res.keys():
            return res[self.name]
        return False

    def _setChecked(self, status):
        dc = self.state.dsgroup
        dc[self.name] = status
        if not status:
            nd = self.state.nodisplay
            if self.name in nd:
                nd.remove(self.name)

    def _getDisplay(self):
        res = self.state.dsgroup
        nd = self.state.nodisplay
        if self.name not in nd:
            if self.name in res.keys():
                return res[self.name]
        return False

    def _setDisplay(self, status):
        dc = self.state.dsgroup
        nd = self.state.nodisplay
        timers = self.state.timers or []
        if self.name in dc.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
                    if self.name in timers:
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


## datasource element class
class CPElement(Element):

    ## constructor
    # \param parent parent widget
    # \param state recorder settings state
    def __init__(self, name, state, group=None):
        super(CPElement, self).__init__(name, CP, state)
        self.group = group

    def _getEnable(self):
        if self.name in self.group.keys():
            vl = self.group[self.name]
            if vl is None:
                return False
        return True

    def _getChecked(self):
        if not self.group:
            res = self.state.cpgroup
        else:
            res = self.group
        if self.name in res.keys():
            return res[self.name] is True
        return False

    def _setChecked(self, status):
        if not self.group:
            dc = self.state.cpgroup
        else:
            dc = self.group
        dc[self.name] = status
        if not status:
            nd = self.state.nodisplay
            if self.name in nd:
                nd.remove(self.name)

    def _getDisplay(self):
        res = self.state.cpgroup
        nd = self.state.nodisplay
        res = self.state.acpgroup
        if self.name not in nd:
            if self.name in res.keys():
                if res[self.name]:
                    return True
        res = self.state.cpgroup
        if self.name not in nd:
            if self.name in res.keys():
                if res[self.name]:
                    return True
        res = self.state.mcplist
        if self.name not in nd:
            if self.name in res:
                return True
        return False

    def _setDisplay(self, status):
        dc = self.state.cpgroup
        mc = self.state.mcplist
        ac = self.state.acpgroup
        nd = self.state.nodisplay
        if self.name in dc.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
                else:
                    dc[self.name] = True
        elif self.name in ac.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
                else:
                    ac[self.name] = True
        elif self.name in mc:
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
        else:
            if self.name in nd:
                nd.remove(self.name)
