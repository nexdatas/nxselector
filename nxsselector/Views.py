#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsselector nexdatas
## \file Views.py
# module with different table views

""" main window application dialog """


try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt

import logging
import json

logger = logging.getLogger(__name__)
from .DynamicTools import DynamicTools
from .LDataDlg import LDataDlg


class RightClickCheckBox(Qt.QCheckBox):

    rightClick = Qt.pyqtSignal()

    def __init__(self, parent=None):
        Qt.QCheckBox.__init__(self, parent)

    @Qt.pyqtSlot()
    def mousePressEvent(self, event):
        Qt.QCheckBox.mousePressEvent(self, event)
        if event.button() == Qt.Qt.RightButton:
            self.rightClick.emit()


class CheckerLabelWidget(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self.checkBox = Qt.QCheckBox(self)
        self.label = Qt.QLabel(self)
        layout = Qt.QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.label)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def isChecked(self):
        return self.checkBox.isChecked()

    def setChecked(self, status):
        self.label.setEnabled(status)
        return self.checkBox.setChecked(status)

    def setCheckable(self, status):
        return self.checkBox.setCheckable(status)

    def setEnabled(self, status):
        return self.checkBox.setEnabled(status)

    def setPolicy(self, policy):
        return self.label.setPolicy(policy)

    def setText(self, text):
        return self.label.setText(text)


class TableView(Qt.QTableView):

    def __init__(self, parent=None):
        Qt.QTableView.__init__(self, parent)
        self.verticalHeader().setVisible(False)
#        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)


class OneTableView(Qt.QTableView):

    dirty = Qt.pyqtSignal()

    def __init__(self, parent=None):
        Qt.QTableView.__init__(self, parent)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)

    def reset(self):
        Qt.QTableView.reset(self)
        for i in range(1, 5):
            self.hideColumn(i)


class CheckerView(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self.model = None
        self.glayout = Qt.QGridLayout(self)
        self.widgets = []
        self.mapper = Qt.QSignalMapper(self)
        self.pmapper = None
        self.dmapper = None
        self.displays = []
        self.mapper.mapped.connect(self.checked)
        self.spacer = None
        self.widget = Qt.QCheckBox
        self.center = True
        self.rowMax = 0
        self.selectedWidgetRow = None
        self.showLabels = True
        self.showNames = True
        self.setContextMenuPolicy(Qt.Qt.PreventContextMenu)

    def close(self):
        self.mapper.mapped.disconnect(self.checked)
        if self.model:
            self.model.dataChanged.disconnect(self.reset)
            self.model.modelReset.disconnect(self.reset)
        Qt.QWidget.close(self)

    @Qt.pyqtSlot(int)
    def checked(self, row):
        self.selectedWidgetRow = row
        ind = self.model.index(row, 0)
        value = Qt.QVariant(self.widgets[row].isChecked())

        if self.dmapper:
            if not value:
                self.displays[row].setChecked(bool(False))

        self.model.setData(ind, value, Qt.Qt.CheckStateRole)

    def setModel(self, model):
        self.model = model
        self.model.dataChanged.connect(self.reset)
        self.model.modelReset.connect(self.reset)
        self.reset()

    def clearLayout(self):
        if self.glayout:
            self.widgets = []
            if self.dmapper:
                self.displays = []
            self.spacer = None
            DynamicTools.cleanupLayoutWithItems(self.glayout)
            self.glayout = Qt.QGridLayout(self)

    def connectMapper(self):
        if self.mapper:
            self.mapper.mapped.disconnect(self.checked)
        self.mapper = Qt.QSignalMapper(self)
        self.mapper.mapped.connect(self.checked)

    @Qt.pyqtSlot()
    @Qt.pyqtSlot(Qt.QModelIndex, Qt.QModelIndex)
    def reset(self):
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
        rowNo = rowMax
        if rowNo < 1:
            rowNo = 1
        fullColumnNo = rowCount / rowNo
        lastRowNo = rowCount % rowNo
        while lastRowNo and fullColumnNo < rowNo - lastRowNo:
            rowNo -= 1
            lastRowNo += fullColumnNo
        return rowNo

    def updateState(self):
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

        self.update()
        self.updateGeometry()

    def __createGrid(self, row, cb, ds, rowNo=None):
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
                lcol = row / rowNo
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
                        Qt.Qt.AlignRight)
                self.glayout.addWidget(ds, lrow, lcol + 1, 1, 1,
                                       Qt.Qt.AlignRight)
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
                self.displays.append(ds)
                if hasattr(cb, "rightClick"):
                    cb.rightClick.connect(self.pmapper.map)
                self.pmapper.setMapping(cb, self.widgets.index(cb))

    def __setWidgets(self, row):
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
            if hasattr(cb, "setCheckable"):
                cb.setCheckable(True)
            if self.dmapper:
                ds = self.widget()
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

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.dmapper = Qt.QSignalMapper(self)
        self.dmapper.mapped.connect(self.dchecked)
        self.center = False
        self.dlabel = 'Dis.'
        self.slabel = 'Sel.'

    @Qt.pyqtSlot(int)
    def dchecked(self, row):
        self.selectedWidgetRow = row
        ind = self.model.index(row, 2)
        value = Qt.QVariant(self.displays[row].isChecked())
        self.model.setData(ind, value, Qt.Qt.CheckStateRole)

    def connectMapper(self):
        CheckerView.connectMapper(self)
        if self.dmapper:
            self.dmapper.mapped.disconnect(self.dchecked)
        self.dmapper = Qt.QSignalMapper(self)
        self.dmapper.mapped.connect(self.dchecked)

    def close(self):
        self.dmapper.mapped.disconnect(self.dchecked)
        CheckerView.close(self)


