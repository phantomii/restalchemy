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

import webob

from restalchemy.api import packers
from restalchemy.api import resources
from restalchemy.common import exceptions as exc


class Controller(object):
    __resource__ = None

    def __init__(self, request):
        self._req = request

    def get_packer(self, content_type, resource_type=None):
        packer = packers.get_packer(content_type)
        rt = resource_type or self.get_resource()
        return packer(rt, request=self._req)

    def process_result(self, result, status_code=200, headers={},
                       add_location=False):

        def correct(body, c=status_code, h={}, *args):
            if add_location:
                headers['Location'] = resources.ResourceMap.get_location(body)
            headers.update(h)
            return body, c, headers

        def create_response(body, status, headers):
            if body is not None:
                headers['Content-Type'] = packers.get_content_type(headers)
                packer = self.get_packer(headers['Content-Type'])
                body = packer.pack(body)

            return webob.Response(
                body=body,
                status=status,
                content_type=headers.get('Content-Type', None),
                headerlist=[(k, v) for k, v in headers.items()])

        if type(result) == tuple:
            return create_response(*correct(*result))
        else:
            return create_response(*correct(result))

    def _make_kwargs(self, parent_resource, **kwargs):
        if parent_resource:
            kwargs['parent_resource'] = parent_resource
        return kwargs

    def do_collection(self, parent_resource=None):
        method = self._req.method

        if method == 'GET':
            # TODO(Eugene Frolov): Method returns NestedMultiDict which it
            #   includes multiple identical keys. It is problem. One must
            #   writes a correct translation NestedMultiDict to a type of dict.
            kwargs = self._make_kwargs(parent_resource,
                                       **dict(self._req.params))
            return self.process_result(self.filter(**kwargs))
        elif method == 'POST':
            content_type = packers.get_content_type(self._req.headers)
            packer = self.get_packer(content_type)
            kwargs = self._make_kwargs(parent_resource,
                                       **packer.unpack(self._req.body))

            return self.process_result(self.create(**kwargs), 201,
                                       add_location=True)
        else:
            raise exc.UnsupportedHttpMethod(method=method)

    def get_resource_by_uuid(self, uuid, parent_resource=None):
        kwargs = self._make_kwargs(parent_resource)
        result = self.get(uuid=uuid, **kwargs)
        if isinstance(result, tuple):
            return result[0]
        return result

    def do_resource(self, uuid, parent_resource=None):
        method = self._req.method
        kwargs = self._make_kwargs(parent_resource)

        if method == 'GET':
            return self.process_result(self.get(uuid=uuid, **kwargs))
        elif method == 'PUT':
            content_type = packers.get_content_type(self._req.headers)
            packer = self.get_packer(content_type)
            kwargs.update(packer.unpack(self._req.body))
            return self.process_result(self.update(uuid=uuid, **kwargs))
        elif method == 'DELETE':
            result = self.delete(uuid=uuid, **kwargs)
            return self.process_result(result, 200 if result else 204)
        else:
            raise exc.UnsupportedHttpMethod(method=method)

    @classmethod
    def get_resource(cls):
        return cls.__resource__

    @property
    def model(self):
        return self.get_resource()

    def create(self, **kwargs):
        raise exc.NotImplementedError()

    def get(self, uuid):
        raise exc.NotImplementedError()

    def filter(self, **kwargs):
        raise exc.NotImplementedError()

    def delete(self, uuid):
        raise exc.NotImplementedError()

    def update(self, uuid, **kwargs):
        raise exc.NotImplementedError()

    def get_context(self):
        try:
            return self._req.context
        except AttributeError:
            return None
