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

#from PyQt4.QtGui import (QMessageBox, QCompleter, QFileDialog)
#from PyQt4.QtCore import (SIGNAL, QString)

from taurus.external.qt import Qt


from .Views import (TableView, OneTableView, 
                    CheckerView, RadioView, ButtonView, 
                    LeftCheckerView, LeftRadioView, 
                    CheckerViewNL, RadioViewNL, ButtonViewNL, 
                    LeftCheckerViewNL, LeftRadioViewNL,
                    CheckerViewNN, RadioViewNN, ButtonViewNN, 
                    LeftCheckerViewNN, LeftRadioViewNN,
                    CheckDisView, RadioDisView,
                    CheckDisViewNL, RadioDisViewNL, 
                    CheckDisViewNN, RadioDisViewNN
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

            Qt.QString('[[[["Components",1],["Timers",5]]],[[["Counters", 4]],' \
                        + '[["ADC",3]]],[[["MCA/SCA",6],["Devices",0]]]]'),
            Qt.QString('[[[["Counters", 4]],[["Channels",0]]],' \
                        + '[[["MCAs", 2],["Misc",1]]],[[["ADC",3]]]]'),
            Qt.QString('[[[["Devices", 0]]],[[["MCAs", 2],["Misc",1]]]]'),
            Qt.QString(
                '[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'), 
            Qt.QString('[[[["My Channels", 0]]],[[["My Components", 1]]]]'), 
            Qt.QString('')]
        self.mgroupshelp = [            
            Qt.QString('{ "3":[["exp_adc*", 0]], "4":[["exp_c*",0]],' \
                        + '"5":[["exp_t*",0]], "6":[["exp_mca*",0],' \
                        + '["sca_exp_*",0]]}'),
            Qt.QString('{"2":[["mca8701*", 1]] , "3":[["exp_adc*", 0]],' \
                        + ' "4":[["exp_c*",0]]}'),
            Qt.QString('{"2":[["ct01", 0], ["ct02",0]], "5":[["appscan", 1]]}'), 
            Qt.QString('')]
        self.serverhelp = [
            Qt.QString(self.state.server)]
        
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
            "Buttons (NN)":ButtonViewNN,
            "CheckBoxes Dis":CheckDisView, 
            "RadioButtons Dis":RadioDisView,
#            "Buttons Dis":ButtonDisView,
            "CheckBoxes Dis (NL)":CheckDisViewNL, 
            "RadioButtons Dis (NL)":RadioDisViewNL,
#            "Buttons Dis (NL)":ButtonDisViewNL,
            "CheckBoxes Dis (NN)":CheckDisViewNN, 
            "RadioButtons Dis (NN)":RadioDisViewNN,
