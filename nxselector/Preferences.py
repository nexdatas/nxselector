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

import logging
logger = logging.getLogger(__name__)

from .Views import TableView, CheckerView, RadioView, ButtonView, LeftCheckerView, LeftRadioView

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString)

from PyQt4.QtGui import (QMessageBox, QCompleter)
import PyTango

## main window class
class Preferences(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None):
        self.ui = ui
        self.state = state


        # frames/columns/groups
        self.frameshelp = [
            QString('[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'), 
            QString('[[[["My Controllers", 0]]],[[["My Components", 1]]]]'), 
            QString('')]
        self.mgroupshelp = [
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
            "CentralRadioButtons":RadioView,
            "RadioButtons":LeftRadioView,
            "Buttons":ButtonView}

        self.maxHelp = 10

    def connectSignals(self):
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

       
    def reset(self):
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

    def on_devSettingsLineEdit_editingFinished(self):
        server = str(self.ui.devSettingsLineEdit.text())
        if server != self.state.server or True:
            try:
                dp = PyTango.DeviceProxy(server)
                if dp.info().dev_class == 'NXSRecSelector':
                    self.state.server = str(server)
                    self.addHint(server, self.serverhelp)
            except:
                self.reset()
            self.ui.preferences.emit(SIGNAL("serverChanged()"))


    def on_groupLineEdit_editingFinished(self):
        string = str(self.ui.groupLineEdit.text())
        try:
            if not string:
                string = '{}'
            mgroups =  json.loads(string)
            if isinstance(mgroups, dict):
                self.mgroups = string
                self.addHint(string, self.mgroupshelp)
                self.ui.preferences.emit(
                    SIGNAL("groupsChanged(QString)"),
                    QString(qstring)) 
        except:    
            self.reset()

    def addHint(self, string, hints):
        qstring = QString(string)
        if qstring not in hints:
            hints.append(string)
        if self.maxHelp < len(hints):
            hints.pop(0)


    def on_frameLineEdit_editingFinished(self):
        string = str(self.ui.frameLineEdit.text())
        try:
            if not string:
                string = '[]'
            mframes =  json.loads(string)
            
            if isinstance(mframes, list):
                self.frames = string
                self.addHint(string, self.frameshelp)
                self.ui.preferences.emit(
                    SIGNAL("framesChanged(QString)"),
                    QString(string)) 
        except:
            self.reset()



    def updateForm(self):
        self.ui.devSettingsLineEdit.setText(self.state.server)
        self.ui.groupLineEdit.setText(self.mgroups)
        self.ui.frameLineEdit.setText(self.frames)
            

    def apply(self):
        pass
