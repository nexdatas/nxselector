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
# editable data dialog

"""  editable data dialog """

import json
import logging
import sys

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

from .MessageBox import MessageBox
from. ElementModel import PROPTEXT


#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

SYNCHTEXT = PROPTEXT["synchronization"]

if sys.version_info > (3,):
    unicode = str


@UILoadable(with_ui='ui')
class LDataDlg(Qt.QDialog):
    """  editable data dialog """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QDialog.__init__(self, parent)
        self.loadUi()
        #: (:obj:`str`) device label
        self.label = ''
        #: (:obj:`str`) nexus path
        self.path = ''
        #: (:obj:`str`) shape in JSON list
        self.shape = None
        #: (:obj:`str`) nexus data type
        self.dtype = ''
        #: (:obj:`bool`) if nxdata link should be created
        self.link = None
        #: (:obj:`bool`) if ds switched to CanFail mode
        self.canfail = None
        #: (:obj:`list` <:obj:`str` > ) available variable names
        self.available_names = None
        #: (:obj:`list` <:obj:`str` > ) special variable names
        self.special = ["shape", "data_type", "nexus_path", "canfail", "link"]
        #: (:obj:`dict` <:obj:`str` , :obj:`str` or :obj:`unicode`> ) \
        #:     (name, value) variable dictionary
        self.variables = {}
        #: (:obj:`dict` <:obj:`str` , :class:`taurus.qt.Qt.QLabel`> ) \
        #:     (name, qlabel) variable dictionary
        self.names = {}
        #: (:obj:`dict` <:obj:`str` , :class:`taurus.qt.Qt.QWidget`> ) \
        #:     (name, qwidget) variable dictionary
        self.widgets = {}
        #: (:obj:`list` <:obj:`str` > ) special variable names
        self.hidden = ["synchronization", "synchronizer",
                       "entryname", "serialno"]
        #: (:obj:`list` <:obj:`str` > ) special variable names
        self.extra = []
        #: (:obj:`list` <:obj:`str` > ) synchronizers
        self.synchronizers = []

    @classmethod
    def __linkText(cls, value):
        """ converts link value to string, i.e. True, False or Default

        :param value: link value
        :type value: :obj:`bool` or `None`
        :returns: True, False or Default
        :rtype: :obj:`str`
        """
        if isinstance(value, bool):
            if value is True:
                return "True"
            if value is False:
                return "False"
        return "Default"

    @classmethod
    def __canfailText(cls, value):
        """ converts canfail value to string, i.e. True, Default

        :param value: canfail value
        :type value: :obj:`bool` or `None`
        :returns: True, False or Default
        :rtype: :obj:`str`
        """
        if isinstance(value, bool):
            if value is True:
                return "True"
        return "Default"

    def createGUI(self):
        """ creates GUI
        """
        self.ui.synchronizationComboBox.hide()
        self.ui.synchronizationLabel.hide()
        self.ui.synchronizerComboBox.hide()
        self.ui.synchronizerLabel.hide()
        self.ui.labelLineEdit.setText(str(str(self.label or "")))
        self.ui.pathLineEdit.setText(str(str(self.path or "")))
        if self.shape is None:
            shape = ''
        else:
            shape = self.shape
        self.ui.shapeLineEdit.setText(
            str(str(shape)))
        self.ui.typeLineEdit.setText(str(str(self.dtype or "")))

        cid = self.ui.linkComboBox.findText(
            str(self.__linkText(self.link)))
        if cid < 0:
            cid = 0
        self.ui.linkComboBox.setCurrentIndex(cid)

        cid = self.ui.canfailComboBox.findText(
            str(self.__canfailText(self.canfail)))
        if cid < 0:
            cid = 0
        self.ui.canfailComboBox.setCurrentIndex(cid)

        if self.available_names:
            completer = Qt.QCompleter(self.available_names, self)
            self.ui.labelLineEdit.setCompleter(completer)

        if self.variables:
            self.addGrid()
        self.adjustSize()

    def addGrid(self):
        """ adds from grid
        """
        index = 0
        for nm, val in self.variables.items():
            if not nm.startswith("__"):
                if (nm not in self.extra and nm not in self.hidden) or \
                   (val and nm not in self.extra and nm in self.hidden):
                    self.names[nm] = Qt.QLabel(self.ui.varFrame)
                    self.names[nm].setText(str(str(nm)))
                    self.ui.varGridLayout.addWidget(
                        self.names[nm], index, 0, 1, 1)
                    self.widgets[nm] = Qt.QLineEdit(self.ui.varFrame)
                    if val is not None:
                        self.widgets[nm].setText(str(str(val or "")))
                    self.ui.varGridLayout.addWidget(
                        self.widgets[nm], index, 1, 1, 1)
                    index += 1

    def addVariables(self, variables):
        """ adds  variables

        :param variables: (name, value) variable dictionary
        :type variables: :obj:`dict` <:obj:`str`, :obj:`str` or :obj:`unicode`>
        """
        leftchannels = False
        for sp in self.special:
            if sp in variables.keys():
                leftchannels = True
        if not leftchannels:
            self.ui.channelFrame.hide()
        for vr, val in variables.items():
            if vr not in self.special:
                self.variables[vr] = val

    def accept(self):
        """ updates class variables with the form content
        """
        link = str(self.ui.linkComboBox.currentText())
        if link == "True":
            self.link = True
        elif link == "False":
            self.link = False
        else:
            self.link = None

        canfail = str(self.ui.canfailComboBox.currentText())
        if canfail == "True":
            self.canfail = True
        else:
            self.canfail = None

        self.label = unicode(self.ui.labelLineEdit.text())
        self.path = unicode(self.ui.pathLineEdit.text())
        self.dtype = unicode(self.ui.typeLineEdit.text())
        tshape = unicode(self.ui.shapeLineEdit.text()).replace("None", "null")
        try:
            if not tshape:
                self.shape = None
            else:
                shape = json.loads(tshape)
                if not isinstance(shape, list):
                    raise Exception("shape is not a list")
                self.shape = shape
        except Exception:
            import traceback
            value = traceback.format_exc()
            text = MessageBox.getText("Wrong structure of Shape")
            MessageBox.warning(
                self,
                "NXSelector: Wrong Data",
                text, str(value))
            self.ui.shapeLineEdit.setFocus()
            return

        for nm, wg in self.widgets.items():
            if nm not in self.extra:
                self.variables[nm] = unicode(wg.text()) or None

        if not self.label:
            Qt.QMessageBox.warning(self, "Wrong Data", "Empty data label")
            self.ui.labelLineEdit.setFocus()
            return

        Qt.QDialog.accept(self)


