#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
logger = logging.getLogger(__name__)


## main window class
@UILoadable(with_ui='ui')
class Selector(Qt.QDialog, TaurusBaseWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, door=None,
                 standalone=False, umode=None,
                 organization='DESY', application='NXS Component Selector',
                 parent=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'NXSExpDescriptionEditor')
        self.setWindowFlags(Qt.Qt.Window)
        self.loadUi()

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
        else:
            self.expert = True
            self.user = False
            self.simple = True

        self.cnfFile = ''
        self.__progress = None
        self.__commandthread = None

        self.__resetServer(server)

    def settings(self):
        logger.debug("settings")

        if self.__progress:
            self.__progress.reset()
            self.__progress.hide()
        if self.__commandthread.error:
            text = MessageBox.getText(
                "Problems in updating Channels",
                self.__commandthread.error)
            MessageBox.warning(
                self, "NXSSelector: Error in Setting Selector Server", text,
                "%s" % str(self.__commandthread.error))
            self.__commandthread.error = None

        settings = Qt.QSettings(self.__organization, self.__application, self)
        self.userView = settings.value('Preferences/UserView',
                                       'CheckBoxes Dis')
        self.rowMax = int(settings.value('Preferences/RowMax', 16))
        if not self.rowMax:
            self.rowMax = 16
        self.displayStatus = int(settings.value('Preferences/DisplayStatus',
                                                2))
        self.cnfFile = str(settings.value("Selector/CnfFile", "./"))

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
            self.preferences.views[self.userView],
            self.rowMax)

        self.data = Data(self.ui, self.state, self.simple)

        self.tabs = [self.selectable, self.automatic, self.data,
                     self.storage, self.preferences]

        self.createGUI()

        sg = settings.value("Selector/Geometry")
        if sg:
            self.restoreGeometry(sg)

        self.title = 'NeXus Component Selector'
        self.__dirty = True
        self.setDirty()
        self.__progress = None
        if self.__servertoupdateFlag:
            self.setModel(self.__model)
        if self.__doortoupdateFlag:
            self.updateDoorName(self.__door)

        logger.debug("settings END")

    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):

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
        self.ui.statusLabel = self.ui.buttonBox.addButton(
            "", Qt.QDialogButtonBox.ActionRole)
        self.ui.statusLabel.setEnabled(False)
        self.ui.buttonBox.setCenterButtons(True)

        layout = self.ui.profileButtonBox.layout()
        for i in range(layout.count()):
            spacer = layout.itemAt(i)
            if isinstance(spacer, Qt.QSpacerItem):
                spacer.changeSize(
                    0, 0, Qt.QSizePolicy.Minimum)

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

        flayout = Qt.QHBoxLayout(self.ui.timerButtonFrame)
        flayout.setContentsMargins(0, 0, 0, 0)
        self.ui.timerAddPushButton = Qt.QPushButton("+")
        self.ui.timerAddPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerAddPushButton)
        self.ui.timerDelPushButton = Qt.QPushButton("-")
        self.ui.timerDelPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerDelPushButton)

        self.ui.statusLabel.setAutoFillBackground(True)
        self.ui.statusLabel.setSizePolicy(Qt.QSizePolicy.Expanding,
                                          Qt.QSizePolicy.Fixed)

        self.ui.statusLabel.setStyleSheet(
            "background-color:white;border-style: outset; "
            "border-width: 1px; border-color: gray; "
            "color:#208020;font:bold;")

        if not self.expert:
            self.ui.groupFrame.hide()
            self.ui.channelFrame.hide()
            self.ui.dynFrame.hide()
            self.ui.measFrame.hide()
            self.ui.mntServerLabel.hide()
            self.ui.mntServerLineEdit.hide()
            self.ui.devConfigLabel.hide()
            self.ui.devConfigLineEdit.hide()
            self.ui.devWriterLabel.hide()
            self.ui.devWriterLineEdit.hide()
            self.ui.devConfigPushButton.hide()
            self.ui.groupsPushButton.hide()
            self.ui.componentFrame.hide()
            self.ui.devSettingsLineEdit.setEnabled(False)
        if self.user:
            self.ui.mntGrpComboBox.setEnabled(False)
            self.ui.mntGrpToolButton.hide()
            self.ui.selectorFrame.hide()
            self.ui.viewServerFrame.hide()
            self.ui.viewFrame.hide()
        if self.simple:
            self.ui.timerAddPushButton.hide()
            self.ui.timerDelPushButton.hide()
            self.ui.mntTimerComboBox.setEnabled(False)
            self.ui.timerButtonFrame.setEnabled(False)
            self.ui.state.hide()
            self.ui.tabWidget.removeTab(1)
            self.ui.tabWidget.setCurrentIndex(1)
        for tab in self.tabs:
            tab.reset()

        self.ui.mntGrpComboBox.setInsertPolicy(
            self.ui.mntGrpComboBox.InsertAtTop)

        self.storage.updateMntGrpComboBox()

        cid = self.ui.viewComboBox.findText(Qt.QString(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid)
        self.ui.rowMaxSpinBox.setValue(self.rowMax)
        self.ui.statusCheckBox.setChecked(self.displayStatus != 0)
        self.connect(self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply),
                     Qt.SIGNAL("pressed()"), self.__applyClicked)
        self.connect(self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset),
                     Qt.SIGNAL("pressed()"), self.__resetClicked)
        if self.__standalone:
            self.connect(self.ui.buttonBox.button(Qt.QDialogButtonBox.Close),
                         Qt.SIGNAL("pressed()"), self.close)
        self.connect(self.ui.clearAllPushButton,
                     Qt.SIGNAL("pressed()"), self.__clearAllClicked)

        self.connect(self.ui.profileButtonBox.button(Qt.QDialogButtonBox.Open),
                     Qt.SIGNAL("pressed()"), self.cnfLoad)
        self.connect(self.ui.profileButtonBox.button(Qt.QDialogButtonBox.Save),
                     Qt.SIGNAL("pressed()"), self.cnfSave)

        self.connect(self.ui.preferences,
                     Qt.SIGNAL("serverChanged()"), self.resetServer)

        self.connect(self.ui.preferences,
                     Qt.SIGNAL("layoutChanged(QString,QString)"),
                     self.resetLayout)

        self.connect(self.ui.preferences,
                     Qt.SIGNAL("layoutChanged(QString,QString)"),
                     self.resetLayout)

        self.connect(self.ui.viewComboBox,
                     Qt.SIGNAL("currentIndexChanged(int)"), self.resetViews)

        self.connect(self.ui.rowMaxSpinBox,
                     Qt.SIGNAL("editingFinished()"), self.resetRows)

        self.connect(self.ui.statusCheckBox,
            Qt.SIGNAL("stateChanged(int)"), self.__displayStatusChanged)

        self.connect(self.ui.selectable, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.state, Qt.SIGNAL("componentChecked"),
                     self.__componentChanged)
        self.connect(self.ui.data, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.storage, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.storage, Qt.SIGNAL("reset"),
                     self.resetViews)
        self.connect(self.ui.storage, Qt.SIGNAL("resetDescriptions"),
                     self.resetDescriptions)
        self.connect(self.ui.storage, Qt.SIGNAL("resetAll"),
                     self.resetAll)
        self.connect(self.ui.storage, Qt.SIGNAL("updateGroups"),
                     self.updateGroups)

    def __componentChanged(self):
        self.setDirty()
        self.selectable.updateViews()

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
                    "color:#A02020;font:bold;")
                self.ui.statusLabel.setText('NOT APPLIED')
                self.setWindowTitle(self.title + ' * ')
            else:
                self.setWindowTitle(self.title)
                self.ui.statusLabel.setStyleSheet(
                    "background-color: white;border-style: outset; "
                    "border-width: 1px; border-color: gray; "
                    "color:#206020;font:bold;")
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
                self.setWindowTitle(self.title + ' * ')
            else:
                self.setWindowTitle(self.title)
                self.ui.buttonBox.button(
                    Qt.QDialogButtonBox.Reset).setEnabled(False)
                self.ui.buttonBox.button(
                    Qt.QDialogButtonBox.Apply).setEnabled(False)
