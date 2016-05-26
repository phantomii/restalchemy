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

# from sqlalchemy.orm import attributes

from restalchemy.common import exceptions as exc


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
        raise exc.LocatorNotFound(uri=uri)

    @classmethod
    def get_resource(cls, request, uri):
        resource_locator = cls.get_locator(uri)
        return resource_locator.get_resource(request, uri)

    @classmethod
    def set_resource_map(cls, resource_map):
        cls.resource_map = resource_map


class BaseResourceMixIn(object):

    @classmethod
    def get_name_fields_map(self):
        return {}

    @classmethod
    def get_hidden_resource_fields(self):
        return []

    @abc.abstractmethod
    def get_resource_id(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_fields(self):
        raise NotImplementedError()


class AbstractResourceMixIn(BaseResourceMixIn):
    __metaclass__ = abc.ABCMeta

    @property
    def _name_fields_map(self):
        return self.get_name_fields_map()

    @property
    def _hidden_resource_fields(self):
        return self.get_hidden_resource_fields()

    @abc.abstractmethod
    def get_resource_id(self):
        return super(AbstractResourceMixIn, self).get_resource_id()

    @abc.abstractmethod
    def get_fields(self):
        return super(AbstractResourceMixIn, self).get_fields()


class ResourceMixIn(AbstractResourceMixIn):

    def get_resource_id(self):
        return self.get_id()

    @classmethod
    def get_fields(cls):
        for name, prop in cls.properties.iteritems():
            if ((name in cls.get_hidden_resource_fields()) or
                    name.startswith('_')):
                continue
            yield name, prop


class SAResourceMixIn(BaseResourceMixIn):

    def get_resource_id(self):
        return self.get_id()

    @classmethod
    def get_fields(cls):
        for column in cls.__table__.get_children():
            name = column.name
            prop = column
            if ((name in cls.get_hidden_resource_fields()) or
                    name.startswith('_')):
                continue
            yield name, prop
