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
# storage tab

""" storage tab """

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt
from .EdListDlg import EdListDlg
from .GroupsDlg import GroupsDlg
from .InfoDlg import InfoDlg
from .OrderDlg import OrderDlg
from .PropertiesDlg import PropertiesDlg
from .MessageBox import MessageBox

import logging
import json
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Storage(Qt.QObject):
    """ storage tab """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) resetviews signal
    resetViews = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) resetall signal
    resetAll = Qt.pyqtSignal()
    #: (:class:`taurus.qt.Qt.pyqtSignal`) updategroups signal
    updateGroups = Qt.pyqtSignal()

    def __init__(self, ui, state=None, simplemode=False):
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
        #: (:class:`taurus.qt.Qt.QHBoxLayout`) the main tab layout
        self.__layout = None
        #: (:obj:`list` <:class:`taurus.qt.Qt.QHBoxLayout`>) timer widget list
        self.__tWidgets = []
        #: (:obj:`bool`) only selected flag
        self.__onlyselected = False
        #: (:obj:`bool`) simple mode
        self.__simplemode = simplemode
        #: (:obj:`str`) module label
        self.__moduleLabel = 'module'
        self.connectSignals()
        #: (:obj:`bool`) connected flag
        self.__connected = True

    def connectTimerButtons(self):
        """ connects timer signals
        """
        self.ui.timerDelPushButton.clicked.connect(self.__delTimer)
        self.ui.timerAddPushButton.clicked.connect(self.__addTimer)

    def disconnectSignals(self):
        """ disconnects all tab signals
        """
        logger.debug("disconnect signals")
        if self.__connected:
            self.__connected = False
            self.ui.fileScanDirToolButton.pressed.disconnect(self.__setDir)
            self.ui.fileScanDirLineEdit.editingFinished.disconnect(
                self.__dirChanged)
            self.ui.fileScanLineEdit.editingFinished.disconnect(
                self.__fileChanged)
            self.ui.fileScanDirLineEdit.textEdited.disconnect(
                self.__dirty)
            self.ui.fileScanLineEdit.textEdited.disconnect(
                self.__dirty)
            # measurement group

            self.ui.mntTimerComboBox.currentIndexChanged.disconnect(self.apply)
            for cb in self.__tWidgets:
                cb.currentIndexChanged.disconnect(self.apply)

            if hasattr(self.ui, "timerDelPushButton"):
                self.ui.timerDelPushButton.clicked.disconnect(self.__delTimer)
                self.ui.timerAddPushButton.clicked.disconnect(self.__addTimer)
            self.ui.mntGrpToolButton.pressed.disconnect(self.__mntgrp_deleted)
            self.ui.mntGrpComboBox.currentIndexChanged.disconnect(
                self.__mntgrp_changed)
            self.ui.mntGrpComboBox.lineEdit().editingFinished.disconnect(
                self.__mntgrp_edited)
            self.ui.mntServerLineEdit.editingFinished.disconnect(self.apply)
            self.ui.mntGrpComboBox.lineEdit().textEdited.disconnect(
                self.__dirty)
            self.ui.mntServerLineEdit.textEdited.disconnect(self.__dirty)

            # device group
            self.ui.devWriterLineEdit.editingFinished.disconnect(self.apply)
            self.ui.devConfigLineEdit.editingFinished.disconnect(self.apply)
            self.ui.devWriterLineEdit.textEdited.disconnect(self.__dirty)
            self.ui.devConfigLineEdit.textEdited.disconnect(self.__dirty)

            # dynamic component group
            self.ui.dcLinksCheckBox.clicked.disconnect(self.apply)
            self.ui.dcPathLineEdit.editingFinished.disconnect(self.apply)
            self.ui.dcPathLineEdit.textEdited.disconnect(self.__dirty)

            # others group
            self.ui.othersEntryCheckBox.clicked.disconnect(self.apply)
            self.ui.devConfigPushButton.clicked.disconnect(self.__variables)
            self.ui.propPushButton.clicked.disconnect(self.__props)
            self.ui.labelsPushButton.clicked.disconnect(self.__labels)
            self.ui.orderToolButton.clicked.disconnect(self.__order)

            self.ui.groupsPushButton.clicked.disconnect(self.__groups)
            self.ui.errorsPushButton.clicked.disconnect(self.__errors)
            self.ui.infoPushButton.clicked.disconnect(self.__info)
            logger.debug("disconnect signals END")

    def connectSignals(self):
        """ connects all tab signals
        """
        logger.debug("connect signals")
        self.__connected = True
        self.ui.fileScanDirToolButton.pressed.connect(self.__setDir)
        self.ui.fileScanDirLineEdit.editingFinished.connect(self.__dirChanged)
        self.ui.fileScanLineEdit.editingFinished.connect(self.__fileChanged)
        self.ui.fileScanDirLineEdit.textEdited.connect(self.__dirty)
        self.ui.fileScanLineEdit.textEdited.connect(self.__dirty)
        # measurement group

        self.ui.mntTimerComboBox.currentIndexChanged.connect(self.apply)
        for cb in self.__tWidgets:
            cb.currentIndexChanged.connect(self.apply)

        if hasattr(self.ui, "timerDelPushButton"):
            self.ui.timerDelPushButton.clicked.connect(self.__delTimer)
            self.ui.timerAddPushButton.clicked.connect(self.__addTimer)
        self.ui.mntGrpToolButton.pressed.connect(self.__mntgrp_deleted)
        self.ui.mntGrpComboBox.currentIndexChanged.connect(
            self.__mntgrp_changed)
        self.ui.mntGrpComboBox.lineEdit().editingFinished.connect(
            self.__mntgrp_edited)
        self.ui.mntServerLineEdit.editingFinished.connect(self.apply)
        self.ui.mntGrpComboBox.lineEdit().textEdited.connect(
            self.__dirty)
        self.ui.mntServerLineEdit.textEdited.connect(self.__dirty)

        # device group
        self.ui.devWriterLineEdit.editingFinished.connect(self.apply)
        self.ui.devConfigLineEdit.editingFinished.connect(self.apply)
        self.ui.devWriterLineEdit.textEdited.connect(self.__dirty)
        self.ui.devConfigLineEdit.textEdited.connect(self.__dirty)

        # dynamic component group
        self.ui.dcLinksCheckBox.clicked.connect(self.apply)
        self.ui.dcPathLineEdit.editingFinished.connect(self.apply)
        self.ui.dcPathLineEdit.textEdited.connect(self.__dirty)

        # others group
        self.ui.othersEntryCheckBox.clicked.connect(self.apply)
        self.ui.devConfigPushButton.clicked.connect(self.__variables)
        self.ui.propPushButton.clicked.connect(self.__props)
        self.ui.labelsPushButton.clicked.connect(self.__labels)
        self.ui.orderToolButton.clicked.connect(self.__order)

        self.ui.groupsPushButton.clicked.connect(self.__groups)
        self.ui.errorsPushButton.clicked.connect(self.__errors)
        self.ui.infoPushButton.clicked.connect(self.__info)
        logger.debug("connect signals END")

    def updateMntGrpComboBox(self):
        """ updates a value of measurement group combo box
        """
        self.disconnectSignals()
        try:
            self.ui.mntGrpComboBox.clear()
            for mg in self.state.avmglist:
                self.ui.mntGrpComboBox.addItem(mg)
            if self.state.mntgrp not in self.state.avmglist:
                self.ui.mntGrpComboBox.addItem(self.state.mntgrp)
            ind = self.ui.mntGrpComboBox.findText(self.state.mntgrp)
            self.ui.mntGrpComboBox.setCurrentIndex(ind)
        finally:
            self.connectSignals()

    @Qt.pyqtSlot()
    def __variables(self):
        """ changes configuration variables
        """
        dform = EdListDlg(self.ui.storage)
        dform.widget.record = self.state.configvars
        dform.simple = True
        dform.available_names = self.state.vrcpdict.keys()
        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.resetViews.emit()
            self.dirty.emit()

    @Qt.pyqtSlot()
    def __labels(self):
        """ changes component labels
        """
        dform = EdListDlg(self.ui.storage)
        dform.widget.record = self.state.labels
        dform.simple = True
        dform.headers = ["Element", "Label"]
        dform.available_names = list(
            set(self.state.avcplist) | set(self.state.avdslist))

        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.resetViews.emit()

    @Qt.pyqtSlot()
    def __order(self):
        """ changes the channel order
        """
        dform = OrderDlg(self.ui.storage)
        dform.channels = list(self.state.orderedchannels)
        dform.selected = list(
            set([cp for cp in self.state.cpgroup.keys()
                 if self.state.cpgroup[cp]])
            | set([ds for ds in self.state.dsgroup.keys()
                   if self.state.dsgroup[ds]])
            | set(self.state.timers or []))
        dform.onlyselected = self.__onlyselected

        dform.createGUI()
        dform.exec_()
        self.__onlyselected = dform.onlyselected
        if dform.dirty:
            self.state.orderedchannels = list(dform.channels)
            self.dirty.emit()

    @Qt.pyqtSlot()
    def __info(self):
        """ shows the server info
        """
        dform = InfoDlg(self.ui.storage)
        dform.state = self.state
        dform.createGUI()
        dform.exec_()

    def showErrors(self, errors=None):
        """ shows errors

        :param errors: error list
        :type errors: :obj:`list` < :obj:`str` >
        """
        if errors is None:
            errors = self.state.fetchErrors()
        text = ""
        details = ""
        comps = ""
        for er in errors:
            try:
                jer = json.loads(er)
                if comps:
                    comps += ", "
                comps += "'" + str(jer["component"]) + "'"
                ler = "'" + str(jer["component"]) + "' because of '" + \
                    str(jer["datasource"]) + "'\n"
                der = "" + str(jer["component"]) + "(" + \
                    str(jer["datasource"]) + "):\n" \
                    + str(jer["message"]) + "\n"
            except Exception:
                ler = str(er) + "\n"
                der = ler
            text += ler
            details += der
        if errors:
            MessageBox.warning(
                self.ui.storage,
                "NXSelector: Descriptive Component(s): "
                "%s will not be stored" % comps,
                str(text), "%s" % str(details))

    @Qt.pyqtSlot()
    def __errors(self):
        """ shows error dialog """
        errors = self.state.fetchErrors()
        self.showErrors(errors)
        if not errors:
            Qt.QMessageBox.information(
                self.ui.storage,
                "NXSelector: Descrption Component:",
                "Tango Servers of Description Components are ON")

    @Qt.pyqtSlot()
    def __groups(self):
        """ runs detgroups or descgroups depending on tab index"""
        index = self.ui.tabWidget.currentIndex()
        if index == 0:
            self.__detgroups()
        elif index == 1:
            self.__descgroups()

    def __detgroups(self):
        """ changes detector component groups
        """
        dform = GroupsDlg(self.ui.storage)
        dform.state = self.state
        # DAC  to be hidden via reselector property
        hidden = set(self.state.mcplist)
        hidden.update(self.state.mutedChannels)
        hidden.update(set(self.state.orderedchannels))
        hidden.update(set(self.state.acqchannels)
                      - set(self.state.motors)
                      - set(self.state.ioregisters))
        hidden.update([cp for cp in self.state.acpgroup.keys()
                       if self.state.acpgroup[cp]])

        stcomps = self.state.stepComponents()
        dform.components = dict(
            (cp, False) for cp in stcomps
            if cp not in hidden and not cp.startswith("__"))
        dform.components.update(
            dict((cp, True) for cp in self.state.cpgroup.keys()
                 if (cp not in hidden and not cp.startswith("__"))))

        cldsources = self.state.clientDataSources()

        hidden.update(
            set(cldsources)
            - set(self.state.motors)
            - set(self.state.ioregisters))
        dform.datasources = dict(
            (cp, False) for cp in self.state.avdslist
            if cp not in hidden and not cp.startswith("__"))
        dform.datasources.update(
            dict((cp, True) for cp in self.state.dsgroup.keys()
                 if (cp not in hidden and not cp.startswith("__"))))

        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            if dform.newdatasources:
                self.state.createDataSources(dform.newdatasources)
            self.__updateGroup(self.state.cpgroup, dform.components, False)
            self.__updateGroup(self.state.dsgroup, dform.datasources, False)
            self.resetViews.emit()
            self.dirty.emit()

    def __descgroups(self):
        """ changes descriptive component groups
        """
        dform = GroupsDlg(self.ui.storage)
        dform.title = "Preselectable Description Elements"
        dform.state = self.state
        hidden = set(self.state.mcplist)
        hidden.update(self.state.mutedChannels)

        nostcomps = set(self.state.avcplist) - set(self.state.stepComponents())
        dform.components = dict(
            (cp, False) for cp in nostcomps
            if cp not in hidden and not cp.startswith("__"))
        dform.components.update(
            dict((cp, True) for cp in self.state.acpgroup.keys()
                 if (cp not in hidden and not cp.startswith("__"))))

        cldsources = self.state.clientDataSources()
        hidden.update(
            set(cldsources)
            - set(self.state.motors)
            - set(self.state.ioregisters))

        dform.datasources = dict(
            (cp, False) for cp in self.state.avdslist
            if cp not in hidden and not cp.startswith("__"))
        dform.datasources.update(
            dict((cp, True) for cp in self.state.idsgroup.keys()
                 if (cp not in hidden and not cp.startswith("__"))))

        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.__updateGroup(self.state.acpgroup, dform.components, True)
            self.__updateGroup(self.state.idsgroup, dform.datasources, True)
            self.resetViews.emit()
            self.dirty.emit()

    def __updateGroup(self, group, dct, dvalue=False):
        """ updates selection dictionary according to the given group

        :param group: component selection dictionary
        :type group: :obj:`dict` <:obj:`str`, :obj:`bool` or `None`>
        :param dct: component group
        :type dct: :obj:`dict` <:obj:`str`, :obj:`bool`>
        :param dvalue: default value
        :type dvalue: :obj:`bool`
        """
        ddsdict = self.state.ddsdict.keys()
        for k, st in group.items():
            if k not in dct.keys() \
               and k not in self.state.orderedchannels \
               and k not in ddsdict:
                group.pop(k)
        for k, st in dct.items():
            if k in group.keys():
                if st is False \
                   and k not in ddsdict:
                    group.pop(k)
            else:
                if st is True:
                    group[k] = dvalue

    def __createList(self, dct):
        """ provides a list of selected components from dictionary

        :param dct: component selection dictionary
        :type group: :obj:`dict` <:obj:`str`, :obj:`bool` or `None`>
        :returns:  list of selected components
        :rtype: :obj:`list` <:obj:`str`>
        """
        return [k for (k, st) in dct.items() if st is True]

    @Qt.pyqtSlot()
    def __props(self):
        """ changes component device properites
        """
        dform = PropertiesDlg(self.ui.storage)
