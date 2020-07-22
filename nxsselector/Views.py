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
# module with different table views

""" component element table views """


try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt

import logging
import json

from .DynamicTools import DynamicTools
from .LDataDlg import LDataDlg
from .LDataDlg import LExDataDlg

#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)


class RightClickCheckBox(Qt.QCheckBox):
    """ right click checkbox table widget
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) rightClick signal
    rightClick = Qt.pyqtSignal()

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QCheckBox.__init__(self, parent)

    @Qt.pyqtSlot()
    def mousePressEvent(self, event):
        """ excecutes right click action

        :param event: mouse event
        :type event: :class:`taurus.qt.Qt.QEvent`
        """
        Qt.QCheckBox.mousePressEvent(self, event)
        if event.button() == Qt.Qt.RightButton:
            self.rightClick.emit()


class CheckerLabelWidget(Qt.QWidget):
    """ checkbox table widget
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QWidget.__init__(self, parent)
        #: (:class:`taurus.qt.Qt.QCheckBox`) element checkbox widget
        self.checkBox = Qt.QCheckBox(self)
        #: (:class:`taurus.qt.Qt.QCheckBox`) element label widget
        self.label = Qt.QLabel(self)
        layout = Qt.QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.label)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def isChecked(self):
        """ provides checkbox status

        :returns: check status
        :rtype: :obj:`bool`
        """
        return self.checkBox.isChecked()

    def setChecked(self, status):
        """ sets checkbox status

        :param status: check status
        :type status: :obj:`bool`
        """
        self.label.setEnabled(status)
        self.checkBox.setChecked(status)

    def setCheckable(self, status):
        """ sets ckeckable checkbox flag

        :param status: checkable flag
        :type status: :obj:`bool`
        """
        return self.checkBox.setCheckable(status)

    def setEnabled(self, status):
        """ sets enable checkbox flag

        :param status: enable flag
        :type status: :obj:`bool`
        """
        return self.checkBox.setEnabled(status)

    def setSizePolicy(self, policy):
        """ sets label size policy

        :param policy: size policy
        :type policy: :class:`taurus.qt.Qt.QSizePolicy`
        """
        self.label.setSizePolicy(policy)
        Qt.QWidget.setSizePolicy(self, policy)

    def setText(self, text):
        """ sets label text

        :param policy: label text
        :type policy: :obj:`str` or :obj:`str`
        """
        self.label.setText(text)


class TableView(Qt.QTableView):
    """ table view with streached last column
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """

        Qt.QTableView.__init__(self, parent)
        self.verticalHeader().setVisible(False)
#        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        try:
            self.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)
        except Exception:
            # workaround for bug in pyqt
            self.horizontalHeader().setSectionResizeMode(
                Qt.QHeaderView.Stretch)


class OneTableView(Qt.QTableView):
    """ table view with stretched last column un unvisible horizontal header
    """

    #: (:class:`taurus.qt.Qt.pyqtSignal`) dirty signal
    dirty = Qt.pyqtSignal()

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QTableView.__init__(self, parent)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        try:
            self.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)
        except Exception:
            # workaround for bug in pyqt
            self.horizontalHeader().setSectionResizeMode(
                Qt.QHeaderView.Stretch)

    def reset(self):
        """ resets table view and hides view columns
        """
        Qt.QTableView.reset(self)
        for i in range(1, 6):
            self.hideColumn(i)


