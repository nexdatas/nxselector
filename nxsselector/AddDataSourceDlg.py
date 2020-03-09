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
# editable list of component groups

"""  editable list dialog """

import sys

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable
# from taurus.qt.qtgui.panel import TaurusModelChooser
from taurus.qt.qtgui.panel import TaurusModelSelectorTree
from taurus.core.taurusbasetypes import TaurusElementType
import taurus

# from .Views import OneTableView
# from .Element import GElement, CP, DS
# from .ElementModel import ElementModel

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


if sys.version_info > (3,):
    unicode = str


class SourceLineEdit(Qt.QLineEdit):

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QLineEdit.__init__(self, parent)
        self.setAcceptDrops(True)

    def dropEvent(self, event):
        """ set the attribute source from the drop event

        :param event: drop event
        :type event: :class:`Qt.QEvent`
        """
        if event.mimeData().hasUrls():
            # urlcount = len(event.mimeData().urls())
            url = event.mimeData().urls()[0]
            source = str(url.toString())
            if source.startswith("tango://"):
                source = source[8:]
            self.setText(source)
            event.accept()


@UILoadable(with_ui='ui')
class AddDataSourceDlg(Qt.QDialog):
    """  editable other device list dialog
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        #: (:obj:`str`) datasource name
        self.name = ""
        #: (:obj:`str`) full name of tango device attribute
        self.source = ""
        #: (:obj:`list` <:obj:`str`>) existing datasources
        self.datasources = []
        #: (:obj:`str`) group title
        self.title = "Create DataSource"
        #: (:obj:`list` <:obj:`str`>) forbidden name characters
        self.__chars = ["/", ":", "#", "->"]

    def createGUI(self):
        """ creates GUI
        """
        self.setWindowTitle(self.title)
        try:
            host = taurus.Factory('tango').getAuthority().getFullName()
        except Exception:
            try:
                host = taurus.Factory('tango').getDatabase().getFullName()
            except Exception:
                host = None

        self.ui.tree = TaurusModelSelectorTree(
            selectables=[TaurusElementType.Attribute],
            buttonsPos=Qt.Qt.BottomToolBarArea)
        self.ui.tree.setModel(host)
        self.ui.tree.treeView().setSelectionMode(
            Qt.QAbstractItemView.SingleSelection)
        self.ui.tree._toolbar.hide()
        self.ui.sourceLineEdit = SourceLineEdit(self)
        self.ui.sourceLineEdit.setToolTip(
            "Drop an attribute from the above tree")
        if host and host.startswith("tango://"):
            host = host[8:]
        self.ui.hostLineEdit.setText(str(host or ""))
        gridLayout = Qt.QGridLayout(self.ui.widget)
        gridLayout.addWidget(self.ui.tree, 0, 0, 1, 1)
        self.ui.gridLayout.addWidget(self.ui.sourceLineEdit, 1, 1, 2, 2)
        self.ui.hostLineEdit.editingFinished.connect(self.__updatehostname)

    @Qt.pyqtSlot()
    def __updatehostname(self):
        """ update the tango host name
        """
        host = str(self.ui.hostLineEdit.text())
        if ":" not in host:
            host = host + ":10000"
            self.ui.hostLineEdit.setText(host)
        self.ui.tree.setModel("tango://%s" % host)

    def accept(self):
        """ updates class variables with the form content
        """
        self.name = unicode(self.ui.nameLineEdit.text())
        self.source = unicode(self.ui.sourceLineEdit.text())

        if not self.name:
            Qt.QMessageBox.warning(
                self, "Wrong form input", "Empty datasource name")
            self.ui.nameLineEdit.setFocus()
            return

        name = self.name
        for ch in self.__chars:
            if ch in name:
                name = name.replace(ch, "_")
        if self.name != name:
            self.ui.nameLineEdit.setText(name)
            self.name = name
            Qt.QMessageBox.warning(
                self, "Wrong form input",
                "Datasource name cannot contain any of '%s'" %
                "', '".join(self.__chars))
            self.ui.nameLineEdit.setFocus()
            return

        if self.name in self.datasources:
            Qt.QMessageBox.warning(
                self, "Wrong form input",
                "DataSource %s already exists" % self.name)
            self.ui.nameLineEdit.setFocus()
            return

        if not self.source:
            Qt.QMessageBox.warning(
                self, "Wrong form input", "Empty attribute name")
            self.ui.sourceLineEdit.setFocus()
            return

        Qt.QDialog.accept(self)
