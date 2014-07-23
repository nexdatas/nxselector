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

import sys 
import PyTango
import json 
 
from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from .ServerState import ServerState

from .Selectable import Selectable
from .Preferences import Preferences
from .State import State
from .Data import Data
from .Storage import Storage

from .ui.ui_selector import Ui_Selector


import logging
logger = logging.getLogger(__name__)

    

## main window class
class Selector(Qt.QDialog, TaurusBaseWidget):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, standalone=False, 
                 organization = 'DESY', application = 'NXS Component Selector',
                 parent=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self,'NXSExpDescriptionEditor')
        logger.debug("PARAMETERS: %s %s", 
                     server, parent)
        self.__organization = organization
        self.__application = application

        self.__standalone = standalone
        self.__ask = False
        
        self.cnfFile = ''
        logger.debug("server0")
        try:
            logger.debug("server1")
            self.state = ServerState(server)
            logger.debug("server2")
            self.state.fetchSettings()
        except PyTango.DevFailed as e:
            value = sys.exc_info()[1]
            Qt.QMessageBox.warning(
                self, 
                "NXSSelector: Error in Setting Selector Server",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
#            sys.exit(-1)
            self.state = ServerState("")
            self.state.setServer()
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            Qt.QMessageBox.warning(
                self, 
                "NXSSelector: Error in Setting Selector Server",
                "%s" % (value))
#            Qt.QMessageBox.warning(
#                self, 
#                "NXSSelector: Error in Setting Server",
#                str(e))
#            sys.exit(-1)
            self.state = ServerState("")
            self.state.setServer()


        settings = Qt.QSettings(self.__organization, self.__application, self)

        self.userView = settings.value('Preferences/UserView', 'CheckBoxes Dis')
        self.rowMax = int(settings.value('Preferences/RowMax', 20))
        self.displayStatus = int(settings.value('Preferences/DisplayStatus', 2))

        ## user interface
        self.ui = Ui_Selector()
        self.preferences = Preferences(self.ui, self.state)
        if self.userView not in self.preferences.views:
            self.userView = 'CheckBoxes Dis'
        self.storage = Storage(self.ui, self.state) 
        self.selectable = Selectable(
            self.ui, self.state, 
            self.preferences.views[self.userView],
            self.rowMax)

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

        self.selectable.mgroups = str(self.preferences.mgroups)
        self.selectable.frames = str(self.preferences.frames)
        self.automatic = State(
            self.ui, self.state, 
            self.preferences.views[self.userView],
            self.rowMax)

        self.data = Data(self.ui, self.state)

        self.tabs = [self.selectable, self.automatic, self.data,
                     self.storage, self.preferences]

        self.createGUI()  
       
        sg = settings.value("Selector/Geometry")
        if sg:
            self.restoreGeometry(sg)

        self.title = 'NeXus Component Selector'
        self.__dirty = True
        self.setDirty()

    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)        

        if not self.__standalone:
            self.ui.mntServerLineEdit.hide()
            self.ui.mntServerLabel.hide()
            self.ui.buttonBox.setStandardButtons(
                Qt.QDialogButtonBox.Reset | Qt.QDialogButtonBox.Apply )
        else:
            self.ui.buttonBox.setStandardButtons(
                Qt.QDialogButtonBox.Reset | Qt.QDialogButtonBox.Apply \
                    | Qt.QDialogButtonBox.Close)
        self.ui.buttonBox.setSizePolicy (Qt.QSizePolicy.Expanding, 
                                         Qt.QSizePolicy.Fixed)

        self.ui.statusLabel = self.ui.buttonBox.addButton(
            "", Qt.QDialogButtonBox.ActionRole)  
        self.ui.statusLabel.setEnabled(False)  
        self.ui.buttonBox.setCenterButtons(True)  


        layout = self.ui.layoutButtonBox.layout() 
        for i in range(layout.count()):
            spacer = layout.itemAt(i)
            if isinstance(spacer, Qt.QSpacerItem):
                spacer.changeSize(
                    0, 0, Qt.QSizePolicy.Minimum)

        layout = self.ui.profileButtonBox.layout() 
        for i in range(layout.count()):
            spacer = layout.itemAt(i)
            if isinstance(spacer, Qt.QSpacerItem):
                spacer.changeSize(
                    0, 0, Qt.QSizePolicy.Minimum)
        
        flayout = Qt.QHBoxLayout(self.ui.timerButtonFrame)
        flayout.setContentsMargins(0,0,0,0)
        self.ui.timerAddPushButton = Qt.QPushButton("+") 
        self.ui.timerAddPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerAddPushButton)
        self.ui.timerDelPushButton = Qt.QPushButton("-")
        self.ui.timerDelPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerDelPushButton)

        self.ui.statusLabel.setAutoFillBackground(True)
        self.ui.statusLabel.setSizePolicy (Qt.QSizePolicy.Expanding, 
                                           Qt.QSizePolicy.Fixed)