class CheckerView(Qt.QWidget):
    """ element view with redefined checkboxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        Qt.QWidget.__init__(self, parent)
        #: (:class:`taurus.qt.Qt.QAbstractTableModel`) view model
        self.model = None
        #: (:class:`taurus.qt.Qt.QGridLayout`) main grid layout
        self.glayout = Qt.QGridLayout(self)
        #: (:obj:`list` <:class:`taurus.qt.Qt.QGridLayout`> ) element widgets
        self.widgets = []
        #: (:class:`taurus.qt.Qt.QSignalMapper`) widget check status mapper
        self.mapper = Qt.QSignalMapper(self)
        #: (:class:`taurus.qt.Qt.QSignalMapper`) widget property mapper
        self.pmapper = None
        #: (:class:`taurus.qt.Qt.QSignalMapper`) widget display status mapper
        self.dmapper = None
        #: (:obj:`list` <:class:`taurus.qt.Qt.QGridLayout`> ) \
        #:     display checkbox widgets
        self.displays = []
        self.mapper.mapped.connect(self.checked)
        #: (:class:`taurus.qt.Qt.QSpacerItem`) spacer view item
        self.spacer = None
        #: (:obj:`type`) widget type
        self.widget = Qt.QCheckBox
        #: (:obj:`bool`) if widget are centered
        self.center = True
        #: (:obj:`int`) maximal number of rows in the column
        self.rowMax = 0
        #: (:obj:`int`) font size for in component column view
        self.fontSize = 11
        #: (:obj:`int`) selected widget row (widget id)
        self.selectedWidgetRow = None
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = True
        #: (:obj:`bool`) if names should be shown
        self.showNames = True
        self.setContextMenuPolicy(Qt.Qt.PreventContextMenu)

    def close(self):
        """ widget close method which disconnect signals """

        self.mapper.mapped.disconnect(self.checked)
        if self.model:
            self.model.dataChanged.disconnect(self.reset)
            self.model.modelReset.disconnect(self.reset)
        Qt.QWidget.close(self)

    @Qt.pyqtSlot(int)
    def checked(self, row):
        """ updates the element model check status for the given widget row

        :param row: widget row
        :type row: :obj:`int`
        """
        self.selectedWidgetRow = row
        ind = self.model.index(row, 0)
        value = (self.widgets[row].isChecked())
        if self.dmapper:
            if not value:
                self.displays[row].setChecked(bool(False))

        self.model.setData(ind, value, Qt.Qt.CheckStateRole)

    def setModel(self, model):
        """
        set the current view model

        :param model: view model to be set
        :type model: :class:`taurus.qt.Qt.QAbstractTableModel`

        """
        self.model = model
        self.model.dataChanged.connect(self.reset)
        self.model.modelReset.connect(self.reset)
        self.reset()

    def clearLayout(self):
        """ clears layouts of the view
        """

        if self.glayout:
            self.widgets = []
            if self.dmapper:
                self.displays = []
            self.spacer = None
            DynamicTools.cleanupLayoutWithItems(self.glayout)
            self.glayout = Qt.QGridLayout(self)

    def connectMapper(self):
        """ reconnects mapper
        """
        if self.mapper:
            self.mapper.mapped.disconnect(self.checked)
        self.mapper = Qt.QSignalMapper(self)
        self.mapper.mapped.connect(self.checked)

    @Qt.pyqtSlot()
    @Qt.pyqtSlot(Qt.QModelIndex, Qt.QModelIndex)
    def reset(self):
        """ resets the view
        """
        self.hide()
        self.clearLayout()
        self.connectMapper()
        self.updateState()
        if self.selectedWidgetRow is not None:
            if len(self.widgets) > self.selectedWidgetRow:
                self.widgets[self.selectedWidgetRow].setFocus()
            self.selectedWidgetRow = None
        self.show()

    def __findRowNumber(self, rowMax, rowCount):
        """ finds physical row number for the element widget

        :param rowMax: maximal number of rows in the column
        :type rowMax: :obj:`int`
        :param rowCount: current model widget row (widget id)
        :type rowCount: :obj:`int`
        """
        rowNo = rowMax
        if rowNo < 1:
            rowNo = 1
        fullColumnNo = rowCount // rowNo
        lastRowNo = rowCount % rowNo
        while lastRowNo and fullColumnNo < rowNo - lastRowNo:
            rowNo -= 1
            lastRowNo += fullColumnNo
        return rowNo

    def updateState(self):
        """ updates state of the view
        """
        if self.model is not None:
            rowCount = self.model.rowCount()
            rowNo = self.__findRowNumber(self.rowMax, rowCount)

            for row in range(rowCount):

                cb, ds = self.__setWidgets(row)
                self.__setNameTips(row, cb)
                self.__createGrid(row, cb, ds, rowNo)

            if not self.spacer:
                self.spacer = Qt.QSpacerItem(
                    10, 10,
                    Qt.QSizePolicy.Minimum,
                    Qt.QSizePolicy.Expanding)
                self.glayout.addItem(self.spacer)
        self.__resetStretchFactors()
        self.update()
        self.updateGeometry()

    def __resetStretchFactors(self):
        """ resets stretch factors """
        grp = self.parent()
        if hasattr(grp, "parent"):
            frm = grp.parent()
            stretch = 0
            grps = [(gp, None) for gp in frm.findChildren(Qt.QGroupBox)]
            hfrmlayout = frm.layout()
            vfrmlayouts = [hl for hl in hfrmlayout.children()
                           if isinstance(hl, Qt.QVBoxLayout)]
            gvls = []
            if vfrmlayouts:
                for vl in vfrmlayouts:
                    kids = [
                        (vl.itemAt(ind).widget(), vl)
                        for ind in range(vl.count())
                        if isinstance(vl.itemAt(ind).widget(), Qt.QGroupBox)]
                    gvls.append(kids)
            else:
                gvls = [grps]

            for gvl in gvls:
                vst = 0
                lvl = None
                for gr, vl in gvl:
                    gst = 0
                    lvl = vl
                    mvws = gr.findChildren(CheckerView)
                    for mvw in mvws:
                        if hasattr(mvw.model, 'rowCount'):
                            lgst = mvw.model.rowCount() // self.rowMax \
                                + (1 if (mvw.model.rowCount() % self.rowMax)
                                   else 0)
                            if lgst > gst:
                                gst = lgst
                    vst = gst
                if lvl:
                    hfrmlayout.setStretchFactor(lvl, vst)
                stretch += vst
            if hasattr(frm, "parent"):
                lyt = frm.parent().layout()
                sizestt = [0, 1, 2, 3, 3, 4, 4, 4, 5, 5, 5, 5]
                if stretch >= len(sizestt):
                    nstretch = 6
                elif stretch < 0:
                    nstretch = 0
                else:
                    nstretch = sizestt[stretch]
                lyt.setStretchFactor(frm, nstretch)

    def __createGrid(self, row, cb, ds, rowNo=None):
        """ add widget into the view grid

        :param row: the row number
        :type row: :obj:`int`
        :param cb: status checkbox or button
        :type cb: :class:`taurus.qt.Qt.QWidget`
        :param ds: display checkbox or button
        :type ds: :class:`taurus.qt.Qt.QWidget`
        :param rowNo: the number of row in the group
        :type rowNo: :obj:`int`
        """
        rowNo = self.rowMax if not rowNo else rowNo
        ind = self.model.index(row, 0)
        ind2 = self.model.index(row, 2)
        status = self.model.data(ind, role=Qt.Qt.CheckStateRole)
        dstatus = self.model.data(ind2, role=Qt.Qt.CheckStateRole)
        if status is not None:
            cb.setChecked(bool(status))
        if self.dmapper:
            if dstatus is not None:
                ds.setChecked(bool(dstatus))
        if row >= len(self.widgets):
            if rowNo:
                lrow = row % rowNo
                lcol = row // rowNo
            else:
                lrow = row
                lcol = 0
            if self.dmapper:
                lrow = lrow + 1
                lcol = 2 * lcol

                if lrow == 1:
                    self.glayout.addWidget(
                        Qt.QLabel(self.slabel), 0, lcol, 1, 1)
                    self.glayout.addWidget(
                        Qt.QLabel(self.dlabel), 0, lcol + 1, 1, 1,
                        Qt.Qt.AlignCenter)
                self.glayout.addWidget(ds, lrow, lcol + 1, 1, 1,
                                       Qt.Qt.AlignCenter)
            self.glayout.addWidget(cb, lrow, lcol, 1, 1)
            self.widgets.append(cb)

            if hasattr(cb, "clicked"):
                cb.clicked.connect(self.mapper.map)
            self.mapper.setMapping(cb, self.widgets.index(cb))
            if self.dmapper:
                self.displays.append(ds)
                if hasattr(ds, "clicked"):
                    ds.clicked.connect(self.dmapper.map)
                self.dmapper.setMapping(ds, self.displays.index(ds))
            if self.pmapper:
                if hasattr(cb, "rightClick"):
                    cb.rightClick.connect(self.pmapper.map)
                self.pmapper.setMapping(cb, self.widgets.index(cb))

    def __setWidgets(self, row):
        """ creates element widgets

        :param row: the row number
        :type row: :obj:`int`
        :returns: (checkbox widget, display widget)
        :rtype: (:class:`taurus.qt.Qt.QWidget`, :class:`taurus.qt.Qt.QWidget`)
        """
        ind = self.model.index(row, 0)
        flags = self.model.flags(ind)
        ind2 = self.model.index(row, 2)
        flags2 = self.model.flags(ind2)
        ds = None
        cb = None
        if row < len(self.widgets):
            cb = self.widgets[row]
            if self.dmapper:
                ds = self.displays[row]
        else:
            cb = self.widget()
            font = cb.font()
            font.setPointSize(self.fontSize)
            cb.setFont(font)
            if hasattr(cb, "setCheckable"):
                cb.setCheckable(True)
            if self.dmapper:
                ds = self.widget()
                font = ds.font()
                font.setPointSize(self.fontSize)
                ds.setFont(font)
                if hasattr(ds, "setCheckable"):
                    ds.setCheckable(True)
            if hasattr(cb, "setSizePolicy") and self.center:
                sizePolicy = Qt.QSizePolicy(
                    Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(10)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(
                    cb.sizePolicy().hasHeightForWidth())
                cb.setSizePolicy(sizePolicy)

        cb.setEnabled(bool(Qt.Qt.ItemIsEnabled & flags))
        if self.dmapper:
            ds.setEnabled(bool(Qt.Qt.ItemIsEnabled & flags2))
        return (cb, ds)

    def __setNameTips(self, row, cb):
        """ set name tips of element widget

        :param row: the row number
        :type row: :obj:`int`
        :param cb: checkbox widget
        :type cb: :class:`taurus.qt.Qt.QWidget`
        """
        ind = self.model.index(row, 0)
        name = self.model.data(ind, role=Qt.Qt.DisplayRole)
        ind1 = self.model.index(row, 1)
        label = self.model.data(ind1, role=Qt.Qt.DisplayRole)

        if name:
            if self.showLabels and label and \
                    str(label).strip():
                if self.showNames:
                    cb.setText("%s [%s]" % (
                        str(label),
                        str(name)))
                else:
                    cb.setText("%s" % (str(label)))
            else:
                cb.setText(str(name))

            # works with:
            # QT_API=pyqt4 ./nxselector  -t cleanlooks
            # QT_API=pyqt5 ./nxselector
            cb.setStyleSheet(
                "QCheckBox:unchecked{ color: black; }"
                "QCheckBox:checked{ color: blue; }"
                "QCheckBox:disabled{ color: gray; }"
            )
        text = self.model.data(ind, role=Qt.Qt.ToolTipRole)
        text = str(text) if text else ""
        if self.showLabels:
            if self.showNames:
                if text.strip():
                    cb.setToolTip(text)
            else:
                if text.strip():
                    cb.setToolTip(
                        "%s: %s" % (str(name), text))
                else:
                    cb.setToolTip(str(name))
        else:
            ln = str(label) if label else str(name)
            if text.strip():
                cb.setToolTip("%s: %s" % (ln, text))
            else:
                cb.setToolTip(ln)


class CheckDisView(CheckerView):
    """ element view with redefined checkboxes with display boxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:class:`taurus.qt.Qt.QSignalMapper`) widget display status mapper
        self.dmapper = Qt.QSignalMapper(self)
        self.dmapper.mapped.connect(self.dchecked)
        #: (:obj:`bool`) if widget are centered
        self.center = False
        #: (:obj:`str`) display status label text
        self.dlabel = 'Dis.'
        #: (:obj:`str`) check status label text
        self.slabel = 'Sel.'

    @Qt.pyqtSlot(int)
    def dchecked(self, row):
        """ updates the element model display for the given widget row

        :param row: widget row
        :type row: :obj:`int`
        """
        self.selectedWidgetRow = row
        ind = self.model.index(row, 2)
        value = (self.displays[row].isChecked())
        self.model.setData(ind, value, Qt.Qt.CheckStateRole)

    def connectMapper(self):
        """ reconnects mapper
        """
        CheckerView.connectMapper(self)
        if self.dmapper:
            self.dmapper.mapped.disconnect(self.dchecked)
        self.dmapper = Qt.QSignalMapper(self)
        self.dmapper.mapped.connect(self.dchecked)

    def close(self):
        """ widget close method which disconnect signals """
        self.dmapper.mapped.disconnect(self.dchecked)
        CheckerView.close(self)


