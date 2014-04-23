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

import inspect
import posixpath

from restalchemy.common import exceptions as exc


GET = 'GET'
PUT = 'PUT'
POST = 'POST'
FILTER = 'FILTER'
CREATE = 'CREATE'
UPDATE = 'UPDATE'
DELETE = 'DELETE'

COLLECTION_ROUTE = 1
RESOURCE_ROUTE = 2


class Route(object):
    __controller__ = None
    __allow_methods__ = [GET, CREATE, UPDATE, DELETE, FILTER]

    def __init__(self, req):
        super(Route, self).__init__()
        self._req = req

    @classmethod
    def is_resource_route(cls):
        return False

    @classmethod
    def is_collection_route(cls):
        return True

    @classmethod
    def get_attr_safe(cls, name, the_class):
        try:
            attr = getattr(cls, name)
            if not (inspect.isclass(attr) and issubclass(attr, the_class)):
                raise exc.NotFoundError()
            return attr
        except AttributeError:
            raise exc.NotFoundError()

    @classmethod
    def get_route(cls, name):
        return cls.get_attr_safe(name, Route)

    @classmethod
    def is_route(cls, name):
        try:
            cls.get_route(name)
            return True
        except exc.NotFoundError:
            return False

    @classmethod
    def get_controller_class(cls):
        return cls.__controller__

    @classmethod
    def get_controller(cls, *args, **kwargs):
        return cls.get_controller_class()(*args, **kwargs)

    @classmethod
    def check_allow_methods(cls, *args):
        for method in args:
            if method not in cls.__allow_methods__:
                return False
        return True

    @classmethod
    def get_allow_methods(cls):
        return cls.__allow_methods__

    def get_method_by_route_type(self, route_type):
        if route_type == COLLECTION_ROUTE:
            mapping = {GET: FILTER, POST: CREATE}
        else:
            mapping = {GET: GET, PUT: UPDATE, DELETE: DELETE}
        try:
            return mapping[self._req.method]
        except KeyError:
            # TODO(Eugene Frolov): Specify error type and message.
            raise exc.NotFoundError()

    @classmethod
    def build_resource_map(cls, root_route, start_path='/'):

        def build_path(resource, location_path):
            tpl_name = '%(' + resource.__name__.lower() + '_uuid)s'
            return posixpath.join(location_path, tpl_name)

        def build(route, path):
            result = []

            controller = route.get_controller_class()
            resource = controller.get_resource()

            if route.check_allow_methods(GET):
                route_path = build_path(resource, path)
                result.append((resource, controller, route_path))

            for name in filter(lambda x: route.is_route(x), dir(route)):
                new_route = route.get_route(name)
                if new_route.is_resource_route():
                    new_path = build_path(resource, path)
                    new_path = posixpath.join(new_path, name, '')
                else:
                    new_path = posixpath.join(path, name, '')
                result += build(route.get_route(name), new_path)

            return result

        class ResourceLocator(object):

            def __init__(self, uri_template, controller):
                self.uri_template = uri_template
                self._controller = controller

            def get_uri(self, resource):
                param_name = '%s_uuid' % type(resource).__name__.lower()
                return self.uri_template % {param_name: resource.get_id()}

            def get_resource(self, request, uri):
                uuid = posixpath.basename(uri)
                return self._controller(request=request).get_resource_by_uuid(
                    uuid)

        resource_map = {}

        for res, controller, template in build(root_route, start_path):
            resource_map[res] = ResourceLocator(template, controller)

        return resource_map

    def do(self, parent_resource=None):
        # TODO(Eugene Frolov): Check the possibility to pass to the method
        #                      specified in a route.
        name, path = self._req.path_info_pop(), self._req.path_info_peek()

        if path is None:
            # Collection or Resource method
            ctrl_method = (self.get_method_by_route_type(COLLECTION_ROUTE)
                           if name == '' else
                           self.get_method_by_route_type(RESOURCE_ROUTE))
            if self.check_allow_methods(ctrl_method):
                worker = self.get_controller(request=self._req)

                if name == '':
                    # Collection method
                    return worker.do_collection(parent_resource)

                # Resource method
                return worker.do_resource(name, parent_resource)
            else:
                raise exc.NotFoundError()

        elif (name != '' and path is not None and self.is_route(name)):
            # Next route
            route = self.get_route(name)
            if route.is_resource_route():
                raise exc.NotFoundError()
            worker = route(self._req)
            return worker.do(parent_resource)
        elif (name != '' and path == 'actions'):
            # Action route
            # TODO(Eugene Frolov): Impliment action processing
            pass
        elif (name != '' and path is not None):
            # Intermediate resource route
            worker = self.get_controller(self._req)
            parent_resource = worker.get_resource_by_uuid(
                name, parent_resource)
            name, path = self._req.path_info_pop(), self._req.path_info_peek()
            route = self.get_route(name)
            if route.is_collection_route():
                raise exc.NotFoundError()
            worker = route(self._req)
            return worker.do(parent_resource)
        else:
            # Other
            raise exc.NotFoundError()


def route(route_class, resource_route=False):

    class RouteBased(route_class):

        @classmethod
        def is_resource_route(cls):
            return resource_route

        @classmethod
        def is_collection_route(cls):
            return not resource_route

    return RouteBased
