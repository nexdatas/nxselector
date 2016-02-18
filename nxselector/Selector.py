#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

import sys
import PyTango
import json
import time

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable


from taurus.qt.qtgui.base import TaurusBaseWidget
from .ServerState import ServerState

from .Selectable import Selectable
from .Preferences import Preferences
from .State import State
from .Data import Data
from .Storage import Storage
from .CommandThread import CommandThread
from .MessageBox import MessageBox

import logging
import gc
logger = logging.getLogger(__name__)


## main window class
@UILoadable(with_ui='ui')
class Selector(Qt.QDialog, TaurusBaseWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, door=None,
                 standalone=False, umode=None,
                 setdefault=False,
                 organization='DESY', application='NXS Component Selector',
                 parent=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'NXSExpDescriptionEditor')
        self.setWindowFlags(Qt.Qt.Window)
        self.loadUi()
        self.debug("SELECTOR load")
        self.show()
        if umode != 'administrator':
            self.ui.tabWidget.removeTab(4)
        logger.debug("PARAMETERS: %s %s",
                     server, parent)
        self.__organization = organization
        self.__application = application
        self.__door = door
        self.__standalone = standalone

        self.__progressFlag = False
        self.__doortoupdateFlag = False
        self.__servertoupdateFlag = False

        self.__model = None
        self.state = None

        self.__setdefault = setdefault
        self.__umode = umode
        self.expert = True
        self.user = False
        self.simple = False
        if self.__umode:
            self.__setmode(self.__umode)
        self.cnfFile = ''
        self.__progress = None
        self.__commandthread = None

        self.__resetServer(server)
        self.__datatab = 2

    def __setmode(self, umode):
        ## expert mode
        if umode == 'expert':
            self.expert = True
            self.user = False
            self.simple = False
        elif umode == 'advanced':
            self.expert = False
            self.user = False
            self.simple = False
        elif umode == 'user':
            self.expert = False
            self.user = True
            self.simple = False
        elif umode == 'simple':
            self.expert = False
            self.user = True
            self.simple = True

    def settings(self):
        logger.debug("settings")

        if self.__progress:
            self.__progress.reset()
            self.__progress.hide()
        if self.__commandthread and self.__commandthread.error:
            text = MessageBox.getText(
                "Problems in updating Channels",
                self.__commandthread.error)
            MessageBox.warning(
                self, "NXSSelector: Error in Setting Selector Server", text,
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
        self.displayStatus = int(settings.value('Preferences/DisplayStatus',
                                                2))
        self.cnfFile = str(settings.value("Selector/CnfFile", "./"))

        self.__addButtonBoxes()

        ## user interface
        self.preferences = Preferences(self.ui, self.state)
        if self.userView not in self.preferences.views:
            self.userView = 'CheckBoxes Dis'
        self.storage = Storage(self.ui, self.state, self.simple)

        self.selectable = Selectable(
            self.ui, self.state,
            self.preferences.views[self.userView],
            self.rowMax, int(self.simple) + 2 * int(self.user))

        self.preferences.mgroups = settings.value(
            'Preferences/Groups', '{}')
        self.preferences.frames = settings.value(
            'Preferences/Frames',
            '[]')
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

        self.selectable.mgroups = str(self.preferences.mgroups)
        self.selectable.frames = str(self.preferences.frames)
        self.automatic = State(
            self.ui, self.state,
            self.preferences.views["CheckBoxes Dis (U)"],
            self.rowMax)

        self.data = Data(self.ui, self.state, self.simple or self.user)

        self.tabs = [self.selectable, self.automatic, self.data,
                     self.storage, self.preferences]

        self.createGUI()

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

        self.waitForThread()
        logger.debug("settings END")

    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):

        self.__setButtonBoxes()
        self.__hideWidgets()
        for tab in self.tabs:
                tab.reset()

        self.__setWidgetValues()
        self.__connectSignals()
        self.__addTips()

    def __addButtonBoxes(self):
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

        self.ui.loadProfilePushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Open)
        self.ui.loadProfilePushButton.setText("Load")

        self.ui.saveProfilePushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Save)

        self.ui.groupsPushButton = self.ui.buttonBox.addButton(
            Qt.QDialogButtonBox.Retry)
        self.ui.groupsPushButton.setText("Det. Content")


        self.ui.statusLabel = self.ui.buttonBox.addButton(
            "", Qt.QDialogButtonBox.ActionRole)
        self.ui.statusLabel.setEnabled(False)
        self.ui.buttonBox.setCenterButtons(True)

    def __setButtonBoxes(self):

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

        cid = self.ui.viewComboBox.findText(Qt.QString(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid)
        self.ui.rowMaxSpinBox.setValue(self.rowMax)
        self.ui.statusCheckBox.setChecked(self.displayStatus != 0)

    def __hideWidgets(self):
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
            self.ui.mntGrpComboBox.setEnabled(False)
            self.ui.mntGrpToolButton.hide()
            self.ui.viewServerFrame.hide()
            self.ui.viewGroupBox.hide()
        if self.simple:
            self.ui.orderToolButton.hide()
            self.ui.timerAddPushButton.hide()
            self.ui.timerDelPushButton.hide()
            self.ui.mntTimerComboBox.setEnabled(False)
            self.ui.timerButtonFrame.setEnabled(False)
            self.ui.state.hide()
            self.ui.tabWidget.removeTab(1)
            self.__datatab -= 1
            self.ui.tabWidget.setCurrentIndex(self.__datatab)

    def __connectSignals(self):
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Apply).pressed.connect(self.__applyClicked)
        self.ui.buttonBox.button(
            Qt.QDialogButtonBox.Reset).pressed.connect(self.__resetClicked)
        if self.__standalone:
            self.ui.buttonBox.button(
                Qt.QDialogButtonBox.Close).pressed.connect(self.close)
        self.ui.clearAllPushButton.pressed.connect(self.__restore)

        self.ui.loadProfilePushButton.pressed.connect(self.cnfLoad)
        self.ui.saveProfilePushButton.pressed.connect(self.cnfSave)

        self.preferences.serverChanged.connect(self.resetServer)
        self.preferences.layoutChanged.connect(self.resetLayout)

        self.ui.viewComboBox.currentIndexChanged.connect(self.resetViews)
        self.ui.rowMaxSpinBox.editingFinished.connect(self.resetRows)
        self.ui.statusCheckBox.stateChanged.connect(
            self.__displayStatusChanged)

        self.selectable.dirty.connect(self.setDirty)
        self.automatic.componentChecked.connect(self.__componentChanged)
        self.data.dirty.connect(self.setDirty)
        self.storage.dirty.connect(self.setDirty)
        self.storage.resetViews.connect(self.resetViews)
        self.storage.resetAll.connect(self.resetAll)
        self.storage.updateGroups.connect(self.updateGroups)
        self.ui.tabWidget.currentChanged.connect(self.__tabChanged)

    def __addTips(self):
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
            "and making synchronization with the Active Measurement Group.\n" +
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
            "Load a previously selected channels from a file.")
        self.ui.saveProfilePushButton.setToolTip(
            "Save the currently selected channels into a file.")
        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Open).setToolTip(
            "Load from a file a previously saved detector layout.")
        self.ui.layoutButtonBox.button(
            Qt.QDialogButtonBox.Save).setToolTip(
            "Save into a file the currently detector layout.")
        self.ui.groupsPushButton.setToolTip(
            "Change the available components in the Detectors tab")

    def setModel(self, model):
        if str(model) != str(self.state.server):
            if self.__progress:
                self.__model = model
                self.__servertoupdateFlag = True
            elif self.__servertoupdateFlag:
                self.ui.devSettingsLineEdit.setText(model)
                self.preferences.changeServer(False)
                self.__servertoupdateFlag = False
                logger.debug("change ServerName %s " % model)
        else:
            self.__servertoupdateFlag = False

    def __saveSettings(self):
        settings = Qt.QSettings(self.__organization, self.__application, self)
        settings.setValue(
            "Selector/Geometry",
            Qt.QVariant(self.saveGeometry()))
        settings.setValue(
            "Preferences/UserView",
            Qt.QVariant(str(self.ui.viewComboBox.currentText())))
        settings.setValue(
            "Preferences/RowMax",
            Qt.QVariant(self.ui.rowMaxSpinBox.value()))
        settings.setValue(
            "Preferences/DisplayStatus",
            Qt.QVariant(2 if self.ui.statusCheckBox.isChecked() else 0))
        settings.setValue(
            "Preferences/Groups",
            Qt.QVariant(str(self.preferences.mgroups)))
        settings.setValue(
            "Preferences/Frames",
            Qt.QVariant(str(self.preferences.frames)))
        settings.setValue(
            "Preferences/FramesHints",
            Qt.QVariant(self.preferences.frameshelp))
        settings.setValue(
            "Preferences/GroupsHints",
            Qt.QVariant(self.preferences.mgroupshelp))
        settings.setValue(
            "Selector/CnfFile", Qt.QVariant(self.cnfFile))
        settings.setValue(
            "Preferences/LayoutFile",
            Qt.QVariant(self.preferences.layoutFile))
        if self.__setdefault:
            settings.setValue(
                "Selector/DefaultMode",
                Qt.QVariant(self.__umode))

    def keyPressEvent(self, event):
        if hasattr(event, "key") and event.key() == Qt.Qt.Key_Escape:
            logger.debug("escape key event")
            self.__saveSettings()
        Qt.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        logger.debug("close event")
        self.__saveSettings()
        Qt.QDialog.closeEvent(self, event)
        logger.debug("close event ended")

    def __resetServer(self, server):
        try:
            self.state = ServerState(server)
            if self.__door:
                self.state.storeData("door", self.__door)
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText(
                "Problems in resetting Server")
            MessageBox.warning(
                self, "NXSSelector: Error in Setting Selector Server",
                text, str(value))
            self.state = ServerState("")
            self.state.setServer()
            if self.__door:
                self.state.storeData("door", self.__door)
        self.runProgress(["updateControllers", "fetchSettings"],
                         "settings")
