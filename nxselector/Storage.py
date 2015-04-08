#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file Storage.py
# storage tab

""" storage tab """

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

from .EdListDlg import EdListDlg
from .GroupsDlg import GroupsDlg
from .InfoDlg import InfoDlg
from .OrderDlg import OrderDlg
from .PropertiesDlg import PropertiesDlg
from .MessageBox import MessageBox

import logging
import json
logger = logging.getLogger(__name__)


## main window class
class Storage(object):

    ## constructor
    # \param settings frame settings
    def __init__(self, ui, state=None, simplemode=False):
        self.ui = ui
        self.state = state
        self.__layout = None
        self.__tWidgets = []
        self.__onlyselected = False
        self.__simplemode = simplemode

        self.__moduleLabel = 'module'

    def disconnectSignals(self):
        self.ui.storage.disconnect(self.ui.fileScanDirLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.disconnect(self.ui.fileScanDirToolButton,
                                   Qt.SIGNAL("pressed()"), self.__setDir)
        self.ui.storage.disconnect(self.ui.fileScanLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)
                                # measurement group

        self.ui.storage.disconnect(self.ui.mntTimerComboBox,
                                   Qt.SIGNAL("currentIndexChanged(int)"),
                                   self.apply)
        for cb in self.__tWidgets:
            self.ui.storage.disconnect(
                cb, Qt.SIGNAL("currentIndexChanged(int)"), self.apply)
        self.ui.storage.disconnect(self.ui.timerAddPushButton,
                                   Qt.SIGNAL("clicked()"), self.__addTimer)
        self.ui.storage.disconnect(self.ui.timerDelPushButton,
                                   Qt.SIGNAL("clicked()"), self.__delTimer)
        self.ui.storage.disconnect(self.ui.mntGrpComboBox,
                                   Qt.SIGNAL("currentIndexChanged(QString)"),
                                   self.__mntgrp_changed)
        self.ui.storage.disconnect(self.ui.mntGrpToolButton,
                                   Qt.SIGNAL("pressed()"),
                                   self.__mntgrp_deleted)
        self.ui.storage.disconnect(self.ui.mntGrpComboBox.lineEdit(),
                                   Qt.SIGNAL("editingFinished()"),
                                   self.__mntgrp_edited)
        self.ui.storage.disconnect(self.ui.mntServerLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)

        # device group
        self.ui.storage.disconnect(self.ui.devWriterLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.disconnect(self.ui.devConfigLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)

        # dynamic component group
#        self.ui.storage.disconnect(self.ui.dcEnableCheckBox,
#                                Qt.SIGNAL("toggled(bool)"), self.apply)
        self.ui.storage.disconnect(self.ui.dcLinksCheckBox,
                                   Qt.SIGNAL("clicked(bool)"), self.apply)
        self.ui.storage.disconnect(self.ui.dcPathLineEdit,
                                   Qt.SIGNAL("editingFinished()"), self.apply)

        # others group
        self.ui.storage.disconnect(self.ui.othersEntryCheckBox,
                                   Qt.SIGNAL("clicked(bool)"), self.apply)

        self.ui.storage.disconnect(self.ui.devConfigPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__variables)

        self.ui.storage.disconnect(self.ui.propPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__props)

        self.ui.storage.disconnect(self.ui.labelsPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__labels)
        self.ui.storage.disconnect(self.ui.orderToolButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__order)
        self.ui.storage.disconnect(self.ui.groupsPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__groups)
        self.ui.storage.disconnect(self.ui.resetDescriptionsPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__resetDescriptions)
        self.ui.storage.disconnect(self.ui.errorsPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__errors)
        self.ui.storage.disconnect(self.ui.infoPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__info)

    def connectSignals(self):
        self.disconnectSignals()
        self.ui.storage.connect(self.ui.fileScanDirToolButton,
                                Qt.SIGNAL("pressed()"), self.__setDir)
        self.ui.storage.connect(self.ui.fileScanDirLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)
#        self.ui.storage.connect(self.ui.fileScanIDSpinBox,
#                                Qt.SIGNAL("valueChanged(int)"), self.apply)
        self.ui.storage.connect(self.ui.fileScanLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)
                                # measurement group

        self.ui.storage.connect(self.ui.mntTimerComboBox,
                                Qt.SIGNAL("currentIndexChanged(int)"),
                                self.apply)
        for cb in self.__tWidgets:
            self.ui.storage.connect(
                cb, Qt.SIGNAL("currentIndexChanged(int)"), self.apply)
        self.ui.storage.connect(self.ui.timerDelPushButton,
                                Qt.SIGNAL("clicked()"), self.__delTimer)
        self.ui.storage.connect(self.ui.timerAddPushButton,
                                Qt.SIGNAL("clicked()"), self.__addTimer)
        self.ui.storage.connect(self.ui.mntGrpToolButton,
                                   Qt.SIGNAL("pressed()"),
                                   self.__mntgrp_deleted)
        self.ui.storage.connect(self.ui.mntGrpComboBox,
                                Qt.SIGNAL("currentIndexChanged(QString)"),
                                self.__mntgrp_changed)
        self.ui.storage.connect(self.ui.mntGrpComboBox.lineEdit(),
                                   Qt.SIGNAL("editingFinished()"),
                                   self.__mntgrp_edited)
        self.ui.storage.connect(self.ui.mntServerLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)

        # device group
        self.ui.storage.connect(self.ui.devWriterLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)
        self.ui.storage.connect(self.ui.devConfigLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)

        # dynamic component group
        self.ui.storage.connect(self.ui.dcLinksCheckBox,
                                Qt.SIGNAL("clicked(bool)"), self.apply)
        self.ui.storage.connect(self.ui.dcPathLineEdit,
                                Qt.SIGNAL("editingFinished()"), self.apply)

        # others group
        self.ui.storage.connect(self.ui.othersEntryCheckBox,
                                Qt.SIGNAL("clicked(bool)"), self.apply)

        self.ui.storage.connect(self.ui.devConfigPushButton,
                                Qt.SIGNAL("clicked()"),
                                self.__variables)

        self.ui.storage.connect(self.ui.propPushButton,
                                Qt.SIGNAL("clicked()"),
                                self.__props)

        self.ui.storage.connect(self.ui.labelsPushButton,
                                Qt.SIGNAL("clicked()"),
                                self.__labels)
        self.ui.storage.connect(self.ui.orderToolButton,
                                Qt.SIGNAL("clicked()"),
                                self.__order)

        self.ui.storage.connect(self.ui.groupsPushButton,
                                Qt.SIGNAL("clicked()"),
                                self.__groups)
        self.ui.storage.connect(self.ui.resetDescriptionsPushButton,
                                Qt.SIGNAL("clicked()"),
                                self.__resetDescriptions)
        self.ui.storage.connect(self.ui.errorsPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__errors)
        self.ui.storage.connect(self.ui.infoPushButton,
                                   Qt.SIGNAL("clicked()"),
                                   self.__info)

    def updateMntGrpComboBox(self):
        self.disconnectSignals()
        self.ui.mntGrpComboBox.clear()
        for mg in self.state.avmglist:
            self.ui.mntGrpComboBox.addItem(mg)
        if self.state.mntgrp not in self.state.avmglist:
            self.ui.mntGrpComboBox.addItem(self.state.mntgrp)
        ind = self.ui.mntGrpComboBox.findText(self.state.mntgrp)
        self.ui.mntGrpComboBox.setCurrentIndex(ind)
        self.connectSignals()

    def __variables(self):
        dform = EdListDlg(self.ui.storage)
        dform.widget.record = self.state.configvars
        dform.simple = True
        dform.available_names = self.state.vrcpdict.keys()
        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.ui.storage.emit(Qt.SIGNAL("dirty"))

    def __labels(self):
        dform = EdListDlg(self.ui.storage)
        dform.widget.record = self.state.labels
        dform.simple = True
        dform.headers = ["Element", "Label"]
        dform.available_names = list(
            set(self.state.avcplist) | set(self.state.avdslist))

        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.ui.storage.emit(Qt.SIGNAL("reset"))

    def __order(self):
        dform = OrderDlg(self.ui.storage)
        dform.channels = list(self.state.orderedchannels)
        dform.selected = list(
            set([cp for cp in self.state.cpgroup.keys()
                 if self.state.cpgroup[cp]])
            | set([ds for ds in self.state.dsgroup.keys()
                   if self.state.dsgroup[ds]])
            | set(self.state.timers))
        dform.onlyselected = self.__onlyselected

        dform.createGUI()
        dform.exec_()
        self.__onlyselected = dform.onlyselected
        if dform.dirty:
            self.state.orderedchannels = list(dform.channels)
            self.ui.storage.emit(Qt.SIGNAL("dirty"))

    def __resetDescriptions(self):
        self.ui.storage.emit(Qt.SIGNAL("resetDescriptions"))

    def __info(self):
        dform = InfoDlg(self.ui.storage)
        dform.state = self.state
        dform.createGUI()
        dform.exec_()

    def __errors(self):
        errors = self.state.fetchErrors()
        text = ""
        details = ""
        for er in errors:
            try:
                jer = json.loads(er)
                ler = "" + str(jer["component"]) + " with " + \
                    str(jer["datasource"]) + "\n"
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
                "NXSSelector: Errors in Descrption Component:",
                str(text), "%s" % str(details))
        else:
            Qt.QMessageBox.information(
                self.ui.storage,
                "NXSSelector: Descrption Component:",
                "Tango Servers of Description Components are ON")

    def __groups(self):
        dform = GroupsDlg(self.ui.storage)
        dform.state = self.state
        dform.det_components = dict((cp, False) for cp in self.state.avcplist)
        dform.det_components.update(
            dict((cp, True) for cp in self.state.cpgroup.keys()))
        dform.det_datasources = dict((cp, False) for cp in self.state.avdslist)
        dform.det_datasources.update(
            dict((cp, True) for cp in self.state.dsgroup.keys()))
        dform.beam_components = dict((cp, False) for cp in self.state.avcplist)
        dform.beam_components.update(
            dict((cp, True) for cp in self.state.acpgroup.keys()))
        dform.beam_datasources = dict(
            (cp, False) for cp in self.state.avdslist)
        dform.beam_datasources.update(
            dict((cp, True) for cp in self.state.idslist))

        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.__updateGroup(self.state.cpgroup, dform.det_components)
            self.__updateGroup(self.state.dsgroup, dform.det_datasources)
            self.__updateGroup(self.state.acpgroup, dform.beam_components)
            self.state.idslist = self.__createList(dform.beam_datasources)
            self.ui.storage.emit(Qt.SIGNAL("updateGroups"))

    def __updateGroup(self, group, dct):
        for k, st in dct.items():
            if k in group.keys():
                if st is False:
                    group.pop(k)
            else:
                if st is True:
                    group[k] = False

    def __createList(self, dct):
        return [k for (k, st) in dct.items() if st is True]

    def __props(self):
        dform = PropertiesDlg(self.ui.storage)
#        dform.widget.labels = self.state.labels
        dform.widget.paths = self.state.labelpaths
        dform.widget.shapes = self.state.labelshapes
        dform.widget.links = self.state.labellinks
        dform.widget.types = self.state.labeltypes

        dform.available_names = list((set(self.state.labels.values())
                                      | set(self.state.avdslist)))
        dform.createGUI()
        dform.exec_()
        if dform.dirty:
            self.ui.storage.emit(Qt.SIGNAL("dirty"))

    def __addTimer(self):
        logger.debug("ADD Timer")
        if len(self.state.atlist) > len(self.__tWidgets) + 1:
            self.__appendTimer()
            self.state.timers.append("")
            self.reset()
            self.apply()
        logger.debug("ADD Timer end")

    def __appendTimer(self):
        cb = Qt.QComboBox(self.ui.storage)
        self.__tWidgets.append(cb)
        if self.__layout is None:
            self.__layout = Qt.QHBoxLayout(self.ui.timerFrame)
            self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.addWidget(cb)
        cb.setEnabled(not self.__simplemode)

    def __delTimer(self):
        logger.debug("delTimer")
        if self.__tWidgets:
            self.__removeTimer()
            self.state.timers.pop()
            self.reset()
            self.apply()
        logger.debug("delTimer end")

    def __removeTimer(self):
        if self.__tWidgets:
            cb = self.__tWidgets.pop()
            cb.hide()
            self.__layout.removeWidget(cb)
            self.ui.storage.disconnect(
                cb, Qt.SIGNAL(
                    "currentIndexChanged(int)"), self.apply)
            cb.close()

    def reset(self):
        logger.debug("reset storage")
        self.disconnectSignals()
        self.updateForm()
        self.connectSignals()
        logger.debug("reset storage ended")

    def __updateTimer(self, widget, nid):
        widget.clear()
        mtimers = sorted(set(self.state.atlist))
        if self.state.timers is not None and len(self.state.timers) > nid:
            timer = self.state.timers[nid]
            if nid:
                mtimers = sorted(set(mtimers) - set(self.state.timers[:nid]))
        else:
            timer = ''
        widget.addItems(
            [Qt.QString(tm) for tm in mtimers])
        cid = widget.findText(Qt.QString(timer))
        if cid < 0:
            cid = 0
            if self.state.atlist:
                timer = self.state.atlist[nid]
                if self.state.timers and len(self.state.timers) > nid:
                    self.state.timers[nid] = timer
                elif nid == 0:
                    self.state.timers.append(timer)

        widget.setCurrentIndex(cid)

    def updateForm(self):
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
            self.__appendTimer()
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
        timer = str(widget.currentText())
        if self.state.timers:
            if len(self.state.timers) <= nid:
                self.state.timers.append(timer)
            elif self.state.timers[nid] != timer:
                self.state.timers[nid] = timer

    def __mntgrp_edited(self):
        logger.debug("mntgrp edited")
        current = str(self.ui.mntGrpComboBox.currentText()).lower()
        if current == self.state.mntgrp:
            return
        self.disconnectSignals()
        if not current:
            self.ui.mntGrpComboBox.setFocus()
            self.connectSignals()
            return
        self.state.mntgrp = current
        if self.state.mntgrp not in self.state.avmglist:
            self.updateMntGrpComboBox()
            self.connectSignals()
            self.apply()
        logger.debug("mntgrp edited end")

    def __mntgrp_changed(self):
        logger.debug("mntgrp changed")
        current = str(self.ui.mntGrpComboBox.currentText()).lower()
        if current == self.state.mntgrp:
            return
        self.disconnectSignals()
        if not current:
            self.ui.mntGrpComboBox.setFocus()
            self.connectSignals()
            return

        self.state.mntgrp = current
        if self.state.mntgrp not in self.state.avmglist:
            self.connectSignals()
            self.apply()
        else:
            self.state.storeData("mntGrp", self.state.mntgrp)
            self.state.fetchMntGrp()
            self.connectSignals()
            self.ui.storage.emit(Qt.SIGNAL("resetAll"))
#        else:
#            self.connectSignals()
#            self.apply()
        logger.debug("mntgrp changed end")

    def __mntgrp_deleted(self):
        logger.debug("mntgrp deleted")
        replay = Qt.QMessageBox.question(
            self.ui.storage,
            "NXSSelector: ",
            "Would you like to delete %s Measurement Group? "
            % self.ui.mntGrpComboBox.currentText(),
            Qt.QMessageBox.Yes | Qt.QMessageBox.No)
        if replay == Qt.QMessageBox.Yes:
            self.disconnectSignals()
            self.state.deleteMntGrp(
                str(self.ui.mntGrpComboBox.currentText()).lower())
            self.connectSignals()
            self.ui.storage.emit(Qt.SIGNAL("resetAll"))
        logger.debug("mntgrp deleted end")

    def __setDir(self):
        dirname = str(Qt.QFileDialog.getExistingDirectory(
                self.ui.storage,
                "Scan Directory",
                self.state.scanDir))
        if str(dirname) and str(dirname) != str(self.state.scanDir):
            self.ui.fileScanDirLineEdit.setText(dirname)
            self.state.scanDir = str(dirname)

    def apply(self):
        logger.debug("updateForm apply")
        self.disconnectSignals()
        if not str(self.ui.mntGrpComboBox.currentText()):
            self.ui.mntGrpComboBox.setFocus()
            self.connectSignals()
            return
        self.state.mntgrp = str(self.ui.mntGrpComboBox.currentText()).lower()

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
        files = str(self.ui.fileScanLineEdit.text())
        sfiles = files.replace(';', ' ').replace(',', ' ').split()
        nxsfiles = []
        for idx, f in enumerate(sfiles):
            if f.split(".")[-1] == 'nxs':
                nxsfiles.append(idx)
        if len(nxsfiles) > 1 \
                and self.state.writerDevice != str(self.__moduleLabel):
            Qt.QMessageBox.warning(
                self.ui.storage,
                "To many 'nxs' scan files",
                "Only %s will be used." % (sfiles[nxsfiles[0]]))

            for f in reversed(nxsfiles[1:]):
                sfiles.pop(f)
        self.state.scanFile = sfiles

        # dynamic component group
        self.state.dynamicComponents = True
        self.state.dynamicLinks = self.ui.dcLinksCheckBox.isChecked()
        self.state.dynamicPath = str(self.ui.dcPathLineEdit.text())

        # others group
        self.state.appendEntry = self.ui.othersEntryCheckBox.isChecked()
        self.connectSignals()

        self.ui.storage.emit(Qt.SIGNAL("dirty"))
        self.ui.storage.emit(Qt.SIGNAL("reset"))
        logger.debug("updateForm apply ended")
