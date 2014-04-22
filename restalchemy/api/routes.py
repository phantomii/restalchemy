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

import collections
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


class RoutesMap(object):

    resource_map = {}

    @classmethod
    def get_resource_location(cls, resource):
        # TODO(Eugene Frolov): Rewrite for the case when a resource has more
        #                      than one path.
        return cls.resource_map[type(resource)][0] % {
            'uuid': resource.get_id()}

    @classmethod
    def set_resource_map(cls, resource_map):
        cls.resource_map = resource_map


class Route(object):
    __controller__ = None
    __allow_methods__ = [GET, PUT, CREATE, UPDATE, DELETE]

    def __init__(self):
        super(Route, self).__init__()
        self.__collection_method_mapping = {
            GET: self._filter,
            POST: self._create
        }
        self.__resource_method_mapping = {
            GET: self._get,
            DELETE: self._delete,
            PUT: self._update
        }

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
    def get_controller(cls, *args, **kwargs):
        return cls.__controller__(*args, **kwargs)

    @classmethod
    def check_allow_methods(cls, *args):
        for method in args:
            if method not in cls.__allow_methods__:
                return False
        return True

    @classmethod
    def build_resource_map(cls, root_route, start_path='/'):

        def build(node, path):
            result = []
            for name in filter(lambda x: node.is_route(x), dir(node)):
                try:
                    route = node.get_route(name)
                    controller = route.get_controller(context=None)
                    resource = controller.get_resource()
                    route_path = posixpath.join(path, name, '')
                    if route.check_allow_methods(GET):
                        route_path = posixpath.join(route_path, '%(uuid)s')
                        if resource is not None:
                            result.append((resource, route_path))
                    result = result + build(route, route_path)
                except AttributeError:
                    pass
            return result

        resource_map = collections.defaultdict(lambda: [])

        for resource, path in build(root_route, start_path):
            resource_map[resource].append(path)
        return dict(resource_map)

    def _result_processing(self, result, status_code=200, headers={},
                           add_location=False):

        def correct(body, c=status_code, h={}, *args):
            if add_location:
                headers['Location'] = RoutesMap.get_resource_location(body)
            headers.update(h)
            return body, c, headers

        if type(result) == tuple:
            return correct(*result)
        return correct(result)

    def _create(self, req, worker=None, parent_resource=None):
        if not worker:
            raise exc.NotImplementedError()

        kwargs = req.parsed_body
        if parent_resource:
            kwargs['parent_resource'] = parent_resource

        return self._result_processing(worker(**kwargs),
                                       status_code=201, add_location=True)

    def _get(self, req, uuid, worker=None, parent_resource=None):
        if not worker:
            raise exc.NotImplementedError()

        kwargs = {'uuid': uuid}
        if parent_resource:
            kwargs['parent_resource'] = parent_resource

        return self._result_processing(worker(**kwargs))

    def _filter(self, req, worker=None, parent_resource=None):
        if not worker:
            raise exc.NotImplementedError()

        # TODO(Eugene Frolov): Method returns NestedMultiDict which it
        #   includes multiple identical keys. It is problem. One must
        #   writes a correct translation NestedMultiDict to a type of dict.
        kwargs = dict(req.params)
        if parent_resource:
            kwargs['parent_resource'] = parent_resource

        return self._result_processing(worker(**kwargs))

    def _delete(self, req, uuid, worker=None, parent_resource=None):
        if not worker:
            raise exc.NotImplementedError()

        kwargs = {'uuid': uuid}
        if parent_resource:
            kwargs['parent_resource'] = parent_resource

        return self._result_processing(worker(**kwargs), status_code=204)

    def _update(self, req, uuid, worker=None, parent_resource=None):
        if not worker:
            raise exc.NotImplementedError()

        kwargs = {'uuid': uuid}
        # TODO(Eugene Frolov): Raise Exception if uuid exist in parsed_body
        kwargs.update(req.parsed_body)
        if parent_resource:
            kwargs['parent_resource'] = parent_resource

        return self._result_processing(worker(**kwargs))

    def do_request(self, req, parent_resource=None):
        # TODO(Eugene Frolov): Check the possibility to pass to the method
        #                      specified in a route.

        name, path = req.path_info_pop(), req.path_info_peek()
        method = req.method

        if (name == '' and path is None):
            # Collection method
            worker = self.__collection_method_mapping[method]
            return worker(req, parent_resource=parent_resource)
        elif (name != '' and path is None):
            # Resource method
            worker = self.__resource_method_mapping[method]
            return worker(req, name, parent_resource)
        elif (name != '' and path is not None and self.is_route(name)):
            # Next route
            route = self.get_route(name)
            if route.is_resource_route():
                raise exc.NotFoundError()
            worker = route()
            return worker.do_request(req, parent_resource)
        elif (name != '' and path == 'actions'):
            # Action route
            # TODO(Eugene Frolov): Impliment action processing
            pass
        elif (name != '' and path is not None):
            # Intermediate resource route
            worker = self.__resource_method_mapping[GET]
            parent_resource = worker(req, name, parent_resource)[0]
            name, path = req.path_info_pop(), req.path_info_peek()
            route = self.get_route(name)
            if route.is_collection_route():
                raise exc.NotFoundError()
            worker = route()
            return worker.do_request(req, parent_resource)
        else:
            # Other
            raise exc.NotFoundError()


def route(route_class, resource_route=False):

    class RouteBased(route_class):

        def __init__(self, *args, **kwargs):
            super(RouteBased, self).__init__(*args, **kwargs)

        def get_context_from_request(self, req):
            try:
                return req.context
            except AttributeError:
                return None

        def get_worker(self, req, name):
            context = self.get_context_from_request(req)
            return getattr(self.get_controller(context=context), name, None)

        def _filter(self, req, parent_resource=None):
            return super(RouteBased, self)._filter(
                req, self.get_worker(req, 'filter'), parent_resource)

        def _create(self, req, parent_resource=None):
            return super(RouteBased, self)._create(
                req, self.get_worker(req, 'create'), parent_resource)

        def _get(self, req, uuid, parent_resource=None):
            return super(RouteBased, self)._get(
                req, uuid, self.get_worker(req, 'get'), parent_resource)

        def _delete(self, req, uuid, parent_resource=None):
            return super(RouteBased, self)._delete(
                req, uuid, self.get_worker(req, 'delete'), parent_resource)

        def _update(self, req, uuid, parent_resource=None):
            return super(RouteBased, self)._update(
                req, uuid, self.get_worker(req, 'update'), parent_resource)

        @classmethod
        def is_resource_route(cls):
            return resource_route

        @classmethod
        def is_collection_route(cls):
            return not resource_route

    return RouteBased