#        self.storage.showErrors()

    @Qt.pyqtSlot()
    def __componentChanged(self):
        self.setDirty()
        self.selectable.updateViews()

    @Qt.pyqtSlot()
    def setDirty(self, flag=True):
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
        logger.debug("reset server")
        self.state.setServer()
        self.resetAll()
        logger.debug("reset server ended")

    @Qt.pyqtSlot(Qt.QString, Qt.QString)
    def resetLayout(self, frames, groups):
        logger.debug("reset layout")
        self.selectable.frames = str(frames)
        self.selectable.mgroups = str(groups)
        self.resetViews()
        logger.debug("reset layout ended")

    @Qt.pyqtSlot()
    def resetRows(self):
        logger.debug("reset rows")
        rowMax = self.ui.rowMaxSpinBox.value()
        for tab in self.tabs:
            tab.rowMax = rowMax
        self.resetViews()
        logger.debug("reset rows ended")

    @Qt.pyqtSlot()
    def updateGroups(self):
        ## QProgressDialog to be added
        self.state.storeGroups()
        self.resetAll()

    @Qt.pyqtSlot()
    def resetViews(self):
        logger.debug("reset view")
        for tab in self.tabs:
            if not isinstance(tab, State):
                tab.userView = self.preferences.views[
                    str(self.ui.viewComboBox.currentText())]
            tab.reset()
        logger.debug("reset view end")

    def reset(self):
        logger.debug("reset selector")
        try:
            self.state.fetchSettings()
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in resetting Server")
            MessageBox.warning(
                self, "NXSSelector: Error in Resetting Selector Server",
                text, str(value))
        for tab in self.tabs:
            #       if tab in [
            #            self.selectable,
            #            self.automatic,
            #            self.data,
            #            self.storage,
            #            self.preferences
            #        ]:
            tab.reset()
        logger.debug("reset selector ended")

    def closeReset(self):
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
                "NXSSelector: Error in updating Selector Server Channels",
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
            self.updateServer(self.__model)
        if self.__doortoupdateFlag:
            self.updateDoorName(self.__door)
        self.waitForThread()
        gc.collect()
        logger.debug("closing Progress ENDED")
        return status

    def waitForThread(self):
        logger.debug("waiting for Thread")
        if self.__commandthread:
            self.__commandthread.wait()
        logger.debug("waiting for Thread ENDED")

    def runProgress(self, commands, onclose="closeReset"):
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
            "Updating preselected devices...", None, 0, 0, self)
        self.__progress.setWindowModality(Qt.Qt.WindowModal)
        self.__progress.rejected.connect(
            self.waitForThread, Qt.Qt.QueuedConnection)
        self.__commandthread.start()
        self.__progress.show()

    def resetClickAll(self):
        logger.debug("reset ALL")
        self.runProgress([
            "switchMntGrp",
            "updateControllers",
            "importMntGrp"
        ])
        self.storage.showErrors()
        logger.debug("reset ENDED")

    @Qt.pyqtSlot()
    def resetAll(self):
        logger.debug("reset ALL")
        self.runProgress([
            "updateControllers", "importMntGrp"])
        self.storage.showErrors()
        logger.debug("reset ENDED")

    def resetDescriptions(self):
        logger.debug("reset Descriptions")
        self.runProgress(["resetDescriptions", "importMntGrp"])
        self.storage.showErrors()
        logger.debug("reset Descriptions ENDED")

    def resetConfiguration(self, expconf):
        logger.debug("reset Configuration")
        conf = self.state.mntGrpConfiguration()
        econf = json.dumps(expconf)
        if conf != econf:
            replay = Qt.QMessageBox.question(
                self.ui.preferences,
                "NXSSelector: Configuration "
                "of Measument Group has been changed.",
                "Would you like to update the changes? ",
                Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if replay == Qt.QMessageBox.Yes:
                self.resetAll()
        logger.debug("reset Configuration END")

    def updateDoorName(self, door):
        logger.debug("update DoorName")
        if self.__progress:
            self.__door = door
            self.__doortoupdateFlag = True
        elif str(door) != str(self.state.door):
            self.ui.mntServerLineEdit.setText(door)
            self.storage.apply()
            logger.debug("change DoorName %s " % door)
            self.__doortoupdateFlag = False

        logger.debug("update DoorName END")

    @Qt.pyqtSlot()
    def __resetClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setFocus()
        self.resetClickAll()

    @Qt.pyqtSlot()
    def __restore(self):
        index = self.ui.tabWidget.currentIndex()
        if index == 0:
            self.__clearAllClicked()
        elif index == 1:
            self.resetDescriptions()

    def __clearAllClicked(self):
        for ds in self.state.dsgroup.keys():
            self.state.dsgroup[ds] = False
        for ds in self.state.cpgroup.keys():
            self.state.cpgroup[ds] = False
        self.resetViews()
        self.setDirty()

    @Qt.pyqtSlot()
    def cnfLoad(self):
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
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in loading profile")
            MessageBox.warning(
                self,
                "NXSSelector: Error in loading Selector Server profile",
                text, str(value))

    @Qt.pyqtSlot()
    def cnfSave(self):
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
                self.resetAll()

        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in saving profile")
            MessageBox.warning(
                self,
                "NXSSelector: Error in saving Selector Server profile",
                text, str(value))

    @Qt.pyqtSlot()
    def __applyClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setFocus()
        self.apply()

    @Qt.pyqtSlot(int)
    def __tabChanged(self, index):
        if index == 0:
            self.ui.groupsPushButton.setText("Det. Content")
            self.ui.groupsPushButton.show()
            self.ui.groupsPushButton.setToolTip(
                "Change the available components in the Detectors tab")
            self.ui.clearAllPushButton.setText("ClearAll")
            self.ui.clearAllPushButton.setToolTip("Deselect all detector components")
            self.ui.clearAllPushButton.show()
        elif index == 1:
            self.ui.groupsPushButton.setText("Desc. Content")
            self.ui.groupsPushButton.show()
            self.ui.groupsPushButton.setToolTip(
                "Change the available components in the Descriptions tab")
            self.ui.clearAllPushButton.setText("Restore Desc.")
            self.ui.clearAllPushButton.setToolTip(
                "Reset the description components into the default set")
            self.ui.clearAllPushButton.show()
        else:
            self.ui.clearAllPushButton.hide()
            self.ui.groupsPushButton.hide()

    @Qt.pyqtSlot(int)
    def __displayStatusChanged(self, state):
        self.displayStatus = state
        self.setDirty(self.__dirty)

    def closeApply(self):
        if not self.closeReset():
            self.setDirty(True)
        else:
            self.setDirty(False)
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)

    def apply(self):
        logger.debug("apply")
        try:
            conf = self.state.updateMntGrp()
            self.emit(Qt.SIGNAL('experimentConfigurationChanged'), conf)
            self.runProgress(["updateControllers", "importMntGrp",
                              "createConfiguration"],
                             "closeApply")
            self.storage.showErrors()
        except Exception as e:
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
                "NXSSelector: Error in applying Selector Server settings",
                text, str(value))

        logger.debug("apply END")

    def defineMissingKeys(self, ctext):
        if ctext:
            missingkeys = json.loads(ctext)
            for key in missingkeys:
                self.state.datarecord[key] = ""
            self.data.reset()
            self.ui.tabWidget.setCurrentIndex(self.__datatab)
