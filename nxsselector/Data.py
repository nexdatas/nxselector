#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsselector nexdatas
## \file Data.py
# user data tab

""" user data tab """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .EdListDlg import EdListWg
#from .DynamicTools import DynamicTools


import logging
logger = logging.getLogger(__name__)


## main window class
class Data(Qt.QObject):

    dirty = Qt.pyqtSignal()

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None, simpleMode=False):
        Qt.QObject.__init__(self)
        self.ui = ui
        self.state = state
        self.glayout = None
        self.__simpleMode = simpleMode
        self.form = EdListWg(self.ui.data)

    def createGUI(self):
        self.ui.data.hide()

        if self.glayout:
            child = self.glayout.takeAt(0)
            while child:
                self.glayout.removeItem(child)
                if isinstance(child, Qt.QWidgetItem):
                    self.glayout.removeWidget(child.widget())
                child = self.glayout.takeAt(0)
            self.form.dirty.disconnect(self.__setDirty)
        else:
            self.glayout = Qt.QHBoxLayout(self.ui.data)

        if self.form:
            self.form.setParent(None)

        if self.__simpleMode:
            self.form.disable = self.state.admindata
        self.form.record = self.state.datarecord
        names = self.state.clientRecords()
        logger.debug("NAMES: %s " % names)
        self.form.available_names = names
        self.form.createGUI()
        self.glayout.addWidget(self.form)
        self.ui.data.update()
        if self.ui.tabWidget.currentWidget() == self.ui.data:
            self.ui.data.show()
        self.form.dirty.connect(self.__setDirty)

    def reset(self):
        self.createGUI()

    @Qt.pyqtSlot()
    def __setDirty(self):
        self.dirty.emit()