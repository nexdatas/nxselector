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
## \file DynamicTools.py
# DynamicTools

""" device Model """

import logging
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except:
    from taurus.qt import Qt


## element class
class DynamicTools(object):

    ## constructor
    def __init__(self):
        pass

    @classmethod
    def cleanupObjects(cls, objects, label=None):
        while objects:
            la = objects.pop()
            try:
                Qt.QObjectCleanupHandler().add(la)
                if label:
                    logger.debug("del %s" % label)
            except:
                if label:
                    logger.debug("ERROR del %s" % label)
            del la

    @classmethod
    def cleanupWidgets(cls, widgets, label=None):
        while widgets:
            if hasattr(widgets, "clearLayout"):
                wg.clearLayout()
            wg = widgets.pop()
            try:
                wg.hide()
                wg.close()
                wg.setParent(None)
                Qt.QObjectCleanupHandler().add(wg)
                if label:
                    logger.debug("del %s" % label)
            except:
                if label:
                    logger.debug("ERROR del %s" % label)
            del wg

    @classmethod
    def cleanupFrames(cls, frames, label=None):
        while frames:
            fr = frames.pop()
            try:
                fr.hide()
                fr.close()
                if label:
                    logger.debug("del %s" % label)
            except:
                if label:
                    logger.debug("ERROR del %s" % label)

    @classmethod
    def cleanupLayoutWithItems(cls, layout):
        if layout:
            logger.debug("COUNTS %s" % layout.count())
            while layout.count():
                child = layout.itemAt(0)
                layout.removeItem(child)
                if isinstance(child, Qt.QWidgetItem):
                    w = child.widget()
                    w.hide()
                    w.close()
                    w.setParent(None)
                    layout.removeWidget(w)
                    if hasattr(w, "deleteLater"):
                        w.deleteLater()
                        logger.debug("WL %s" % type(w))
                    else:
                        logger.debug("WW %s" % type(w))
                    Qt.QObjectCleanupHandler().add(w)
                    del w
                    w = None
                del child
            Qt.QWidget().setLayout(layout)
