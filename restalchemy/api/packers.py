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
import types


DEFAULT_CONTENT_TYPE = 'application/json'


def get_content_type(headers):
    return headers.get('Content-Type') or DEFAULT_CONTENT_TYPE


class BaseResourcePacker(object):

    def __init__(self, resource_type, request):
        self._rt = resource_type
        self._req = request

    def pack_resource(self, obj):
        if isinstance(obj, (types.StringTypes,
                            types.IntType,
                            types.LongType,
                            types.FloatType,
                            types.BooleanType,
                            types.NoneType,
                            types.ListType,
                            types.TupleType,
                            types.DictType)):
            return obj
        else:
            result = {}
            for name, prop in self._rt.get_fields():
                api_name = prop.api_name
                value = getattr(obj, name)
                if (value is not None and prop.is_public()):
                    result[api_name] = prop.dump_value(value)

            return result

    def pack(self, obj):
        if (isinstance(obj, list) or
            isinstance(obj, types.GeneratorType)):
            return [self.pack_resource(resource) for resource in obj]
        else:
            return self.pack_resource(obj)

    def unpack(self, obj):
        obj = copy.deepcopy(obj)
        result = {}
        for name, prop in self._rt.get_fields():
            api_name = prop.api_name
            value = obj.pop(api_name, None)
            if value is not None:
                if not prop.is_public():
                    raise ValueError("Property %s is private" % api_name)
                result[name] = prop.parse_value(self._req, value)

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
