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

"""
Curl examples:

Create VM:


    curl --request POST \
        --url http://127.0.0.1:8000/vms/ \
        --header 'cache-control: no-cache' \
        --header 'content-type: application/json' \
        --data '{"name": "test vm2"}' \
        --verbose

    Note: Unnecessary use of -X or --request, POST is already inferred.
    *   Trying 127.0.0.1...
    * Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
    > POST /vms/ HTTP/1.1
    > Host: 127.0.0.1:8000
    > User-Agent: curl/7.49.0
    > Accept: */*
    > cache-control: no-cache
    > content-type: application/json
    > postman-token: 4b87c0bf-8b73-1ae1-87c3-399378410441
    > Content-Length: 20
    >
    * upload completely sent off: 20 out of 20 bytes
    * HTTP 1.0, assume close after body
    < HTTP/1.0 201 Created
    < Date: Wed, 20 Jul 2016 20:58:22 GMT
    < Server: WSGIServer/0.1 Python/2.7.10
    < Content-Type: application/json
    < Location: http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043
    < Content-Length: 84
    <
    * Closing connection 0
    {
        "state": "off",
        "name": "test vm2",
        "uuid": "4fafef62-a145-4ffe-b829-2d9dccd89043"
    }


List VMs:

    curl --request GET \
        --url http://127.0.0.1:8000/vms/ \
        --header 'cache-control: no-cache' \
        --header 'content-type: application/json' \
        --verbose

    Note: Unnecessary use of -X or --request, GET is already inferred.
    *   Trying 127.0.0.1...
    * Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
    > GET /vms/ HTTP/1.1
    > Host: 127.0.0.1:8000
    > User-Agent: curl/7.49.0
    > Accept: */*
    > cache-control: no-cache
    > content-type: application/json
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Date: Wed, 20 Jul 2016 21:02:58 GMT
    < Server: WSGIServer/0.1 Python/2.7.10
    < Content-Type: application/json
    < Location: http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043
    < Content-Length: 344
    <
    * Closing connection 0
    [
        {
            "state": "off",
            "name": "test vm1",
            "uuid": "34b19989-e4db-446e-abd9-dd6be4356083"
        }, {
            "state": "off",
            "name": "test vm4",
            "uuid": "eb58565f-4f88-4d94-9e07-afc1412b529d"
        }, {
            "state": "off",
            "name": "test vm3",
            "uuid": "b9921490-c9fd-4e25-b73b-cf673edb9005"
        }, {
            "state": "off",
            "name": "test vm2",
            "uuid": "4fafef62-a145-4ffe-b829-2d9dccd89043"
        }
    ]


Update VM name:

    curl --request PUT \
        --url http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043 \
        --header 'cache-control: no-cache' \
        --header 'content-type: application/json' \
        --data '{"name": "test vm10"}' \
        --verbose

    *   Trying 127.0.0.1...
    * Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
    > PUT /vms/4fafef62-a145-4ffe-b829-2d9dccd89043 HTTP/1.1
    > Host: 127.0.0.1:8000
    > User-Agent: curl/7.49.0
    > Accept: */*
    > cache-control: no-cache
    > content-type: application/json
    > postman-token: 78544265-505f-298e-bb9e-35392302efda
    > Content-Length: 21
    >
    * upload completely sent off: 21 out of 21 bytes
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Date: Wed, 20 Jul 2016 21:08:30 GMT
    < Server: WSGIServer/0.1 Python/2.7.10
    < Content-Type: application/json
    < Location: http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043
    < Content-Length: 85
    <
    * Closing connection 0
    {
        "state": "off",
        "name": "test vm10",
        "uuid": "4fafef62-a145-4ffe-b829-2d9dccd89043"
    }


Call poweron action:

    curl --request POST \
        --url http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043/\
actions/poweron/invoke \
        --header 'cache-control: no-cache' \
        --header 'content-type: application/json' \
        --verbose

    *   Trying 127.0.0.1...
    * Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
    > POST /vms/4fafef62-a145-4ffe-b829-2d9dccd89043/actions/poweron/invoke \
HTTP/1.1
    > Host: 127.0.0.1:8000
    > User-Agent: curl/7.49.0
    > Accept: */*
    > cache-control: no-cache
    > content-type: application/json
    >
    * HTTP 1.0, assume close after body
    < HTTP/1.0 200 OK
    < Date: Wed, 20 Jul 2016 21:11:27 GMT
    < Server: WSGIServer/0.1 Python/2.7.10
    < Content-Type: application/json
    < Location: http://127.0.0.1:8000/vms/4fafef62-a145-4ffe-b829-2d9dccd89043
    < Content-Length: 84
    <
    * Closing connection 0
    {
        "state": "on",
        "name": "test vm10",
        "uuid": "4fafef62-a145-4ffe-b829-2d9dccd89043"
    }

"""

