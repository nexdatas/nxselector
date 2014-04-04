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
## \package nxselecto nexdatas
## \file Selector.py
# Main window of the application

""" main window application dialog """

import os
import PyTango
import json

 
from PyQt4 import QtCore, QtGui
 
from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView, QDialogButtonBox,
    QLabel, QFrame, QHeaderView)

from .Frames import Frames
from .Element import Element, DSElement, CPElement, CP, DS
from .ElementModel import ElementModel, ElementDelegate
from .ServerState import ServerState
from .ui.ui_selector import Ui_Selector

from .Selectable import Selectable
from .Preferences import Preferences
from .Automatic import Automatic
from .Mandatory import Mandatory
from .Storage import Storage


from .Views import TableView, CheckerView, RadioView

import logging
logger = logging.getLogger(__name__)

    

## main window class
class Selector(QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, parent=None):
        super(Selector, self).__init__(parent)
        logger.debug("PARAMETERS: %s %s", 
                     server, parent)

        
        self.state = ServerState(server)
        self.state.fetchSettings()


        self.userView = TableView
        self.userView = RadioView
        self.userView = CheckerView

        ## user interface
        self.ui = Ui_Selector()
        self.selectable = Selectable(self.ui, self.state, self.userView)
        self.automatic = Automatic(self.ui, self.state, self.userView)
        self.mandatory = Mandatory(self.ui, self.state, self.userView)
        self.storage = Storage(self.ui, self.state)
        self.preferences = Preferences(self.ui, self.state)

        self.createGUI()            
        self.updateGroups()
        self.setModels()
        
        settings = QSettings()
        self.restoreGeometry(
            settings.value("Selector/Geometry").toByteArray())

    def updateGroups(self):
        self.selectable.updateGroups()
        self.automatic.updateGroups()
        self.mandatory.updateGroups()
        
                
    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
        self.selectable.createGUI()
        self.automatic.createGUI()
        self.mandatory.createGUI()

        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Apply), 
                     SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Reset), 
                     SIGNAL("clicked()"), self.reset)





            
    def setModels(self):
        self.selectable.setModels()
        self.automatic.setModels()
        self.mandatory.setModels()
            
    def updateViews(self):
        self.selectable.updateViews()
        self.automatic.updateViews()
        self.mandatory.updateViews()

    def __saveSettings(self):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))
                    
    def closeEvent(self, event):
        self.__saveSettings()

    def reset(self):
        self.state.fetchSettings()
        self.selectable.reset()
        self.automatic.reset()
        self.mandatory.reset()

    def apply(self):
        self.state.updateMntGrp()
