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
 
 
from taurus.external.qt import Qt
#from PyQt4.QtGui import (
#    QDialog, QMessageBox, QDialogButtonBox, QFileDialog, 
#    QPushButton,QHBoxLayout)
#from PyQt4.QtCore import (
#    SIGNAL, QSettings, QVariant,  QString)
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
    def __init__(self, server=None, parent=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self,'NXSExpDescriptionEditor')
        logger.debug("PARAMETERS: %s %s", 
                     server, parent)


        try:
            self.state = ServerState(server)
        except PyTango.DevFailed as e:
            value = sys.exc_info()[1]
            Qt.QMessageBox.warning(
                self, 
                "Error in Setting Server",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
            sys.exit(-1)
        except Exception as e:
            Qt.QMessageBox.warning(
                self, 
                "Error in Setting Server",
                str(e))
            sys.exit(-1)

        self.state.fetchSettings()

        settings = Qt.QSettings()

        self.userView = settings.value('Preferences/UserView', 'CheckBoxes')
        self.rowMax = int(settings.value('Preferences/RowMax', 20))


        ## user interface
        self.ui = Ui_Selector()
        self.preferences = Preferences(self.ui, self.state)
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
        
        self.restoreGeometry(
            settings.value("Selector/Geometry"))

        self.title = 'NeXus Component Selector'
        self.setDirty()



    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
        self.ui.buttonBox.setStandardButtons(
           Qt.QDialogButtonBox.Reset | Qt.QDialogButtonBox.Apply \
                | Qt.QDialogButtonBox.Close)

        flayout = Qt.QHBoxLayout(self.ui.timerButtonFrame)
        flayout.setContentsMargins(0,0,0,0)
        self.ui.timerAddPushButton = Qt.QPushButton("+") 
        self.ui.timerAddPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerAddPushButton)
        self.ui.timerDelPushButton = Qt.QPushButton("-")
        self.ui.timerDelPushButton.setMaximumWidth(30)
        flayout.addWidget(self.ui.timerDelPushButton)
    
        for tab in self.tabs:
            tab.reset()

    
        cid = self.ui.viewComboBox.findText(Qt.QString(self.userView))
        if cid >= 0:
            self.ui.viewComboBox.setCurrentIndex(cid) 
        self.ui.rowMaxSpinBox.setValue(self.rowMax)    
            
        self.connect(self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply), 
                     Qt.SIGNAL("pressed()"), self.__applyClicked)
        self.connect(self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset), 
                     Qt.SIGNAL("pressed()"), self.__resetClicked)

        self.connect(self.ui.cnfLoadPushButton, 
                     Qt.SIGNAL("pressed()"), self.cnfLoad)
        self.connect(self.ui.cnfSavePushButton, 
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
        if flag:
            self.setWindowTitle(self.title + ' **[NOT APPLIED]**' )
        else:
            self.setWindowTitle(self.title)       
        

    def __saveSettings(self):
        settings = Qt.QSettings()
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

                    
    def closeEvent(self, _):
        self.__saveSettings()

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
        self.state.fetchSettings()
        for tab in self.tabs:
            tab.reset()
        logger.debug("reset selector ended")

    def resetAll(self):
        logger.debug("reset ALL")
        self.state.updateControllers()
        self.reset()
        logger.debug("reset ENDED")
        
    def __resetClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).hide()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).show()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Reset).setFocus()
        self.resetAll()

    def cnfLoad(self):    
        filename = str(Qt.QFileDialog.getOpenFileName(
                self.ui.storage,
                "Load Configuration",        
                self.state.cnfFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("loading configuration from %s" % filename)
        if filename:
            self.state.load(filename)
            self.resetAll()
            self.setDirty()

    def cnfSave(self):
        filename = str(Qt.QFileDialog.getSaveFileName(
                self.ui.storage,
                "Save Configuration",
                self.state.cnfFile,
                "JSON files (*.json);;All files (*)"))
        logger.debug("saving configuration to %s" % filename)
        if filename:
            self.state.save(filename)
            self.resetAll()

    def __applyClicked(self):
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).hide()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).show()
        self.ui.buttonBox.button(Qt.QDialogButtonBox.Apply).setFocus()
        self.apply()


    def apply(self):
        try:
            self.state.updateMntGrp()
            self.resetAll()
            self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
            self.setDirty(False)
        except PyTango.DevFailed as e:
            value = sys.exc_info()[1]
            Qt.QMessageBox.warning(
                self, 
                "Error in updating Measurement Group",
                "%s" % str("\n".join(["%s " % (err.desc) for err in value])))
        except Exception as e:
            Qt.QMessageBox.warning(
                self, 
                "Error in updating Measurement Group",
                str(e))