#            "Buttons Dis (NN)":ButtonDisViewNN
            }

        self.maxHelp = 10
        self.profFile = os.getcwd()

    def disconnectSignals(self):
        self.ui.preferences.disconnect(
            self.ui.devSettingsLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_devSettingsLineEdit_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.groupLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_layoutLineEdits_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.frameLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_layoutLineEdits_editingFinished)

        self.ui.preferences.disconnect(
            self.ui.profLoadPushButton, 
            Qt.SIGNAL("pressed()"), self.profileLoad)
        self.ui.preferences.disconnect(
            self.ui.profSavePushButton, 
            Qt.SIGNAL("pressed()"), self.profileSave)

    def connectSignals(self):
        self.disconnectSignals()
        self.ui.preferences.connect(
            self.ui.frameLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_layoutLineEdits_editingFinished)

        self.ui.preferences.connect(
            self.ui.groupLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_layoutLineEdits_editingFinished)

        self.ui.preferences.connect(
            self.ui.devSettingsLineEdit,
            Qt.SIGNAL("editingFinished()"), 
            self.on_devSettingsLineEdit_editingFinished)

        self.ui.preferences.connect(
            self.ui.profLoadPushButton, 
            Qt.SIGNAL("pressed()"), self.profileLoad)
        self.ui.preferences.connect(
            self.ui.profSavePushButton, 
            Qt.SIGNAL("pressed()"), self.profileSave)
       
    def reset(self):
        logger.debug("reset preferences")
        self.disconnectSignals()
        if self.ui.viewComboBox.count() != len(self.views.keys()):
            self.ui.viewComboBox.clear()
            self.ui.viewComboBox.addItems(sorted(self.views.keys()))
        completer = Qt.QCompleter(self.mgroupshelp, self.ui.preferences)
        self.ui.groupLineEdit.setCompleter(completer)
        completer = Qt.QCompleter(self.serverhelp, self.ui.preferences)
        self.ui.devSettingsLineEdit.setCompleter(completer) 
        completer = Qt.QCompleter(self.frameshelp, self.ui.preferences)
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
            replay = Qt.QMessageBox.question(
                self.ui.preferences, 
                "Setting server has changed.", 
                "Changing server will cause loosing the current data. " \
                    + " Are you sure?",
                Qt.QMessageBox.Yes|Qt.QMessageBox.No)
            if replay == Qt.QMessageBox.Yes:
                try:
                    dp = PyTango.DeviceProxy(server)
                    if dp.info().dev_class == 'NXSRecSelector':
                        self.state.server = str(server)
                        self.addHint(server, self.serverhelp)
                except:
                    self.reset()
                self.connectSignals()
                self.ui.preferences.emit(Qt.SIGNAL("serverChanged()"))
            else:
                self.ui.devSettingsLineEdit.setText(Qt.QString(self.state.server))
        self.connectSignals()
        logger.debug("server changed")


    def addHint(self, string, hints):
        qstring = Qt.QString(string)
        if qstring not in hints:
            hints.append(string)
        if self.maxHelp < len(hints):
            hints.pop(0)

    def on_layoutLineEdits_editingFinished(self):
        logger.debug("on_groupLineEdit_editingFinished")
        self.disconnectSignals()

        groups = str(self.ui.groupLineEdit.text())
        frames = str(self.ui.frameLineEdit.text())
        try:
            if not frames:
                frames = '[]'
            mframes =  json.loads(frames)
            if isinstance(mframes, list):
                self.frames = frames
                self.addHint(frames, self.frameshelp)

            if not groups:
                groups = '{}'
            mgroups =  json.loads(groups)

            if isinstance(mgroups, dict):
                self.mgroups = groups
                self.addHint(groups, self.mgroupshelp)

                if isinstance(mframes, list):
                    self.connectSignals()
                    self.ui.preferences.emit(
                        Qt.SIGNAL("layoutChanged(QString,QString)"),
                        Qt.QString(frames),Qt.QString(groups)) 
        except Exception as e :    
            logger.debug(str(e))
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
            Qt.QFileDialog.getOpenFileName(
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
                            Qt.QString(profile["server"]))
                        self.on_devSettingsLineEdit_editingFinished()
                    if "frames" in profile.keys():
                        self.ui.frameLineEdit.setText(
                            Qt.QString(profile["frames"]))
                        self.on_layoutLineEdits_editingFinished()
                    if "groups" in profile.keys():
                        self.ui.groupLineEdit.setText(
                            Qt.QString(profile["groups"]))
                        self.ui.groupLineEdit.emit(
                            Qt.SIGNAL("groupsChanged(QString)"),
                            self.ui.groupLineEdit.text()) 
                        self.on_layoutLineEdits_editingFinished()
                    if "rowMax" in profile.keys():
                        self.ui.rowMaxSpinBox.setValue(
                            int(profile["rowMax"]))
                        
            except Exception as e:
                Qt.QMessageBox.warning(
                    self.ui.preferences, 
                    "Error during reading the file",
                    str(e))
                

    def profileSave(self):
        filename = str(Qt.QFileDialog.getSaveFileName(
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
            