#        dform.widget.labels = self.state.labels
        dform.widget.paths = self.state.labelpaths
        dform.widget.shapes = self.state.labelshapes
        dform.widget.links = self.state.labellinks
        dform.widget.canfailflags = self.state.labelcanfailflags
        dform.widget.types = self.state.labeltypes

        dform.available_names = list((set(self.state.labels.values())
                                      | set(self.state.avdslist)))
        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.resetViews.emit()
            self.dirty.emit()

    @Qt.pyqtSlot()
    def __addTimer(self):
        """ adds timers
        """
        logger.debug("ADD Timer")
        if len(self.state.atlist) > len(self.__tWidgets) + 1:
            self.__appendTimer()
            self.state.timers.append("")
            self.reset()
            self.apply()
        logger.debug("ADD Timer end")

    def __appendTimer(self, connect=True):
        """ appends a new timer into the configuration

        :param connect: if currentIndexChanged should be connected to apply
        :type connect: :obj:`bool`
        """
        cb = Qt.QComboBox(self.ui.storage)
        self.__tWidgets.append(cb)
        if self.__layout is None:
            self.__layout = Qt.QHBoxLayout(self.ui.timerFrame)
            self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.addWidget(cb)
        cb.setEnabled(not self.__simplemode)
        if connect:
            cb.currentIndexChanged.connect(self.apply)

    @Qt.pyqtSlot()
    def __delTimer(self):
        """ removes the last timer from the configuration and widgets
        """
        logger.debug("delTimer")
        if self.__tWidgets:
            self.__removeTimer()
            self.state.timers.pop()
            self.reset()
            self.apply()
        logger.debug("delTimer end")

    def __removeTimer(self):
        """ removes the last timer from widgets
        """
        if self.__tWidgets:
            cb = self.__tWidgets.pop()
            cb.hide()
            try:
                cb.currentIndexChanged.disconnect(self.apply)
            except Exception:
                pass
            self.__layout.removeWidget(cb)
            cb.close()

    def reset(self):
        """ resets the storage tab
        """
        logger.debug("reset storage")
        self.disconnectSignals()
        try:
            self.updateForm()
        finally:
            self.connectSignals()
        logger.debug("reset storage ended")

    def __updateTimer(self, widget, nid):
        """ updates timer combobox list

        :param widget: timer combobox widget
        :type widget: :class:`taurus.qt.Qt.QComboBox`
        :param nid: timer index
        :type nid: :obj:`int`
        """
        widget.clear()
        mtimers = sorted(set(self.state.atlist))
        if self.state.timers is not None and len(self.state.timers) > nid:
            timer = self.state.timers[nid]
            if nid:
                mtimers = sorted(set(mtimers) - set(self.state.timers[:nid]))
        else:
            timer = ''
        widget.addItems(
            [str(tm) for tm in mtimers])
        cid = widget.findText(str(timer))
        if cid < 0:
            cid = 0
            if self.state.atlist:
                timer = self.state.atlist[nid]
                if self.state.timers and len(self.state.timers) > nid:
                    self.state.timers[nid] = timer
                elif nid == 0:
                    self.state.timers.append(timer)

        widget.setCurrentIndex(cid)

    @Qt.pyqtSlot()
    def updateScanID(self):
        """ updates scanid
        """
        logger.debug("updateForm storage")
        self.state.fetchEnvData({"ScanID": "scanID"})
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
        logger.debug("updateForm storage ended")

    def updateForm(self):
        """ updates storage form
        """
        logger.debug("updateForm storage")
        # file group
        if self.state.scanDir is not None:
            self.ui.fileScanDirLineEdit.setText(self.state.scanDir)
        self.ui.fileScanIDSpinBox.setValue(self.state.scanID)
        self.ui.fileScanIDSpinBox.setEnabled(False)

        sfile = ""
        if self.state.scanFile:
            if isinstance(self.state.scanFile, (list, tuple)):
                sfile = ", ".join(self.state.scanFile)
            else:
                sfile = self.state.scanFile
            self.ui.fileScanLineEdit.setText(sfile)
        self.__updateTimer(self.ui.mntTimerComboBox, 0)
        while self.state.timers is not None and \
                len(self.state.timers) > len(self.__tWidgets) + 1:
            logger.debug("ADDING timer")
            self.__appendTimer(connect=False)
        while self.state.timers and \
                len(self.state.timers) < len(self.__tWidgets) + 1:
            logger.debug("removing timer")
            self.__removeTimer()
        for nid, widget in enumerate(self.__tWidgets):
            self.__updateTimer(widget, nid + 1)

        # measurement group
        if self.state.mntgrp is not None:
            self.ui.mntGrpComboBox.setEditText(self.state.mntgrp)
        self.ui.mntServerLineEdit.setText(self.state.door)

        # device group
        self.ui.devWriterLineEdit.setText(self.state.writerDevice)
        self.ui.devConfigLineEdit.setText(self.state.configDevice)

        # dynamic component group
