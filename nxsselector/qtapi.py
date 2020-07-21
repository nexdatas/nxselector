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
# Main window of the application

""" main window application dialog """

import os

qt_api = os.getenv("QT_API", os.getenv('DEFAULT_QT_API', 'pyqt5'))
if qt_api != 'pyqt4':
    try:
        __import__("PyQt5")
        qt_api = 'pyqt5'
    except Exception:
        __import__("PyQt4")
        qt_api = 'pyqt4'
else:
    __import__("PyQt4")
    qt_api = 'pyqt4'


__all__ = ["qt_api"]
