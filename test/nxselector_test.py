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
import unittest
import os
import sys
import random
import struct
import binascii
# import time
# import threading
# import PyTango
# import json
import nxsselector
from nxsselector import Selector


try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


if sys.version_info > (3,):
    unicode = str
    long = int


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

# from nxsconfigserver.XMLConfigurator  import XMLConfigurator
# from nxsconfigserver.Merger import Merger
# from nxsconfigserver.Errors import (
# NonregisteredDBRecordError, UndefinedTagError,
#                                    IncompatibleNodeError)
# import nxsconfigserver


def myinput(w, text):
    myio = os.fdopen(w, 'w')
    myio.write(text)

    # myio.close()


# test fixture
class NXSSelectorTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self.helperror = "Error: too few arguments\n"

        self.helpinfo = """Usage: nxselector [options]

Options:
  -h, --help            show this help message and exit
  -s SERVER, --server=SERVER
                        selector server
  -d DOOR, --door=DOOR  door device name
  -t STYLE, --style=STYLE
                        Qt style
  -y STYLESHEET, --stylesheet=STYLESHEET
                        Qt stylesheet
  -m MODE, --mode=MODE  interface mode, i.e. simple, user, advanced, special,
                        expert
  --set-as-default-mode
                        set the current mode as default
  --dont-switch-mntgrp  do not switch MntGrp to the ActiveMntGrp
  --version             show program's version number and exit

  Taurus Options:
    Basic options present in any taurus application

    --taurus-log-level=LEVEL
                        taurus log level. Allowed values are (case
                        insensitive): critical, error, warning/warn, info,
                        debug, trace
    --taurus-polling-period=MILLISEC
                        taurus global polling period in milliseconds
    --taurus-serialization-mode=SERIAL
                        taurus serialization mode. Allowed values are (case
                        insensitive): serial, concurrent (default)
    --tango-host=TANGO_HOST
                        Tango host name (either HOST:PORT or a Taurus URI,
                        e.g. tango://foo:1234)
    --remote-console-port=PORT
                        enables remote debugging using the given port
    --default-formatter=FORMATTER
                        Override the default formatter
"""

        try:
            # random seed
            self.seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            # random seed
            self.seed = long(time.time() * 256)  # use fractional seconds

        self.__rnd = random.Random(self.seed)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__args = '{"host":"localhost", "db":"nxsconfig", ' \
                      '"read_default_file":"/etc/my.cnf", "use_unicode":true}'
        self.__cmps = []
        self.__ds = []
        self.__man = []
        self.children = ("record", "doc", "device", "database", "query",
                         "datasource", "result")

        from os.path import expanduser
        home = expanduser("~")
        self.__args2 = '{"host":"localhost", "db":"nxsconfig", ' \
                       '"read_default_file":"%s/.my.cnf", ' \
                       '"use_unicode":true}' % home

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # comp_available test
    # \brief It tests NXSelector
    def mtest_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = mystdout = StringIO()
        sys.stderr = mystderr = StringIO()
        old_argv = sys.argv
        sys.argv = ['nxselector']
        try:
            with self.assertRaises(SystemExit):
                Selector.main()
        except Exception:
            Selector.main()

        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        vl = mystdout.getvalue()
        er = mystderr.getvalue()
        print(vl)
        print(er)
        # self.assertEqual(self.helpinfo, vl)
        # self.assertEqual(self.helperror, er)

    # comp_available test
    # \brief It tests NXSelector
    def test_version(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        ver = nxsselector.__version__
        self.assertTrue(ver)
        self.assertTrue("." in ver)

    # comp_available tesQt
    # \brief It tests XMLConfigurator
    def test_help(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        helps = ['--help']
        for hl in helps:
            print(hl)
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = mystdout = StringIO()
            sys.stderr = mystderr = StringIO()
            old_argv = sys.argv
            sys.argv = ['nxselector', hl]
            try:
                with self.assertRaises(SystemExit):
                    Selector.main()
            except Exception:
                Selector.main()

            sys.argv = old_argv
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            vl = mystdout.getvalue()
            er = mystderr.getvalue()
            self.assertTrue(vl.endswith(self.helpinfo))
            self.assertEqual('', er)

    # comp_available tesQt
    # \brief It tests XMLConfigurator
    def test_help2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        helps = ['-h']
        for hl in helps:
            print(hl)
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = mystdout = StringIO()
            sys.stderr = mystderr = StringIO()
            old_argv = sys.argv
            sys.argv = ['nxselector', hl]
            try:
                with self.assertRaises(SystemExit):
                    Selector.main()
            except Exception:
                Selector.main()

            sys.argv = old_argv
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            vl = mystdout.getvalue()
            er = mystderr.getvalue()
            self.assertTrue(vl.endswith(self.helpinfo))
            self.assertEqual('', er)


if __name__ == '__main__':
    unittest.main()
