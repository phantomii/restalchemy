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

from restalchemy.server import base


METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_DELETE = 'DELETE'
METHOD_PUT = 'PUT'


class BaseAction(base.RestfulObject):

    def __init__(self, model):
        super(BaseAction, self).__init__()
        self._method_mapping = {
            METHOD_GET: self._get,
            METHOD_POST: self._post,
            METHOD_PUT: self._put
        }
        self.model = model

    def _get(self, req, worker_name='get'):
        worker = self._get_worker_method(worker_name)
        return self._result_processing(worker())

    def _post(self, req, worker_name='post'):
        worker = self._get_worker_method(worker_name)
        return self._result_processing(worker())

    def _put(self, req, worker_name='put'):
        worker = self._get_worker_method(worker_name)
        return self._result_processing(worker())

    def do_request(self, req):
        return self._method_mapping[req.method](req)


class Action(object):

    def __init__(self, action_class, invoke=False):
        super(Action, self).__init__()
        self.__action_class = action_class
        self.__invoke = invoke

    def invoke(self):
        return self.__invoke

    def action_factory(self, *args, **kwargs):
        return self.__action_class(*args, **kwargs)
