#!/usr/bin/env python
#   This file is part of nexdatas - Tanog Server for NeXus data writer
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
# selactable tab

""" detector component tab """

import json
import fnmatch

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from .Element import DSElement, CPElement, CP, DS
from .ElementModel import ElementModel
from .Frames import Frames
from .DynamicTools import DynamicTools

from .Views import CheckerView

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class Detectors(Qt.QObject):
    """ detector component tab widget
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, ui, state=None, userView=CheckerView, rowMax=0,
                 simpleMode=0, fontSize=11):
        """ constructor

        :param ui: ui instance
        :type ui: :class:`taurus.qt.qtgui.util.ui.__UI`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        :param userView: widget for description optional components
        :type userView: :class:`taurus.qt.Qt.QWidget`
        :param rowMax: maximal row number in component column view
        :type rowMax: :obj:`int`
        :param simpleMode: if simple display mode: \
                           `1` for negative hidden, `2` for negative disable
        :type simpleMode: :obj:`int`
        :param fontSize: font size in component column view
        :type fontSize: :obj:`int`
        """

        Qt.QObject.__init__(self)

        #: (:class:`taurus.qt.qtgui.util.ui.__UI`) ui instance
        self.ui = ui
        #: (:class:`nxsselector.ServerState.ServerState`) server state
        self.state = state
        #: (:class:`taurus.qt.Qt.QWidget`) \
        #:     widget for description optional components
        self.userView = userView
        #: (:obj:`int`) maximal row number in component column view
        self.rowMax = rowMax
        #: (:obj:`int`) font size for in component column view
        self.fontSize = fontSize
        #: (:obj:`bool`) if simple view mode
        self.__simpleMode = simpleMode
        #: (:class:`taurus.qt.Qt.QLayout`) component layout
        self.glayout = None
        #: (:obj:`str`)  JSON dictionary as \
        #: with nested list frames [[[[group_name, group_id ], ...], ...], ...]
        self.frames = None
        #: (:obj:`str`)  JSON dictionary as \
        #: (:obj:`dict` <:obj:`int`, :obj:`list` <:obj:`str`> >) \
        #:    component group filters
        self.mgroups = None
        #: (:obj:`dict` <:obj:`int`, :class:`taurus.qt.Qt.QWidget`>) \
        #:    (OPTIONAL, MANDATORY, OTHERS) component views
        self.groups = {}
        #: (:obj:`dict` <:obj:`int`, :class:`taurus.qt.Qt.QWidget`>) \
        #:    (OPTIONAL, MANDATORY, OTHERS) component views
        self.views = {}
        #: (:obj:`list` <:class:`taurus.qt.Qt.QFrame`>) \
        #:  list of component group frames
        self.mframes = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QLayout`>) \
        #:  list of column layouts
        self.column_layouts = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QLayout`>) \
        #:  list of  group layouts
        self.group_layouts = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QLayout`>) \
        #:  list of widget layouts
        self.auto_layouts = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QGroupBox`>) \
        #:  list of component group boxes
        self.groupboxes = []
        #: (:obj:`list` <:class:`nxsselector.ElementModel.ElementModel`>) \
        #:    element model list
        self.models = []

    def updateGroups(self):
        """ filters component/datasource selection state
        """

        self.groups = {}
        ucp = set()
        uds = set()
        try:
            mgroups = json.loads(self.mgroups)
        except Exception:
            mgroups = {}
        for k, gr in mgroups.items():
            if int(k) in self.__availableGroups():
                group = []
                for elem in gr:
                    if isinstance(elem, list) and elem:
                        ielem = elem[0]
                    else:
                        ielem = elem
                    cpfiltered = fnmatch.filter(
                        self.state.cpgroup.keys(),
                        ielem)
                    dsfiltered = fnmatch.filter(
                        self.state.dsgroup.keys(),
                        ielem)
                    filtered = set(cpfiltered)
                    filtered.update(dsfiltered)
                    for felem in filtered:
                        if felem in self.state.avcplist:
                            group.append(
                                CPElement(felem, self.state))
                            ucp.add(felem)
                        else:
                            group.append(
                                DSElement(felem, self.state))
                            uds.add(felem)
                if group:
                    if int(k) not in self.groups:
                        self.groups[int(k)] = []
                    self.groups[int(k)].extend(group)

        for ds in self.state.dsgroup.keys():
            if ds not in uds and ds not in ucp:
                if DS not in self.groups:
                    self.groups[DS] = []
                if ds in self.state.avcplist:
                    self.groups[DS].append(CPElement(ds, self.state))
                    ucp.add(ds)
                else:
                    self.groups[DS].append(DSElement(ds, self.state))
                    uds.add(ds)
        for cp in self.state.cpgroup.keys():
            if cp not in ucp and cp not in uds \
                    and cp not in self.state.mcplist \
                    and cp not in self.state.acplist:
                if CP not in self.groups:
                    self.groups[CP] = []
                self.groups[CP].append(CPElement(cp, self.state))

    def __availableGroups(self):
        """ provides a set of Frames with available groups

        :returns: set of Frames with available groups
        :rtype: :obj:`set` <:obj:`nxsselector.Frames.Frames`>
        """
        res = set()
        try:
            frames = Frames(self.frames)
            for frame in frames:
                for column in frame:
                    for group in column:
                        res.add(group[1])
        except Exception:
            pass
        return res

    def __clearFrames(self):
        """ clears component frames
        """
        DynamicTools.cleanupObjects(self.models, "model")
        if self.views:
            views = list(self.views.values())
            DynamicTools.cleanupWidgets(views, "views")
            self.views = {}
        DynamicTools.cleanupObjects(self.auto_layouts, "auto")
        DynamicTools.cleanupWidgets(self.groupboxes, "groupbox")
        DynamicTools.cleanupObjects(self.group_layouts, "group")
        DynamicTools.cleanupObjects(self.column_layouts, "column")
        DynamicTools.cleanupFrames(self.mframes, "frames")
        DynamicTools.cleanupLayoutWithItems(self.glayout)

    def __calcMaxRowNumbers(self):
        """ calculates row numbers for groups

        :returns:  a dictionry with rownumbers
        :rtype: :obj:`dict`< :obj:`int`, :obj:`int`>
        """
        maxrownumbers = {}
        gpsizes = dict([(gk, len(gr)) for gk, gr in self.groups.items()])
        for frame in json.loads(self.frames):
            for column in frame:
                clm = [gr[1] for gr in column]
                if len(clm) > 1:
                    gpsum = sum([(gpsizes[gr[1]] if gr[1] in gpsizes else 0)
                                 for gr in column])
                    for gr in column:
                        la = float(
                            gpsizes[gr[1]] if gr[1] in gpsizes else 0) / \
                            max(gpsum, 1)
                        maxrownumbers[gr[1]] =  \
                            max(1, int(la * (self.rowMax - 2*len(clm) + 2)))
                else:
                    maxrownumbers[column[0][1]] = self.rowMax
        return maxrownumbers

    def createGUI(self):
        """ creates widget GUI
        """

        self.__clearFrames()
        self.glayout = Qt.QHBoxLayout(self.ui.detectorsWidget)

        frames = Frames(self.frames, DS in self.groups, CP in self.groups)
        maxrownumbers = self.__calcMaxRowNumbers()
        for frame in frames:
            mframe = Qt.QFrame(self.ui.detectorsWidget)
            self.mframes.append(mframe)
            mframe.setFrameShape(Qt.QFrame.StyledPanel)
            mframe.setFrameShadow(Qt.QFrame.Raised)
            layout_columns = Qt.QHBoxLayout(mframe)
            self.column_layouts.append(layout_columns)

            for column in frame:
                layout_groups = Qt.QVBoxLayout()
                self.group_layouts.append(layout_groups)

                for group in column:
                    hide = False
                    try:
                        ig = int(group[1])
                        if (self.__simpleMode & 1) and ig < 0:
                            hide = True
                    except Exception:
                        pass
                    if not hide:
                        mgroup = Qt.QGroupBox(mframe)
                        self.groupboxes.append(mgroup)
                        mgroup.setTitle(group[0])
                        layout_auto = Qt.QGridLayout(mgroup)
                        self.auto_layouts.append(layout_auto)
                        mview = self.userView(mgroup)
                        if hasattr(mview, "rowMax"):
                            if group[1] in maxrownumbers.keys():
                                mview.rowMax = maxrownumbers[group[1]]
                            else:
                                mview.rowMax = self.rowMax
                        if hasattr(mview, "fontSize"):
                            mview.fontSize = self.fontSize

                        layout_auto.addWidget(mview, 0, 0, 1, 1)
                        self.views[group[1]] = mview
                        layout_groups.addWidget(mgroup)
                if layout_groups.count():
                    layout_columns.addLayout(layout_groups)
            if layout_columns.count():
                self.glayout.addWidget(mframe)
            else:
                mframe.hide()
        self.ui.detectorsWidget.update()
        if self.ui.tabWidget.currentWidget() == self.ui.detectors:
            self.ui.detectorsWidget.show()

    def setModels(self):
        """ sets view models
        """
        for k in self.views.keys():
            if k in self.groups.keys():
                md = ElementModel(self.groups[k])
            else:
                md = ElementModel([])
            self.models.append(md)
            try:
                ig = int(k)
                if (self.__simpleMode & 2) and ig < 0:
                    md.enable = False
                    md.disEnable = False
            except Exception:
                pass
            self.views[k].setModel(md)

            md.componentChecked.connect(self.updateViews)
            md.dirty.connect(self.setDirty)

    @Qt.pyqtSlot()
    def setDirty(self):
        """ emits the `dirty` signal
        """
        self.dirty.emit()

    def reset(self):
        """ recreates widget GUI
        """
        logger.debug("reset views")
        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
        logger.debug("reset views end")

    @Qt.pyqtSlot()
    def updateViews(self):
        """ resets frame views
        """
        logger.debug("update views")
        for vw in self.views.values():
            vw.reset()

        logger.debug("update views end")