#        self.ui.dcEnableCheckBox.setChecked(self.state.dynamicComponents)
        if self.state.dynamicLinks is not None:
            self.ui.dcLinksCheckBox.setChecked(self.state.dynamicLinks)
        if self.state.dynamicPath is not None:
            self.ui.dcPathLineEdit.setText(self.state.dynamicPath)

        # others group
        if self.state.appendEntry is not None:
            self.ui.othersEntryCheckBox.setChecked(self.state.appendEntry)

        logger.debug("updateForm storage ended")

    def __applyTimer(self, widget, nid):
        """ store timer into server state

        :param widget: timer combobox widget
        :type widget: :class:`taurus.qt.Qt.QComboBox`
        :param nid: timer index
        :type nid: :obj:`int`
        """
        timer = str(widget.currentText())
        if self.state.timers:
            if len(self.state.timers) <= nid:
                self.state.timers.append(timer)
            elif self.state.timers[nid] != timer:
                self.state.timers[nid] = timer

    @Qt.pyqtSlot()
    def __mntgrp_edited(self):
        """ updates application state on editing measurement group
        """
        logger.debug("mntgrp edited")
        current = str(self.ui.mntGrpComboBox.currentText()).lower()
        if current == self.state.mntgrp:
            return
        self.disconnectSignals()
        if not current:
            try:
                self.ui.mntGrpComboBox.setFocus()
            finally:
                self.connectSignals()
            return
        self.state.mntgrp = current
        if self.state.mntgrp not in self.state.avmglist:
            try:
                self.updateMntGrpComboBox()
            finally:
                self.connectSignals()
            self.apply()
        logger.debug("mntgrp edited end")

    @Qt.pyqtSlot()
    def __mntgrp_changed(self):
        """ updates application state on changing measurement group
        """
        logger.debug("mntgrp changed")
        current = str(self.ui.mntGrpComboBox.currentText()).lower()
        if current == self.state.mntgrp:
            return
        self.disconnectSignals()
        if not current:
            try:
                self.ui.mntGrpComboBox.setFocus()
            finally:
                self.connectSignals()
            return

        self.state.mntgrp = current
        if self.state.mntgrp not in self.state.avmglist:
            self.connectSignals()
            self.apply()
        else:
            try:
                self.state.storeData("mntGrp", self.state.mntgrp)
                self.state.fetchMntGrp()
            finally:
                self.connectSignals()
            self.resetAll.emit()
