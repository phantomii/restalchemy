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

from restalchemy.common import exceptions as exc
from restalchemy.orm import base


class BaseProperty(base.AbstractProperty):
    pass


def Property(value_type, default=None, required=False,
             read_only=False):

    class PropertyClass(BaseProperty):

        def __init__(self):
            super(PropertyClass, self).__init__()
            self.__value_type = (value_type() if type(value_type) == type
                                 else value_type)
            self.__default = self._safe_value(default()) if callable(
                default) else self._safe_value(default)
            self.__value = None
            self._required = required
            self._read_only = read_only

        def _safe_value(self, value):
            if self.__value_type.validate(value):
                return value
            else:
                raise exc.ValueError(class_name=self.__value_type.__class__,
                                     value=value)

        @property
        def value(self):
            return self.__default if (self.__value == None and
                                      self.__default != None) else self.__value

        @value.setter
        def value(self, value):
            if self._read_only:
                raise exc.ReadOnlyPropertyError()
            self.__value = self._safe_value(value)

    return PropertyClass
