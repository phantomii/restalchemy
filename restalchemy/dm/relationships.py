#!/usr/bin/env python
# Copyright (c) 2014 Eugene Frolov <eugene@frolov.net.ru>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from restalchemy.common import exceptions as exc
from restalchemy.dm import properties


class BaseRelationship(properties.AbstractProperty):
    pass


def relationship(*args, **kwargs):

    class Relationship(BaseRelationship):

        def __init__(self):
            self._read_only = kwargs.pop('read_only', False)
            self._required = kwargs.pop('required', False)
            default = kwargs.pop('default', None)
            self._models = args
            self._default = self._safe_value(default()) if callable(
                default) else self._safe_value(default)
            self._value = None

        def _safe_value(self, value):
            if value is None or isinstance(value, self._models):
                return value
            raise exc.ValueError(class_name=self._models, value=value)

        def restore_value(self, value):
            self._value = self._safe_value(value)

        @property
        def value(self):
            return self._value or self._default

        @value.setter
        def value(self, value):
            if self.is_read_only():
                raise exc.ReadOnlyPropertyError
            self._value = self._safe_value(value)

        def set_value_force(self, value):
            self._value = self._safe_value(value)

        def is_read_only(self):
            return self._read_only

        def check(self):
            if self._required and self.value is None:
                raise exc.ValueRequiredError()

    return Relationship
