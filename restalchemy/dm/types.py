# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Eugene Frolov <eugene@frolov.net.ru>
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc
import copy
import re


UUID_RE_TEMPLATE = "[a-f0-9]{8,8}-([a-f0-9]{4,4}-){3,3}[a-f0-9]{12,12}"


class BaseType(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, value):
        pass


class BaseRegExpType(BaseType):

    def __init__(self, pattern):
        super(BaseType, self).__init__()
        self._pattern = re.compile(pattern)

    def validate(self, value):
        try:
            return self._pattern.match(value) is not None
        except TypeError:
            return False


# TODO(Eugene Frolov): Check uuid using UUID form uuid module
class UUID(BaseRegExpType):

    def __init__(self):
        super(UUID, self).__init__(pattern="^%s$" % UUID_RE_TEMPLATE)


class Uri(BaseRegExpType):

    def __init__(self):
        super(Uri, self).__init__(pattern="^(/[A-Za-z0-9\-_]*)*/%s$" %
                                  UUID_RE_TEMPLATE)


class Mac(BaseRegExpType):

    def __init__(self):
        super(Mac, self).__init__("^([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}$")


class BasePythonType(BaseType):

    def __init__(self, python_type):
        super(BasePythonType, self).__init__()
        self._python_type = python_type

    def validate(self, value):
        return isinstance(value, self._python_type)


class String(BasePythonType):

    #TODO(Eugene Frolov): Make possible to create "infinite" value
    def __init__(self, min_length=0, max_length=255):
        super(String, self).__init__(basestring)
        self.min_length = int(min_length)
        self.max_length = int(max_length)

    def validate(self, value):
        result = super(String, self).validate(value)
        l = len(str(value))
        return result and l >= self.min_length and l <= self.max_length


class Integer(BasePythonType):

    #TODO(Eugene Frolov): Make possible to create "infinite" value
    def __init__(self, min_value=0, max_value=65535):
        super(Integer, self).__init__(int)
        self.min_value = int(min_value)
        self.max_value = int(max_value)

    def validate(self, value):
        result = super(Integer, self).validate(value)
        return result and value >= self.min_value and value <= self.max_value


class Dict(BasePythonType):

    def __init__(self):
        super(Dict, self).__init__(dict)


class Enum(BaseType):

    def __init__(self, enum_values):
        super(Enum, self).__init__()
        self._enums_values = copy.deepcopy(enum_values)

    def validate(self, value):
        return value in self._enums_values
