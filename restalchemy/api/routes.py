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


class BaseRoute(object):
    __metaclass__ = abc.ABCMeta

    __controller__ = None
    __allow_methods__ = []

    def __init__(self, req):
        super(BaseRoute, self).__init__()
        self._req = req

    @classmethod
    def get_controller_class(cls):
        return cls.__controller__

    @classmethod
    def get_controller(cls, *args, **kwargs):
        return cls.get_controller_class()(*args, **kwargs)

    @classmethod
    def get_allow_methods(cls):
        return cls.__allow_methods__

    @abc.abstractmethod
    def do(self):
        pass


class Route(BaseRoute):
    __controller__ = None
    __allow_methods__ = [GET, CREATE, UPDATE, DELETE, FILTER]

    @classmethod
    def is_resource_route(cls):
        return False

    @classmethod
    def is_collection_route(cls):
        return True

    @classmethod
    def get_attr_safe(cls, name, the_class):
        try:
            attr = getattr(cls, name.replace('-', '_'))
            if not (inspect.isclass(attr) and issubclass(attr, the_class)):
                raise exc.NotFoundError()
            return attr
        except AttributeError:
            raise exc.NotFoundError()

    @classmethod
    def get_route(cls, name):
        return cls.get_attr_safe(name, Route)

    @classmethod
    def get_action(cls, name):
        return cls.get_attr_safe(name, Action)

    @classmethod
    def is_route(cls, name):
        try:
            cls.get_route(name)
            return True
        except exc.NotFoundError:
            return False

    @classmethod
    def get_routes(cls):
        return filter(lambda x: cls.is_route(x), dir(cls))

    @classmethod
    def check_allow_methods(cls, *args):
        for method in args:
            if method not in cls.__allow_methods__:
                return False
        return True

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
    def build_resource_map(cls, root_route, path_stack=None):
        path_stack = path_stack or []

        def build_path(resource, path_stack):
            path_stack = path_stack[:]
            path_stack.append(resource)
            return path_stack

        def build(route, path_stack):
            result = []

            controller = route.get_controller_class()
            resource = controller.get_resource()

            if route.check_allow_methods(GET):
                route_path_stack = build_path(resource, path_stack)
                result.append((resource, controller, route_path_stack))

            for name in route.get_routes():
                name = name.replace('_', '-')
                new_route = route.get_route(name)
                new_path = (build_path(resource, path_stack) if
                            new_route.is_resource_route() else path_stack[:])
                new_path.append(name)
                result += build(route.get_route(name), new_path)

            return result

        class ResourceLocator(object):

            def __init__(self, path_stack, controller):
                self.path_stack = path_stack
                self._controller = controller

            def is_your_uri(self, uri):
                uri_pieces = uri.split('/')[1:]
                if len(uri_pieces) == len(self.path_stack):
                    for piece1, piece2 in zip(uri_pieces, self.path_stack):
                        if ((isinstance(piece2, basestring) and
                                piece1 == piece2) or (
                                not isinstance(piece2, basestring))):
                            continue
                        return False
                    return True
                else:
                    return False

            def get_parent_resource(self, parent_type, resource):
                if hasattr(resource, 'get_parent_resource'):
                    return resource.get_parent_resource()
                res = [r for r in resource.values()
                       if isinstance(r, parent_type)]
                if len(res) > 1:
                    raise TypeError("Can't change resource from %s. Please "
                                    "indicate the parent resources" % str(res))
                return res[0]

            def get_uri(self, resource):
                path = str(resource.get_resource_id())
                for piece in reversed(self.path_stack[:-1]):
                    if isinstance(piece, basestring):
                        path = posixpath.join(piece, path)
                    else:
                        resource = self.get_parent_resource(piece, resource)
                        path = posixpath.join(resource.get_resource_id(), path)
                # FIXME(Eugene Frolov): Header must be string. Not unicode.
                return str(posixpath.join('/', path))

            def get_resource(self, request, uri):
                uuid = posixpath.basename(uri)
                return self._controller(request=request).get_resource_by_uuid(
                    uuid)

        resource_map = {}

        for res, controller, stack in build(root_route, path_stack):
            resource_map[res] = ResourceLocator(stack, controller)

        return resource_map

    def do(self, parent_resource=None):
        super(Route, self).do()

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
            worker = self.get_controller(self._req)
            resource = worker.get_resource_by_uuid(name, parent_resource)
            self._req.path_info_pop()
            action_name = self._req.path_info_peek()
            action = self.get_action(action_name)
            worker = action(self._req)
            return worker.do(resource=resource)

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


class Action(BaseRoute):
    __controller__ = None
    __allow_methods__ = [GET]

    def is_invoke(self):
        return False

    def do(self, resource):
        super(Action, self).do()

        method = self._req.method
        action_name = self._req.path_info_pop().replace("-", "_")
        invoke_info = self._req.path_info_pop()
        if invoke_info == 'invoke':
            invoke = True
        elif invoke_info is None:
            invoke = False
        else:
            # TODO(Eugene Frolov): Specify exception and exception message
            raise exc.NotFoundError()
        controller = self.get_controller(self._req)
        action = getattr(controller, action_name)
        if ((method in [GET, POST, PUT] and self.is_invoke() and invoke) or
            (method == GET and not self.is_invoke() and not invoke)):
            action_method = getattr(action, 'do_%s' % method.lower())
            return action_method(controller=controller, resource=resource)
        else:
            # TODO(Eugene Frolov): Specify exception type and message
            raise


def action(action_class, invoke=False):

    class ActionBased(action_class):

        def is_invoke(self):
            return invoke

    return ActionBased