class CheckPropView(CheckDisView):

    def __init__(self, parent=None):
        CheckDisView.__init__(self, parent)
        self.widget = RightClickCheckBox
        self.pmapper = Qt.QSignalMapper(self)
        self.pmapper.mapped.connect(self.pchecked)

    @Qt.pyqtSlot(int)
    def pchecked(self, row):
        self.selectedWidgetRow = row
        ind = self.model.index(row, 0)
        name = self.model.data(ind, role=Qt.Qt.DisplayRole)
        ind5 = self.model.index(row, 5)
        props = self.model.data(ind5, role=Qt.Qt.DisplayRole)

        if props:
            prs = json.loads(str(props))
            dform = LDataDlg(self)
            dform.label = name
            dform.dtype = prs["data_type"] if "data_type" in prs else None
            dform.shape = prs["shape"] if "shape" in prs else None
            dform.link = prs["link"] if "link" in prs else None
            dform.path = prs["nexus_path"] if "nexus_path" in prs else None
            dform.addVariables(prs)
            dform.createGUI()

            dform.ui.labelLineEdit.setEnabled(False)
            if dform.exec_():
                if "data_type" in prs:
                    prs["data_type"] = dform.dtype or None
                    prs["link"] = dform.link
                    prs["shape"] = dform.shape
                    prs["nexus_path"] = dform.shape or None
                for nm, val in dform.variables.items():
                    prs[nm] = val
                self.model.setData(ind5, Qt.QVariant(
                    Qt.QString(str(json.dumps(prs)))))

    def connectMapper(self):
        CheckDisView.connectMapper(self)
        if self.pmapper:
            self.pmapper.mapped.disconnect(self.pchecked)
        self.pmapper = Qt.QSignalMapper(self)
        self.pmapper.mapped.connect(self.pchecked)

    def close(self):
        self.dmapper.mapped.disconnect(self.pchecked)
        CheckDisView.close(self)


class RadioView(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.widget = Qt.QRadioButton


class LeftRadioView(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.widget = Qt.QRadioButton
        self.center = False


class LeftCheckerView(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.center = False


class ButtonView(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.widget = Qt.QPushButton
        self.center = False


class CheckerViewNL(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.showLabels = False


class LeftCheckerViewNL(LeftCheckerView):

    def __init__(self, parent=None):
        LeftCheckerView.__init__(self, parent)
        self.showLabels = False


class ButtonViewNL(ButtonView):

    def __init__(self, parent=None):
        ButtonView.__init__(self, parent)
        self.showLabels = False


class RadioViewNL(RadioView):

    def __init__(self, parent=None):
        RadioView.__init__(self, parent)
        self.showLabels = False


class LeftRadioViewNL(LeftRadioView):

    def __init__(self, parent=None):
        LeftRadioView.__init__(self, parent)
        self.showLabels = False


class CheckerViewNN(CheckerView):

    def __init__(self, parent=None):
        CheckerView.__init__(self, parent)
        self.showNames = False


class LeftCheckerViewNN(LeftCheckerView):

    def __init__(self, parent=None):
        LeftCheckerView.__init__(self, parent)
        self.showNames = False


class ButtonViewNN(ButtonView):

    def __init__(self, parent=None):
        ButtonView.__init__(self, parent)
        self.showNames = False


class RadioViewNN(RadioView):

    def __init__(self, parent=None):
        RadioView.__init__(self, parent)
        self.showNames = False


class LeftRadioViewNN(LeftRadioView):

    def __init__(self, parent=None):
        LeftRadioView.__init__(self, parent)
        self.showNames = False


class RadioDisView(CheckDisView):

    def __init__(self, parent=None):
        CheckDisView.__init__(self, parent)
        self.widget = Qt.QRadioButton


class ButtonDisView(CheckDisView):

    def __init__(self, parent=None):
        CheckDisView.__init__(self, parent)
        self.widget = Qt.QPushButton
        self.center = False


class CheckDisViewNL(CheckDisView):

    def __init__(self, parent=None):
        CheckDisView.__init__(self, parent)
        self.showLabels = False


class CheckPropViewNL(CheckPropView):

    def __init__(self, parent=None):
        CheckPropView.__init__(self, parent)
        self.showLabels = False


class ButtonDisViewNL(ButtonDisView):

    def __init__(self, parent=None):
        ButtonDisView.__init__(self, parent)
        self.showLabels = False


class RadioDisViewNL(RadioDisView):

    def __init__(self, parent=None):
        RadioDisView.__init__(self, parent)
        self.showLabels = False


class CheckDisViewNN(CheckDisView):

    def __init__(self, parent=None):
        CheckDisView.__init__(self, parent)
        self.showNames = False


class CheckPropViewNN(CheckPropView):

    def __init__(self, parent=None):
        CheckPropView.__init__(self, parent)
        self.showNames = False


class CheckerLabelViewNN(CheckerViewNN):
    def __init__(self, parent=None):
        CheckerViewNN.__init__(self, parent)
        self.widget = CheckerLabelWidget


class ButtonDisViewNN(ButtonDisView):

    def __init__(self, parent=None):
        ButtonDisView.__init__(self, parent)
        self.showNames = False


class RadioDisViewNN(RadioDisView):

    def __init__(self, parent=None):
        RadioDisView.__init__(self, parent)
        self.showNames = False
