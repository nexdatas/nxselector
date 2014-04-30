#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file Views.py
# module with different table views

""" main window application dialog """



from PyQt4.QtCore import (
    SIGNAL, Qt, QVariant, SIGNAL, QSignalMapper, SLOT)

from PyQt4.QtGui import (QTableView, QHeaderView, QWidget, QGridLayout, 
                         QCheckBox, QSpacerItem,
                         QRadioButton, QPushButton, QWidgetItem,
                         QSizePolicy, QLabel)



import logging
logger = logging.getLogger(__name__)
        
class TableView(QTableView):

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)        
#        self.horizontalHeader().setVisible(False)        
        self.horizontalHeader().setStretchLastSection(True)        
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        

class OneTableView(QTableView):

    def __init__(self, parent=None):
        super(OneTableView, self).__init__(parent)
        self.verticalHeader().setVisible(False)        
        self.horizontalHeader().setVisible(False)        
        self.horizontalHeader().setStretchLastSection(True)        
        self.horizontalHeader().setResizeMode(QHeaderView.Stretch)



    def reset(self):
        super(OneTableView, self).reset()
        self.hideColumn(1)

class CheckerView(QWidget):

    def __init__(self, parent=None):
        super(CheckerView, self).__init__(parent)
        self.model = None
        self.layout = QGridLayout(self)
        self.widgets = []
        self.mapper = QSignalMapper(self)
        self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                     self.checked)
        self.spacer = None
        self.widget = QCheckBox
        self.center = True
        self.rowMax = 0
        self.selectedWidgetRow = None
        self.showLabels = True
        self.showNames = True

    def checked(self, widget):
        row = self.widgets.index(widget)        
        self.selectedWidgetRow = row
        ind = self.model.index(row, 0)
        value = QVariant(self.widgets[row].isChecked())
        self.model.setData(ind, value, Qt.CheckStateRole)
            
    def setModel(self, model):
        self.model = model
        self.connect(self.model,
                     SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                     self.updateState)
        self.connect(self.model,
                     SIGNAL("modelReset()"),
                     self.updateState)
        self.updateState()

    def reset(self):
        self.hide()
        if self.layout:
            self.widgets = []
            self.spacer = None
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
            self.mapper = QSignalMapper(self)
            self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                         self.checked)
        self.updateState()
        if self.selectedWidgetRow is not None:
            if len(self.widgets) > self.selectedWidgetRow:
                self.widgets[self.selectedWidgetRow].setFocus()
            self.selectedWidgetRow = None
        self.show()

    def updateState(self):
        if not self.model is None:
            for row in range(self.model.rowCount()):
                ind = self.model.index(row, 0)
                ind1 = self.model.index(row, 1)
                name = self.model.data(ind, role = Qt.DisplayRole)
                label = self.model.data(ind1, role = Qt.DisplayRole)
                status = self.model.data(ind, role = Qt.CheckStateRole)
                flags = self.model.flags(ind)
#                flags1 = self.model.flags(ind1)
                if row < len(self.widgets):
                    cb = self.widgets[row]
                else:
                    cb = self.widget()
                    if hasattr(cb, "setCheckable"):
                        cb.setCheckable(True)
#                    if self.showLabels:
#                        cb.setEditable(True)
                    if hasattr(cb, "setSizePolicy") and self.center: 
                        sizePolicy = QSizePolicy(
                            QSizePolicy.Fixed, QSizePolicy.Fixed)
                        sizePolicy.setHorizontalStretch(0)
                        sizePolicy.setVerticalStretch(0)
                        sizePolicy.setHeightForWidth(
                            cb.sizePolicy().hasHeightForWidth())
                        cb.setSizePolicy(sizePolicy)

                cb.setEnabled(bool(Qt.ItemIsEnabled & flags))
                if name:
                    if self.showLabels and label and \
                            str(label.toString()).strip():
                        if self.showNames:
                            cb.setText("%s [%s]" % (
                                    str(label.toString()),
                                    str(name.toString())))
                        else:
                            cb.setText("%s" % (str(label.toString())))
                    
                    else:
                        cb.setText(str(name.toString()))
                if status is not None:    