#        self.ui.statusLabel.setFrameShape(Qt.QFrame.StyledPanel)
#        self.ui.statusLabel.setFrameShadow(Qt.QFrame.Raised)
#        self.ui.statusLabel.setAlignment(Qt.Qt.AlignHCenter)

        self.ui.statusLabel.setStyleSheet("background-color:white;border-style: outset; border-width: 1px; border-color: gray; color:#208020;font:bold;")
     
        for tab in self.tabs:
            tab.reset()

    
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


        self.connect(self.ui.profileButtonBox.button(Qt.QDialogButtonBox.Open), 
                     Qt.SIGNAL("pressed()"), self.cnfLoad)
        self.connect(self.ui.profileButtonBox.button(Qt.QDialogButtonBox.Save), 
                     Qt.SIGNAL("pressed()"), self.cnfSave)

        self.connect(self.ui.preferences, 
                     Qt.SIGNAL("serverChanged()"), self.resetServer)

        self.connect(self.ui.preferences, 
                     Qt.SIGNAL("layoutChanged(QString,QString)"), self.resetLayout)

        self.connect(self.ui.preferences, 
                     Qt.SIGNAL("layoutChanged(QString,QString)"), self.resetLayout)

        self.connect(self.ui.viewComboBox, 
                     Qt.SIGNAL("currentIndexChanged(int)"), self.resetViews)

        self.connect(self.ui.rowMaxSpinBox, 
                     Qt.SIGNAL("valueChanged(int)"), self.resetRows)

        self.connect(self.ui.statusCheckBox, 
            Qt.SIGNAL("stateChanged(int)"), self.__displayStatusChanged)

        self.connect(self.ui.selectable, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.state, Qt.SIGNAL("componentChecked"), 
                     self.__componentChanged)
        self.connect(self.ui.data, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.storage, Qt.SIGNAL("dirty"), self.setDirty)
        self.connect(self.ui.storage, Qt.SIGNAL("reset"), self.resetViews)


    def __componentChanged(self):
        self.setDirty()
        self.selectable.updateViews()


    def setDirty(self, flag = True):
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
                self.ui.statusLabel.setStyleSheet("background-color: white;border-style: outset; border-width: 1px; border-color: gray; color:#A02020;font:bold;")
#                self.ui.statusLabel.setText('<font color=#A02020 size=3><b>NOT APPLIED</b></font>' )
                self.ui.statusLabel.setText('NOT APPLIED')
                self.setWindowTitle(self.title + ' * ' )
            else:
                self.setWindowTitle(self.title)
                self.ui.statusLabel.setStyleSheet("background-color: white;border-style: outset; border-width: 1px; border-color: gray; color:#206020;font:bold;")
