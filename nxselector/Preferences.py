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

from .Views import TableView, CheckerView, RadioView

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString)

from PyQt4.QtGui import (QMessageBox)
import PyTango

## main window class
class Preferences(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None):
        self.ui = ui
        self.state = state

        self.views = {"CheckBoxes":CheckerView, "Tables":TableView, "RadioButtons":RadioView}
        

    def connectSignals(self):
        self.ui.preferences.disconnect(self.ui.devSettingsLineEdit,
                                       SIGNAL("editingFinished()"), 
                                       self.on_devSettingsLineEdit_editingFinished)
        self.ui.preferences.connect(self.ui.devSettingsLineEdit,
                                    SIGNAL("editingFinished()"), 
                                    self.on_devSettingsLineEdit_editingFinished)
       
    def reset(self):
        if self.ui.viewComboBox.count() != len(self.views.keys()):
            self.ui.viewComboBox.clear()
            self.ui.viewComboBox.addItems(sorted(self.views.keys()))
        self.updateForm()
        self.connectSignals()

    def on_devSettingsLineEdit_editingFinished(self):
        server = str(self.ui.devSettingsLineEdit.text())
        if server != self.state.server or True:
            try:
                dp = PyTango.DeviceProxy(server)
                if dp.info().dev_class == 'NXSRecSettings':
                    self.state.server = str(server)
            except:
                self.reset()
            self.ui.preferences.emit(SIGNAL("serverChanged()"))

    def updateForm(self):
        self.ui.devSettingsLineEdit.setText(self.state.server)
            
            

    def apply(self):
        pass