#                    cb.setCheckState(status)
                    cb.setChecked(bool(status))
                if row >= len(self.widgets):
                    if self.rowMax:
                        lrow = row % self.rowMax 
                        lcol = row / self.rowMax
                    else :
                        lrow = row 
                        lcol = 0
                        
                    self.layout.addWidget(cb, lrow, lcol, 1, 1)
                    self.widgets.append(cb)
                    self.connect(cb, SIGNAL("clicked()"),
                                 self.mapper, SLOT("map()"))
                    self.mapper.setMapping(cb, cb)
            if not self.spacer:
                self.spacer = QSpacerItem(10, 10, 
                                          QSizePolicy.Minimum,
#                                         QSizePolicy.Expanding, 
                                          QSizePolicy.Expanding)
                self.layout.addItem(self.spacer)
                
            
        self.update()
        self.updateGeometry()
        

class CheckDisView(CheckerView):

    def __init__(self, parent=None):
        super(CheckDisView, self).__init__(parent)
        self.displays = []
        self.dmapper = QSignalMapper(self)
        self.connect(self.dmapper, SIGNAL("mapped(QWidget*)"),
                     self.dchecked)
        self.center = False
        self.dlabel = 'Dis.'
        self.slabel = 'Sel.'

    def dchecked(self, widget):
        row = self.displays.index(widget)        
        self.selectedWidgetRow = row
        ind = self.model.index(row, 2)
        value = QVariant(self.displays[row].isChecked())
        self.model.setData(ind, value, Qt.CheckStateRole)


    def reset(self):
        self.hide()
        if self.layout:
            self.widgets = []
            self.displays = []
            self.spacer = None
            child = self.layout.takeAt(0)
            while child:
                self.layout.removeItem(child)
                if isinstance(child, QWidgetItem):
                    child.widget().hide()
                    child.widget().close()
                    self.layout.removeWidget(child.widget())
                child = self.layout.takeAt(0)
            self.mapper = QSignalMapper(self)
            self.connect(self.mapper, SIGNAL("mapped(QWidget*)"),
                         self.checked)
            self.dmapper = QSignalMapper(self)
            self.connect(self.dmapper, SIGNAL("mapped(QWidget*)"),
                         self.dchecked)
        self.updateState()
        if self.selectedWidgetRow is not None:
            if len(self.widgets) > self.selectedWidgetRow:
                self.widgets[self.selectedWidgetRow].setFocus()
            self.selectedWidgetRow = None
        self.show()

            
    def updateState(self):
        if not self.model is None:
            for row in range(self.model.rowCount()):
                ind = self.model.index(row, 0)
                ind1 = self.model.index(row, 1)
                ind2 = self.model.index(row, 2)
                name = self.model.data(ind, role = Qt.DisplayRole)
                label = self.model.data(ind1, role = Qt.DisplayRole)
                status = self.model.data(ind, role = Qt.CheckStateRole)
                dstatus = self.model.data(ind2, role = Qt.CheckStateRole)
                flags = self.model.flags(ind)
                if row < len(self.widgets):
                    cb = self.widgets[row]
                    ds = self.displays[row]
                else:
                    cb = self.widget()
                    ds = self.widget()
                    if hasattr(cb, "setCheckable"):
                        cb.setCheckable(True)
                    if hasattr(ds, "setCheckable"):
                        ds.setCheckable(True)
                    if hasattr(cb, "setSizePolicy") and self.center: 
                        sizePolicy = QSizePolicy(
                            QSizePolicy.Fixed, QSizePolicy.Fixed)
                        sizePolicy.setHorizontalStretch(10)
                        sizePolicy.setVerticalStretch(0)
                        sizePolicy.setHeightForWidth(
                            cb.sizePolicy().hasHeightForWidth())
                        cb.setSizePolicy(sizePolicy)

                cb.setEnabled(bool(Qt.ItemIsEnabled & flags))
                ds.setEnabled(bool(Qt.ItemIsEnabled & flags))
                if name:
                    if self.showLabels and label and \
                            str(label.toString()).strip():
                        if self.showNames:
                            cb.setText("%s [%s]" % (
                                    str(label.toString()),
                                    str(name.toString())))
                        else:
                            cb.setText("%s" % (str(label.toString())))
                    
                    else:
                        cb.setText(str(name.toString()))
                if status is not None:    
                    cb.setChecked(bool(status))
                if dstatus is not None:    
                    ds.setChecked(bool(dstatus))
                if row >= len(self.widgets):
                    if self.rowMax:
                        lrow = row % self.rowMax + 1
                        lcol = row / self.rowMax
                    else :
                        lrow = row +1
                        lcol = 0
                    if lrow == 1:    
                        self.layout.addWidget(
                            QLabel(self.slabel), 0, 2*lcol, 1, 1)
                        self.layout.addWidget(
                            QLabel(self.dlabel), 0, 2*lcol+1, 1, 1, 
                            Qt.AlignRight)
                    self.layout.addWidget(cb, lrow, 2*lcol, 1, 1)
                    self.layout.addWidget(ds, lrow, 2*lcol+1, 1, 1, 
                                          Qt.AlignRight)
                    self.widgets.append(cb)
                    self.displays.append(ds)
                    self.connect(cb, SIGNAL("clicked()"),
                                 self.mapper, SLOT("map()"))
                    self.mapper.setMapping(cb, cb)
                    self.connect(ds, SIGNAL("clicked()"),
                                 self.dmapper, SLOT("map()"))
                    self.dmapper.setMapping(ds, ds)
            if not self.spacer:
                self.spacer = QSpacerItem(10, 10, 
                                          QSizePolicy.Minimum,
#                                         QSizePolicy.Expanding, 
                                          QSizePolicy.Expanding)
                self.layout.addItem(self.spacer)
                
            
        self.update()
        self.updateGeometry()


