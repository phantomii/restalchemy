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

import anyjson
import copy

from restalchemy.api import resources
from restalchemy.dm import properties
from restalchemy.dm import relationships


DEFAULT_CONTENT_TYPE = 'application/json'


def get_content_type(headers):
    return headers.get('Content-Type') or DEFAULT_CONTENT_TYPE


class BaseResourcePacker(object):

    def __init__(self, resource_type, request):
        self._ps = properties.PropertySearcher(resource_type)
        self._rt = resource_type
        self._req = request

    def pack_resource(self, obj):
        if self._rt is not None and isinstance(obj, self._rt):
            result = {}
            for name, cls_prop in obj.get_fields():
                prop = obj.get_attr(name)
                api_name = obj._name_fields_map.get(name, name)
                if prop.value is not None:
                    result[api_name.replace('_', '-')] = (
                        resources.ResourceMap.get_location(
                            prop.value) if isinstance(
                                prop, relationships.BaseRelationship) else
                        prop.value)
            return result
        else:
            return obj

    def pack(self, obj):
        if isinstance(obj, list):
            return [self.pack_resource(resource) for resource in obj]
        else:
            return self.pack_resource(obj)

    def unpack(self, obj):
        obj = copy.deepcopy(obj)
        result = {}
        for name, prop in self._rt.get_fields():
                api_name = self._rt._name_fields_map.get(name, name)
                value = obj.pop(api_name.replace('_', '-'), None)
                if value is not None:
                    result[name] = (
                        resources.ResourceMap.get_resource(
                            self._req, value) if issubclass(
                                prop, relationships.BaseRelationship)
                        else value)

        if len(obj) > 0:
            raise TypeError("%s is not compatible with %s" % (obj, self._rt))

        return result


class JSONPacker(BaseResourcePacker):

    def pack(self, obj):
        return anyjson.serialize(super(JSONPacker, self).pack(obj))

    def unpack(self, value):
        return super(JSONPacker, self).unpack(anyjson.deserialize(value))


packer_mapping = {
    'application/json': JSONPacker
}


def get_packer(content_type):
    try:
        return packer_mapping[content_type]
    except KeyError:
        # TODO(Eugene Frolov): Specify Exception Type and message
        raise Exception("Packer can't found for content type %s " %
                        content_type)
