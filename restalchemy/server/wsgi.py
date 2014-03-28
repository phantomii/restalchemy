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

import webob
from webob import dec

from restalchemy.server import collections
from restalchemy.server import packers


DEFAULT_CONTENT_TYPE = 'application/json'


class WSGIApp(object):

    def __init__(self):
        pass

    @abc.abstractmethod
    def do_request(self, req):
        pass

    def _get_content_type(self, headers):
        return headers.get('Content-Type') or DEFAULT_CONTENT_TYPE

    def processing(self, req):
        req.route_path = '/'.join(reversed(req.path.split('/')))[:-1]
        if req.body:
            content_type = self._get_content_type(req.headers)
            req.parsed_body = packers.unpack(content_type, req.body)
        return self.do_request(req)

    @dec.wsgify
    def __call__(self, req):
        body, status, headers = self.processing(req)
        headers['Content-Type'] = self._get_content_type(headers)
        return webob.Response(
            body=packers.pack(headers['Content-Type'], body),
            status=status,
            content_type=headers.get('Content-Type'),
            headerlist=[(k, v) for k, v in headers.items()])


class Application(collections.Collection, WSGIApp):

    def __init__(self, resource_locator_class):
        super(Application, self).__init__()
        self.locator = resource_locator_class(self)
