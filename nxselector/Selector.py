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

import os

from PyQt4.QtCore import (
    SIGNAL, QSettings, Qt, QVariant)
from PyQt4.QtGui import (QHBoxLayout,QVBoxLayout,
    QDialog, QGroupBox,QGridLayout,QSpacerItem,QSizePolicy,
    QMessageBox, QIcon, QTableView,
    QLabel, QFrame)

from .ui.ui_selector import Ui_Selector

import logging
logger = logging.getLogger(__name__)


## main window class
class Selector(QDialog):

    ## constructor
    # \param parent parent widget
    def __init__(self, server=None, parent=None):
        super(Selector, self).__init__(parent)
        logger.debug("PARAMETERS: %s %s %s %s", 
                     server, parent)


        ## user interface
        self.ui = Ui_Selector()
        

        settings = QSettings()

        self.createGUI()            

        self.restoreGeometry(
            settings.value("Selector/Geometry").toByteArray())

#        status = self.createStatusBar()        
#        status.showMessage("Ready", 5000)

#        self.setWindowTitle("NXS Component Designer")

    ##  creates GUI
    # \brief It create dialogs for the main window application
    def createGUI(self):
        self.ui.setupUi(self)
        layout = QHBoxLayout(self.ui.selectable)
        
        ## frames/columns/groups
        frames =[[["Counters1", "Counters2"],["VCounters"]],[[ "MCAs","SCAs" ]],[[ "Misc" ]]]
        
        self.views =[]
        for frame in frames:


            mframe = QFrame(self.ui.selectable)
            mframe.setFrameShape(QFrame.StyledPanel)
            mframe.setFrameShadow(QFrame.Raised)
            layout_columns = QHBoxLayout(mframe)

            for column in frame: 
                layout_groups = QVBoxLayout()

                for group in column:
                    mgroup = QGroupBox(mframe)
                    mgroup.setTitle(group)
                    layout_auto = QGridLayout(mgroup)
                    mview = QTableView(mgroup)

                    layout_auto.addWidget(mview,0,0,1,1)
                    layout_groups.addWidget(mgroup)

                    self.views.append(mview)

                layout_columns.addLayout(layout_groups)

            layout.addWidget(mframe)



        
        

    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue(
            "Selector/Geometry",
            QVariant(self.saveGeometry()))