class CheckPropView(CheckDisView):
    """ element view with property widget
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckDisView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = RightClickCheckBox
        #: (:class:`taurus.qt.Qt.QSignalMapper`) widget property mapper
        self.pmapper = Qt.QSignalMapper(self)
        self.pmapper.mapped.connect(self.pchecked)
        self.propdlg = LDataDlg

    @Qt.pyqtSlot(int)
    def pchecked(self, row):
        """ updates the element model properties for the given widget row

        :param row: widget row
        :type row: :obj:`int`
        """
        self.selectedWidgetRow = row
        ind = self.model.index(row, 0)
        name = self.model.data(ind, role=Qt.Qt.DisplayRole)
        ind5 = self.model.index(row, 5)
        props = self.model.data(ind5, role=Qt.Qt.DisplayRole)
        if props:
            prs = json.loads(str(props))
            dform = self.propdlg(self)
            dform.label = name
            if "__triggergatelist__" in prs:
                dform.synchronizers = list(prs["__triggergatelist__"])
            dform.dtype = prs["data_type"] if "data_type" in prs else None
            dform.shape = prs["shape"] if "shape" in prs else None
            dform.link = prs["link"] if "link" in prs else None
            dform.path = prs["nexus_path"] if "nexus_path" in prs else None
            dform.canfail = prs["canfail"] if "canfail" in prs else None
            dform.addVariables(prs)
            dform.createGUI()

            dform.ui.labelLineEdit.setEnabled(False)
            if dform.exec_():
                if "data_type" in prs:
                    prs["data_type"] = dform.dtype or None
                    prs["link"] = dform.link
                    prs["canfail"] = dform.canfail
                    prs["shape"] = dform.shape
                    prs["nexus_path"] = dform.shape or None
                for nm, val in dform.variables.items():
                    prs[nm] = val
                self.model.setData(ind5, (
                    str(str(json.dumps(prs)))))

    def connectMapper(self):
        """ reconnects mappers
        """
        CheckDisView.connectMapper(self)
        if self.pmapper:
            self.pmapper.mapped.disconnect(self.pchecked)
        self.pmapper = Qt.QSignalMapper(self)
        self.pmapper.mapped.connect(self.pchecked)

    def close(self):
        """ widget close method which disconnect signals """
        self.pmapper.mapped.disconnect(self.pchecked)
        CheckDisView.close(self)


class CheckExPropView(CheckPropView):
    """ element view with extended property widget
    """

    def __init__(self, parent=None):
        CheckPropView.__init__(self, parent)
        #: (:obj:`bool`) if widget are centered
        self.propdlg = LExDataDlg


class RadioView(CheckerView):
    """ element view with radio checkboxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = Qt.QRadioButton


