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
    # \param proxy recorder settings proxy
    # \param params parameters
    def __init__(self, name, eltype, proxy, params = None):
        self.name = name
        self.eltype = eltype
        self.dp = proxy
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
    # \param proxy recorder settings proxy
    # \param params parameters
    def __init__(self, name, proxy, params=None):
        super(DSElement, self).__init__(name, DS, proxy, params)


    def _getChecked(self):
        dsg = self.dp.read_attribute("DataSourceGroup").value
        dc = json.loads(dsg)
        if isinstance(dc, dict):
            res = dc
            if self.name in res.keys():
                return res[self.name]
        return False

    def _setChecked(self, status):
        dsg = self.dp.read_attribute("DataSourceGroup").value
        dc = json.loads(dsg)
        if isinstance(dc, dict):
            dc[self.name] = status
            att = json.dumps(dc)
            dsg = self.dp.DataSourceGroup = att


## datasource element class
class CPElement(Element):
    
    ## constructor
    # \param parent parent widget
    # \param proxy recorder settings proxy
    # \param params parameters
    def __init__(self, name, proxy, params=None):
        super(CPElement, self).__init__(name, CP, proxy, params)

    def _getChecked(self):
        cpg = self.dp.read_attribute("ComponentGroup").value
        dc = json.loads(cpg)
        if isinstance(dc, dict):
            res = dc
            if self.name in res.keys():
                return res[self.name]
        return False

    def _setChecked(self, status):
        dsg = self.dp.read_attribute("ComponentGroup").value
        dc = json.loads(dsg)
        if isinstance(dc, dict):
            dc[self.name] = status
            att = json.dumps(dc)
            dsg = self.dp.ComponentGroup = att
