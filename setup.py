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
## \file setup.py
# GUI for setting NeXus Sardana Recorder

""" setup.py for NXS Component Designer """

import os
import sys
from distutils.util import get_platform
from distutils.core import setup
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_scripts import install_scripts
import shutil

## package name
TOOL = "nxselector"
## package instance
ITOOL = __import__(TOOL)


## reading a file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

UIDIR = os.path.join(TOOL, "ui")
QRCDIR = os.path.join(TOOL, "qrc")
SCRIPTS = ['nxscomp_selector']


## ui and qrc builder for python
class toolBuild(build):

    ## creates the python qrc files
    # \param qfile qrc file name
    # \param path  qrc file path
    @classmethod
    def makeqrc(cls, qfile, path):
        qrcfile = os.path.join(path, "%s.qrc" % qfile)
        pyfile = os.path.join(path, "qrc_%s.py" % qfile)

        compiled = os.system("pyrcc4 %s -o %s" % (qrcfile, pyfile))
        if compiled == 0:
            print "Built: %s -> %s" % (qrcfile, pyfile)
        else:
            print >> sys.stderr, "Error: Cannot build  %s" % (pyfile)

    ## creates the python ui files
    # \param ufile ui file name
    # \param path  ui file path
    @classmethod
    def makeui(cls, ufile, path):
        uifile = os.path.join(path, "%s.ui" % ufile)
        pyfile = os.path.join(path, "ui_%s.py" % ufile)
        compiled = os.system("pyuic4 %s -o %s" % (uifile, pyfile))
        if compiled == 0:
            print "Compiled %s -> %s" % (uifile, pyfile)
        else:
            print >> sys.stderr,  "Error: Cannot build %s" % (pyfile)

    ## runner
    # \brief It is running during building
    def run(self):
        try:
            ufiles = [(ufile[:-3],
                       UIDIR) for ufile
                      in os.listdir(UIDIR) if ufile.endswith('.ui')]
            for ui in ufiles:
                if not ui[0] in (".", ".."):
                    self.makeui(ui[0], ui[1])
        except TypeError as e:
            print >> sys.stderr, "No .ui files to build", e

        try:
            qfiles = [(qfile[:-4], QRCDIR) for qfile
                      in os.listdir(QRCDIR) if qfile.endswith('.qrc')]
            for qrc in qfiles:
                if not qrc[0] in (".", ".."):
                    self.makeqrc(qrc[0], qrc[1])
        except TypeError:
            print >> sys.stderr, "No .qrc files to build"

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                shutil.copy(script, script + ".pyw")
        build.run(self)


## cleaner for python
class toolClean(clean):

    ## runner
    # \brief It is running during cleaning
    def run(self):

        cfiles = [os.path.join(TOOL, cfile) for cfile
                  in os.listdir("%s" % TOOL) if cfile.endswith('.pyc')]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(UIDIR, cfile) for cfile
                  in os.listdir(UIDIR) if cfile.endswith('.pyc') or
                  (cfile.endswith('.py')
                   and cfile.endswith('__init_.py'))]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(QRCDIR, cfile) for cfile
                  in os.listdir(QRCDIR) if cfile.endswith('.pyc')
                  or (cfile.endswith('.py')
                      and cfile.endswith('__init_.py'))]
        for fl in cfiles:
            os.remove(str(fl))

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                if os.path.exists(script + ".pyw"):
                    os.remove(script + ".pyw")
        clean.run(self)


## provides windows scripts
def get_scripts(scripts):
    if get_platform()[:3] == 'win':
        return scripts + [sc + '.pyw' for sc in scripts]
    return scripts

## metadata for distutils
SETUPDATA = dict(
    name="nxselector",
    version=ITOOL.__version__,
    author="Jan Kotanski",
    author_email="jankotan@gmail.com",
    maintainer="Jan Kotanski",
    maintainer_email="jankotan@gmail.com",
    description=("GUI for Setting Nexus Sardana Recorder"),
    license=read('COPYRIGHT'),
#    license="GNU GENERAL PUBLIC LICENSE, version 3",
    keywords="configuration scan nexus sardana recorder tango component data",
    url="http://www.desy.de/~jkotan/",
    platforms=("Linux", " Windows", " MacOS "),
    packages=[TOOL, UIDIR, QRCDIR],
    scripts=get_scripts(SCRIPTS),
    long_description=read('README'),
    cmdclass={"build": toolBuild, "clean": toolClean}
)


## the main function
def main():
    setup(**SETUPDATA)

if __name__ == '__main__':
    main()
