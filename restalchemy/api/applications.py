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
from webob import dec

from restalchemy.api import packers
from restalchemy.api import routes


DEFAULT_CONTENT_TYPE = 'application/json'


class WSGIApp(object):

    def __init__(self, route_class):
        super(WSGIApp, self).__init__()
        self._main_route = routes.route(route_class)()
        routes.RoutesMap.set_resource_map(
            routes.Route.build_resource_map(route_class))

    def _get_content_type(self, headers):
        return headers.get('Content-Type') or DEFAULT_CONTENT_TYPE

    @dec.wsgify
    def __call__(self, req):
        if req.body:
            content_type = self._get_content_type(req.headers)
            req.parsed_body = packers.unpack(content_type, req.body)

        body, status, headers = self._main_route.do_request(req)

        headers['Content-Type'] = self._get_content_type(headers)

        return webob.Response(
            body=packers.pack(headers['Content-Type'], body),
            status=status,
            content_type=headers.get('Content-Type'),
            headerlist=[(k, v) for k, v in headers.items()])


Application = WSGIApp
