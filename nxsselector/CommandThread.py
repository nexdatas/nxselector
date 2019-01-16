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
# command thread

""" command thread """

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt


class CommandThread(Qt.QThread):
    """ thread which executes a list of commands
    """
    #: (:class:`taurus.qt.Qt.pyqtSignal`) finisched signal
    finished = Qt.pyqtSignal()

    def __init__(self, instance, commands, parent):
        """ thread contructor

        :param instance: command instance
        :type instance: :obj:`instanceobj` or :obj:`type`
        :param commands: a list of commands
        :type commands: :obj:`list` <:obj:`str`>
        :param parent: thread parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """

        Qt.QThread.__init__(self, parent)
        #: (:obj:`instanceobj` or :obj:`type`) command instance
        self.instance = instance
        #: (:obj:`list` <:obj:`str`>) a list of commands
        self.commands = list(commands)
        #: (:obj:`Exception`) error thrown by the executed command
        self.error = None

    def run(self):
        """ run thread method
        """
        try:
            for cmd in self.commands:
                getattr(self.instance, cmd)()
        except Exception as e:
            self.error = e
        finally:
            self.finished.emit()
