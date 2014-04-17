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
import uuid

from restalchemy.dm import properties
from restalchemy.dm import types


class Model(properties.PropertyBasedObject):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        super(Model, self).__init__(properties.AbstractProperty, **kwargs)

    @classmethod
    def restore(cls, **kwargs):
        return super(Model, cls).restore(properties.AbstractProperty, **kwargs)

    @abc.abstractmethod
    def get_id(self):
        pass


class ModelWithUUID(Model):
    uuid = properties.property(types.UUID, read_only=True,
                               default=lambda: str(uuid.uuid4()))

    def get_id(self):
        return self.uuid
