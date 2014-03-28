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

import json

# TODO(Eugene Frolov): Kill this hard code
from restalchemy.utils import json_util

json_util.monkey_patch()


class JSONPacker(object):

    def pack(self, obj):
        return json.dumps(obj)

    def unpack(self, value):
        return json.loads(value)


packer_mapping = {
    'application/json': JSONPacker()
}


def pack(content_type, obj):
    return packer_mapping[content_type].pack(obj)


def unpack(content_type, value):
    return packer_mapping[content_type].unpack(value)
