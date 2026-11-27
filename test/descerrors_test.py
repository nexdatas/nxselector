#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2018 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package test nexdatas
# \file XMLConfiguratorTest.py
# unittests for field Tags running Tango Server
#
# \file descerrors_test.py
# unittests for descriptive datasources and their errors
#
import json
import unittest

from nxsselector import Storage as StorageModule
from nxsselector.ServerState import ServerState

try:
    from taurus.external.qt import Qt
    APP = Qt.QApplication.instance() or Qt.QApplication([])
except Exception:
    APP = None


class FakeState(object):
    """ server state stand-in """

    def __init__(self):
        self.mcplist = []
        self.mutedChannels = []
        self.avcplist = ["slits"]
        self.acpgroup = {"slits": True}
        self.avdslist = ["energy"]
        self.idsgroup = {"energy": True}
        self.motors = []
        self.ioregisters = []
        self.ddsdict = {}
        self.created = []

    def stepComponents(self):
        return []

    def clientDataSources(self):
        return []

    def createDataSources(self, datasources):
        self.created.append(dict(datasources))


class FakeGroupsDlg(object):
    """ groups dialog stand-in creating a datasource """

    def __init__(self, parent=None):
        self.newdatasources = {}
        self.dirty = False
        self.components = {}
        self.datasources = {}

    def createGUI(self):
        pass

    def exec_(self):
        self.newdatasources = {"mypath": "haso:10000/p/dev/1/Path"}
        self.datasources["mypath"] = True
        self.dirty = True


class UI(object):
    storage = None


class DescErrorsTest(unittest.TestCase):

    def test_error_messages(self):
        state = ServerState.__new__(ServerState)
        state.errors = [
            json.dumps({"component": "mypath",
                        "datasource": "mypath [p/dev/1/Path]",
                        "message": "Empty Attribute"}),
            json.dumps({"component": "slits", "datasource": "...",
                        "message": "slits not defined in Configuration "
                                   "Server"}),
            json.dumps({"component": "mypath", "datasource": "mypath",
                        "message": "ALARM STATE"}),
            "plain error",
        ]
        self.assertEqual(state.errorMessages("mypath"), [
            "mypath [p/dev/1/Path]: Empty Attribute", "ALARM STATE"])
        self.assertEqual(state.errorMessages("slits"), [
            "...: slits not defined in Configuration Server"])
        self.assertEqual(state.errorMessages("other"), [])
        state.errors = None
        self.assertEqual(state.errorMessages("mypath"), [])

    @unittest.skipIf(APP is None, "Qt is not available")
    def test_descriptive_datasources_are_created(self):
        state = FakeState()
        # only the dialog handling of Storage is used
        storage = StorageModule.Storage.__new__(StorageModule.Storage)
        Qt.QObject.__init__(storage)
        storage.ui = UI()
        storage.state = state
        orig = StorageModule.GroupsDlg
        StorageModule.GroupsDlg = FakeGroupsDlg
        try:
            storage._Storage__descgroups()
        finally:
            StorageModule.GroupsDlg = orig
        # datasources created in the Descriptions tab exist on the server
        self.assertEqual(state.created,
                         [{"mypath": "haso:10000/p/dev/1/Path"}])
        self.assertEqual(state.idsgroup["mypath"], True)


if __name__ == '__main__':
    unittest.main()
