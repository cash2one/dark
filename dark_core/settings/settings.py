import six
import json
import copy
from collections import MutableMapping
from importlib import import_module

import default_settings


class SettingsAttribute(object):
    """Class for storing data related to settings attributes.

    This class is intended for internal usage, you should try Settings class
    for settings configuration, not this one.
    """

    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def __str__(self):
        return "<SettingsAttribute value={self.value!r}> ".format(self=self)

    __repr__ = __str__


class Settings(object):
    def __init__(self, values=None):
        self.frozen = False
        self.attributes = {}
        self.setmodule(default_settings)

    def __getitem__(self, opt_name):
        value = None
        if opt_name in self.attributes:
            value = self.attributes[opt_name].value
        return value

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getbool(self, name, default=False):
        return bool(int(self.get(name, default)))

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0):
        return float(self.get(name, default))

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value, six.string_types):
            value = value.split(',')
        return list(value)

    def getdict(self, name, default=None):
        value = self.get(name, default or {})
        if isinstance(value, six.string_types):
            value = json.loads(value)
        return dict(value)

    def set(self, name, value):
        self._assert_mutability()
        if name not in self.attributes:
            self.attributes[name] = SettingsAttribute(value)
        else:
            self.attributes[name].set(value)

    def setdict(self, values):
        self._assert_mutability()
        for name, value in six.iteritems(values):
            self.set(name, value)

    def setmodule(self, module):
        self._assert_mutability()
        if isinstance(module, six.string_types):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def _assert_mutability(self):
        if self.frozen:
            raise TypeError("Trying to modify an immutable Settings object")

    def copy(self):
        return copy.deepcopy(self)

    def freeze(self):
        self.frozen = True

    def frozencopy(self):
        copy = self.copy()
        copy.freeze()
        return copy


def iter_default_settings():
    """Return the default settings as an iterator of (name, value) tuples"""
    for name in dir(default_settings):
        if name.isupper():
            yield name, getattr(default_settings, name)


settings = Settings()

if __name__ == "__main__":
    settings = Settings()
    print settings.get("BL_COLUMNS")
