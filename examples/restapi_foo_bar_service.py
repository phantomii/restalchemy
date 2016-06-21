# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2016 Eugene Frolov <eugene@frolov.net.ru>
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

import six

from wsgiref.simple_server import make_server

from restalchemy.api import applications
from restalchemy.api import controllers
from restalchemy.api import resources
from restalchemy.api import routes
from restalchemy.dm import models
from restalchemy.dm import properties
from restalchemy.dm import types

HOST = '0.0.0.0'
PORT = 8000


# Storage for foo objects
foo_storage = {}
# Storage for bar objects
bar_objects = {}


# -----------------------------------------------------------------------------
# Models section
# -----------------------------------------------------------------------------


class FooModel(models.ModelWithUUID):
    foo_field1 = properties.property(types.Integer)
    foo_field2 = properties.property(types.String)


# -----------------------------------------------------------------------------
# Controllers section
# -----------------------------------------------------------------------------


class V1Controller(controllers.Controller):
    """Handle http://127.0.0.1:8000/"""

    def filter(self, **kwargs):
        return ['v1']


class FooController(controllers.Controller):
    """Handle http://127.0.0.1:8000/foo/"""

    __resource__ = resources.ResourceByRAModel(FooModel)

    def create(self, foo_field1, foo_field2):
        foo = self.model(foo_field1=foo_field1, foo_field2=foo_field2)
        foo_storage[str(foo.get_id())] = foo
        return foo

    def get(self, uuid):
        return foo_storage[uuid]

    def filter(self):
        return foo_storage.values()


# -----------------------------------------------------------------------------
# Routes section
# -----------------------------------------------------------------------------


class FooRoute(routes.Route):
    __controller__ = FooController
    __allow_methods__ = [routes.FILTER, routes.CREATE, routes.GET]


class V1Route(routes.Route):
    """Router for / path"""
    __controller__ = V1Controller
    __allow_methods__ = [routes.FILTER]

    # V1Route include two nested routes
    # The first route for /foo/ path
    foo = routes.route(FooRoute)


def main():
    # Create python WSGI server on any interface with 8000 port
    server = make_server(HOST, PORT, applications.WSGIApp(route_class=V1Route))

    try:
        six.print_("Serve forever on %s:%s" % (HOST, PORT))
        server.serve_forever()
    except KeyboardInterrupt:
        six.print_('Bye')

if __name__ == '__main__':
    main()
