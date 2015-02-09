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
## \file OrderDlg.py
# editable list dialog

"""  editable list dialog """

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .ui.ui_orderdlg import Ui_OrderDlg


import logging
logger = logging.getLogger(__name__)


class OrderDlg(Qt.QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None):
        super(OrderDlg, self).__init__(parent)
        self.ui = Ui_OrderDlg()
        self.dirty = False
        self.channels = []



    def __setDirty(self):
        self.dirty = True



    def createGUI(self):
        self.ui.setupUi(self)
        self.ui.closePushButton = self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close)

        self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close).hide()
        self.ui.upPushButton = self.ui.upDownButtonBox.addButton(
            "&Up", Qt.QDialogButtonBox.ActionRole)
        self.ui.downPushButton = self.ui.upDownButtonBox.addButton(
            "&Down", Qt.QDialogButtonBox.ActionRole)

        if self.channels:
            item = self.channels[0]
        else:
            item = None
        self.__populateList(item)
        self.connect(self.ui.upPushButton, Qt.SIGNAL("clicked()"),
                     self.__up)
        self.connect(self.ui.downPushButton, Qt.SIGNAL("clicked()"),
                     self.__down)

        self.connect(
            self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close),
            Qt.SIGNAL("clicked()"),
            self.accept)
        self.ui.closePushButton.show()
        self.connect(self, Qt.SIGNAL("dirty"), self.__setDirty)


    def __populateList(self, selectedChannel=None):
        selected = None
        self.ui.listWidget.clear()
        for ch in self.channels:
            item = Qt.QListWidgetItem(Qt.QString(ch))
            self.ui.listWidget.addItem(item)
            if selectedChannel is not None and selectedChannel == ch:
                selected = item
            if selected is not None:
                selected.setSelected(True)
                self.ui.listWidget.setCurrentItem(selected)

    def __currentName(self):
        name = None
        row = self.ui.listWidget.currentRow()
        if len(self.channels) > row and row >= 0:
            name = self.channels[row]
        return name

    def __up(self):
        name = self.__currentName()
        ni = self.channels.index(name)
        if ni > 0:
            self.channels[ni], self.channels[ni-1] = \
                self.channels[ni-1], self.channels[ni]  
            self.emit(Qt.SIGNAL("dirty"))
            self.__populateList(name)

    def __down(self):
        name = self.__currentName()
        ni = self.channels.index(name)
        if ni < len(self.channels) - 1:
            self.channels[ni], self.channels[ni+1] = \
                self.channels[ni+1], self.channels[ni]  
            self.emit(Qt.SIGNAL("dirty"))
            self.__populateList(name)
