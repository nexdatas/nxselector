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
# Main window of the application

""" main window application dialog """

import json
import os
import sys

from .qtapi import qt_api

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable


from taurus.qt.qtgui.base import TaurusBaseWidget
from .ServerState import ServerState, Checker

from .Detectors import Detectors
from .Preferences import Preferences
from .Descriptions import Descriptions
from .Data import Data
from .Storage import Storage
from .CommandThread import CommandThread
from .MessageBox import MessageBox

from . import __version__
from . import qrc

import logging
import gc
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


@UILoadable(with_ui='ui')
class Selector(Qt.QDialog, TaurusBaseWidget):
    """ main window application dialog """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) doorName  signal
    doorName = Qt.pyqtSignal(str)

    #: (:class:`taurus.qt.Qt.pyqtSignal`)
    # experimentConfigurationChanged signal
    experimentConfigurationChanged = Qt.pyqtSignal(dict)

    def __init__(self, server=None, door=None,
                 standalone=False, umode=None,
                 setdefault=False,
                 switch=True,
                 organization='DESY',
                 application='NXS Component Selector',
                 parent=None):
        """ constructor

        :param server: selector server name
        :type server: :obj:`str`
        :param door: door device name
        :type door: :obj:`str`
        :param standalone: application run without macrogui
        :type standalone: :obj:`bool`
        :param umode: user mode, i.e. simple, user, advanced, special, \
                        expert, administrator
        :type umode: :obj:`str`
        :param setdefault: set default
        :type setdefault: :obj:`bool`
        :param organization: organization name
        :type organization: :obj:`str`
        :param application: application name
        :type application: :obj:`str`
        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'NXSExpDescriptionEditor')
        self.setWindowFlags(Qt.Qt.Window)
        self.loadUi()
        self.debug("SELECTOR load")
        if umode != 'administrator':
            self.ui.tabWidget.removeTab(4)
        logger.debug("PARAMETERS: %s %s", server, parent)
        #: (:obj:`str`) organization name
        self.__organization = organization
        #: (:obj:`str`) application name
        self.__application = application
        #: (:obj:`str`) door name
        self.__door = door
        #: (:obj:`str`) skip configuration reset
        self.__skipconfig = True
        #: (:obj:`bool`) application executed without macrogui
        self.__standalone = standalone

        #: (:obj:`bool`) progressbar is running
        self.__progressFlag = False
        #: (:obj:`bool`) door has to be updated
        self.__doortoupdateFlag = False
        #: (:obj:`bool`) selector server has to be updated
        self.__servertoupdateFlag = False

        #: (:obj:`str`) selector server
        self.__model = None
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = None

        #: (:obj:`bool`) set default configuration
        self.__setdefault = setdefault
        #: (:obj:`bool`) switch MntGrp into ActiveMntGrp
        self.__switch = switch
        #: (:obj:`str`) user mode
        self.__umode = umode
        #: (:obj:`bool`)  expert mode on
        self.expert = True
        #: (:obj:`bool`)  user mode on
        self.user = False
        #: (:obj:`bool`)  simple mode on
        self.simple = False
        #: (:obj:`bool`)  negative hidden mode on
        self.hidden = False

        #: (:obj:`bool`)  if QSettings loaded
        self.__settingsloaded = False
        if self.__umode:
            self.__setmode(self.__umode)
        #: (:obj:`str`)  configuration file name
        self.cnfFile = ''
        #: (:class:`taurus.qt.Qt.QProgressDialog`) progress bar
        self.__progress = None
        #: (:obj:`list` <:class:`nxsselector.CommandThread.CommandThread`>) \
        #:     command thread
        self.__commandthread = None

        self.__resetServer(server)
        #: (:obj:`int`) user data tab number
        self.__datatab = 2

    def __setmode(self, umode):
        """ sets user mode

        :param umode: user mode, i.e. simple, user, advanced, expert, \
                        administrator
        :type umode: :obj:`str`
        """
        if umode == 'expert':
            self.expert = True
            self.user = False
            self.simple = False
            self.hidden = False
        elif umode == 'advanced':
            self.expert = False
            self.user = False
            self.simple = False
            self.hidden = False
        elif umode == 'user':
            self.expert = False
            self.user = True
            self.simple = False
            self.hidden = False
        elif umode == 'simple':
            self.expert = False
            self.user = True
            self.simple = True
            self.hidden = True
        elif umode == 'special':
            self.expert = True
            self.user = False
            self.simple = False
            self.hidden = True

    def settings(self):
        """ sets configuration
        """
        logger.debug("settings")

        if self.__progress:
            self.__progress.reset()
            self.__progress.hide()
        if self.__commandthread and self.__commandthread.error:
            text = MessageBox.getText(
                "Problems in updating Channels",
                self.__commandthread.error)
            MessageBox.warning(
                self, "NXSelector: Error in Setting Selector Server", text,
                "%s" % str(self.__commandthread.error))
            self.__commandthread.error = None

        settings = Qt.QSettings(self.__organization, self.__application, self)
        if not self.__umode or self.__umode == 'None':
            self.__umode = str(settings.value("Selector/DefaultMode",
                                              self.__umode))
            if not self.__umode or self.__umode == 'None':
                self.__umode = 'expert'
        self.__setmode(self.__umode)
        self.userView = settings.value('Preferences/UserView',
                                       'CheckBoxes Prop')
        self.rowMax = int(settings.value('Preferences/RowMax', 16))
        if not self.rowMax:
            self.rowMax = 16

        self.fontSize = int(self.font().pointSize())
        self.fontSize = int(
            settings.value('Preferences/FontSize', self.fontSize))
        self.displayStatus = int(
            settings.value('Preferences/DisplayStatus', 2))
        self.scanFileExtStatus = int(
            settings.value('Preferences/ScanFileExtStatus', 2))
        self.cnfFile = str(settings.value("Selector/CnfFile", "./"))

        self.__addButtonBoxes()

        # user interface
        self.preferences = Preferences(self.ui, self.state)
        if self.userView not in self.preferences.views:
            self.userView = 'CheckBoxes Dis'
        self.storage = Storage(self.ui, self.state, self.simple)
        self.state.synchthread.scanidchanged.connect(
            self.storage.updateScanID, Qt.Qt.DirectConnection)
        self.state.synchthread.mgconfchanged.connect(
            self.checkDirty, Qt.Qt.DirectConnection)
        self.state.serverChanged.connect(
            self.resetServer, Qt.Qt.DirectConnection)
        self.state.synchthread.restart()

        self.detectors = Detectors(
            self.ui, self.state,
            self.preferences.views[self.userView],
            self.rowMax,
            int(self.hidden) + 2 * int(self.user),
            self.fontSize)

        self.preferences.mgroups = settings.value(
            'Preferences/Groups', '{}')
        self.preferences.frames = settings.value(
            'Preferences/Frames', '[]')
        self.preferences.mgroupshelp = settings.value(
            'Preferences/GroupsHints',
            self.preferences.mgroupshelp)
        self.preferences.frameshelp = settings.value(
            'Preferences/FramesHints',
            self.preferences.frameshelp)

        self.preferences.addHint(
            self.preferences.mgroups,
            self.preferences.mgroupshelp)
        self.preferences.addHint(
            self.preferences.frames,
            self.preferences.frameshelp)

        self.preferences.layoutFile = str(
            settings.value("Preferences/LayoutFile", "./"))

        self.detectors.mgroups = str(self.preferences.mgroups)
        self.detectors.frames = str(self.preferences.frames)
        self.descriptions = Descriptions(
            self.ui, self.state,
            self.preferences.views["CentralCheckBoxes"],
            self.preferences.views["CheckBoxes Dis (U)"],
            self.rowMax,
            self.fontSize)

        self.data = Data(self.ui, self.state, self.simple or self.user)

        self.tabs = [self.detectors, self.descriptions, self.data,
                     self.storage, self.preferences]

        self.waitForThread()
        try:
            if self.__switch:
                self.resetClickAll()
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText(
                "Problems in Switching MntGrp")
            MessageBox.warning(
                self, "NXSelector: Error in Switching MntGrp",
                text, str(value))
        self.createGUI()
        self.__tabChanged(0)

        sg = settings.value("Selector/Geometry")
        if sg:
            self.restoreGeometry(sg)

#        self.resize(0, 0)

        self.title = 'NeXus Component Selector'
        self.__dirty = True
        self.setDirty()
        self.__progress = None
        if self.__servertoupdateFlag:
            self.setModel(self.__model)
        if self.__doortoupdateFlag:
            self.updateDoorName(self.__door)

        self.__scanFileExtStatusChanged(int(
            settings.value('Preferences/ScanFileExtStatus', 2)))
        self.ui.fileExtScanCheckBox.setChecked(
            self.scanFileExtStatus != 0)

        self.__settingsloaded = True
        self.__skipconfig = False
        logger.debug("settings END")

    def createGUI(self):
        """ creates GUI for the main window
        """

        self.__setButtonBoxes()
        self.__hideWidgets()
        for tab in self.tabs:
            tab.reset()

        self.__setWidgetValues()
        self.__connectSignals()
        self.__addTips()

    def __addButtonBoxes(self):
        """adds button boxes into the main buttonbox"""
        if not self.__standalone:
            self.ui.mntServerLineEdit.hide()
            self.ui.mntServerLabel.hide()
            self.ui.buttonBox.setStandardButtons(
                Qt.QDialogButtonBox.Reset | Qt.QDialogButtonBox.Apply)
        else:
            self.ui.buttonBox.setStandardButtons(
                Qt.QDialogButtonBox.Reset | Qt.QDialogButtonBox.Apply
                | Qt.QDialogButtonBox.Close)
        self.ui.buttonBox.setSizePolicy(Qt.QSizePolicy.Expanding,
                                        Qt.QSizePolicy.Fixed)

        self.ui.clearAllPushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.RestoreDefaults)
        self.ui.clearAllPushButton.setText("ClearAll")
        self.ui.unlockPushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.RestoreDefaults)
        self.ui.unlockPushButton.setText("Unlock")
        self.ui.unlockPushButton.hide()

        self.ui.loadProfilePushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Open)
        self.ui.loadProfilePushButton.setText("Load")

        self.ui.saveProfilePushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Save)

        self.ui.groupsPushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Retry)
        self.ui.groupsPushButton.setText("Others")

        self.ui.statusLabel = self.ui.buttonBox.addButton(
            "", Qt.QDialogButtonBox.ActionRole)
        self.ui.statusLabel.setEnabled(False)
        self.ui.buttonBox.setCenterButtons(True)

    def __setButtonBoxes(self):
        """sets button boxes in the main buttonbox"""

        flayout = Qt.QHBoxLayout(self.ui.timerButtonFrame)
        flayout.setContentsMargins(0, 0, 0, 0)
        self.ui.timerAddPushButton = Qt.QPushButton("+")
        self.ui.timerAddPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerAddPushButton)
        self.ui.timerDelPushButton = Qt.QPushButton("-")
        self.ui.timerDelPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerDelPushButton)
        self.storage.connectTimerButtons()

    def __setWidgetValues(self):
        """sets widget values"""

        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Open).setText("Load")
        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Save).setText("Save")

        layout = self.ui.layoutButtonBox.layout()
        for i in range(layout.count()):
            spacer = layout.itemAt(i)
            if isinstance(spacer, Qt.QSpacerItem):
                spacer.changeSize(
                    0, 0, Qt.QSizePolicy.Minimum)

        self.ui.defaultPushButton = Qt.QPushButton()
#        self.ui.defaultPushButton.resize(0,0)
        self.ui.defaultPushButton.setDefault(True)
#        self.ui.defaultPushButton.setAutoDefault(True)
        layout.addWidget(self.ui.defaultPushButton)
        self.ui.defaultPushButton.hide()

        self.ui.statusLabel.setAutoFillBackground(True)
        self.ui.statusLabel.setSizePolicy(Qt.QSizePolicy.Expanding,
                                          Qt.QSizePolicy.Fixed)

        self.ui.statusLabel.setStyleSheet(
            "background-color:white;border-style: outset; "
            "border-width: 1px; border-color: gray; "
            "color:#208020;font:bold;font-size: 14pt;")
        self.ui.mntGrpComboBox.setInsertPolicy(
            self.ui.mntGrpComboBox.InsertAtTop)

        self.storage.updateMntGrpComboBox()

        cid = self.ui.viewComboBox.findText(str(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid)
        self.ui.rowMaxSpinBox.setValue(self.rowMax)
        self.ui.fontSizeSpinBox.setValue(self.fontSize)
        self.ui.statusCheckBox.setChecked(self.displayStatus != 0)
        self.ui.fileExtScanCheckBox.setChecked(self.scanFileExtStatus != 0)

    def __hideWidgets(self):
        """ hides widgets according to set user mode
        """
        if not self.expert:
            self.ui.groupGroupBox.hide()
            self.ui.frameGroupBox.hide()
            self.ui.dynFrame.hide()
            self.ui.devConfigPushButton.hide()
            self.ui.devSettingsLineEdit.setEnabled(False)
            self.ui.devWriterLineEdit.setEnabled(False)
            self.ui.devConfigLineEdit.setEnabled(False)
            self.ui.mntServerLineEdit.setEnabled(False)
        if self.user:
            self.ui.componentGroupBox.hide()
            self.ui.mntGrpToolButton.hide()
            self.ui.viewServerFrame.hide()
            self.ui.viewGroupBox.hide()
            self.ui.tabWidget.removeTab(3)
        if self.simple:
            self.ui.mntGrpComboBox.setEnabled(False)
            self.ui.orderToolButton.hide()
            self.ui.timerAddPushButton.hide()
            self.ui.timerDelPushButton.hide()
            self.ui.mntTimerComboBox.setEnabled(False)
            self.ui.timerButtonFrame.setEnabled(False)
            self.ui.descriptions.hide()
            self.ui.tabWidget.removeTab(3)
            self.ui.tabWidget.removeTab(1)
            self.__datatab -= 1
            self.ui.tabWidget.setCurrentIndex(self.__datatab)

    def __connectSignals(self):
        """ connects all signals
        """
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).pressed.connect(self.__applyClicked)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Reset).pressed.connect(self.__resetClicked)
        if self.__standalone:
            self.ui.buttonBox.button(
                Qt.QDialogButtonBox.Close).pressed.connect(self.close)
        self.ui.clearAllPushButton.pressed.connect(self.__restore)
        self.ui.unlockPushButton.pressed.connect(self.__unlock)

        self.ui.loadProfilePushButton.pressed.connect(self.cnfLoad)
        self.ui.saveProfilePushButton.pressed.connect(self.cnfSave)

        self.preferences.serverChanged.connect(self.resetServer)
        self.preferences.layoutChanged.connect(self.resetLayout)

        self.ui.viewComboBox.currentIndexChanged.connect(self.resetViews)
        self.ui.rowMaxSpinBox.editingFinished.connect(self.resetRows)
        self.ui.fontSizeSpinBox.editingFinished.connect(self.resetRows)
        self.ui.statusCheckBox.stateChanged.connect(
            self.__displayStatusChanged)
        self.ui.fileExtScanCheckBox.stateChanged.connect(
            self.__scanFileExtStatusChanged)

        self.detectors.dirty.connect(self.setDirty)
        self.preferences.dirty.connect(self.setDirty)
        self.descriptions.componentChecked.connect(self.__componentChanged)
        self.data.dirty.connect(self.setDirty)
        self.storage.dirty.connect(self.setDirty)
        self.storage.resetViews.connect(self.resetViews)
        self.storage.resetAll.connect(self.resetAll)
        self.storage.updateGroups.connect(self.updateGroups)
        self.ui.tabWidget.currentChanged.connect(self.__tabChanged)

    def __addTips(self):
        """ adds button tips
        """
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.RestoreDefaults).setToolTip(
            "Deselect all detector components")
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).setToolTip(
            "Send the current profile into the selector server\n" +
            "Update the current measurement group" +
            " and set it into ActiveMntGrp.\n" +
            "Update preselection of description components "
        )
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Reset).setToolTip(
            "Reset local modifications " +
            "by fetching the current profile from the selector server\n" +
            "and updating the profile by the Active Measurement Group.\n" +
            "Update preselection of description components ")
        if self.ui.buttonBox.button(
                Qt.QDialogButtonBox.Close):
            self.ui.buttonBox.button(
                Qt.QDialogButtonBox.Close).setToolTip(
                "Close the Component Selector")
        self.ui.timerAddPushButton.setToolTip("Add a non-master timer")
        self.ui.timerDelPushButton.setToolTip(
            "Remove the last non-master timer ")
        self.ui.loadProfilePushButton.setToolTip(
            "Load a profile with previously selected channels from a file.")
        self.ui.saveProfilePushButton.setToolTip(
            "Save the current profile with the selected channels into a file.")
        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Open).setToolTip(
            "Load from a file a previously saved detector layout.")
        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Save).setToolTip(
            "Save into a file the currently detector layout.")
        self.ui.groupsPushButton.setToolTip(
            "Change the available components in the Detectors tab")

    def setModel(self, model):
        """ sets model

        :param model: selector server model
        :type model: :obj:`str`
        """
        if str(model) != str(self.state.server):
            if self.__progress:
                self.__model = model
                self.__servertoupdateFlag = True
            elif self.__servertoupdateFlag:
                self.__servertoupdateFlag = False
                self.ui.devSettingsLineEdit.setText(model)
                self.preferences.changeServer(False)
                logger.debug("change ServerName %s " % model)
        else:
            self.__servertoupdateFlag = False

    def __saveSettings(self):
        """ saves settings
        """
        settings = Qt.QSettings(self.__organization, self.__application, self)
        settings.setValue(
            "Selector/Geometry",
            (self.saveGeometry()))
        settings.setValue(
            "Preferences/UserView",
            (str(self.ui.viewComboBox.currentText())))
        settings.setValue(
            "Preferences/RowMax",
            (self.ui.rowMaxSpinBox.value()))
        settings.setValue(
            "Preferences/FontSize",
            (self.ui.fontSizeSpinBox.value()))
        settings.setValue(
            "Preferences/DisplayStatus",
            (2 if self.ui.statusCheckBox.isChecked() else 0))
        settings.setValue(
            "Preferences/ScanFileExtStatus",
            (2 if self.ui.fileExtScanCheckBox.isChecked() else 0))
        settings.setValue(
            "Preferences/Groups",
            (str(self.preferences.mgroups)))
        settings.setValue(
            "Preferences/Frames",
            (str(self.preferences.frames)))
        settings.setValue(
            "Preferences/FramesHints",
            (self.preferences.frameshelp))
        settings.setValue(
            "Preferences/GroupsHints",
            (self.preferences.mgroupshelp))
        settings.setValue(
            "Selector/CnfFile", (self.cnfFile))
        settings.setValue(
            "Preferences/LayoutFile",
            (self.preferences.layoutFile))
        if self.__setdefault:
            settings.setValue(
                "Selector/DefaultMode",
                (self.__umode))

    def keyPressEvent(self, event):
        """ adds saving settings on escape key

        :param event: key event
        :type event: :class:`taurus.qt.Qt.QEvent`
        """
        if hasattr(event, "key") and event.key() == Qt.Qt.Key_Escape:
            logger.debug("escape key event")
            if self.__settingsloaded:
                self.__saveSettings()
        Qt.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        """ adds saving settings on close event

        :param event: close event
        :type event: :class:`taurus.qt.Qt.QEvent`
        """
        logger.debug("close event")
        if self.__settingsloaded:
            self.__saveSettings()
        Qt.QDialog.closeEvent(self, event)
        logger.debug("close event ended")

    @Qt.pyqtSlot()
    def checkDirty(self):
        if not self.state.isMntGrpChanged():
            self.setDirty()

    def __resetServer(self, server):
        """ resets server state variables

        :param server: server name
        :type server: :obj:`str`
        """
        if self.state:
            with Qt.QMutexLocker(self.state.mutex):
                self.state.synchthread.running = False
            if hasattr(self, "storage"):
                self.state.synchthread.mgconfchanged.disconnect(
                    self.checkDirty)
                self.state.synchthread.scanidchanged.disconnect(
                    self.storage.updateScanID)
                self.state.serverChanged.disconnect(self.resetServer)
            self.state.synchthread.wait()
        try:
            self.state = ServerState(server)
            if self.__door:
                self.state.storeData("door", self.__door)
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText(
                "Problems in resetting Server")
            MessageBox.warning(
                self, "NXSelector: Error in Setting Selector Server",
                text, str(value))
            self.state = ServerState("")
            self.state.setServer()
            if self.__door:
                self.state.storeData("door", self.__door)
        if hasattr(self, "storage"):
            self.state.synchthread.scanidchanged.connect(
                self.storage.updateScanID, Qt.Qt.DirectConnection)
            self.state.synchthread.mgconfchanged.connect(
                self.checkDirty, Qt.Qt.DirectConnection)
            self.state.serverChanged.connect(
                self.resetServer, Qt.Qt.DirectConnection)
            self.state.synchthread.restart()
        if self.__switch:
            cmds = ["fetchSettings"]
        else:
            cmds = ["updateControllers",
                    "fetchSettings"]
        self.runProgress(cmds, "settings")

    def __resetStateThread(self):
        """ resets server state variables
        """
        if self.state:
            with Qt.QMutexLocker(self.state.mutex):
                self.state.synchthread.running = False
            if hasattr(self, "storage"):
                self.state.synchthread.scanidchanged.disconnect(
                    self.storage.updateScanID)
                self.state.synchthread.mgconfchanged.disconnect(
                    self.checkDirty)
            self.state.synchthread.wait()
            if hasattr(self, "storage"):
                self.state.synchthread.scanidchanged.connect(
                    self.storage.updateScanID, Qt.Qt.DirectConnection)
                self.state.synchthread.mgconfchanged.connect(
                    self.checkDirty, Qt.Qt.DirectConnection)
                self.state.synchthread.restart()

    @Qt.pyqtSlot()
    def __componentChanged(self):
        """ updates detector view
        """
        self.setDirty()
        self.detectors.updateViews()

    @Qt.pyqtSlot()
    def setDirty(self, flag=True):
        """ sets dirty flag

        :param flag: dirty flag
        :type flag: :obj:`bool`
        """
        self.__dirty = flag
        self.ui.statusLabel.hide()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setEnabled(True)
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setEnabled(True)
#        self.ui.applyPushButton.setEnabled(True)
#        self.ui.resetPushButton.setEnabled(True)
        self.ui.buttonHorizontalLayout = self.ui.buttonBox.layout()
        spacer = None
        if self.displayStatus:
            self.ui.buttonBox.setCenterButtons(True)
            for i in range(self.ui.buttonHorizontalLayout.count()):
                spacer = self.ui.buttonHorizontalLayout.itemAt(i)
                if isinstance(spacer, Qt.QSpacerItem):
                    spacer.changeSize(
                        0, 0, Qt.QSizePolicy.Minimum)

            if flag:
                self.ui.statusLabel.setStyleSheet(
                    "background-color: white;border-style: outset; "
                    "border-width: 1px; border-color: gray; "
                    "color:#A02020;font:bold;font-size: 14pt;")
                self.ui.statusLabel.setText('NOT APPLIED')
                self.setWindowTitle(
                    '%s (%s mode) * ' % (self.title, self.__umode))
            else:
                self.setWindowTitle(
                    '%s (%s mode)' % (self.title, self.__umode))
                self.ui.statusLabel.setStyleSheet(
                    "background-color: white;border-style: outset; "
                    "border-width: 1px; border-color: gray; "
                    "color:#206020;font:bold;font-size: 14pt;")
                self.ui.statusLabel.setText('APPLIED')
            self.ui.statusLabel.show()
        else:
            self.ui.buttonBox.setCenterButtons(False)
            for i in range(self.ui.buttonHorizontalLayout.count()):
                spacer = self.ui.buttonHorizontalLayout.itemAt(i)
                if isinstance(spacer, Qt.QSpacerItem):
                    spacer.changeSize(
                        40, 20, Qt.QSizePolicy.Expanding)

            if flag:
                self.setWindowTitle(
                    '%s (%s mode) * ' % (self.title, self.__umode))
            else:
                self.setWindowTitle(
                    '%s (%s mode)' % (self.title, self.__umode))
                self.ui.buttonBox.button(
                    Qt.QDialogButtonBox.Reset).setEnabled(False)
                self.ui.buttonBox.button(
                    Qt.QDialogButtonBox.Apply).setEnabled(False)
#                self.ui.applyPushButton.setEnabled(False)
#                self.ui.resetPushButton.setEnabled(False)
            self.ui.statusLabel.hide()

    @Qt.pyqtSlot()
    def resetServer(self):
        """ resets server settings
        """
        logger.debug("reset server")
        self.state.setServer()
        self.__resetStateThread()
        self._resetAll()
        logger.debug("reset server ended")

    @Qt.pyqtSlot(str, str)
    def resetLayout(self, frames, groups):
        """ resets application layout
        """
        logger.debug("reset layout")
        self.detectors.frames = str(frames)
        self.detectors.mgroups = str(groups)
        self.resetViews()
        logger.debug("reset layout ended")

    @Qt.pyqtSlot()
    def resetRows(self):
        """ resets a maximum number of rows in element columns
        """
        logger.debug("reset rows")
        rowMax = self.ui.rowMaxSpinBox.value()
        fontSize = self.ui.fontSizeSpinBox.value()
        for tab in self.tabs:
            if hasattr(tab, "rowMax"):
                tab.rowMax = rowMax
            if hasattr(tab, "fontSize"):
                tab.fontSize = fontSize
        self.resetViews()
        logger.debug("reset rows ended")

    @Qt.pyqtSlot()
    def updateGroups(self):
        """ updates elements groups
        """
        self.state.storeGroups()
        self._resetAll()

    @Qt.pyqtSlot()
    def resetViews(self):
        """ resets all tab views
        """
        logger.debug("reset view")
        self.state.ddsdirty = True
        for tab in self.tabs:
            if not isinstance(tab, Descriptions):
                tab.userView = self.preferences.views[
                    str(self.ui.viewComboBox.currentText())]
            tab.reset()
        logger.debug("reset view end")

    def reset(self):
        """ fetches configuration and resets all tab views
        """
        logger.debug("reset selector")
        try:
            self.state.fetchSettings()
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in resetting Server")
            MessageBox.warning(
                self, "NXSelector: Error in Resetting Selector Server",
                text, str(value))
        for tab in self.tabs:
            tab.reset()
        logger.debug("reset selector ended")

    def closeReset(self):
        """ close reset method for progressbar
        """
        status = True
        logger.debug("closing Progress")
        if self.__progress:
            self.__progress.reset()
        if self.__commandthread.error:
            text = MessageBox.getText(
                "Problems in updating Channels",
                self.__commandthread.error)
            MessageBox.warning(
                self,
                "NXSelector: Error in updating Selector Server Channels",
                text,
                "%s" % str(self.__commandthread.error))
            self.__commandthread.error = None
            status = False
        self.reset()
        self.storage.updateMntGrpComboBox()
        self.setDirty(True)
        if self.__progress:
            self.__progress.setParent(None)
            self.__progress = None
        if self.__servertoupdateFlag:
            self.setModel(self.__model)
        if self.__doortoupdateFlag:
            self.updateDoorName(self.__door)
        self.waitForThread()
        gc.collect()
        logger.debug("closing Progress ENDED")
        return status

    def closeResetShowErrors(self):
        self.storage.showErrors()
        self.closeReset()
        self.__skipconfig = False

    def waitForThread(self):
        """ waits for running thread
        """
        logger.debug("waiting for Thread")
        if self.__commandthread:
            self.__commandthread.wait()
        logger.debug("waiting for Thread ENDED")

    def runProgress(self, commands, onclose="closeReset"):
        """ starts progress thread with the given commands

        :param commands: list of commands
        :type commands: :obj:`list` <:obj:`str`>
        :param onclose: close command name
        :type onclose: :obj:`str`
        """
        if self.__progress:
            return
        if self.__commandthread:
            self.__commandthread.setParent(None)
            self.__commandthread = None
        self.__commandthread = CommandThread(self.state, commands, self)
        oncloseaction = getattr(self, onclose)
        self.__commandthread.finished.connect(
            oncloseaction, Qt.Qt.QueuedConnection)
        self.__progress = None
        self.__progress = Qt.QProgressDialog(
            "Updating preselected devices...", "Cancel", 0, 0, self)
        self.__progress.setWindowModality(Qt.Qt.WindowModal)
        self.__progress.setCancelButton(None)
        self.__progress.rejected.connect(
            self.waitForThread, Qt.Qt.QueuedConnection)
        self.__commandthread.start()
        self.__progress.show()

    def resetClickAll(self):
        """ updates the current mntgrp and resets all settings """
        logger.debug("reset ALL")
        self.state.switchMntGrp()
        self._synchDoor()
        self.runProgress(
            [
                "updateControllers",
                "importMntGrp"],
            onclose="closeResetShowErrors")
        logger.debug("reset ENDED")

    def _synchDoor(self):
        """ synchronize the current door name with macroserver
        """
        if not self.__door:
            self.__door = self.state.door
        elif not self.state.isDoorFromMacroServer(self.__door):
            replay = Qt.QMessageBox.question(
                self.ui.preferences,
                "NXSelector: The New Measurement Group"
                "was created for not the current MacroServer.",
                "Would you like to apply change or the current MacroServer"
                " or reset door in the new measurement group? ",
                Qt.QMessageBox.Apply | Qt.QMessageBox.Reset
                | Qt.QMessageBox.Close)
            if replay == Qt.QMessageBox.Apply:
                self.__door = self.state.door
                self.doorName.emit(str(self.state.door))
            elif replay == Qt.QMessageBox.Reset:
                self.updateDoorName(self.__door)
        else:
            self.updateDoorName(self.__door)

    @Qt.pyqtSlot()
    def resetAll(self):
        """ resets all settings and synchronize the current door"""
        self._synchDoor()
        self._resetAll()

    def _resetAll(self):
        """ resets all settings """
        logger.debug("reset ALL")
        self.runProgress(["updateControllers", "importMntGrp"],
                         onclose="closeResetShowErrors")
        logger.debug("reset ENDED")

    def resetDescriptions(self):
        """ resets description selection to the default values"""
        logger.debug("reset Descriptions")
        self.runProgress(["resetDescriptions", "importMntGrp"],
                         onclose="closeResetShowErrors")
        logger.debug("reset Descriptions ENDED")

    def compareConf(self, cnf, ecnf):
        """ copares two dictionaries

        :param cnf: current configuration
        :type cnf: :obj:`dict`
        :param ecnf: external configuration
        :type ecnf: :obj:`dict`
        :returns: if configurations are the same
        :rtype: :obj:`bool`
        """
        if not isinstance(cnf, dict):
            return False
        if not isinstance(ecnf, dict):
            return False

        ekeys = list(set(ecnf.keys()))
        if 'ScanFile' in ekeys:
            if self.state.scanFile != ecnf['ScanFile']:
                return False

        if 'ScanDir' in ekeys:
            if self.state.scanDir != ecnf['ScanDir']:
                return False
        if 'ActiveMntGrp' not in ekeys:
            return False
        amg = ecnf['ActiveMntGrp']
        if amg != cnf['ActiveMntGrp']:
            return False
        if 'MntGrpConfigs' not in ekeys:
            return False
        if not isinstance(cnf['MntGrpConfigs'], dict) or \
           amg not in cnf['MntGrpConfigs']:
            return False
        if not isinstance(ecnf['MntGrpConfigs'], dict) or \
           amg not in ecnf['MntGrpConfigs']:
            return False
        status = Checker().compDict(
            cnf['MntGrpConfigs'][amg], ecnf['MntGrpConfigs'][amg])

        return status

    def resetConfiguration(self, expconf):
        """ resets measurement group configuration

        :param expconf: new measurement group configuration
        :type expconf: :obj:`str`
        """
        logger.debug("reset Configuration")
        if not self.__skipconfig:
            conf = json.loads(self.state.lastMntGrpConfiguration())
            econf = expconf

            if not self.compareConf(conf, econf):
                self.__skipconfig = True
                replay = Qt.QMessageBox.question(
                    self.ui.preferences,
                    "NXSelector: Configuration "
                    "of Measument Group has been changed.",
                    "Would you like to update the changes? ",
                    Qt.QMessageBox.Yes | Qt.QMessageBox.No)
                if replay == Qt.QMessageBox.Yes:
                    self._resetAll()
        logger.debug("reset Configuration END")

    def updateDoorName(self, door):
        """ updates door name

        :param door: new door name
        :type door: :obj:`str`
        """

        logger.debug("update DoorName")
        if self.__progress:
            self.__door = door
            self.__doortoupdateFlag = True
        elif str(door) != str(self.state.door):
            self.__doortoupdateFlag = False
            self.ui.mntServerLineEdit.setText(door)
            self.storage.apply()
            logger.debug("change DoorName %s " % door)

        logger.debug("update DoorName END")

    @Qt.pyqtSlot()
    def __resetClicked(self):
        """ sets reset button focus and resets all settings"""
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setFocus()
        self.resetClickAll()

    @Qt.pyqtSlot()
    def __restore(self):
        """ unselected all selected elements for detectors
            or reset description to defualt values
        """
        index = self.ui.tabWidget.currentIndex()
        if index == 0:
            self.__clearAllClicked()
        elif index == 1:
            self.resetDescriptions()

    @Qt.pyqtSlot()
    def __unlock(self):
        """ unlock inaccessable descriptive components
        """
        for ds in self.state.idsgroup.keys():
            if self.state.idsgroup[ds] is None:
                self.state.idsgroup[ds] = False
        for cp in self.state.acpgroup.keys():
            if self.state.acpgroup[cp] is None:
                self.state.acpgroup[cp] = False
        self.state.ddsdirty = True
        self.resetViews()
        self.setDirty()

    def __clearAllClicked(self):
        """ unselected all selected elements for detectors
        """
        for ds in self.state.dsgroup.keys():
            self.state.dsgroup[ds] = False
        for ds in self.state.cpgroup.keys():
            self.state.cpgroup[ds] = False
        self.state.ddsdirty = True
        self.resetViews()
        self.setDirty()

    @Qt.pyqtSlot()
    def cnfLoad(self):
        """ loads selection settings from a file"""
        try:
            filename = str(Qt.QFileDialog.getOpenFileName(
                self.ui.storage,
                "Load Profile",
                self.cnfFile,
                "JSON files (*.json);;All files (*)"))
            logger.debug("loading configuration from %s" % filename)
            if filename:
                self.cnfFile = filename
                jconf = open(filename).read()

                self.state.setConfiguration(jconf)
                self.apply()
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in loading profile")
            MessageBox.warning(
                self,
                "NXSelector: Error in loading Selector Server profile",
                text, str(value))

    @Qt.pyqtSlot()
    def cnfSave(self):
        """ saves selection settings in a file"""
        try:
            filename = str(Qt.QFileDialog.getSaveFileName(
                self.ui.storage,
                "Save Profile",
                self.cnfFile,
                "JSON files (*.json);;All files (*)"))
            logger.debug("saving configuration to %s" % filename)
            if filename:
                if (len(filename) < 4 or filename[-4] != '.') and \
                        not (len(filename) > 5 and filename[-5] == '.'):
                    filename = filename + '.json'

                jconf = self.state.getConfiguration()
                self.cnfFile = filename

                with open(filename, 'w') as myfile:
                    myfile.write(jconf)
                self._resetAll()

        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in saving profile")
            MessageBox.warning(
                self,
                "NXSelector: Error in saving Selector Server profile",
                text, str(value))

    @Qt.pyqtSlot()
    def __applyClicked(self):
        """ focuses on apply button and performs apply action"""
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setFocus()
        self.__skipconfig = True
        self.apply()

    @Qt.pyqtSlot(int)
    def __tabChanged(self, index):
        """  updates button views on tab change

        :param index:  tag index
        :type index: :obj:`int`
        """
        if index == 0:
            self.ui.groupsPushButton.setText("Others")
            self.ui.groupsPushButton.show()
            self.ui.groupsPushButton.setToolTip(
                "Change the available components in the Detectors tab")
            self.ui.clearAllPushButton.setText("ClearAll")
            self.ui.clearAllPushButton.setToolTip(
                "Deselect all detector components")
            self.ui.clearAllPushButton.show()
            self.ui.unlockPushButton.hide()
        elif index == 1:
            self.ui.groupsPushButton.setText("Others")
            self.ui.groupsPushButton.show()
            self.ui.groupsPushButton.setToolTip(
                "Change the available components in the Descriptions tab")
            self.ui.clearAllPushButton.setText("Reset Desc.")
            self.ui.clearAllPushButton.setToolTip(
                "Reset profile and the description components "
                "into the default set")
            self.ui.clearAllPushButton.show()
            self.ui.unlockPushButton.setToolTip(
                "Unlock inaccessible description components")
            self.ui.unlockPushButton.show()
        else:
            self.ui.unlockPushButton.hide()
            self.ui.clearAllPushButton.hide()
            self.ui.groupsPushButton.hide()

    @Qt.pyqtSlot(int)
    def __displayStatusChanged(self, state):
        """  displays status in buttonbox

        :param state:  status state
        :type index: :obj:`int`
        """
        self.displayStatus = state
        self.setDirty(self.__dirty)

    @Qt.pyqtSlot(int)
    def __scanFileExtStatusChanged(self, state):
        """  scan file extension status in buttonbox

        :param state:  status state
        :type index: :obj:`int`
        """
        self.scanFileExtStatus = state
        if state:
            self.ui.fileExtScanLineEdit.show()
            self.ui.fileExtScanLabel.show()
            self.state.scanFile = self.storage.fileNames(False, False)
            # self.storage.apply()
            self.storage.updateForm(True)
        else:
            self.ui.fileExtScanLineEdit.hide()
            self.ui.fileExtScanLabel.hide()
            self.state.scanFile = self.storage.fileNames(False, True)
            # self.storage.apply()
            self.storage.updateForm(False)
        self.setDirty(self.__dirty)

    def closeApply(self):
        """ close action for apply command """
        self.storage.showErrors()
        if not self.closeReset():
            self.setDirty(True)
        else:
            self.setDirty(False)
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
        self.__skipconfig = False

    def apply(self):
        """ applies seeting on selection server and
            creates a new measurement group"""
        logger.debug("apply")
        try:
            conf = self.state.updateMntGrp()
            self.experimentConfigurationChanged.emit(conf)
            self.runProgress(["updateControllers", "importMntGrp",
                              "createConfiguration"],
                             "closeApply")
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in resetting Server")
            self.setDirty(True)
            if str(text).startswith("Exception: User Data not defined ["):
                ctext = str(text).replace(
                    "Exception: User Data not defined ", "").replace(
                    "'", '"').split('\n')[0].strip()
                self.defineMissingKeys(ctext)
            MessageBox.warning(
                self,
                "NXSelector: Error in applying Selector Server settings",
                text, str(value))

        logger.debug("apply END")

    def defineMissingKeys(self, ctext):
        """ adds missing keys to the user data table

        :param ctext: json list of missing user data keys
        :type ctext: :obj:`str`
        """
        if ctext:
            missingkeys = json.loads(ctext)
            for key in missingkeys:
                self.state.datarecord[key] = ""
            self.data.reset()
            self.ui.tabWidget.setCurrentIndex(self.__datatab)


def main():
    """ the main function
    """
    if "GNOME_DESKTOP_SESSION_ID" not in os.environ:
        os.environ["GNOME_DESKTOP_SESSION_ID"] = "qtconfig"
    if os.path.isdir("/usr/lib/kde4/plugins/") and \
       "QT_PLUGIN_PATH" not in os.environ:
        os.environ["QT_PLUGIN_PATH"] = "/usr/lib/kde4/plugins/"
    try:
        from taurus.external.qt import Qt
    except Exception:
        from taurus.qt import Qt
    try:
        from taurus.external.qt import __qt
    except Exception:
        from taurus.qt import __qt
    Qt.QCoreApplication.setAttribute(Qt.Qt.AA_X11InitThreads)
    Qt.QResource.registerResource(
        os.path.join(qrc.__path__[0], "resources.rcc"))

    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    standalone = app is None
    server = None
    # expert = True
    umode = None
    setdefault = False
    door = None
    switch = True

    logger.debug("Using %s" % qt_api)
    if standalone:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()

        parser.add_option(
            "-s", "--server", dest="server",
            help="selector server")
        parser.add_option(
            "-d", "--door", dest="door",
            help="door device name")
        parser.add_option(
            "-t", "--style", dest="style",
            help="Qt style")
        parser.add_option(
            "-y", "--stylesheet", dest="stylesheet",
            help="Qt stylesheet")
        parser.add_option(
            "-m", "--mode", dest="mode",
            help="interface mode, i.e. simple, user, advanced, "
            "special, expert")
        parser.add_option(
            "", "--set-as-default-mode",
            action="store_true",
            default=False,
            dest="setdefault",
            help="set the current mode as default")
        parser.add_option(
            "", "--dont-switch-mntgrp",
            action="store_false",
            default=True,
            dest="switch",
            help="do not switch MntGrp to the ActiveMntGrp")

        app = Application(
            sys.argv,
            cmd_line_parser=parser,
            app_name="NXS Component Selector",
            app_version=__version__,
            org_domain="desy.de",
            org_name="DESY")

        app.setWindowIcon(Qt.QIcon(":/configtools.png"))

        (options, _) = parser.parse_args()
        if options.style:
            app.setStyle(options.style)

        server = options.server
        if options.stylesheet:
            app.setStyleSheet(options.stylesheet)
        elif options.style == "cleanlooks":
            pyqtver = __qt.PYQT_VERSION.split(".")
            if pyqtver and pyqtver[0] == "4":
                # fix for cleanlooks tooltip colors
                app.setStyleSheet(
                    "QToolTip{ color: black; background-color: white; }"
                )

        if options.mode:
            umode = options.mode
        else:
            umode = None
        setdefault = options.setdefault
        door = options.door
        switch = options.switch

    form = Selector(server, standalone=True, umode=umode,
                    setdefault=setdefault,
                    door=door,
                    switch=switch)
    form.show()

    if standalone:
        sys.exit(app.exec_())
    else:
        return form


if __name__ == "__main__":
    main()
