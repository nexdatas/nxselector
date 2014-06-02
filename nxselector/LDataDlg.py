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
## \file LDataDlg.py
# editable data dialog

"""  editable data dialog """

import json

#from PyQt4.QtGui import ( QMessageBox,
#                          QDialog, QCompleter)
#from PyQt4.QtCore import (QString)
from taurus.external.qt import Qt

from .ui.ui_ldatadlg import Ui_LDataDlg

import logging
logger = logging.getLogger(__name__)

## main window class
class LDataDlg(Qt.QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(LDataDlg, self).__init__(parent)
        self.label = ''
        self.path = ''
        self.shape = None
        self.dtype = ''
        self.link = None
        self.available_names = None
        self.ui = Ui_LDataDlg()

    @classmethod    
    def __linkText(cls, value):
        if value == True:
            return "True"
        if value == False:
            return "False"
        return "Default"
        

    def createGUI(self):

        self.ui.setupUi(self) 
        self.ui.labelLineEdit.setText(Qt.QString(str(self.label)))
        self.ui.pathLineEdit.setText(Qt.QString(str(self.path)))
        if self.shape is None:
            shape = ''
        else:
            shape = self.shape
        self.ui.shapeLineEdit.setText(Qt.QString(str(shape)))
        self.ui.typeLineEdit.setText(Qt.QString(str(self.dtype)))
   
        cid = self.ui.linkComboBox.findText(Qt.QString(self.__linkText(self.link)))
        if cid < 0:
            cid = 0
        self.ui.linkComboBox.setCurrentIndex(cid) 

        if self.available_names:
            completer = Qt.QCompleter(self.available_names, self)
            self.ui.labelLineEdit.setCompleter(completer)

    def accept(self):
        link = str(self.ui.linkComboBox.currentText())
        if link == "True":
            self.link = True
        elif link == "False":
            self.link = False
        else:
            self.link = None

        self.label = unicode(self.ui.labelLineEdit.text())
        self.path = unicode(self.ui.pathLineEdit.text())
        self.dtype = unicode(self.ui.typeLineEdit.text())
        tshape = unicode(self.ui.shapeLineEdit.text())
        try:
            if not tshape:
                self.shape = None
            else:
                shape = json.load(tshape)
                assert isinstance(shape, list)
                self.shape = shape
        except:
            Qt.QMessageBox.warning(self, "Wrong Data", "Wrong structure of Shape" )
            self.ui.shapeLineEdit.setFocus()
            return
            
        self.dtype = unicode(self.ui.typeLineEdit.text())

           
        if not self.label:
            Qt.QMessageBox.warning(self, "Wrong Data", "Empty data label" )
            self.ui.labelLineEdit.setFocus()
            return

        QDialog.accept(self)