class LExDataDlg(LDataDlg):
    """  extension of editable data dialog """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        LDataDlg.__init__(self, parent)
        #: (:obj:`list` <:obj:`str` > ) special variable names
        self.extra = ["synchronization", "synchronizer"]

    def createGUI(self):
        """ creates GUI
        """
        LDataDlg.createGUI(self)
        self.ui.synchronizationComboBox.show()
        self.ui.synchronizationLabel.show()
        self.ui.synchronizerComboBox.show()
        self.ui.synchronizerLabel.show()

        if self.variables and "synchronization" in self.variables:
            synch = int(self.variables["synchronization"] or 0)
        else:
            synch = 0
        cid = self.ui.synchronizationComboBox.findText(
            str(SYNCHTEXT[synch]))
        if cid < 0:
            cid = 0
        self.ui.synchronizationComboBox.setCurrentIndex(cid)

        if self.variables and "synchronizer" in self.variables:
            val = self.variables["synchronizer"] or "software"
        else:
            val = "software"

        self.ui.synchronizerComboBox.clear()
        self.ui.synchronizerComboBox.addItem("software")
        for sch in self.synchronizers:
            self.ui.synchronizerComboBox.addItem(sch)

        cid = self.ui.synchronizerComboBox.findText(
            str(str(val)))
        if cid < 0:
            cid = 0
        self.ui.synchronizerComboBox.setCurrentIndex(cid)

#        if val is not None:
#            self.ui.synchronizerLineEdit.setText(
#                str(str(val or "")))
        self.adjustSize()

    def accept(self):
        """ updates class variables with the form content
        """

        textsynch = str(self.ui.synchronizationComboBox.currentText())
        synch = SYNCHTEXT.index(textsynch) \
            if textsynch in SYNCHTEXT else None
        if synch or "synchronization" in self.variables:
            self.variables["synchronization"] = synch

        syncher = unicode(self.ui.synchronizerComboBox.currentText())
        if syncher != "software" or "synchronizer" in self.variables:
            self.variables["synchronizer"] = syncher

        LDataDlg.accept(self)
