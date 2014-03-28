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

import collections as cl

from wsgiref.simple_server import make_server

from restalchemy.common import exceptions as exc
from restalchemy.orm import models
from restalchemy.orm import properties
from restalchemy.orm import relationship
from restalchemy.orm import types
from restalchemy.server import actions
from restalchemy.server import collections
from restalchemy.server import controllers
from restalchemy.server import resources
from restalchemy.server import wsgi


class BoxModel(models.SimpleModel):
    __uri__ = '/v1/boxes/'

    name = properties.Property(types.StringType(min_length=1, max_length=15),
                               required=False)
    shelf = properties.Property(types.StringType(min_length=1, max_length=1),
                                required=True, default="a")


class PelvisModel(models.SimpleModel):
    __uri__ = '/v1/pelvises/'

    name = properties.Property(types.StringType(min_length=1, max_length=15),
                               required=True)


class ItemModel(models.SimpleModel):
    __uri__ = '/v1/items/'

    name = properties.Property(types.StringType(min_length=2, max_length=15),
                               required=True)
    param = properties.Property(types.StringType(), default="default value")

    box = relationship.relationship(BoxModel, required=True)
    pelvis = relationship.relationship(PelvisModel, required=True)


class CollectionNameModel(models.BaseModel):
    __uri__ = '/v1/'

    name = properties.Property(types.StringType(min_length=1, max_length=15))

    def __to_json__(self):
        return self.name


class VersionModel(models.BaseModel):
    __uri__ = '/'

    ver = properties.Property(types.StringType(min_length=2, max_length=2))

    def __init__(self, version):
        super(VersionModel, self).__init__()
        self.ver = version


items_store = cl.defaultdict(lambda: [])
box_store = []
pelvis_store = []


class ColorAction(actions.BaseAction):

    def get(self):
        return "Red"


class CountAction(actions.BaseAction):

    def get(self):
        return len(items_store[self.model.uuid])


class ItemsCollection(collections.Collection):

    color = actions.Action(ColorAction, invoke=True)

    def __init__(self):
        super(ItemsCollection, self).__init__()
        self.model = ItemModel

    def get_all(self, **kwargs):
        return items_store[self.get_parent_model().uuid]

    def create(self, model):
        items_store[model.box.uuid].append(model)
        return model


class PelvisCollection(collections.Collection):

    def __init__(self):
        super(PelvisCollection, self).__init__()
        self.model = PelvisModel

    def create(self, pelvis_model):
        pelvis_store.append(pelvis_model)
        return pelvis_model

    def get_all(self, **kwargs):
        return pelvis_store

    def get_one(self, uuid):
        for i in pelvis_store:
            if i.uuid == uuid:
                return i
        raise exc.NotFoundError()


class BoxCollection(collections.Collection):

    items = controllers.Controller(ItemsCollection)
    count = actions.Action(CountAction, invoke=True)

    def __init__(self):
        super(BoxCollection, self).__init__()
        self.model = BoxModel

    def get_all(self, **kwargs):
        return box_store

    def create(self, box_model):
        box_store.append(box_model)
        return box_model

    def get_one(self, uuid):
        for i in box_store:
            if i.uuid == uuid:
                return i
        raise exc.NotFoundError()

    def delete(self, uuid):
        for i in box_store[:]:
            if i.uuid == uuid:
                box_store.remove(i)
                return
        raise exc.NotFoundError()

    def update(self, uuid, model):
        old_model = self.get_one(uuid)
        old_model.update(model)
        return old_model


class V1Collection(collections.Collection):

    boxes = controllers.Controller(BoxCollection)
    pelvises = controllers.Controller(PelvisCollection)

    def __init__(self):
        super(V1Collection, self).__init__()
        self.model = CollectionNameModel

    def get_all(self, **kwargs):
        return [self.model(name='boxes'), self.model(name='pelvises')]


class BoxApplication(wsgi.Application):

    v1 = controllers.Controller(V1Collection)

    def __init__(self, resource_locator_class):
        super(BoxApplication, self).__init__(resource_locator_class)
        self.model = VersionModel

    def get_all(self, **kwargs):
        return [self.model(ver='v1')]


httpd = make_server('127.0.0.1', 8000, BoxApplication(
    resources.ResourceLocator))

httpd.serve_forever()