class LeftRadioView(CheckerView):
    """ element view with left radio checkboxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = Qt.QRadioButton
        #: (:obj:`bool`) if widget are centered
        self.center = False


class LeftCheckerView(CheckerView):
    """ element view with left checkboxes
    """

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        #: (:obj:`bool`) if widget are centered
        self.center = False


class ButtonView(CheckerView):
    """ element view with button checkboxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = Qt.QPushButton
        #: (:obj:`bool`) if widget are centered
        self.center = False


class CheckerViewNL(CheckerView):
    """ element view with checkboxes without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class LeftCheckerViewNL(LeftCheckerView):
    """ element view with left checkboxes without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        LeftCheckerView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class ButtonViewNL(ButtonView):
    """ element view with button checkboxes without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        ButtonView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class RadioViewNL(RadioView):
    """ element view with radio checkboxes without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        RadioView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class LeftRadioViewNL(LeftRadioView):
    """ element view with left radio checkboxes without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        LeftRadioView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class CheckerViewNN(CheckerView):
    """ element view with checkboxes with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class LeftCheckerViewNN(LeftCheckerView):
    """ element view with checkboxes with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        LeftCheckerView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class ButtonViewNN(ButtonView):
    """ element view with button checkboxes with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        ButtonView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class RadioViewNN(RadioView):
    """ element view with radio checkboxes with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        RadioView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class LeftRadioViewNN(LeftRadioView):
    """ element view with left radio checkboxes with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        LeftRadioView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class RadioDisView(CheckDisView):
    """ element view with left radio checkboxes and display boxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckDisView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = Qt.QRadioButton


class ButtonDisView(CheckDisView):
    """ element view with left button checkboxes and display boxes
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckDisView.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = Qt.QPushButton
        #: (:obj:`bool`) if widget are centered
        self.center = False


