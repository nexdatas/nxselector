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
## \file Storage.py
# storage tab 

""" storage tab """

import os
import PyTango
import json

import logging
logger = logging.getLogger(__name__)

from .Views import TableView, CheckerView, RadioView

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString)

## main window class
class Storage(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None):
        self.ui = ui
        self.state = state



    def connectSignals(self):
        self.ui.storage.disconnect(self.ui.fileScanDirLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
#        self.ui.storage.disconnect(self.ui.fileScanIDSpinBox,
#                                SIGNAL("valueChanged(int)"), self.apply)
        self.ui.storage.disconnect(self.ui.fileScanLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
                                # measurement group    

        self.ui.storage.disconnect(self.ui.mntTimerComboBox,
                                SIGNAL("currentIndexChanged(int)"), self.apply)
        self.ui.storage.disconnect(self.ui.mntGrpLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.disconnect(self.ui.mntServerLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        
        # device group    
        self.ui.storage.disconnect(self.ui.devWriterLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.disconnect(self.ui.devConfigLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        

        # dynamic component group
        self.ui.storage.disconnect(self.ui.dcEnableCheckBox,
                                SIGNAL("toggled(bool)"), self.apply)
        self.ui.storage.disconnect(self.ui.dcLinksCheckBox,
                                SIGNAL("toggled(bool)"), self.apply)
        self.ui.storage.disconnect(self.ui.dcPathLineEdit,
                                SIGNAL("editingFinished()"), self.apply)

        # others group
        self.ui.storage.disconnect(self.ui.othersEntryCheckBox,
                                SIGNAL("toggled(bool)"), self.apply)
        self.ui.storage.disconnect(self.ui.othersTimeZoneLineEdit,
                                SIGNAL("editingFinished()"), self.apply)

        self.ui.storage.connect(self.ui.fileScanDirLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
#        self.ui.storage.connect(self.ui.fileScanIDSpinBox,
#                                SIGNAL("valueChanged(int)"), self.apply)
        self.ui.storage.connect(self.ui.fileScanLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
                                # measurement group    

        self.ui.storage.connect(self.ui.mntTimerComboBox,
                                SIGNAL("currentIndexChanged(int)"), self.apply)
        self.ui.storage.connect(self.ui.mntGrpLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.connect(self.ui.mntServerLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        
        # device group    
        self.ui.storage.connect(self.ui.devWriterLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.connect(self.ui.devConfigLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
       

        # dynamic component group
        self.ui.storage.connect(self.ui.dcEnableCheckBox,
                                SIGNAL("clicked(bool)"), self.apply)
        self.ui.storage.connect(self.ui.dcLinksCheckBox,
                                SIGNAL("clicked(bool)"), self.apply)
        self.ui.storage.connect(self.ui.dcPathLineEdit,
                                SIGNAL("editingFinished()"), self.apply)

        # others group
        self.ui.storage.connect(self.ui.othersEntryCheckBox,
                                SIGNAL("clicked(bool)"), self.apply)
        self.ui.storage.connect(self.ui.othersTimeZoneLineEdit,
                                SIGNAL("editingFinished()"), self.apply)
        

    def reset(self):
        self.connectSignals()
        self.updateForm()


    def updateForm(self):
        print "MNT0", self.state.mntgrp
        # file group
        self.ui.fileScanDirLineEdit.setText(self.state.scanDir)
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
        self.ui.fileScanIDSpinBox.setEnabled(False)

        sfile = ""
        if self.state.scanFile:
            if isinstance(self.state.scanFile, (list,tuple)):
                sfile = ", ".join(self.state.scanFile)
            else:
                sfile = self.state.scanFile    
            self.ui.fileScanLineEdit.setText(sfile)

        print "MNT1", self.state.mntgrp
        # measurement group    
        self.ui.mntTimerComboBox.clear()
        print "MNT2", self.state.mntgrp
        self.ui.mntTimerComboBox.addItems([QString(tm) for tm in self.state.atlist])
        for tm in self.state.atlist:
            print "tm", tm
#            self.ui.mntTimerComboBox.addItem(QString(tm))
        print "MNT3", self.state.mntgrp
        cid = self.ui.mntTimerComboBox.findText(QString(self.state.timer))
        print "MNT4", self.state.mntgrp
        if cid < 0:
            cid = 0
        self.ui.mntTimerComboBox.setCurrentIndex(cid)

        print "MNT5", self.state.mntgrp
        self.ui.mntGrpLineEdit.setText(self.state.mntgrp)
        print "MNT", self.state.mntgrp
        self.ui.mntServerLineEdit.setText(self.state.macroServer)

        # device group    
        self.ui.devWriterLineEdit.setText(self.state.writerDevice)
        self.ui.devConfigLineEdit.setText(self.state.configDevice)


        # dynamic component group
        self.ui.dcEnableCheckBox.setChecked(self.state.dynamicComponents)
        self.ui.dcLinksCheckBox.setChecked(self.state.dynamicLinks)
        self.ui.dcPathLineEdit.setText(self.state.dynamicPath)

        # others group
        self.ui.othersEntryCheckBox.setChecked(self.state.appendEntry)
        self.ui.othersTimeZoneLineEdit.setText(self.state.timeZone)


    def apply(self):
        self.state.scanDir = str(self.ui.fileScanDirLineEdit.text())
#        self.state.scanID = int(self.ui.fileScanIDSpinBox.value())
        files = str(self.ui.fileScanLineEdit.text())
        self.state.scanFile = files.split()

        # measurement group    
        self.state.timer = str(self.ui.mntTimerComboBox.currentText())
        self.state.mntgrp = str(self.ui.mntGrpLineEdit.text())
        self.state.macroServer = str(self.ui.mntServerLineEdit.text())

        # device group    
        self.state.writerDevice = str(self.ui.devWriterLineEdit.text())
        self.state.configDevice = str(self.ui.devConfigLineEdit.text())

        # dynamic component group
        self.state.dynamicComponents = self.ui.dcEnableCheckBox.isChecked()
        self.state.dynamicLinks = self.ui.dcLinksCheckBox.isChecked()
        self.state.dynamicPath = str(self.ui.dcPathLineEdit.text())

        # others group
        self.state.appendEntry = self.ui.othersEntryCheckBox.isChecked()
        self.state.timeZone = str(self.ui.othersTimeZoneLineEdit.text())
        

        
