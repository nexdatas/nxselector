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

import os
import PyTango
import json

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView,
    QLabel, QFrame)

from .Frames import Frames


import logging
logger = logging.getLogger(__name__)


DS,CP = range(2) 

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


    checked = property(__getChecked, __setChecked,
                       doc = 'check status')

    def __str__(self):
        return (self.name, self.eltype, self.selected, self.params)

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
#        self.state.dsgroup = dc


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
#        self.state.cpgroup = dc

