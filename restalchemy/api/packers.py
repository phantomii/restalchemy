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
import types

from restalchemy.api import routes
from restalchemy.dm import models


class BasePacker(object):

    def prepare_resource(self, obj):
        if isinstance(obj, list):
            return [self.prepare_resource(i) for i in obj]
        elif isinstance(obj, models.Model):
            result = {}
            for key, value in obj.items():
                result[key] = (
                    value if not isinstance(value, models.Model) else
                    routes.RoutesMap.get_resource_location(value))
            return result
        elif isinstance(obj, (dict, basestring, int, long, bool, float,
                              types.NoneType)):
            return obj
        else:
            raise TypeError("%s can't converted to serializable" % str(obj))


class JSONPacker(BasePacker):

    def pack(self, obj):
        return anyjson.serialize(self.prepare_resource(obj))

    def unpack(self, value):
        return anyjson.deserialize(value)


packer_mapping = {
    'application/json': JSONPacker()
}


def pack(content_type, obj):
    return packer_mapping[content_type].pack(obj)


def unpack(content_type, value):
    return packer_mapping[content_type].unpack(value)
