#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# preferences tab

""" preferences tab """

import os
import PyTango
import json

from .MessageBox import MessageBox
from .DynamicTools import DynamicTools
try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from .Views import (TableView, OneTableView,
                    CheckerLabelViewNN,
                    CheckerView, RadioView, ButtonView,
                    LeftCheckerView, LeftRadioView,
                    CheckerViewNL, RadioViewNL, ButtonViewNL,
                    LeftCheckerViewNL, LeftRadioViewNL,
                    CheckerViewNN, RadioViewNN, ButtonViewNN,
                    LeftCheckerViewNN, LeftRadioViewNN,
                    CheckDisView, RadioDisView,
                    CheckDisViewNL, RadioDisViewNL,
                    CheckDisViewNN, RadioDisViewNN,
                    CheckPropView,
                    CheckPropViewNL,
                    CheckPropViewNN,
                    CheckExPropView,
                    CheckExPropViewNL,
                    CheckExPropViewNN,
                    )

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Preferences(Qt.QObject):
    """ preferences tab """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) server changed signal
    serverChanged = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) layout changed signal
    layoutChanged = Qt.pyqtSignal(str, str)
    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, ui, state=None):
        """ constructor

        :param ui: ui instance
        :type ui: :class:`taurus.qt.qtgui.util.ui.__UI`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        """
        Qt.QObject.__init__(self)
        #: (:class:`taurus.qt.qtgui.util.ui.__UI`) ui instance
        self.ui = ui
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = state

        #: (:obj:`list` <:obj:`str`>) \
        #:     list of nested frames/columns/groups configuration frame layout
        self.frameshelp = [
            str(
                '[[[["Components",1],["Timers",5]]],[[["Counters", 4]],'
                + '[["ADC",3]],[["VFC",7]]],'
                + '[[["MCA/SCA",6],["Additional",0]]]]'),
            str('[[[["Components",1],["Timers",5]]],[[["Counters", 4]],'
                + '[["ADC",3]]],[[["MCA/SCA",6],["Devices",0]]]]'),
            str('[[[["Counters", 4]],[["Channels",0]]],'
                + '[[["MCAs", 2],["Misc",1]]],[[["ADC",3]]]]'),
            str('[[[["Devices", 0]]],[[["MCAs", 2],["Misc",1]]]]'),
            str(
                '[[[["Counters1", 0], ["Counters2", 2]], [["VCounters", 3]]],'
                + '[[["MCAs", 1], ["SCAs", 4]]], [[["Misc", 5] ]]]'),
            str('[[[["My Channels", 0]]],[[["My Components", 1]]]]'),
            str('')]
        #: (:obj:`list` <:class:`taurus.qt.str`>) \
        #:     list of configuration group content,
        #:      "<id>":[<pattern1>, <pattern2>, ...]
        self.mgroupshelp = [
            str('{ "3":["*_adc*"], "4":["*_c*"],'
                + '"5":["*_t*"], "6":["*_mca*"],'
                + '"7":["*_vfc*"]}'),
            str('{ "3":["exp_adc*"], "4":["exp_c*"],'
                + '"5":["exp_t*"], "6":["exp_mca*"],'
                + '["sca_exp_*"]}'),
            str('{"2":["mca8701*"]] , "3":["exp_adc*"],'
                + ' "4":["exp_c*"]}'),
            str('{"2":["ct01", "ct02"], "5":["appscan"]}'),
            str('')]
        #: (:obj:`list` <:obj:`str`>) \
        #:     list of configuration server
        self.serverhelp = [
            str(self.state.server)]

        #: (:obj:`str`) defualt group configuration
        self.__mgroups = str(self.mgroupshelp[0])
        #: (:obj:`str`) defualt frame configuration
        self.__frames = str(self.frameshelp[0])

        #: (:obj:`dict` <:obj:`str`, :class:`taurus.qt.Qt.QWidget`>) \
        #:    available element views
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
            "CheckBoxes Prop (A)": CheckPropView,
            "CheckBoxes Synch (A)": CheckExPropView,
            "RadioButtons Dis (A)": RadioDisView,
            "CheckBoxes Dis (N)": CheckDisViewNL,
            "CheckBoxes Prop (N)": CheckPropViewNL,
            "CheckBoxes Synch (N)": CheckExPropViewNL,
            "RadioButtons Dis (N)": RadioDisViewNL,
            "CheckBoxes Dis": CheckDisViewNN,
            "CheckBoxes Prop": CheckPropViewNN,
            "CheckBoxes Synch": CheckExPropViewNN,
            "RadioButtons Dis": RadioDisViewNN,
            "CheckBoxes Dis (U)": CheckerLabelViewNN,
        }

        #: (:obj:`int`) maximum size of the helper for lineedits
        self.maxHelp = 10
        #: (:obj:`str`) layout file path
        self.layoutFile = os.getcwd()
        #: (:obj:`list` <:obj:`taurus.qt.Qt.QCompleter`>) \
        #:    qcompleter list
        self.completers = []

        #: (:obj:`bool`) if siganal connected
        self.connected = False
        self.connectSignals()

    def __setmgroups(self, groups):
        """ setter for mgroups

        :param groups: group configuration
        :type groups: :obj:`str`
        """
        try:
            lgroups = json.loads(groups)
            for gr in lgroups.values():
                for i in range(len(gr)):
                    if isinstance(gr[i], list) and gr[i]:
                        gr[i] = gr[i][0]
            self.__mgroups = json.dumps(lgroups)
        except Exception:
            self.__mgroups = "{}"

    def __getmgroups(self):
        """ getter for mgroups

        :returns: group configuration
        :rtype: :obj:`str`
        """
        return self.__mgroups

    #: (:obj:`str`) the json data string
    mgroups = property(__getmgroups, __setmgroups,
                       doc='device groups')

    def __setframes(self, frames):
        """ setter for frame configuration

        :param groups: frame configuration
        :type groups: :obj:`str`
        """
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
            print(str(e))

    def __getframes(self):
        """ getter for frame configuration

        :returns: group configuration
        :rtype: :obj:`str`
        """
        return self.__frames

    #: (:obj:`str`) the json data string
    frames = property(__getframes, __setframes,
                      doc='detector frames')

    def disconnectSignals(self):
        """ disconnects all signals
        """
        if self.connected:
            self.ui.devSettingsLineEdit.editingFinished.disconnect(
                self.on_devSettingsLineEdit_editingFinished)
            self.ui.devSettingsLineEdit.textEdited.disconnect(self.__dirty)
            self.ui.groupLineEdit.editingFinished.disconnect(
                self.on_layoutLineEdits_editingFinished)
            self.ui.frameLineEdit.editingFinished.disconnect(
                self.on_layoutLineEdits_editingFinished)

            self.ui.layoutButtonBox.button(
                Qt.QDialogButtonBox.Open).pressed.disconnect(self.layoutLoad)
            self.ui.layoutButtonBox.button(
                Qt.QDialogButtonBox.Save).pressed.disconnect(self.layoutSave)
        self.connected = False

    def connectSignals(self):
        """ connects all signals
        """
        if not self.connected:
            self.ui.devSettingsLineEdit.editingFinished.connect(
                self.on_devSettingsLineEdit_editingFinished)
            self.ui.devSettingsLineEdit.textEdited.connect(self.__dirty)
            self.ui.groupLineEdit.editingFinished.connect(
                self.on_layoutLineEdits_editingFinished)
            self.ui.frameLineEdit.editingFinished.connect(
                self.on_layoutLineEdits_editingFinished)

            self.ui.layoutButtonBox.button(
                Qt.QDialogButtonBox.Open).pressed.connect(self.layoutLoad)
            self.ui.layoutButtonBox.button(
                Qt.QDialogButtonBox.Save).pressed.connect(self.layoutSave)
        self.connected = True

    def __clearCompleters(self):
        """ clears completer list
        """
        self.ui.groupLineEdit.setCompleter(None)
        self.ui.devSettingsLineEdit.setCompleter(None)
        self.ui.frameLineEdit.setCompleter(None)
        DynamicTools.cleanupObjects(self.completers)

    def reset(self):
        """ resets whole Preferences
        """
        logger.debug("reset preferences")
        self.disconnectSignals()
        self.__clearCompleters()
        if self.ui.viewComboBox.count() != len(self.views.keys()):
            self.ui.viewComboBox.clear()
            self.ui.viewComboBox.addItems(sorted(self.views.keys()))
        completer = Qt.QCompleter(self.mgroupshelp, self.ui.preferences)
        self.ui.groupLineEdit.setCompleter(completer)
        self.completers.append(completer)
        completer = Qt.QCompleter(self.serverhelp, self.ui.preferences)
        self.ui.devSettingsLineEdit.setCompleter(completer)
        self.completers.append(completer)
        completer = Qt.QCompleter(self.frameshelp, self.ui.preferences)
        self.ui.frameLineEdit.setCompleter(completer)
        self.completers.append(completer)
        self.updateForm()
        self.connectSignals()
        logger.debug("reset preferences ended")

    def changeServer(self, ask=True):
        """ changes the selector server

        :param ask: ask  for confirmation from the user
        :type ask: :obj:`bool`
        """
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
                except Exception:
                    self.reset()
                self.connectSignals()
                self.serverChanged.emit()
            else:
                self.ui.devSettingsLineEdit.setText(str(
                    self.state.server if self.state.server else 'module'))
        self.connectSignals()

    @Qt.pyqtSlot()
    def on_devSettingsLineEdit_editingFinished(self):
        """ changes  selector server
        """
        logger.debug("on_devSettingsLineEdit_editingFinished")
        self.changeServer()
        logger.debug("server changed")

    def addHint(self, string, hints):
        """ adds hint

        :param string: string hint
        :type string: :obj:`str`
        :param hints: a list of hints
        :type hints: :obj:`list` <:obj:`str`>
        """
        qstring = str(string)
        if qstring not in hints:
            hints.insert(0, string)
        if self.maxHelp < len(hints):
            hints.pop(len(hints) - 1)

    @Qt.pyqtSlot()
    def on_layoutLineEdits_editingFinished(self):
        """ updates layout according to new frame and group configurations
        """
        logger.debug("on_layoutLineEdit_editingFinished")
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
                oldgroups = self.mgroups
                self.mgroups = groups
                self.addHint(groups, self.mgroupshelp)

                if oldframes != self.frames or oldgroups != self.mgroups:
                    self.connectSignals()
                    self.layoutChanged.emit(
                        str(frames), str(groups))
        except Exception as e:
            text = MessageBox.getText("Problem in setting layout")
            MessageBox.warning(
                self.ui.preferences,
                "NXSelector: Error during settings layout",
                text, str(e))
            logger.debug(str(e))
            self.reset()
        self.connectSignals()

    def updateForm(self):
        """ updates the form according to the class variables
        """
        self.ui.devSettingsLineEdit.setText(
            self.state.server if self.state.server else 'module')
        self.ui.groupLineEdit.setText(self.mgroups)
        self.ui.frameLineEdit.setText(self.frames)

    def apply(self):
        """ does nothing"""

    @Qt.pyqtSlot()
    def layoutLoad(self):
        """ loads a layout from the file
        """
        filename = str(
            Qt.QFileDialog.getOpenFileName(
                self.ui.preferences,
                "Load Layout",
                self.layoutFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("loading profile from %s" % filename)
        if filename:
            self.layoutFile = filename
            jprof = open(filename).read()
            try:
                profile = json.loads(jprof)
                if isinstance(profile, dict):
                    if "server" in profile.keys():
                        self.ui.devSettingsLineEdit.setText(
                            str(profile["server"]))
                        self.on_devSettingsLineEdit_editingFinished()
                    if "frames" in profile.keys():
                        self.ui.frameLineEdit.setText(
                            str(profile["frames"]))
                        self.on_layoutLineEdits_editingFinished()
                    if "groups" in profile.keys():
                        self.ui.groupLineEdit.setText(
                            str(profile["groups"]))
                        self.on_layoutLineEdits_editingFinished()
                    if "rowMax" in profile.keys():
                        self.ui.rowMaxSpinBox.setValue(
                            int(profile["rowMax"]))

            except Exception as e:
                text = MessageBox.getText("Problem in reading the layout")
                MessageBox.warning(
                    self.ui.preferences,
                    "NXSelector: Error during reading the file",
                    text, str(e))

    @Qt.pyqtSlot()
    def __dirty(self):
        """ sets dirty flag """
        self.dirty.emit()

    @Qt.pyqtSlot()
    def layoutSave(self):
        """ loads the current layout into a file
        """
        try:
            filename = str(Qt.QFileDialog.getSaveFileName(
                self.ui.storage,
                "Save Layout",
                self.layoutFile,
                "JSON files (*.json);;All files (*)"))
            logger.debug("saving profile to %s" % filename)
            if filename:
                if (len(filename) < 4 or filename[-4] != '.') and \
                        not (len(filename) > 5 and filename[-5] == '.'):
                    filename = filename + '.json'

                self.layoutFile = filename
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
                "NXSelector: Error during saving the file",
                text, str(e))
