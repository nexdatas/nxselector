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
## \file CommandThread.py
# command thread

""" command thread """

import logging
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt


class CommandThread(Qt.QThread):
    def __init__(self, instance, commands, parent):
        super(CommandThread, self).__init__(parent)
        self.instance = instance
        self.commands = list(commands)

    def run(self):
        try:
            for cmd in self.commands:
                getattr(self.instance, cmd)()
        finally:
            self.emit(Qt.SIGNAL("finished"))