#        else:
#            self.connectSignals()
#            self.apply()
        logger.debug("mntgrp changed end")

    @Qt.pyqtSlot()
    def __mntgrp_deleted(self):
        """ updates application state on deleting measurement group
        """
        logger.debug("mntgrp deleted")
        replay = Qt.QMessageBox.question(
            self.ui.storage,
            "NXSelector: ",
            "Would you like to delete %s Measurement Group? "
            % self.ui.mntGrpComboBox.currentText(),
            Qt.QMessageBox.Yes | Qt.QMessageBox.No)
        if replay == Qt.QMessageBox.Yes:
            self.disconnectSignals()
            try:
                self.state.deleteMntGrp(
                    str(self.ui.mntGrpComboBox.currentText()).lower())
            finally:
                self.connectSignals()
            self.resetAll.emit()
        logger.debug("mntgrp deleted end")

    @Qt.pyqtSlot()
    def __setDir(self):
        """ sets scan directory
        """
        dirname = str(Qt.QFileDialog.getExistingDirectory(
            self.ui.storage,
            "Scan Directory",
            self.state.scanDir))
        if str(dirname) and str(dirname) != str(self.state.scanDir):
            self.ui.fileScanDirLineEdit.setText(dirname)
            self.state.scanDir = str(dirname)
            self.apply()

    @Qt.pyqtSlot()
    def __dirty(self):
        """ sets dirty flag
        """
        self.dirty.emit()

    @Qt.pyqtSlot()
    def __dirChanged(self):
        """ updates application state on a scan directory change
        """
        dirname = str(self.ui.fileScanDirLineEdit.text())
        if self.state.scanDir != dirname:
            self.apply()

    @Qt.pyqtSlot()
    def __fileChanged(self):
        """ updates application state on a scan file change
        """
        fnames = self.__fileNames(False)
        if json.dumps(self.state.scanFile) != json.dumps(fnames):
            self.apply()

    def __fileNames(self, message=True):
        """ corrects the scan file name lists

        :param message: message on false
        :type message: :obj:`str`
        :returns: scan file name or a list of scan file names
        :rtype: :obj:`str` or :obj:`list` <:obj:`str`>
        """
        files = str(self.ui.fileScanLineEdit.text())
        sfiles = files.replace(';', ' ').replace(',', ' ').split()
        nxsfiles = []
        for idx, f in enumerate(sfiles):
            if f.split(".")[-1] == 'nxs':
                nxsfiles.append(idx)

        if message and len(nxsfiles) > 1 \
                and self.state.writerDevice != str(self.__moduleLabel):
            Qt.QMessageBox.warning(
                self.ui.storage,
                "To many 'nxs' scan files",
                "Only %s will be used." % (sfiles[nxsfiles[0]]))

            for f in reversed(nxsfiles[1:]):
                sfiles.pop(f)
        return sfiles[0] if len(sfiles) == 1 else sfiles

    @Qt.pyqtSlot()
    def apply(self):
        """ stores form values into server state object
        """
        logger.debug("updateForm apply")
        self.disconnectSignals()
        if not str(self.ui.mntGrpComboBox.currentText()):
            try:
                self.ui.mntGrpComboBox.setFocus()
            finally:
                self.connectSignals()
            return
        try:
            self.state.mntgrp = str(
                self.ui.mntGrpComboBox.currentText()).lower()

            logger.debug("apply Timers")
            self.__applyTimer(self.ui.mntTimerComboBox, 0)
            for nid, widget in enumerate(self.__tWidgets):
                self.__applyTimer(widget, nid + 1)
            logger.debug("apply Timers ended")

            self.state.door = str(self.ui.mntServerLineEdit.text())

            # device group
            self.state.writerDevice = str(self.ui.devWriterLineEdit.text())
            self.state.configDevice = str(self.ui.devConfigLineEdit.text())

            self.state.scanDir = str(self.ui.fileScanDirLineEdit.text())
    #        self.state.scanID = int(self.ui.fileScanIDSpinBox.value())
            self.state.scanFile = self.__fileNames()

            # dynamic component group
            self.state.dynamicComponents = True
            self.state.dynamicLinks = self.ui.dcLinksCheckBox.isChecked()
            self.state.dynamicPath = str(self.ui.dcPathLineEdit.text())

            # others group
            self.state.appendEntry = self.ui.othersEntryCheckBox.isChecked()
        finally:
            self.connectSignals()

        self.dirty.emit()
        self.resetViews.emit()
        logger.debug("updateForm apply ended")
