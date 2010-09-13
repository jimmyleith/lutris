# -*- coding:Utf-8 -*-
###############################################################################
## Lutris
##
## Copyright (C) 2009, 2010 Mathieu Comandon <strycore@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

import subprocess
import platform
import hashlib
import logging

from lutris.config import LutrisConfig

class Runner(object):
    """Generic runner (base class for other runners) """

    def __init__(self):
        """ Initialize runner """
        self.executable = None
        self.is_installable = False
        self.arguments = []
        self.error_messages = []
        self.game = None
        self.depends = None

    def load(self, game):
        """ Load a game """
        self.game = game

    def play(self):
        pass

    def check_depends(self):
        """Check if all the dependencies for a runner are installed."""
        if not self.depends:
            return true

        classname = "lutris.runners." + self.depends
        parts = classname.split('.')
        module = ".".join(parts[:-1])
        module = __import__(module)
        for component in parts[1:]:
            module = getattr(module, component)
        runner = getattr(module, self.depends)
        runner_instance = runner()

        return runner_instance.is_installed()

    def is_installed(self):
        """ Check if runner is installed

        Return a boolean
        """
        is_installed = False
        if not self.executable:
            return False
        cmdline = "which " + self.executable
        cmdline = str.split(cmdline, " ")
        result = subprocess.Popen(cmdline, stdout=subprocess.PIPE).communicate()[0]
        if result == '' :
            is_installed = False
        else:
            is_installed = True
        return is_installed

    def get_game_options(self):
        return None

    def get_runner_options(self):
        return None

    def md5sum(self, filename):
        md5check = hashlib.md5()
        file_ = open(filename, "rb")
        content = file_.readlines()
        file_.close()
        for line in content:
            md5check.update(line)
        return md5check.hexdigest()

    def install(self):
        """Install runner using package management systems."""

        # Return false if runner has no package, must be then another method
        # and install method should be overridden by the specific runner
        if not hasattr(self, 'package'):
            return False
        linux_dist = platform.dist()[0]

        #Add the package manager with arguments for your favorite distro :)
        if linux_dist == 'Ubuntu' or linux_dist == 'Debian':
            package_manager = 'apt-get'
            install_args = '-y install'
        elif linux_dist == 'Fedora':
            package_manager = 'yum'
            install_args = 'install'
        else:
            logging.error("The distribution you're running is not supported yet.")
            logging.error("Edit runners/runner.py to add support for it")
            return False

        if hasattr(self, "ppa"):
            if (linux_dist != "Ubuntu"):
                print "this runner requires a ppa to be installed"
                #TODO : check if the PPA is already installed
                #TODO : check the ubuntu version available for the ppa,
                #       choose the one corresponding to the current install
                #       or the closest one.     
                subprocess.Popen('gksu add-apt-repository %s' % self.ppa)
                subprocess.Popen('gksu apt-get update')

        print subprocess.Popen("gksu \"%s %s %s\"" % (package_manager,
                                                      install_args,
                                                      self.package),
                               shell=True,
                               stdout=subprocess.PIPE).communicate()[0]

    def write_config(self, id, name, fullpath):
        """Write game configuration to settings directory."""
        system = self.__class__.__name__
        index = fullpath.rindex("/")
        exe = fullpath[index + 1:]
        path = fullpath[:index]
        if path.startswith("file://"):
            path = path[7:]
        gameConfig = LutrisConfig()
        gameConfig.config = {
                "main": {
                    "path": path,
                    "exe":exe,
                    "realname": name,
                    "runner": system
                    }
                }
        gameConfig.save(id, values)