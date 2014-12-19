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

from .MessageBox import MessageBox
try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt


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
from .ServerState import ServerState

import logging
logger = logging.getLogger(__name__)


## main window class
class Preferences(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None):
        self.ui = ui
        self.state = state

        # frames/columns/groups
        self.frameshelp = [
            Qt.QString(
                '[[[["Components",1],["Timers",5]]],[[["Counters", 4]],' 
                + '[["ADC",3]],[["VFC",7]]],[[["MCA/SCA",6],["Others",0]]]]'),
            Qt.QString('[[[["Components",1],["Timers",5]]],[[["Counters", 4]],'
                       + '[["ADC",3]]],[[["MCA/SCA",6],["Devices",0]]]]'),
            Qt.QString('[[[["Counters", 4]],[["Channels",0]]],'
                       + '[[["MCAs", 2],["Misc",1]]],[[["ADC",3]]]]'),
            Qt.QString('[[[["Devices", 0]]],[[["MCAs", 2],["Misc",1]]]]'),
            Qt.QString(
                '[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'),
            Qt.QString('[[[["My Channels", 0]]],[[["My Components", 1]]]]'),
            Qt.QString('')]
        self.mgroupshelp = [
            Qt.QString('{ "3":["*_adc*"], "4":["*_c*"],'
                       + '"5":["*_t*"], "6":["*_mca*"],'
                       + '"7":["*_vfc*"]}'),
            Qt.QString('{ "3":["exp_adc*"], "4":["exp_c*"],'
                       + '"5":["exp_t*"], "6":["exp_mca*"],'
                       + '["sca_exp_*"]}'),
            Qt.QString('{"2":["mca8701*"]] , "3":["exp_adc*"],'
                       + ' "4":["exp_c*"]}'),
            Qt.QString('{"2":["ct01", "ct02"], "5":["appscan"]}'),
            Qt.QString('')]
        self.serverhelp = [
            Qt.QString(self.state.server)]

        self.__mgroups = str(self.mgroupshelp[0])
        self.__frames = str(self.frameshelp[0])

        self.views = {
            "CentralCheckBoxes (A)": CheckerView,
            "CheckBoxes (A)": LeftCheckerView,
            "Tables": TableView,
            "Columns": OneTableView,
            "CentralRadioButtons (A)": RadioView,
            "RadioButtons (A)": LeftRadioView,
            "Buttons (A)": ButtonView,
            "CentralCheckBoxes (N)": CheckerViewNL,
            "CheckBoxes (N)": LeftCheckerViewNL,
            "CentralRadioButtons (N)": RadioViewNL,
            "RadioButtons (N)": LeftRadioViewNL,
            "Buttons (N)": ButtonViewNL,
            "CentralCheckBoxes": CheckerViewNN,
            "CheckBoxes": LeftCheckerViewNN,
            "CentralRadioButtons": RadioViewNN,
            "RadioButtons": LeftRadioViewNN,
            "Buttons": ButtonViewNN,
            "CheckBoxes Dis (A)": CheckDisView,
            "RadioButtons Dis (A)": RadioDisView,
            "CheckBoxes Dis (N)": CheckDisViewNL,
            "RadioButtons Dis (N)": RadioDisViewNL,
            "CheckBoxes Dis": CheckDisViewNN,
            "RadioButtons Dis": RadioDisViewNN,
            }

        self.maxHelp = 10
        self.profFile = os.getcwd()    

    def __setmgroups(self, groups):
        try:
            lgroups = json.loads(groups)
            for k, gr in lgroups.items():
                for i in range(len(gr)):
                    if isinstance(gr[i], list) and gr[i]:
                        gr[i] = gr[i][0]
            self.__mgroups = json.dumps(lgroups)
        except:
            self.__mgroups = "{}"


    def __getmgroups(self):
        return self.__mgroups

      ## the json data string
    mgroups = property(__getmgroups, __setmgroups,
                       doc='device groups')     


    def __setframes(self, frames):
        try:
            nml = []
            lframes = json.loads(frames)
            for fr in lframes:
                for cl in fr:
                    for rw in cl:
                        nm = int(rw[1])
                        if nm not in nml:
                            nml.append(nm)
                        else:
                            raise Exception("Duplicated id")
            self.__frames = frames
        except Exception as e:
            print str(e)


    def __getframes(self):
        return self.__frames

      ## the json data string
    frames = property(__getframes, __setframes,
                       doc='detector frames')     

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
            self.ui.layoutButtonBox.button(Qt.QDialogButtonBox.Open),
            Qt.SIGNAL("pressed()"), self.layoutLoad)
        self.ui.preferences.disconnect(
            self.ui.layoutButtonBox.button(Qt.QDialogButtonBox.Save),
            Qt.SIGNAL("pressed()"), self.layoutSave)

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
            self.ui.layoutButtonBox.button(Qt.QDialogButtonBox.Open),
            Qt.SIGNAL("pressed()"), self.layoutLoad)
        self.ui.preferences.connect(
            self.ui.layoutButtonBox.button(Qt.QDialogButtonBox.Save),
            Qt.SIGNAL("pressed()"), self.layoutSave)

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


    def changeServer(self, ask=True):
        self.disconnectSignals()
        logger.debug("server changing")
        server = str(self.ui.devSettingsLineEdit.text())
        logger.debug("from %s to  %s" % (self.state.server, server))
        replay = Qt.QMessageBox.Yes
        if not server or server != self.state.server:
            if ask:
                replay = Qt.QMessageBox.question(
                    self.ui.preferences,
                    "Setting server has changed.",
                    "Changing server will cause loosing the current data. "
                    " Are you sure?",
                    Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if replay == Qt.QMessageBox.Yes:
                try:
                    if server == 'module':
                            self.state.server = ''
                            self.state.setServer()
                            self.state.fetchSettings()
                            self.addHint(server, self.serverhelp)
                    else:
                        if not server:
                            self.state.findServer()
                            self.state.setServer()
                            self.state.fetchSettings()
                        dp = PyTango.DeviceProxy(server)
                        if dp.info().dev_class == 'NXSRecSelector':
                            self.state.server = str(server)
                            self.state.setServer()
                            self.state.fetchSettings()
                            self.addHint(server, self.serverhelp)
                except Exception as e:
                    self.reset()
                self.connectSignals()
                self.ui.preferences.emit(Qt.SIGNAL("serverChanged()"))
            else:
                self.ui.devSettingsLineEdit.setText(Qt.QString(
                        self.state.server if self.state.server else 'module'))
        self.connectSignals()
    

    def on_devSettingsLineEdit_editingFinished(self):
        logger.debug("on_devSettingsLineEdit_editingFinished")
        self.changeServer()
        logger.debug("server changed")

    def addHint(self, string, hints):
        qstring = Qt.QString(string)
        if qstring not in hints:
            hints.insert(0, string)
        if self.maxHelp < len(hints):
            hints.pop(len(hints)-1)

    def on_layoutLineEdits_editingFinished(self):
        logger.debug("on_groupLineEdit_editingFinished")
        self.disconnectSignals()

        groups = str(self.ui.groupLineEdit.text())
        frames = str(self.ui.frameLineEdit.text())
        try:
            if not frames:
                frames = '[]'
            oldframes = self.frames    
            self.frames = frames
            self.addHint(self.frames, self.frameshelp)

            if not groups:
                groups = '{}'
            mgroups = json.loads(groups)

            if isinstance(mgroups, dict):
                self.mgroups = groups
                self.addHint(groups, self.mgroupshelp)

                if oldframes != self.frames:
                    self.connectSignals()
                    self.ui.preferences.emit(
                        Qt.SIGNAL("layoutChanged(QString,QString)"),
                        Qt.QString(frames), Qt.QString(groups))
        except Exception as e:
            text = MessageBox.getText("Problem in setting layout")
            MessageBox.warning(
                self.ui.preferences,
                "NXSSelector: Error during settings layout",
                text, str(e))
            logger.debug(str(e))
            self.reset()
        self.connectSignals()

    def updateForm(self):
        self.ui.devSettingsLineEdit.setText(
            self.state.server if self.state.server else 'module')
        self.ui.groupLineEdit.setText(self.mgroups)
        self.ui.frameLineEdit.setText(self.frames)

    def apply(self):
        pass

    def layoutLoad(self):
        filename = str(
            Qt.QFileDialog.getOpenFileName(
                self.ui.preferences,
                "Load Layout",
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
                text = MessageBox.getText("Problem in reading the layout")
                MessageBox.warning(
                    self.ui.preferences,
                    "NXSSelector: Error during reading the file",
                    text, str(e))

    def layoutSave(self):
        try:
            filename = str(Qt.QFileDialog.getSaveFileName(
                    self.ui.storage,
                    "Save Layout",
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
        except Exception as e:
            text = MessageBox.getText("Problem in saving the layout")
            MessageBox.warning(
                self.ui.preferences,
                "NXSSelector: Error during saving the file",
                text, str(e))
