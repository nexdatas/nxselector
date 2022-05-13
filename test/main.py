#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \file runtest.py
# the unittest runner
#

import sys
import unittest

import nxselector_test

try:
    __import__("PyTango")
    # if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError as e:
    PYTANGO_AVAILABLE = False
    print("PyTango is not available: %s" % e)

try:
    try:
        __import__("pni.io.nx.h5")
    except Exception:
        __import__("pni.nx.h5")
    # if module pni avalable
    PNI_AVAILABLE = True
except Exception as e:
    PNI_AVAILABLE = False
    print("pni is not available: %s" % e)

try:
    __import__("h5py")
    # if module pni avalable
    H5PY_AVAILABLE = True
except Exception as e:
    H5PY_AVAILABLE = False
    print("h5py is not available: %s" % e)

try:
    __import__("pninexus.h5cpp")
    # if module pni avalable
    H5CPP_AVAILABLE = True
except Exception as e:
    H5CPP_AVAILABLE = False
    print("h5cpp is not available: %s" % e)


if not PNI_AVAILABLE and not H5PY_AVAILABLE and not H5CPP_AVAILABLE:
    raise Exception("Please install h5py, h5cpp or pni")

# if PNI_AVAILABLE:
# if H5PY_AVAILABLE:
# if PNI_AVAILABLE and H5PY_AVAILABLE:


# list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    # connection arguments to MYSQL DB
    args = {}
    args["db"] = 'tango'
    args["read_default_file"] = '/etc/my.cnf'
    # inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except Exception:
    try:
        import MySQLdb
        from os.path import expanduser
        home = expanduser("~")
        # connection arguments to MYSQL DB
        args2 = {'db': u'tango',
            'read_default_file': u'%s/.my.cnf' % home, 'use_unicode': True
        }
        # inscance of MySQLdb
        mydb = MySQLdb.connect(**args2)
        mydb.close()
        DB_AVAILABLE.append("MYSQL")

    except ImportError as e:
        print("MYSQL not available: %s" % e)
    except Exception as e:
        print("MYSQL not available: %s" % e)
    except Exception:
        print("MYSQL not available")


try:
    import psycopg2
    # connection arguments to PGSQL DB
    args = {}
    args["database"] = 'mydb'
    # inscance of psycog2
    pgdb = psycopg2.connect(**args)
    pgdb.close()
    DB_AVAILABLE.append("PGSQL")
except ImportError as e:
    print("PGSQL not available: %s" % e)
except Exception as e:
    print("PGSQL not available: %s" % e)
except Exception:
    print("PGSQL not available")


try:
    import cx_Oracle
    passwd = ""
    # pwd
    # passwd = open(
    #    '%s/pwd' % os.path.dirname(ConvertersTest.__file__)).read()[:-1]

    # connection arguments to ORACLE DB
    args = {}
    args["dsn"] = \
        "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=dbsrv01.desy.de)" \
        "(PORT=1521))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVER=DEDICATED)" \
        "(SERVICE_NAME=desy_db.desy.de)(FAILOVER_MODE=(TYPE=NONE)" \
        "(METHOD=BASIC)(RETRIES=180)(DELAY=5))))"
    args["user"] = "read"
    args["password"] = passwd
    # inscance of cx_Oracle
    ordb = cx_Oracle.connect(**args)
    ordb.close()
    DB_AVAILABLE.append("ORACLE")
except ImportError as e:
    print("ORACLE not available: %s" % e)
except Exception as e:
    print("ORACLE not available: %s" % e)
except Exception:
    print("ORACLE not available")


# main function
def main():

    # test server
    # ts = None

    # test suit
    suite = unittest.TestSuite()

    suite.addTests(
          unittest.defaultTestLoader.loadTestsFromModule(
              nxselector_test)
    )

    # test runner
    runner = unittest.TextTestRunner()
    # test result
    result = runner.run(suite).wasSuccessful()
    sys.exit(not result)

    #   if ts:
    #       ts.tearDown()


if __name__ == "__main__":
    main()