class RadioView(CheckerView):

    def __init__(self, parent=None):
        super(RadioView, self).__init__(parent)
        self.widget = QRadioButton

class LeftRadioView(CheckerView):

    def __init__(self, parent=None):
        super(LeftRadioView, self).__init__(parent)
        self.widget = QRadioButton
        self.center = False

class LeftCheckerView(CheckerView):

    def __init__(self, parent=None):
        super(LeftCheckerView, self).__init__(parent)
        self.center = False

class ButtonView(CheckerView):

    def __init__(self, parent=None):
        super(ButtonView, self).__init__(parent)
        self.widget = QPushButton
        self.center = False


class CheckerViewNL(CheckerView):

    def __init__(self, parent=None):
        super(CheckerViewNL, self).__init__(parent)
        self.showLabels = False


class LeftCheckerViewNL(LeftCheckerView):

    def __init__(self, parent=None):
        super(LeftCheckerViewNL, self).__init__(parent)
        self.showLabels = False

class ButtonViewNL(ButtonView):

    def __init__(self, parent=None):
        super(ButtonViewNL, self).__init__(parent)
        self.showLabels = False


class RadioViewNL(RadioView):

    def __init__(self, parent=None):
        super(RadioViewNL, self).__init__(parent)
        self.showLabels = False

class LeftRadioViewNL(LeftRadioView):

    def __init__(self, parent=None):
        super(LeftRadioViewNL, self).__init__(parent)
        self.showLabels = False


class CheckerViewNN(CheckerView):

    def __init__(self, parent=None):
        super(CheckerViewNN, self).__init__(parent)
        self.showNames = False


class LeftCheckerViewNN(LeftCheckerView):

    def __init__(self, parent=None):
        super(LeftCheckerViewNN, self).__init__(parent)
        self.showNames = False

class ButtonViewNN(ButtonView):

    def __init__(self, parent=None):
        super(ButtonViewNN, self).__init__(parent)
        self.showNames = False


class RadioViewNN(RadioView):

    def __init__(self, parent=None):
        super(RadioViewNN, self).__init__(parent)
        self.showNames = False

class LeftRadioViewNN(LeftRadioView):

    def __init__(self, parent=None):
        super(LeftRadioViewNN, self).__init__(parent)
        self.showNames = False




class RadioDisView(CheckDisView):

    def __init__(self, parent=None):
        super(RadioDisView, self).__init__(parent)
        self.widget = QRadioButton

class ButtonDisView(CheckDisView):

    def __init__(self, parent=None):
        super(ButtonDisView, self).__init__(parent)
        self.widget = QPushButton
        self.center = False


class CheckDisViewNL(CheckDisView):

    def __init__(self, parent=None):
        super(CheckDisViewNL, self).__init__(parent)
        self.showLabels = False



class ButtonDisViewNL(ButtonDisView):

    def __init__(self, parent=None):
        super(ButtonDisViewNL, self).__init__(parent)
        self.showLabels = False


class RadioDisViewNL(RadioDisView):

    def __init__(self, parent=None):
        super(RadioDisViewNL, self).__init__(parent)
        self.showLabels = False


class CheckDisViewNN(CheckDisView):

    def __init__(self, parent=None):
        super(CheckDisViewNN, self).__init__(parent)
        self.showNames = False


class ButtonDisViewNN(ButtonDisView):

    def __init__(self, parent=None):
        super(ButtonDisViewNN, self).__init__(parent)
        self.showNames = False


class RadioDisViewNN(RadioDisView):

    def __init__(self, parent=None):
        super(RadioDisViewNN, self).__init__(parent)
        self.showNames = False

