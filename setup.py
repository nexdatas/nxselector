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


""" setup.py for setting NeXus Sardana Recorder """

import os
import sys
from distutils.util import get_platform
from distutils.core import setup
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.install_scripts import install_scripts
import shutil

#: package name
TOOL = "nxsselector"
#: package instance
ITOOL = __import__(TOOL)


from sphinx.setup_command import BuildDoc

def read(fname):
    """ read the file 

    :param fname: readme file name
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

UIDIR = os.path.join(TOOL, "ui")
QRCDIR = os.path.join(TOOL, "qrc")
SCRIPTS = ['nxselector']


class toolBuild(build):
    """ ui and qrc builder for python
    """

    @classmethod
    def makeqrc(cls, qfile, path):
        """  creates the python qrc files
        
        :param qfile: qrc file name
        :param path:  qrc file path
        """
        qrcfile = os.path.join(path, "%s.qrc" % qfile)
        rccfile = os.path.join(path, "%s.rcc" % qfile)

        compiled = os.system("rcc %s -o %s -binary" % (qrcfile, rccfile))
        if compiled == 0:
            print "Built: %s -> %s" % (qrcfile, rccfile)
        else:
            print >> sys.stderr, "Error: Cannot build  %s" % (rccfile)


    def run(self):
        """ runner

        :\brief: It is running during building
        """

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


class toolClean(clean):
    """ cleaner for python
    """

    def run(self):
        """ runner
        
        :brief: It is running during cleaning
        """

        cfiles = [os.path.join(TOOL, cfile) for cfile
                  in os.listdir("%s" % TOOL) if cfile.endswith('.pyc')]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(UIDIR, cfile) for cfile
                  in os.listdir(UIDIR) if (
                cfile.endswith('.pyc') or
                (cfile.endswith('.py')
                 and not cfile.endswith('__init__.py')))]
        for fl in cfiles:
            os.remove(str(fl))

        cfiles = [os.path.join(QRCDIR, cfile) for cfile
                  in os.listdir(QRCDIR) if ( 
                cfile.endswith('.pyc')
                or cfile.endswith('.rcc') or 
                (cfile.endswith('.py')
                 and not cfile.endswith('__init__.py')))]
        for fl in cfiles:
            os.remove(str(fl))

        if get_platform()[:3] == 'win':
            for script in SCRIPTS:
                if os.path.exists(script + ".pyw"):
                    os.remove(script + ".pyw")
        clean.run(self)


def get_scripts(scripts):
    """ provides windows names of python scripts

    :param scripts: list of script names
    """
    if get_platform()[:3] == 'win':
        return scripts + [sc + '.pyw' for sc in scripts]
    return scripts

package_data = {
    'nxsselector': ['ui/*.ui', 'qrc/*.rcc']
}

release = ITOOL.__version__
version = ".".join(release.split(".")[:2])
name = "NXS Component Selector"


#: metadata for distutils
SETUPDATA = dict(
    name="nxsselector",
    version=ITOOL.__version__,
    author="Jan Kotanski",
    author_email="jankotan@gmail.com",
    maintainer="Jan Kotanski",
    maintainer_email="jankotan@gmail.com",
    description=("GUI for Setting Nexus Sardana Recorder"),
    license=read('COPYRIGHT'),
#    license="GNU GENERAL PUBLIC LICENSE, version 3",
    keywords="configuration scan nexus sardana recorder tango component data",
    url="https://github.com/jkotan/nexdatas",
    platforms=("Linux", " Windows", " MacOS "),
    packages=[TOOL, UIDIR, QRCDIR],
    package_data=package_data,
    scripts=get_scripts(SCRIPTS),
    cmdclass={"build": toolBuild, "clean": toolClean,
              'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release)}},
    long_description=read('README.rst')
)


## the main function
def main():
    setup(**SETUPDATA)

if __name__ == '__main__':
    main()
