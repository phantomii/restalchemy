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

import uuid as pyuuid

from restalchemy.api import actions
from restalchemy.api import controllers
from restalchemy.api import resources
from restalchemy.tests.functional.restapi.ra_based.microservice import (
    storable_models as models)


class VMController(controllers.Controller):
    """VM controller

    Handle POST http://127.0.0.1:8000/v1/vms/
    Handle GET http://127.0.0.1:8000/v1/vms/
    Handle GET http://127.0.0.1:8000/v1/vms/<uuid>
    Handle PUT http://127.0.0.1:8000/v1/vms/<uuid>
    Handle DELETE http://127.0.0.1:8000/v1/vms/<uuid>
    Handle GET http://127.0.0.1:8000/v1/vms/<uuid>/actions/poweron/invoke
    Handle GET http://127.0.0.1:8000/v1/vms/<uuid>/actions/poweroff/invoke
    """

    __resource__ = resources.ResourceByRAModel(models.VM)

    def _get_session(self):
        ctx = self.get_context()
        return ctx.session

    def create(self, name):
        session = self._get_session()
        vm = self.model(name=name)
        vm.insert(session=session)
        session.commit()
        return vm

    def get(self, uuid):
        session = self._get_session()
        vm = self.model.objects.get_one(filters={'uuid': pyuuid.UUID(uuid)},
                                        session=session)
        return vm

    def delete(self, uuid):
        session = self._get_session()
        vm = self.get(uuid)
        vm.delete(session=session)
        session.commit()

    def update(self, uuid, name, **kwargs):
        session = self._get_session()
        vm = self.get(uuid)
        vm.name = name
        vm.save(session=session)
        session.commit()
        return vm

    def filter(self):
        session = self._get_session()
        vms = self.model.objects.get_all(session=session)
        return vms

    @actions.post
    def poweron(self, resource):
        session = self._get_session()
        resource.state = "on"
        resource.save(session=session)
        session.commit()
        return resource

    @actions.post
    def poweroff(self, resource):
        session = self._get_session()
        resource.state = "off"
        resource.save(session=session)
        session.commit()
        return resource


class V1Controller(controllers.Controller):

    def filter(self):
        return ["vms"]


class RootController(controllers.Controller):

    def filter(self):
        return ["v1"]