import uuid

import six
from wsgiref.simple_server import make_server

from restalchemy.api import actions
from restalchemy.api import applications
from restalchemy.api import controllers
from restalchemy.api import resources
from restalchemy.api import routes
import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm


HOST = '0.0.0.0'
PORT = 8000

DATABASE_URL = "sqlite://"


# -----------------------------------------------------------------------------
# Models section
# -----------------------------------------------------------------------------

Base = declarative.declarative_base()


class VM(Base):
    __tablename__ = 'vms'

    uuid = sa.Column(sa.String(36), primary_key=True,
                     default=lambda: str(uuid.uuid4()))
    state = sa.Column(sa.String(10), nullable=False)
    name = sa.Column(sa.String(255), nullable=False)

    def __init__(self, name, state="off"):
        super(VM, self).__init__()
        self.name = name
        self.state = state

# SetUp SQLAlchemy
ENGINE = sa.create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(ENGINE)
SESSION_MAKER = orm.sessionmaker(bind=ENGINE)
SESSION = SESSION_MAKER()


# -----------------------------------------------------------------------------
# Controllers section
# -----------------------------------------------------------------------------
class VMController(controllers.Controller):
    """VM controller
    Handle POST http://127.0.0.1:8000/vms/
    Handle GET http://127.0.0.1:8000/vms/
    Handle GET http://127.0.0.1:8000/vms/<uuid>
    Handle PUT http://127.0.0.1:8000/vms/<uuid>
    Handle DELETE http://127.0.0.1:8000/vms/<uuid>
    Handle GET http://127.0.0.1:8000/vms/<uuid>/actions/poweron/invoke
    Handle GET http://127.0.0.1:8000/vms/<uuid>/actions/poweroff/invoke
    """

    __resource__ = resources.ResourceBySAModel(VM)

    def create(self, name):
        vm = self.model(name=name)
        SESSION.add(vm)
        SESSION.commit()
        return vm

    def get(self, uuid):
        vm = SESSION.query(VM).filter(VM.uuid == uuid).one()
        return vm

    def delete(self, uuid):
        SESSION.query(VM).filter(VM.uuid == uuid).delete()
        SESSION.commit()

    def update(self, uuid, name, **kwargs):
        vm = SESSION.query(VM).filter(VM.uuid == uuid).one()
        vm.name = name
        SESSION.commit()
        return vm

    def filter(self):
        vms = SESSION.query(VM).all()
        return vms

    @actions.post
    def poweron(self, resource):
        resource.state = "on"
        SESSION.commit()
        return resource

    @actions.post
    def poweroff(self, resource):
        resource.state = "off"
        SESSION.commit()
        return resource


class RootController(controllers.Controller):

    def filter(self):
        return ["vms"]
        # session = SESSION_MAKER()
        # vms = session.query(VM).all()
        # session.close()
        # return vms


# -----------------------------------------------------------------------------
# Routes section
# -----------------------------------------------------------------------------

class VMPowerOnAction(routes.Action):
    __controller__ = VMController


class VMPowerOffAction(routes.Action):
    __controller__ = VMController


class VMRoute(routes.Route):
    __controller__ = VMController
    __allow_methods__ = [routes.CREATE, routes.GET, routes.DELETE,
                         routes.FILTER, routes.UPDATE]

    poweron = routes.action(VMPowerOnAction, invoke=True)
    poweroff = routes.action(VMPowerOffAction, invoke=True)


class Root(routes.Route):
    __controller__ = RootController
    __allow_methods__ = [routes.FILTER]

    vms = routes.route(VMRoute)


def main():
    # Create python WSGI server on any interface with 8000 port
    server = make_server(HOST, PORT,
                         applications.WSGIApp(route_class=Root))

    try:
        six.print_("Serve forever on %s:%s" % (HOST, PORT))
        server.serve_forever()
    except KeyboardInterrupt:
        six.print_('Bye')

if __name__ == '__main__':
    main()
