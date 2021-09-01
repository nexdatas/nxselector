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
# descriptions tab

""" descriptions tab """


try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

from .Element import CPElement
from .ElementModel import ElementModel
from .Views import CheckerView
from .DynamicTools import DynamicTools

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

#: (:obj:`int`) component type enum
OPTIONAL, MANDATORY, OTHERS = range(3)


class Descriptions(Qt.QObject):
    """ descriptions tab widget
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) component checked signal
    componentChecked = Qt.pyqtSignal()

    def __init__(self, ui, state=None, userView=CheckerView,
                 mandUserView=CheckerView, rowMax=0, fontSize=11):
        """ constructor

        :param ui: ui instance
        :type ui: :class:`taurus.qt.qtgui.util.ui.__UI`
        :param state: server state
        :type state: :class:`nxsselector.ServerState.ServerState`
        :param userView: widget for description optional components
        :type userView: :class:`taurus.qt.Qt.QWidget`
        :param mandUserView: widget for description mandatory components
        :type mandUserView: :class:`taurus.qt.Qt.QWidget`
        :param rowMax: maximal row number in component column view
        :type rowMax: :obj:`int`
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
        #: (:class:`taurus.qt.Qt.QWidget`) \
        #:     widget for description mandatory components
        self.mandUserView = mandUserView
        #: (:obj:`int`) font size for in component column view
        self.fontSize = fontSize
        #: (:obj:`int`) maximal row number in component column view
        self.rowMax = rowMax

        #: (:obj:`list` <:class:`nxsselector.Element.CPElement`>) \
        #:    group of optional component elements
        self.agroup = []
        #: (:obj:`list` <:class:`nxsselector.Element.CPElement`>) \
        #:    group of other component elements
        self.igroup = []
        #: (:obj:`list` <:class:`nxsselector.Element.CPElement`>) \
        #:    group of mandator component elements
        self.mgroup = []

        #: (:obj:`list` <:class:`taurus.qt.Qt.QFrame`>) \
        #:  list of component group frames
        self.mframes = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QLayout`>) \
        #:  list of group layouts
        self.group_layouts = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QLayout`>) \
        #:  list of widget layouts
        self.auto_layouts = []
        #: (:obj:`list` <:class:`taurus.qt.Qt.QGroupBox`>) \
        #:  list of component group boxes
        self.groupboxes = []
        #: (:obj:`dict` <:obj:`int`, :class:`taurus.qt.Qt.QWidget`>) \
        #:    (OPTIONAL, MANDATORY, OTHERS) component views
        self.views = {}
        #: (:obj:`list` <:class:`nxsselector.ElementModel.ElementModel`>) \
        #:    element model list
        self.models = []
        #: (:class:`taurus.qt.Qt.QLayout`) component layout
        self.__cplayout = None
        #: (:class:`taurus.qt.Qt.QLayout`) other component layout
        self.__dslayout = None
        #: (:class:`taurus.qt.Qt.QLayout`) main layout
        self.__mainlayout = None

    def updateGroups(self):
        """ updates component/datasource selection state
        """

        self.agroup = []
        for cp in self.state.acpgroup.keys():
            self.agroup.append(
                CPElement(cp, self.state,
                          group=self.state.acpgroup))

        self.mgroup = []
        mcpgroup = {}
        for cp in self.state.mcplist:
            mcpgroup[cp] = True
        for cp in mcpgroup.keys():
            self.mgroup.append(
                CPElement(cp, self.state, group=mcpgroup))

        self.igroup = []
        for ds in self.state.idsgroup.keys():
            self.igroup.append(
                CPElement(ds, self.state,
                          group=self.state.idsgroup))

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
        DynamicTools.cleanupFrames(self.mframes, "frames")
        DynamicTools.cleanupLayoutWithItems(self.__cplayout)
        DynamicTools.cleanupLayoutWithItems(self.__dslayout)
        DynamicTools.cleanupLayoutWithItems(self.__mainlayout)
        self.__cplayout = None
        self.__dslayout = None

    def createGUI(self):
        """ creates widget GUI
        """
        if self.__cplayout and self.__dslayout:
            self.__clearFrames()
        self.__mainlayout = Qt.QHBoxLayout(self.ui.descriptionsWidget)
        self.__cplayout = Qt.QVBoxLayout()
        self.__dslayout = Qt.QVBoxLayout()
        self.__mainlayout.addLayout(self.__cplayout)
        self.__mainlayout.addLayout(self.__dslayout)
        self.__mainlayout.setStretchFactor(self.__cplayout, 3)
        self.__mainlayout.setStretchFactor(
            self.__dslayout, 1 if self.igroup else 0)

        self.views[OTHERS] = self.__addView(
            "Other Optional", self.userView, self.rowMax,
            self.__dslayout, not self.igroup)

        la = len(self.agroup)
        lm = len(self.mgroup)
        if la + lm:
            la, lm = [float(la) / (la + lm), float(lm) / (la + lm)]

        self.views[OPTIONAL] = self.__addView(
            "Optional", self.userView, max(1, int(la * (self.rowMax - 2))))
        self.views[MANDATORY] = self.__addView(
            "Mandatory", self.mandUserView,
            max(1, int(lm * (self.rowMax - 2))))

        self.ui.descriptionsWidget.update()
        if self.ui.tabWidget.currentWidget() == self.ui.descriptions:
            self.ui.descriptionsWidget.show()

    def __addView(self, label, view, rowMax, layout=None, hide=False):
        """ adds component group frame views

        :param label: component group label
        :type label: :obj:`str`
        :param view: component view widget
        :type view: :class:`taurus.qt.Qt.QWidget`
        :param rowMax: maximal row number in component column view
        :type rowMax: :obj:`int`
        :param layout: component group frame layout
        :type layout: :class:`taurus.qt.Qt.QLayout`
        :param hide: if frame should be hidden
        :type hide: :obj:`bool`
        """
        if layout is None:
            layout = self.__cplayout
        mframe = Qt.QFrame(self.ui.descriptionsWidget)
        mframe.setFrameShape(Qt.QFrame.StyledPanel)
        mframe.setFrameShadow(Qt.QFrame.Raised)
        self.mframes.append(mframe)
        layout_groups = Qt.QHBoxLayout(mframe)
        self.group_layouts.append(layout_groups)

        mgroup = Qt.QGroupBox(mframe)
        mgroup.setTitle(label)
        self.groupboxes.append(mgroup)
        layout_auto = Qt.QGridLayout(mgroup)
        self.auto_layouts.append(layout_auto)
        mview = view(mgroup)
        if hasattr(mview, "rowMax"):
            mview.rowMax = rowMax
        if hasattr(mview, "fontSize"):
            mview.fontSize = self.fontSize
        if hasattr(mview, 'dmapper'):
            mview.dmapper = None

        layout_auto.addWidget(mview, 0, 0, 1, 1)
        layout_groups.addWidget(mgroup)

        layout.addWidget(mframe)
        if hide:
            mframe.hide()
        else:
            mframe.show()
        return mview

    def setModels(self):
        """ sets view models
        """

        md = ElementModel(self.agroup)
#        md.enable = False
        self.models.append(md)
        self.views[OPTIONAL].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

        md = ElementModel(self.mgroup)
        md.enable = False
        self.models.append(md)
        self.views[MANDATORY].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

        md = ElementModel(self.igroup)
#        md.enable = False
        self.models.append(md)
        self.views[OTHERS].setModel(md)
        md.componentChecked.connect(self.__componentChecked)

    @Qt.pyqtSlot()
    def __componentChecked(self):
        """ emits the component checked signal
        """

        self.componentChecked.emit()

    def updateViews(self):
        """ resets frame views
        """

        for vw in self.views.values():
            vw.reset()

    def reset(self):
        """ resets whole content of frame views
        """

        self.updateGroups()
        self.createGUI()
        self.setModels()
        self.updateViews()