#                self.ui.statusLabel.setText('<font color=#206020 size=3><b>APPLIED</b></font>' )
                self.ui.statusLabel.setText('APPLIED' )
            self.ui.statusLabel.show()
        else:
            self.ui.buttonBox.setCenterButtons(False)  
            for i in range(self.ui.buttonHorizontalLayout.count()):
                spacer = self.ui.buttonHorizontalLayout.itemAt(i)
                if isinstance(spacer, Qt.QSpacerItem):
                    spacer.changeSize(
                        40, 20, Qt.QSizePolicy.Expanding)
            
            if flag:    
                self.setWindowTitle(self.title + ' * ' )
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

                    
    def closeEvent(self, event):
        logger.debug("close event")
        self.__saveSettings()
        Qt.QWidget.closeEvent(self, event)
        logger.debug("close event ended")

    def resetServer(self):
        logger.debug("reset server")
        self.state.setServer()
        self.reset()
        logger.debug("reset server ended")

    def resetLayout(self, frames, groups):
        logger.debug("reset layout")
        self.selectable.frames = str(frames)
        self.selectable.mgroups = str(groups)
        self.resetViews()
        logger.debug("reset layout ended")


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
        try:
            self.state.fetchSettings()
        except Exception as e:
            import traceback
            value = traceback.format_exc()
            Qt.QMessageBox.warning(
                self, 
                "NXSSelector: Error in Setting Selector Server",
                "%s" % (value))

        for tab in self.tabs:
            tab.reset()
        logger.debug("reset selector ended")

    def resetAll(self, ask = True):
        logger.debug("reset ALL")
        self.state.updateControllers()
        self.state.importMntGrp()
        self.reset()
        self.setDirty(False)
        logger.debug("reset ENDED")


    def resetConfiguration(self, expconf):
        logger.debug("reset Configuration")
        conf = self.state.mntGrpConfiguration()
        econf = json.dumps(expconf)
        if conf != econf:
            replay = Qt.QMessageBox.question(
                self.ui.preferences, 
                "NXSSelector: Configuration of Measument Group has been changed.", 
                "Would you like to update the changes? " ,
                Qt.QMessageBox.Yes|Qt.QMessageBox.No)
            if replay == Qt.QMessageBox.Yes:
                self.resetAll(False)
        logger.debug("reset Configuration END")


    def updateDoorName(self, door):
        if str(door) != str(self.state.door):
            self.ui.mntServerLineEdit.setText(door)
            self.storage.apply()
            logger.debug("change DoorName %s " % door)
           
        logger.debug("update DoorName")

        
    def __resetClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).hide()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).show()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setFocus()

#        self.ui.resetPushButton.hide()
#        self.ui.resetPushButton.show()
#        self.ui.resetPushButton.setFocus()
        
        self.resetAll()

    def cnfLoad(self):    
        filename = str(Qt.QFileDialog.getOpenFileName(
                self.ui.storage,
                "Load Configuration",        
                self.cnfFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("loading configuration from %s" % filename)
        if filename:
            self.cnfFile = filename
            jconf = open(filename).read()

            self.state.setConfiguration(jconf)
            self.resetAll()

    def cnfSave(self):
        filename = str(Qt.QFileDialog.getSaveFileName(
                self.ui.storage,
                "Save Configuration",
                self.cnfFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("saving configuration to %s" % filename)
        if filename:
            jconf = self.state.getConfiguration()
            self.cnfFile = filename

            with open(filename, 'w') as myfile:
                myfile.write(jconf)
            self.resetAll()

    def __applyClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).hide()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).show()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setFocus()
#        self.ui.applyPushButton.hide()
#        self.ui.applyPushButton.show()
#        self.ui.applyPushButton.setFocus()
        self.apply()

        
    def __displayStatusChanged(self, state):
        self.displayStatus = state
        self.setDirty(self.__dirty)


    def apply(self):
        logger.debug("apply")
        try:
            conf = self.state.updateMntGrp()
            self.resetAll()
            self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
            self.setDirty(False)
            self.emit(Qt.SIGNAL('experimentConfigurationChanged'), conf)
        except PyTango.DevFailed as e:
            value = sys.exc_info()[1]
            Qt.QMessageBox.warning(
                self, 
                "NXSSelector: Error in updating Measurement Group",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
        except Exception as e:
            Qt.QMessageBox.warning(
                self, 
                "NXSSelector: Error in updating Measurement Group",
                str(e))

        logger.debug("apply END")
            
