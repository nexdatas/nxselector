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
## \file Preferences.py
# preferences tab 

""" preferences tab """

import os
import PyTango
import json


from PyQt4.QtCore import (SIGNAL, QString)

from PyQt4.QtGui import (QMessageBox, QCompleter, QFileDialog)

from .Views import (TableView, OneTableView, CheckerView, RadioView, 
                    ButtonView, 
                    LeftCheckerView, LeftRadioView, 
                    CheckerViewNL, RadioViewNL, ButtonViewNL, 
                    LeftCheckerViewNL, LeftRadioViewNL,
                    CheckerViewNN, RadioViewNN, ButtonViewNN, 
                    LeftCheckerViewNN, LeftRadioViewNN
                    )

import logging
logger = logging.getLogger(__name__)

## main window class
class Preferences(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None):
        self.ui = ui
        self.state = state


        # frames/columns/groups
        self.frameshelp = [\
            QString('[[[["Devices", 0]]],[[["MCAs", 2],["Misc",1]]]]'),
            QString(
                '[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'), 
            QString('[[[["My Controllers", 0]]],[[["My Components", 1]]]]'), 
            QString('')]
        self.mgroupshelp = [
            QString('[[[["Counters", 0]]],[[["MCAs", 2],["Misc",1]]]]'),
            QString('{"2":[["ct01", 0], ["ct02",0]], "5":[["appscan", 1]]}'), 
            QString('')]
        self.serverhelp = [
            QString(self.state.server)]
        
        self.mgroups = str(self.mgroupshelp[0])
        self.frames = str(self.frameshelp[0])

        self.views = {
            "CentralCheckBoxes":CheckerView, 
            "CheckBoxes":LeftCheckerView, 
            "Tables":TableView, 
            "Columns":OneTableView, 
            "CentralRadioButtons":RadioView,
            "RadioButtons":LeftRadioView,
            "Buttons":ButtonView,
            "CentralCheckBoxes (NL)":CheckerViewNL, 
            "CheckBoxes (NL)":LeftCheckerViewNL, 
            "CentralRadioButtons (NL)":RadioViewNL,
            "RadioButtons (NL)":LeftRadioViewNL,
            "Buttons (NL)":ButtonViewNL,
            "CentralCheckBoxes (NN)":CheckerViewNN, 
            "CheckBoxes (NN)":LeftCheckerViewNN, 
            "CentralRadioButtons (NN)":RadioViewNN,
            "RadioButtons (NN)":LeftRadioViewNN,
            "Buttons (NN)":ButtonViewNN
            }

        self.maxHelp = 10
        self.profFile = os.getcwd()

    def disconnectSignals(self):
        self.ui.preferences.disconnect(
            self.ui.devSettingsLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_devSettingsLineEdit_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.groupLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_groupLineEdit_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.frameLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_frameLineEdit_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.profLoadPushButton, 
            SIGNAL("pressed()"), self.profileLoad)
        self.ui.preferences.disconnect(
            self.ui.profSavePushButton, 
            SIGNAL("pressed()"), self.profileSave)

    def connectSignals(self):
        self.disconnectSignals()
        self.ui.preferences.connect(
            self.ui.frameLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_frameLineEdit_editingFinished)

        self.ui.preferences.connect(
            self.ui.groupLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_groupLineEdit_editingFinished)

        self.ui.preferences.connect(
            self.ui.devSettingsLineEdit,
            SIGNAL("editingFinished()"), 
            self.on_devSettingsLineEdit_editingFinished)

        self.ui.preferences.connect(
            self.ui.profLoadPushButton, 
            SIGNAL("pressed()"), self.profileLoad)
        self.ui.preferences.connect(
            self.ui.profSavePushButton, 
            SIGNAL("pressed()"), self.profileSave)
       
    def reset(self):
        logger.debug("reset preferences")
        self.disconnectSignals()
        if self.ui.viewComboBox.count() != len(self.views.keys()):
            self.ui.viewComboBox.clear()
            self.ui.viewComboBox.addItems(sorted(self.views.keys()))
        completer = QCompleter(self.mgroupshelp, self.ui.preferences)
        self.ui.groupLineEdit.setCompleter(completer)
        completer = QCompleter(self.serverhelp, self.ui.preferences)
        self.ui.devSettingsLineEdit.setCompleter(completer) 
        completer = QCompleter(self.frameshelp, self.ui.preferences)
        self.ui.frameLineEdit.setCompleter(completer)
        self.updateForm()
        self.connectSignals()
        logger.debug("reset preferences ended")

    def on_devSettingsLineEdit_editingFinished(self):
        logger.debug("on_devSettingsLineEdit_editingFinished")
        self.disconnectSignals()
        logger.debug("server changing")
        server = str(self.ui.devSettingsLineEdit.text())
        logger.debug("from %s to  %s" % (self.state.server, server))
        if server != self.state.server:
            replay = QMessageBox.question(
                self.ui.preferences, 
                "Setting server has changed.", 
                "Changing server will cause loosing the current data. " \
                    + " Are you sure?",
                QMessageBox.Yes|QMessageBox.No)
            if replay == QMessageBox.Yes:
                try:
                    dp = PyTango.DeviceProxy(server)
                    if dp.info().dev_class == 'NXSRecSelector':
                        self.state.server = str(server)
                        self.addHint(server, self.serverhelp)
                except:
                    self.reset()
                self.connectSignals()
                self.ui.preferences.emit(SIGNAL("serverChanged()"))
            else:
                self.ui.devSettingsLineEdit.setText(QString(self.state.server))
        self.connectSignals()
        logger.debug("server changed")

    def on_groupLineEdit_editingFinished(self):
        logger.debug("on_groupLineEdit_editingFinished")
        self.disconnectSignals()
        string = str(self.ui.groupLineEdit.text())
        try:
            if not string:
                string = '{}'
            mgroups =  json.loads(string)
            if isinstance(mgroups, dict):
                self.mgroups = string
                self.addHint(string, self.mgroupshelp)
                self.connectSignals()
                self.ui.preferences.emit(
                    SIGNAL("groupsChanged(QString)"),
                    QString(string)) 
        except Exception as e :    
            logger.debug(str(e))
            self.reset()
        self.connectSignals()

    def addHint(self, string, hints):
        qstring = QString(string)
        if qstring not in hints:
            hints.append(string)
        if self.maxHelp < len(hints):
            hints.pop(0)

    def on_frameLineEdit_editingFinished(self):
        logger.debug("on_frameLineEdit_editingFinished")
        self.disconnectSignals()
        string = str(self.ui.frameLineEdit.text())
        try:
            if not string:
                string = '[]'
            mframes =  json.loads(string)
            
            if isinstance(mframes, list):
                self.frames = string
                self.addHint(string, self.frameshelp)
                self.connectSignals()
                self.ui.preferences.emit(
                    SIGNAL("framesChanged(QString)"),
                    QString(string)) 
        except:
            self.reset()

        self.connectSignals()


    def updateForm(self):
        self.ui.devSettingsLineEdit.setText(self.state.server)
        self.ui.groupLineEdit.setText(self.mgroups)
        self.ui.frameLineEdit.setText(self.frames)
            

    def apply(self):
        pass


    def profileLoad(self):    
        filename = str(
            QFileDialog.getOpenFileName(
                self.ui.preferences,
                "Load Profile",        
                self.profFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("loading profile from %s" % filename)
        if filename:
            self.profFile = filename
            jprof = open(filename).read()
            try:
                profile = json.loads(jprof)
                if isinstance(profile, dict):
                    if "server" in profile.keys():
                        self.ui.devSettingsLineEdit.setText(
                            QString(profile["server"]))
                        self.on_devSettingsLineEdit_editingFinished()
                    if "frames" in profile.keys():
                        self.ui.frameLineEdit.setText(
                            QString(profile["frames"]))
                        self.on_frameLineEdit_editingFinished()
                    if "groups" in profile.keys():
                        self.ui.groupLineEdit.setText(
                            QString(profile["groups"]))
                        self.ui.groupLineEdit.emit(
                            SIGNAL("groupsChanged(QString)"),
                            self.ui.groupLineEdit.text()) 
                        self.on_groupLineEdit_editingFinished()
                    if "rowMax" in profile.keys():
                        self.ui.rowMaxSpinBox.setValue(
                            int(profile["rowMax"]))
                        
            except Exception as e:
                QMessageBox.warning(
                    self.ui.preferences, 
                    "Error during reading the file",
                    str(e))
                

    def profileSave(self):
        filename = str(QFileDialog.getSaveFileName(
                self.ui.storage,
                "Save Profile",
                self.profFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("saving profile to %s" % filename)
        if filename:
            self.profFile = filename
            profile = {}
            profile["server"] = str(self.ui.devSettingsLineEdit.text())
            profile["frames"] = str(self.ui.frameLineEdit.text())
            profile["groups"] = str(self.ui.groupLineEdit.text())
            profile["rowMax"] = self.ui.rowMaxSpinBox.value()
            jprof = json.dumps(profile)
            with open(filename, 'w') as myfile:
                myfile.write(jprof)
            
