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

import re


UUID_RE_TEMPLATE = "[a-f0-9]{8,8}-([a-f0-9]{4,4}-){3,3}[a-f0-9]{12,12}"


class BaseType(object):

    def __init__(self, pattern):
        super(BaseType, self).__init__()
        self._pattern = re.compile(pattern)

    def validate(self, value):
        return True if (value == None or self._pattern.match(value)) else False


class UUIDType(BaseType):

    def __init__(self):
        super(UUIDType, self).__init__(pattern="^%s$" % UUID_RE_TEMPLATE)


class StringType(BaseType):

    def __init__(self, min_length=0, max_length=255):
        super(StringType, self).__init__(pattern="^.{%d,%d}$" % (
            min_length, max_length))


class UriType(BaseType):

    def __init__(self):
        super(UriType, self).__init__(pattern="^(/[a-z0-9\-_]*)*/%s$" %
                                      UUID_RE_TEMPLATE)


class MacType(BaseType):

    def __init__(self):
        super(MacType, self).__init__("^([0-9a-f]{2,2}:){5,5}[0-9a-f]{2,2}$")


class BasePythonType(object):

    def __init__(self, python_type):
        self._python_type = python_type

    def validate(self, value):
        return isinstance(value, self._python_type)


class IntegerType(BasePythonType):

    def __init__(self, min_value=0, max_value=65535):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        return (isinstance(value, int) and value >= self.min_value and
                value <= self.max_value)


class DictType(BasePythonType):

    def __init__(self):
        super(DictType, self).__init__(dict)


class EnumType(object):

    def __init__(self, enum_values):
        self._enums_values = enum_values

    def validate(self, value):
        return value in self._enums_values
