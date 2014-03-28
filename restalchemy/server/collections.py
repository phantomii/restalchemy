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

import os

from restalchemy.common import exceptions as exc
from restalchemy.orm import models
from restalchemy.server import actions
from restalchemy.server import base
from restalchemy.server import controllers


METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_DELETE = 'DELETE'
METHOD_PUT = 'PUT'

COLLECTION_METHOD = 1
COLLECTION_ACTION = 2
COLLECTION_PROPERTY = 3

RESOURCE_METHOD = 4
RESOURCE_ACTION = 5
RESOURCE_PROPERTY = 6

CONTROLLER = 7


class BaseCollection(base.RestfulObject):

    def __init__(self):
        super(BaseCollection, self).__init__()
        self._collection_method_mapping = {
            METHOD_GET: self._get_all,
            METHOD_POST: self._create
        }
        self._resource_method_mapping = {
            METHOD_GET: self._get_one,
            METHOD_DELETE: self._delete,
            METHOD_PUT: self._update
        }
        self.model = models.BaseModel
        self.__parent_model = None

    def _create(self, req, worker_name='create', parent_model=None):
        self.__parent_model = parent_model
        worker = self._get_worker_method(worker_name)
        model = self.model.factory(req.parsed_body, parent_model=parent_model)
        model.check()
        return self._result_processing(worker(model), status_code=201,
                                       add_location=True)

    def _get_one(self, req, worker_name='get_one', parent_model=None):
        self.__parent_model = parent_model
        worker = self._get_worker_method(worker_name)
        uuid = os.path.basename(req.route_path)
        return self._result_processing(worker(uuid))

    def _get_all(self, req, worker_name='get_all', parent_model=None):
        self.__parent_model = parent_model
        worker = self._get_worker_method(worker_name)

        # TODO(Eugene Frolov): Method returns NestedMultiDict which it
        #   includes multiple identical keys. It is problem. One must
        #   writes a correct translation NestedMultiDict to a type of dict.
        return self._result_processing(worker(**dict(req.params)))

    def _delete(self, req, worker_name='delete', parent_model=None):
        self.__parent_model = parent_model
        worker = self._get_worker_method(worker_name)
        uuid = os.path.basename(req.route_path)
        worker(uuid)
        return self._result_processing(None, status_code=204)

    def _update(self, req, worker_name='update', parent_model=None):
        self.__parent_model = parent_model
        worker = self._get_worker_method(worker_name)
        model = self.model.factory(req.parsed_body, parent_model=parent_model)
        uuid = os.path.basename(req.route_path)
        return self._result_processing(worker(uuid, model))

    def lookup(self, req):

        def make_result(target, target_worker, req=req):
            return target, target_worker, req

        path, name = os.path.split(req.route_path)
        method = req.method

        if (name == '' and path == ''):
            return make_result(
                COLLECTION_METHOD, self._collection_method_mapping[method])
        elif (name != '' and path == ''):
            return make_result(RESOURCE_METHOD,
                               self._resource_method_mapping[method])
        elif (name != '' and path != '' and self._is_collection(name)):
            req.route_path = path[:-1] if path == '/' else path
            return make_result(
                CONTROLLER, self._get_collection(name), req)
        elif (name == "actions" and path != '' and
              self._is_action(os.path.basename(path))):
            req.route_path, action_name = os.path.split(path)
            return make_result(RESOURCE_ACTION, self._get_action(action_name),
                               req=req)
        elif name != '':
            return make_result(RESOURCE_METHOD,
                               self._resource_method_mapping[METHOD_GET])
        else:
            raise exc.NotFoundError()

    def _get_instance(self, name, the_class):
        try:
            attr = getattr(self, name)
            if not isinstance(attr, the_class):
                raise exc.NotFoundError()
            return attr
        except AttributeError:
            raise exc.NotFoundError()

    def _get_collection(self, name):
        return self._get_instance(name, controllers.Controller)

    def _is_collection(self, name):
        try:
            self._get_collection(name)
            return True
        except exc.NotFoundError:
            return False

    def _get_action(self, name):
        return self._get_instance(name, actions.Action)

    def _is_action(self, name):
        try:
            self._get_action(name)
            return True
        except exc.NotFoundError:
            return False

    def get_parent_model(self):
        return self.__parent_model

    def do_request(self, req, parent_model=None):

        target, target_method, req = self.lookup(req)

        if target == COLLECTION_METHOD:
            return target_method(req, parent_model=parent_model)
        elif target == CONTROLLER:
            return target_method.controller_factory().do_request(
                req, parent_model)
        elif target == RESOURCE_METHOD:
            if not os.path.dirname(req.route_path):
                return target_method(req, parent_model=parent_model)
            else:
                result = target_method(req, parent_model=parent_model)
                req.route_path = os.path.dirname(req.route_path)
                return self.do_request(req, parent_model=result[0])
        elif target == RESOURCE_ACTION:
            path, name = os.path.split(req.route_path)
            if (path != '' and (name != "invoke" or name != '')):
                raise
            invoke = True if name else False
            if (target_method.invoke() == invoke and (req.method ==
                                                      METHOD_GET or invoke)):
                return target_method.action_factory(
                    parent_model).do_request(req)
            else:
                raise

        raise exc.NotImplementedError()


Collection = BaseCollection