class CheckDisViewNL(CheckDisView):
    """ element view with left button checkboxes and display boxes
    without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckDisView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class CheckPropViewNL(CheckPropView):
    """ element view with checkboxes and properties
    without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckPropView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class CheckExPropViewNL(CheckExPropView):
    """ element view with checkboxes and properties
    without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckExPropView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class ButtonDisViewNL(ButtonDisView):
    """ element view with left button checkboxes and display boxes
    without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        ButtonDisView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class RadioDisViewNL(RadioDisView):
    """ element view with left radio checkboxes and display boxes
    without name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        RadioDisView.__init__(self, parent)
        #: (:obj:`bool`) if name labels should be shown
        self.showLabels = False


class CheckDisViewNN(CheckDisView):
    """ element view with redefined checkboxes with display boxes
    without names
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckDisView.__init__(self, parent)
        self.showNames = False


class CheckPropViewNN(CheckPropView):
    """ element view with redefined checkboxes with properties
    without names
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckPropView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class CheckExPropViewNN(CheckExPropView):
    """ element view with redefined checkboxes with properties
    without names
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckExPropView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class CheckerLabelViewNN(CheckerViewNN):
    """ element view with CheckerLabelWidget checkboxes with only name labels
    """
    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        CheckerViewNN.__init__(self, parent)
        #: (:obj:`type`) widget type
        self.widget = CheckerLabelWidget


class ButtonDisViewNN(ButtonDisView):
    """ element view with button checkboxes and display boxes
    with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        ButtonDisView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False


class RadioDisViewNN(RadioDisView):
    """ element view with radio checkboxes and display boxes
    with only name labels
    """

    def __init__(self, parent=None):
        """ constructor

        :param parent: parent object
        :type parent: :class:`taurus.qt.Qt.QObject`
        """
        RadioDisView.__init__(self, parent)
        #: (:obj:`bool`) if names should be shown
        self.showNames = False
