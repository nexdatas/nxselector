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
# error message box

""" error message box """

import sys
import logging
import PyTango
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt


class MessageBox(Qt.QObject):
    """ error message box """

    def __init__(self, parent):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QObject.__init__(self, parent)

    @classmethod
    def getText(cls, default, error=None):
        """ provides error message text fro sys.exc_info()

        :param default: default message test
        :type default: :obj:`str`
        :param error: exception to describe
        :type error: :obj:`Exception`
        :returns: exception message
        :rtype: :obj:`str`
        """
        if error is None:
            error = sys.exc_info()[1]
        text = default
        try:
            if isinstance(error, PyTango.DevFailed):
                if hasattr(error, "args"):
                    text = str(
                        "\n".join(["%s " % (err.desc) for err in error.args]))
                else:
                    text = str(
                        "\n".join(["%s " % (err.desc) for err in error]))
            else:
                text = str(error)
        except Exception:
            pass
        return text

    @classmethod
    def warning(cls, parent, title, text, detailedText=None, icon=None):
        """ creates warning messagebox

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        :param title: message box title
        :type title: :obj:`str`
        :param text: message box text
        :type text: :obj:`str`
        :param detailedText: message box detailed text
        :type detailedText: :obj:`str`
        :param icon: message box icon
        :type icon:  :class:`taurus.qt.Qt.QIcon`
        """
        msgBox = Qt.QMessageBox(parent)
        msgBox.setText(title)
        msgBox.setInformativeText(text)
        if detailedText is not None:
            msgBox.setDetailedText(detailedText)
        if icon is None:
            icon = Qt.QMessageBox.Warning
        msgBox.setIcon(icon)
        spacer = Qt.QSpacerItem(800, 0, Qt.QSizePolicy.Minimum,
                                Qt.QSizePolicy.Expanding)
        layout = msgBox.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())
        msgBox.exec_()
        msgBox.setParent(None)
