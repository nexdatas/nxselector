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
## \package nxselector nexdatas
## \file OrderDlg.py
# editable list dialog

"""  editable list dialog """

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable


import logging
logger = logging.getLogger(__name__)


@UILoadable(with_ui='ui')
class OrderDlg(Qt.QDialog):
    ## constructor
    # \param parent parent widget
    def __init__(self, parent=None): 
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        self.dirty = False
        self.channels = []
        self.selected = []
        self.onlyselected = False

    def __setDirty(self):
        self.dirty = True

    def createGUI(self):
        self.ui.closePushButton = self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close)

        self.ui.closeButtonBox.button(Qt.QDialogButtonBox.Close).hide()
        self.ui.upPushButton = self.ui.upDownButtonBox.addButton(
            "&Up", Qt.QDialogButtonBox.ActionRole)
        self.ui.downPushButton = self.ui.upDownButtonBox.addButton(
            "&Down", Qt.QDialogButtonBox.ActionRole)
        self.ui.selPushButton = self.ui.closeButtonBox.addButton(
            "&Only Selected", Qt.QDialogButtonBox.ActionRole)
        self.ui.selPushButton.setCheckable(True)
        self.ui.selPushButton.setChecked(self.onlyselected)

        if self.channels:
            item = self.channels[0]
        else:
            item = None
        self.selected = list(set(self.channels) & set(self.selected))

        self.__populateList(item)
        self.ui.upPushButton.clicked.connect(self.__up)
        self.ui.downPushButton.clicked.connect(self.__down)
        self.ui.selPushButton.clicked.connect(self.__setfilter)

        self.ui.closeButtonBox.button(
            Qt.QDialogButtonBox.Close).clicked.connect(self.accept)
        self.ui.closePushButton.show()

    def __populateList(self, selectedChannel=None):
        selected = None
        self.ui.listWidget.clear()
        for ch in self.channels:
            if self.onlyselected:
                if ch not in self.selected:
                    continue
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
        if not self.onlyselected:
            if len(self.channels) > row and row >= 0:
                name = self.channels[row]
        else:
            index = -1
            for i, channel in enumerate(self.channels):
                if channel in self.selected:
                    index += 1
                if row == index:
                    name = self.channels[i]
                    break
        return name

    @Qt.pyqtSlot()
    def __up(self):
        name = self.__currentName()
        if not name:
            return
        ni = self.channels.index(name)
        if ni > 0:
            nim1 = ni - 1
            if self.onlyselected:
                while nim1 and self.channels[nim1] not in self.selected:
                    nim1 -= 1
            self.channels[ni], self.channels[nim1] = \
                self.channels[nim1], self.channels[ni]
            self.__populateList(name)
            self.__setDirty()

    @Qt.pyqtSlot()
    def __down(self):
        name = self.__currentName()
        if not name:
            return
        ni = self.channels.index(name)
        if ni < len(self.channels) - 1:
            nip1 = ni + 1
            if self.onlyselected:
                while nip1 < len(self.channels) - 1 \
                        and self.channels[nip1] not in self.selected:
                    nip1 += 1
            self.channels[ni], self.channels[nip1] = \
                self.channels[nip1], self.channels[ni]
            self.__populateList(name)
            self.__setDirty()

    @Qt.pyqtSlot()
    def __setfilter(self):
        self.onlyselected = bool(self.ui.selPushButton.isChecked())
        name = self.__currentName()
        self.__populateList(name)
