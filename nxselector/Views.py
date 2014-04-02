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
## \file Views.py
# module with different table views

""" main window application dialog """

import os
import PyTango
import json

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtGui, QtCore

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant, SIGNAL, QString, QSignalMapper,
    SLOT)
from PyQt4.QtGui import (QTableView, QHeaderView, QWidget, QGridLayout, 
                         QCheckBox, QAbstractScrollArea, QPalette,
                         QAbstractItemView, QLabel, QFrame)



        
class TableView(QTableView):

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)        
        self.horizontalHeader().setVisible(False)        
        self.horizontalHeader().setStretchLastSection(True)        
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)




class CheckerView(QWidget):
#class CheckerView(QAbstractItemView):

    def __init__(self, parent=None):
        super(CheckerView, self).__init__(parent)
        self.model = None
#        self.layout = QtGui.QFormLayout(self)
        self.frame = QFrame(self)
        self.layout = QGridLayout(self.frame)
        self.widgets = []
        self.mapper = QSignalMapper(self.frame)
        self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                     self.checked)

    def checked(self, widget):
        print "checked", widget.text(), widget
        row = self.widgets.index(widget)
        
        ind = self.model.index(row, 1)
        value = QVariant(self.widgets[row].isChecked())
        self.model.setData(ind, value, Qt.CheckStateRole)
            
    def setModel(self, model):
        self.model = model
        self.connect(self.model,
                     SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.updateState)
        self.connect(self.model,
                     SIGNAL("modelReset()"),
                     self.updateState)
        self.updateState()

    def reset(self):
        print "RESET", [str(w.text()) for w in self.widgets]   
        self.frame = QFrame(self)
        self.layout = QGridLayout(self.frame)
#        self.widgets = []
#        self.mapper = QSignalMapper(self.frame)
#        self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
#                     self.checked)
        self.updateState(new = False)
        print "END RESET"

    def updateState(self, new = False):
        if not self.model is None:
            print "UPDATE", [str(w.text()) for w in self.widgets]   
#        self.scrollArea = QtGui.QScrollArea(self)
#        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
#        self.scrollArea.setWidgetResizable(True)
#        self.scrollArea.setBackgroundRole(QPalette.Dark)
#        self.scrollAreaWidgetContents = QtGui.QWidget()
#        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 380, 280))
#        self.formLayout = QtGui.QFormLayout(self.scrollAreaWidgetContents)

#        self.checkLayout = QtGui.QGridLayout()

#        self.pushButton = QtGui.QPushButton(self.scrollAreaWidgetContents)
#        self.checkLayout.addWidget(self.pushButton, 0, 0, 1, 1)
#        self.pushButton_2 = QtGui.QPushButton(self.scrollAreaWidgetContents)
#        self.checkLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
            for row in range(self.model.rowCount()):
                print "A1"
                ind = self.model.index(row,1)
                print "A2"
                name = self.model.data(ind, role = Qt.DisplayRole)
                print "A3"
                status = self.model.data(ind, role = Qt.CheckStateRole)
                print "A4"
                flags = self.model.flags(ind)
                print "A5"
                if row < len(self.widgets):
                    cb = self.widgets[row]
                    print "OLD"
                else:
                    cb = QCheckBox()
                    print "NEW", row
                cb.setEnabled(bool(Qt.ItemIsEnabled & flags))
                if name:
                    cb.setText(str(name.toString()))
                if status is not None:    
                    cb.setCheckState(status)
                if row >= len(self.widgets):
                    self.layout.addWidget(cb, row, 0, 1, 1)
                    self.widgets.append(cb)
                    print "APPENDING", cb.text(), cb
                    self.connect(cb, SIGNAL("clicked()"),
                                 self.mapper, SLOT("map()"))
                    self.mapper.setMapping(cb, cb)
                print "END LOOP"    
#        self.formLayout.setLayout(0, QtGui.QFormLayout.LabelRole, self.checkLayout)
#        self.layout.setLayout(0, QtGui.QFormLayout.LabelRole, self.checkLayout)

#        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
#        self.layout.addWidget(self.scrollArea, 0, 0, 1, 1)
            
#        self.update()
#        self.updateGeometry()