#                self.ui.applyPushButton.setEnabled(False)
#                self.ui.resetPushButton.setEnabled(False)
            self.ui.statusLabel.hide()

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

    def resetServer(self):
        logger.debug("reset server")
        self.state.setServer()
        self.resetAll()
        logger.debug("reset server ended")

    def resetLayout(self, frames, groups):
        logger.debug("reset layout")
        self.selectable.frames = str(frames)
        self.selectable.mgroups = str(groups)
        self.resetViews()
        logger.debug("reset layout ended")

    def resetRows(self):
        logger.debug("reset rows")
        rowMax = self.ui.rowMaxSpinBox.value()
        for tab in self.tabs:
            tab.rowMax = rowMax
        self.resetViews()
        logger.debug("reset rows ended")

    def updateGroups(self):
        ## QProgressDialog to be added
        self.state.storeGroups()
        self.resetAll()

    def resetViews(self):
        logger.debug("reset view")
        for tab in self.tabs:
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
            tab.reset()
        logger.debug("reset selector ended")

    def closeReset(self):
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
        self.reset()
        self.storage.updateMntGrpComboBox()
        self.setDirty(True)
        self.__progress = None
        if self.__servertoupdateFlag:
            self.updateServer(self.__model)
        if self.__doortoupdateFlag:
            self.updateDoorName(self.__door)
        logger.debug("closing Progress ENDED")

    def waitForThread(self):
        logger.debug("waiting for Thread")
        if self.__commandthread:
            self.__commandthread.wait()
        logger.debug("waiting for Thread ENDED")

    def runProgress(self, commands, onclose="closeReset"):
        if self.__progress:
            return
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

    def resetAll(self):
        logger.debug("reset ALL")
        self.runProgress(["updateControllers", "importMntGrp"])
        logger.debug("reset ENDED")

    def resetDescriptions(self):
        logger.debug("reset Descriptions")
        self.runProgress(["resetDescriptions", "importMntGrp"])
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

    def __resetClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setFocus()
        self.resetAll()

    def __clearAllClicked(self):
        for ds in self.state.dsgroup.keys():
            self.state.dsgroup[ds] = False
        for ds in self.state.cpgroup.keys():
            self.state.cpgroup[ds] = False
        self.resetViews()
        self.setDirty()

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
                self.resetAll()
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in loading profile")
            MessageBox.warning(
                self,
                "NXSSelector: Error in loading Selector Server profile",
                text, str(value))

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
            text = MessageBox.getText("Problems in loading profile")
            MessageBox.warning(
                self,
                "NXSSelector: Error in loading Selector Server profile",
                text, str(value))

    def __applyClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setFocus()
        self.apply()

    def __displayStatusChanged(self, state):
        self.displayStatus = state
        self.setDirty(self.__dirty)

    def closeApply(self):
        self.closeReset()
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
        self.setDirty(False)

    def apply(self):
        logger.debug("apply")
        try:
            conf = self.state.updateMntGrp()
            self.emit(Qt.SIGNAL('experimentConfigurationChanged'), conf)
            self.runProgress(["updateControllers", "importMntGrp"],
                             "closeApply")
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Problems in resetting Server")
            MessageBox.warning(
                self,
                "NXSSelector: Error in applying Selector Server settings",
                text, str(value))

        logger.debug("apply END")
