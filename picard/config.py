# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from PyQt4 import QtCore

class ConfigSection(object):
    """Configuration section."""

    def __init__(self, config, name):
        self.__dict__["_config"] = config
        self.__dict__["_name"] = name

    def __getattr__(self, name):
        opt = Option.get(self._name, name)
        key = "%s/%s" % (self._name, name)
        if self._config.contains(key):
            return opt.convert(self._config.value(key))
        return opt.default

    def __setattr__(self, name, value):
        self._config.setValue("%s/%s" % (self._name, name),
                              QtCore.QVariant(value))

class Config(QtCore.QSettings):
    """Configuration."""

    def __init__(self):
        """Initializes the configuration."""
        QtCore.QSettings.__init__(self, "MusicBrainz",
                                  "MusicBrainz Picard 1.0")
        self.setting = ConfigSection(self, "setting")
        self.persist = ConfigSection(self, "persist")
        self.profile = ConfigSection(self, "profile/default")
        self.current_preset = "default"

    def switchProfile(self, profilename):
        """Sets the current profile."""
        key = u"profile/%s" % (profilename,)
        if self.contains(key):
            self.profile.name = key
        else:
            raise ConfigError, "Unknown profile '%s'" % (profilename,) 

class Option(QtCore.QObject):
    """Generic option."""

    registry = {}

    def __init__(self, section, name, default, convert=None):
        self.section = section
        self.name = name
        self.default = default
        self.convert = convert
        if not self.convert:
            self.convert = type(self.default)
        self.registry[(self.section, self.name)] = self

    @classmethod
    def get(cls, section, name):
        try:
            return cls.registry[(section, name)]
        except KeyError:
            raise KeyError, "Option %s.%s not found." % (section, name)

class TextOption(Option):
    """Option with a text value."""

    def __init__(self, section, name, default):
        def convert(value):
            return unicode(value.toString())
        Option.__init__(self, section, name, default, convert)

class BoolOption(Option):
    """Option with a boolean value."""

    def __init__(self, section, name, default):
        Option.__init__(self, section, name, default, QtCore.QVariant.toBool)

class IntOption(Option):
    """Option with an integer value."""

    def __init__(self, section, name, default):
        def convert(value):
            return value.toInt()[0]
        Option.__init__(self, section, name, default, convert)

