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

from restalchemy.common import exceptions as exc
from restalchemy.dm import properties


class ResourceMap(object):

    resource_map = {}

    @classmethod
    def get_location(cls, resource):
        return cls.resource_map[type(resource)].get_uri(resource)

    @classmethod
    def get_locator(cls, uri):
        for resource, locator in cls.resource_map.items():
            if locator.is_your_uri(uri):
                return locator
        raise exc.NotFoundError()

    @classmethod
    def get_resource(cls, request, uri):
        resource_locator = cls.get_locator(uri)
        return resource_locator.get_resource(request, uri)

    @classmethod
    def set_resource_map(cls, resource_map):
        cls.resource_map = resource_map


class AbstractResource(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_resource_id(self):
        pass

    @abc.abstractmethod
    def get_fields(self):
        pass


class ResourceMixIn(AbstractResource):

    _hidden_resource_fields = []
    _name_fields_map = {}

    def get_resource_id(self):
        return self.get_id()

    @classmethod
    def get_fields(cls):
        ps = properties.PropertySearcher(cls)
        for name, prop in ps.search_all(properties.AbstractProperty):
            if ((name in cls._hidden_resource_fields) or
                    name.startswith('_')):
                continue
            yield name, prop
