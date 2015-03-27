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
## \package nxselector nexdatas
## \file Data.py
# automatic tab

""" automatic tab """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .EdListDlg import EdListWg

import logging
logger = logging.getLogger(__name__)


## main window class
class Data(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None, simpleMode=False):
        self.ui = ui
        self.state = state
        self.layout = None
        self.form = None
        self.__simpleMode = simpleMode
        self.disable = ["beamtime_id", "title"]

    def createGUI(self):
        self.ui.data.hide()

        if self.layout:
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, Qt.QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
        else:
            self.layout = Qt.QHBoxLayout(self.ui.data)

        self.form = EdListWg(self.ui.data)
        if self.__simpleMode:
            self.form.disable = self.disable
        self.form.record = self.state.datarecord
        names = self.state.clientRecords()
        logger.debug("NAMES: %s " % names)
        self.form.available_names = names
        self.form.createGUI()
        self.layout.addWidget(self.form)
        self.ui.data.update()
        if self.ui.tabWidget.currentWidget() == self.ui.data:
            self.ui.data.show()
        self.ui.data.connect(self.form, Qt.SIGNAL("dirty"), self.__setDirty)

    def reset(self):
        self.createGUI()

    def __setDirty(self):
        self.ui.data.emit(Qt.SIGNAL("dirty"))
