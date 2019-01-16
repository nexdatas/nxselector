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
# info about tango servers

"""  info about tango servers """

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


@UILoadable(with_ui='ui')
class InfoDlg(Qt.QDialog):
    """  info about tango servers """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = None

    def createGUI(self):
        """ creates GUI
        """
        if self.state:
            self.ui.writerLabel.setText(self.state.writerDevice)
            self.ui.configLabel.setText(self.state.configDevice)
            self.ui.doorLabel.setText(self.state.door)
            self.ui.selectorLabel.setText(str(
                self.state.server if self.state.server else 'module'))
