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
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString)
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

        settings = QSettings()

        self.userView = self.restoreString(
            settings, 'Preferences/UserView', 'CheckBoxes')


        ## user interface
        self.ui = Ui_Selector()
        self.preferences = Preferences(self.ui, self.state)
        self.storage = Storage(self.ui, self.state)
        self.selectable = Selectable(
            self.ui, self.state, 
            self.preferences.views[self.userView])

        self.preferences.mgroups = str(self.restoreString(
                settings, 'Preferences/Groups', '{}'))
        self.preferences.frames = self.restoreString(
                settings, 'Preferences/Frames', '[]')

        self.preferences.mgroupshelp = self.restoreList(
                settings, 'Preferences/GroupsHints', 
                self.preferences.mgroupshelp)
        self.preferences.frameshelp = self.restoreList(
                settings, 'Preferences/FramesHints',
                self.preferences.frameshelp)
        
        self.preferences.addHint(
            self.preferences.mgroups,
            self.preferences.mgroupshelp)
        self.preferences.addHint(
            self.preferences.frames,
            self.preferences.frameshelp)

        self.selectable.mgroups = str(self.preferences.mgroups)
        self.selectable.frames = Frames(self.preferences.frames)
        self.automatic = Automatic(
            self.ui, self.state, 
            self.preferences.views[self.userView])
        self.mandatory = Mandatory(
            self.ui, self.state, 
            self.preferences.views[self.userView])


        self.tabs = [self.selectable, self.automatic, self.mandatory,
                     self.storage, self.preferences]

        self.createGUI()  
        
        self.restoreGeometry(
            settings.value("Selector/Geometry").toByteArray())



    def restoreString(self, settings, name, default):
        res = default
        try:
            res = unicode(settings.value(name).toString())  
            if not res:
                res = default
        except:
            res = default
        return res

    def restoreList(self, settings, name, default):
        res = default
        try:
            res = settings.value(name).toList()
            if not res:
                res = default
        except:
            res = default
        return res



    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
        for tab in self.tabs:
            tab.reset()
            
        cid = self.ui.viewComboBox.findText(QString(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid) 
            
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Apply), 
                     SIGNAL("clicked()"), self.apply)
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Reset), 
                     SIGNAL("clicked()"), self.reset)

        self.connect(self.ui.preferences, 
                     SIGNAL("serverChanged()"), self.resetServer)

        self.connect(self.ui.preferences, 
                     SIGNAL("groupsChanged(QString)"), self.resetGroups)

        self.connect(self.ui.preferences, 
                     SIGNAL("framesChanged(QString)"), self.resetFrames)

        self.connect(self.ui.viewComboBox, 
                     SIGNAL("currentIndexChanged(int)"), self.resetViews)

        

    def __saveSettings(self):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))
        settings.setValue(
            "Preferences/UserView",
            QVariant(str(self.ui.viewComboBox.currentText())))
        settings.setValue(
            "Preferences/Groups",
            QVariant(str(self.preferences.mgroups)))
        settings.setValue(
            "Preferences/Frames",
            QVariant(str(self.preferences.frames)))
        settings.setValue(
            "Preferences/FramesHints",
            QVariant(str(self.preferences.frameshelp)))
        settings.setValue(
            "Preferences/GroupsHints",
            QVariant(str(self.preferences.mgroupshelp)))

                    
    def closeEvent(self, event):
        self.__saveSettings()

    def resetServer(self):
        self.state.setServer()
        self.reset()

    def resetGroups(self, groups):
        self.selectable.mgroups = str(groups)
        self.resetViews()


    def resetFrames(self, frames):
        self.selectable.frames = Frames(str(frames))
        self.resetViews()

    def resetViews(self):
        for tab in self.tabs:
            tab.userView = self.preferences.views[
                str(self.ui.viewComboBox.currentText())]
        self.reset()
        
    def reset(self):
        self.state.fetchSettings()
        for tab in self.tabs:
            tab.reset()

    def apply(self):
        self.state.updateMntGrp()
