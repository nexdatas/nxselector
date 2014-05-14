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
## \file Data.py
# automatic tab

""" automatic tab """


from PyQt4.QtCore import (
    SIGNAL)
from PyQt4.QtGui import (QHBoxLayout,
    QGroupBox, QGridLayout, QFrame, QWidgetItem)

from .Element import CPElement
from .ElementModel import ElementModel
from .Views import CheckerView
from .EdListDlg import EdListWg

import logging
logger = logging.getLogger(__name__)


## main window class
class Data(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state = None):
        self.ui = ui
        self.state = state
        self.layout = None
        self.form = None

    def createGUI(self):
        self.ui.data.hide()       

        if self.layout:
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
        else: 
            self.layout = QHBoxLayout(self.ui.data)


        self.form  = EdListWg(self.ui.data)
        self.form.record = self.state.datarecord
        self.form.available_names = self.state.clientRecords().values()
        self.form.createGUI()
#        gb = QGroupBox(self.ui.data)
#        gb.setTitle("Data")
#        self.layout.addWidget(gb)
#        self.layout.addWidget(self.form)
#        gb = QGroupBox(self.ui.data)
#        gb.setTitle("Data2")
#        self.layout.addWidget(gb)
        self.layout.addWidget(self.form)
#        self.form.show()
        self.ui.data.update()
        if self.ui.tabWidget.currentWidget() == self.ui.data:
            self.ui.data.show()
        self.ui.data.connect(self.form, SIGNAL("dirty"),self.__setDirty)


    def reset(self):
        self.createGUI()


    def __setDirty(self):
        self.ui.data.emit(SIGNAL("dirty"))
        
