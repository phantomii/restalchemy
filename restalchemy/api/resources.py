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

import posixpath

from restalchemy.common import exceptions as exc


class ResourceMap(object):

    resource_map = {}

    @classmethod
    def get_location(cls, resource):
        return cls.resource_map[type(resource)].get_uri(resource)

    @classmethod
    def get_locator(cls, uri):
        for resource, locator in cls.resource_map.items():
            path_a = posixpath.dirname(uri)
            path_b = posixpath.dirname(locator.uri_template)
            if path_a == path_b:
                return locator
        raise exc.NotFoundError()

    @classmethod
    def get_resource(cls, request, uri):
        resource_locator = cls.get_locator(uri)
        return resource_locator.get_resource(request, uri)

    @classmethod
    def set_resource_map(cls, resource_map):
        cls.resource_map = resource_map
