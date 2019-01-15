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
# DynamicTools

""" dynamic widget tools """

import logging
#: (:obj:`logging.Logger`) logger object
logger = logging.getLogger(__name__)

try:
    from taurus.external.qt import Qt
except Exception:
    from taurus.qt import Qt


class DynamicTools(object):
    """  dynamic widget tools """

    @classmethod
    def cleanupObjects(cls, objects, label=None):
        """ cleans up qt objects

        :param objects: qt objects to be cleaned up
        :type objects: :obj:`list` <:class:`taurus.qt.Qt.QObject`>
        :param label: qt objects label
        :type label: :obj:`str`
        """

        while objects:
            la = objects.pop()
            try:
                if hasattr(la, "deleteLater"):
                    la.deleteLater()
                if label:
                    logger.debug("del %s" % label)
            except Exception:
                if label:
                    logger.debug("ERROR del %s" % label)

    @classmethod
    def cleanupWidgets(cls, widgets, label=None):
        """ cleans up qt widgets

        :param widgets: qt widgets to be cleaned up
        :type widgets: :obj:`list` <:class:`taurus.qt.Qt.QWidget`>
        :param label: qt object label
        :type label: :obj:`str`
        """
        while widgets:
            wg = widgets.pop()
            if hasattr(wg, "clearLayout"):
                wg.clearLayout()
            try:
                wg.hide()
                wg.close()
                if hasattr(wg, "deleteLater"):
                    wg.deleteLater()
                if label:
                    logger.debug("del %s" % label)
            except Exception:
                if label:
                    logger.debug("ERROR del %s" % label)

    @classmethod
    def cleanupFrames(cls, frames, label=None):
        """ cleans up qt widgets

        :param frames: qt frames to be cleaned up
        :type frames: :obj:`list` <:class:`taurus.qt.Qt.QFrame`>
        :param label: qt object label
        :type label: :obj:`str`
        """
        while frames:
            fr = frames.pop()
            try:
                fr.hide()
                fr.close()
                if label:
                    logger.debug("del %s" % label)
            except Exception:
                if label:
                    logger.debug("ERROR del %s" % label)

    @classmethod
    def cleanupLayoutWithItems(cls, layout):
        """ cleans up qt layout with its items

        :param layout: qt layout to be cleaned up
        :type layout: :class:`taurus.qt.Qt.QLayout`>
        """
        if layout:
            logger.debug("COUNTS %s" % layout.count())
            while layout.count():
                child = layout.itemAt(0)
                layout.removeItem(child)
                if isinstance(child, Qt.QWidgetItem):
                    w = child.widget()
                    w.hide()
                    w.close()
                    layout.removeWidget(w)
                    if hasattr(w, "deleteLater"):
                        w.deleteLater()
                        logger.debug("WL %s" % type(w))
                    else:
                        logger.debug("WW %s" % type(w))
                    w = None
            Qt.QWidget().setLayout(layout)
