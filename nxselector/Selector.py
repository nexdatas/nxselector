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
import sys 
import PyTango
import json
 
from PyQt4 import QtCore, QtGui
 
from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView, QDialogButtonBox,
    QLabel, QFrame, QHeaderView, QFileDialog)

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

        
        try:
            self.state = ServerState(server)
        except PyTango.DevFailed as e:
            exctype , value = sys.exc_info()[:2]
            QMessageBox.warning(
                self, 
                "Error in Setting Server",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
            sys.exit(-1)
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Error in Setting Server",
                str(e.DevError))
            sys.exit(-1)

        self.state.fetchSettings()

        settings = QSettings()

        self.userView = self.restoreString(
            settings, 'Preferences/UserView', 'CheckBoxes')

        self.rowMax = self.restoreInt(
            settings, 'Preferences/RowMax', 0)


        ## user interface
        self.ui = Ui_Selector()
        self.preferences = Preferences(self.ui, self.state)
        self.storage = Storage(self.ui, self.state)
        self.selectable = Selectable(
            self.ui, self.state, 
            self.preferences.views[self.userView],
            self.rowMax)

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
            self.preferences.views[self.userView],
            self.rowMax)
        self.mandatory = Mandatory(
            self.ui, self.state, 
            self.preferences.views[self.userView],
            self.rowMax)


        self.tabs = [self.selectable, self.automatic, self.mandatory,
                     self.storage, self.preferences]

        self.createGUI()  
        
        self.restoreGeometry(
            settings.value("Selector/Geometry").toByteArray())



    def restoreInt(self, settings, name, default):
        res = default
        try:
            res = int(settings.value(name).toInt()[0])  
            if not res:
                res = default
        except:
            res = default
        return res

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
        self.ui.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Reset | QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Close)
        for tab in self.tabs:
            tab.reset()
            
        cid = self.ui.viewComboBox.findText(QString(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid) 
        self.ui.rowMaxSpinBox.setValue(self.rowMax)    
            
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Apply), 
                     SIGNAL("pressed()"), self.apply)
        self.connect(self.ui.buttonBox.button(QDialogButtonBox.Reset), 
                     SIGNAL("pressed()"), self.resetAll)

        self.connect(self.ui.cnfLoadPushButton, 
                     SIGNAL("pressed()"), self.cnfLoad)
        self.connect(self.ui.cnfSavePushButton, 
                     SIGNAL("pressed()"), self.cnfSave)

        self.connect(self.ui.preferences, 
                     SIGNAL("serverChanged()"), self.resetServer)

        self.connect(self.ui.preferences, 
                     SIGNAL("groupsChanged(QString)"), self.resetGroups)

        self.connect(self.ui.preferences, 
                     SIGNAL("framesChanged(QString)"), self.resetFrames)

        self.connect(self.ui.viewComboBox, 
                     SIGNAL("currentIndexChanged(int)"), self.resetViews)

        self.connect(self.ui.rowMaxSpinBox, 
                     SIGNAL("valueChanged(int)"), self.resetRows)

        

    def __saveSettings(self):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))
        settings.setValue(
            "Preferences/UserView",
            QVariant(str(self.ui.viewComboBox.currentText())))
        settings.setValue(
            "Preferences/RowMax",
            QVariant(self.ui.rowMaxSpinBox.value()))
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
        logger.debug("reset server")
        self.state.setServer()
        self.reset()
        logger.debug("reset server ended")

    def resetGroups(self, groups):
        logger.debug("reset groups")
        self.selectable.mgroups = str(groups)
        self.resetViews()
        logger.debug("reset groups ended")


    def resetFrames(self, frames):
        logger.debug("reset famces")
        self.selectable.frames = Frames(str(frames))
        self.resetViews()
        logger.debug("reset famces ended")


    def resetRows(self, rowMax):
        logger.debug("reset rows")
        for tab in self.tabs:
            tab.rowMax = rowMax
        self.resetViews()
        logger.debug("reset rows ended")
        
    def resetViews(self):
        for tab in self.tabs:
            tab.userView = self.preferences.views[
                str(self.ui.viewComboBox.currentText())]
            tab.reset()
        
    def reset(self):
        logger.debug("reset selector")
        self.state.fetchSettings()
        for tab in self.tabs:
            tab.reset()
        logger.debug("reset selector ended")

    def resetAll(self):
        logger.debug("reset ALL")
        self.state.updateControllers()
        self.reset()
        logger.debug("reset ENDED")
        

    def cnfLoad(self):    
        filename = str(QFileDialog.getOpenFileName(
                self.ui.preferences,
                "Load File",        
                self.state.cnfFile,
                "JSON files (*.json, *.cfg);;All files (*)"))
        logger.debug("loading from %s" % filename)
        if filename:
            self.state.load(filename)
            self.resetAll()
        

    def cnfSave(self):
        filename = str(QFileDialog.getSaveFileName(
                self.ui.preferences,
                "Save File",
                self.state.cnfFile,
                "JSON files (*.json, *.cfg);;All files (*)"))
        logger.debug("saving to %s" % filename)
        if filename:
            self.state.save(filename)
            self.resetAll()


    def apply(self):
        try:
            self.state.updateMntGrp()
            self.resetAll()
        except PyTango.DevFailed as e:
            exctype , value = sys.exc_info()[:2]
            QMessageBox.warning(
                self, 
                "Error in updating Measurement Group",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Error in updating Measurement Group",
                str(e.DevError))
