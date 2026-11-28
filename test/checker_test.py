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
# \file checker_test.py
# unittests for comparisons of measurement group configurations
#
import json
import unittest

from nxsselector.ServerState import Checker


def conf(runtime=True):
    ch1 = {"name": "exp_c01", "index": 0, "enabled": True}
    ch2 = {"name": "lima", "index": 1, "enabled": True}
    if runtime:
        ch1["value_stream_ref"] = {}
        ch2["value_stream_ref"] = {"backend": "blissdata",
                                   "scan_key": "esrf:scan:1"}
    ctrl1 = {"synchronization": 0, "channels": {"expchan/c/1": ch1}}
    ctrl2 = {"units": {"0": {"channels": {"expchan/l/1": ch2}}}}
    if runtime:
        ctrl1["streamable"] = True
        ctrl2["units"]["0"]["streamable"] = True
    return {"label": "mg1", "timer": "exp_t01",
            "controllers": {"ctrl1": ctrl1, "ctrl2": ctrl2}}


class CheckerTest(unittest.TestCase):

    def test_strip(self):
        checker = Checker()
        mgconf = conf()
        self.assertEqual(checker.stripMntGrp(mgconf), conf(False))
        # the given configuration is not changed
        self.assertEqual(mgconf, conf())
        self.assertEqual(
            json.loads(checker.stripMntGrp(json.dumps(conf()))), conf(False))
        # configurations of older Sardana versions stay the same
        self.assertEqual(checker.stripMntGrp(conf(False)), conf(False))
        for value in ["", "[1]", "{wrong"]:
            self.assertEqual(checker.stripMntGrp(value), value)

    def test_runtime_keys_are_ignored(self):
        checker = Checker()
        self.assertTrue(checker.compDict(
            checker.stripMntGrp(conf()), checker.stripMntGrp(conf(False))))
        other = conf()
        other["timer"] = "exp_t02"
        self.assertFalse(checker.compDict(
            checker.stripMntGrp(other), checker.stripMntGrp(conf(False))))

    def test_compdict(self):
        checker = Checker()
        self.assertTrue(checker.compDict({}, {}))
        self.assertTrue(checker.compDict(conf(), conf()))
        self.assertFalse(checker.compDict(conf(), []))
        self.assertFalse(checker.compDict({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(checker.compDict({"a": 1}, {"b": 1}))
        # all nested dictionaries are compared, not only the first one
        c1 = {"a": {"x": 1}, "b": {"y": 1}}
        c2 = {"a": {"x": 1}, "b": {"y": 2}}
        self.assertFalse(checker.compDict(c1, c2))
        self.assertFalse(checker.compDict(c2, c1))
        c3 = {"a": {"x": 1}, "z": 3}
        self.assertFalse(checker.compDict(c3, {"a": {"x": 1}, "z": 4}))
        # changes of later controllers are found
        other = conf(False)
        other["controllers"]["ctrl2"]["units"]["0"]["channels"][
            "expchan/l/1"]["enabled"] = False
        self.assertFalse(checker.compDict(conf(False), other))
        # special keys of profiles
        p1 = {"DataSourceSelection": json.dumps({"a": True}),
              "PreselectingDataSources": json.dumps(["a", "b"]),
              "Other": "1"}
        p2 = {"DataSourceSelection": json.dumps({"a": True}),
              "PreselectingDataSources": json.dumps(["b", "a"]),
              "Other": "1"}
        self.assertTrue(checker.compDict(p1, p2, True))
        self.assertFalse(checker.compDict(p1, p2))
        p2["Other"] = "2"
        self.assertFalse(checker.compDict(p1, p2, True))
        p2["Other"] = "1"
        p2["DataSourceSelection"] = json.dumps({"a": False})
        self.assertFalse(checker.compDict(p1, p2, True))


if __name__ == '__main__':
    unittest.main()
