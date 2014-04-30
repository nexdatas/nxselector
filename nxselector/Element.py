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
    # \param params parameters
    def __init__(self, name, eltype, state, params = None):
        self.name = name
        self.eltype = eltype
        self.state = state
        self.params = params 

        
    def __getChecked(self):
        return self._getChecked()

    def __setChecked(self, status):
        self._setChecked(status)

    def _getChecked(self):
        pass

    def _setChecked(self, _):
        pass

    checked = property(__getChecked, __setChecked,
                       doc = 'check status')
    
    


        
    def __getDisplay(self):
        return self._getDisplay()

    def __setDisplay(self, status):
        self._setDisplay(status)

    def _getDisplay(self):
        pass

    def _setDisplay(self, _):
        pass

    display = property(__getDisplay, __setDisplay,
                       doc = 'check status')
    
    


    def __str__(self):
        return (self.name, self.eltype, self.state, self.params)

## datasource element class
class DSElement(Element):
    
    ## constructor
    # \param parent parent widget
    # \param state recorder settings state
    # \param params parameters
    def __init__(self, name, state, params=None):
        super(DSElement, self).__init__(name, DS, state, params)


    def _getChecked(self):
        res = self.state.dsgroup
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
        if self.name in dc.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
        else:
            if self.name in nd:
                nd.remove(self.name)

## datasource element class
class CPElement(Element):
    
    ## constructor
    # \param parent parent widget
    # \param state recorder settings state
    # \param params parameters
    def __init__(self, name, state, params=None, group=None):
        super(CPElement, self).__init__(name, CP, state, params)
        self.group = group

    def _getChecked(self):
        if not self.group:
            res = self.state.cpgroup
        else:
            res = self.group
        if self.name in res.keys():
            return res[self.name]
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
        if self.name not in nd:
            if self.name in res.keys():
                return res[self.name]
        return False


    def _setDisplay(self, status):
        dc = self.state.cpgroup
        nd = self.state.nodisplay
        if self.name in dc.keys():
            if self.name in nd:
                if status:
                    nd.remove(self.name)
            else:
                if not status:
                    nd.append(self.name)
        else:
            if self.name in nd:
                nd.remove(self.name)

