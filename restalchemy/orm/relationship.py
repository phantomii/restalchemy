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
from restalchemy.server import resources


class BaseRelationship(base.AbstractProperty):
    pass


def relationship(value_type, required=False, read_only=False):

    class RelationshipClass(BaseRelationship):

        def __init__(self):
            super(RelationshipClass, self).__init__()
            self.__value = None
            self._required = required
            self._read_only = read_only

        def _safe_value(self, value):
            if (value_type == type(value) or value == None):
                return value
            else:
                raise exc.ValueError(class_name=value_type, value=value)

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, value):
            if self._read_only:
                raise exc.ReadOnlyPropertyError()
            if isinstance(value, basestring):
                locator = resources.ResourceLocator()
                value = locator.get_resource(value)
            self.__value = self._safe_value(value)

        @classmethod
        def is_compatible(cls, model):
            return value_type == type(model)

    return RelationshipClass


class ForeignKey(object):

    def __init__(self, field):
        self.field = field
