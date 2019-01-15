#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# user data tab

""" user data tab """


try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from .EdListDlg import EdListWg


import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Data(Qt.QObject):
    """ User data tab widget
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, ui, state=None, simpleMode=False):
        """ constructor

        :param ui: ui instance
        :type ui: :class:`taurus.qt.qtgui.util.ui.__UI`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        :param simpleMode: if simple display mode
        :type simpleMode: :obj:`bool`
        """
        Qt.QObject.__init__(self)
        #: (:class:`taurus.qt.qtgui.util.ui.__UI`) ui instance
        self.ui = ui
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = state
        #: (:class:`taurus.qt.Qt.QLayout`)
        self.glayout = None
        #: (:obj:`bool`) if simple view mode
        self.__simpleMode = simpleMode
        #: (:class:`nxsselector.EdListWg.EdListWg`) table editing widget
        self.form = EdListWg(self.ui.data)

    def createGUI(self):
        """ creates widget GUI
        """
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
        """ recreates widget GUI
        """
        self.createGUI()

    @Qt.pyqtSlot()
    def __setDirty(self):
        """ emits the `dirty` signal
        """
        self.dirty.emit()
