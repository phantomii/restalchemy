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

import uuid

from restalchemy.common import exceptions as exc
from restalchemy.orm import base
from restalchemy.orm import properties
from restalchemy.orm import relationship
from restalchemy.orm import types


class PropertySearcher(object):

    def __init__(self, target):
        self.target = target

    def search_all(self, property_type):
        for name in filter(lambda x: not x.startswith('_'), dir(self.target)):
            try:
                if type(self.target) == type:
                    yield (name, self.get_property_from_class(
                        name, property_type))
                else:
                    yield (name, self.get_property_from_instance(
                        name, property_type))
            except exc.PropertyNotFoundError:
                pass

    def _safe_value(self, attr, name, property_type):
        if isinstance(attr, property_type) or (
            type(attr) == type and issubclass(attr, property_type)):
            return attr
        else:
            raise exc.PropertyNotFoundError(class_name=property_type,
                                            property_name=name)

    def get_property_from_instance(self, name, property_type):
        return self._safe_value(self.target.get_attr(name), name,
                                property_type)

    def get_property_from_class(self, name, property_type):
        return self._safe_value(getattr(self.target, name), name,
                                property_type)


class BaseModel(object):

    def __init__(self, **kwargs):
        super(BaseModel, self).__init__()
        super(BaseModel, self).__setattr__('searcher', PropertySearcher(self))

        for name, prop in self.searcher.search_all(base.AbstractProperty):
            super(BaseModel, self).__setattr__(name, prop())

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattribute__(self, attr):
        attr = super(BaseModel, self).__getattribute__(attr)
        if (isinstance(attr, properties.BaseProperty) or
            isinstance(attr, relationship.BaseRelationship)):
            return attr.value
        else:
            return attr

    def __setattr__(self, attr, value):
        attr = super(BaseModel, self).__getattribute__(attr)
        if (isinstance(attr, properties.BaseProperty) or
            isinstance(attr, relationship.BaseRelationship)):
            attr.value = value
        else:
            super(BaseModel, self).__setattr__(attr, value)

    @classmethod
    def factory(cls, obj, parent_model=None):
        if parent_model:
            obj[cls.get_relationship_name(parent_model)] = parent_model

        return cls(**obj)

    def get_attr(self, name):
        return super(BaseModel, self).__getattribute__(name)

    def check(self):
        for name, prop in self.searcher.search_all(base.AbstractProperty):
            prop.check()

    def __to_json__(self):
        result = {}
        for name, prop in self.searcher.search_all(base.AbstractProperty):
            result[name] = (prop.value.get_uri() if isinstance(
                prop, relationship.BaseRelationship) else prop.value)
        return result

    def update(self, model, skip_read_only=True):
        if type(self) != type(model):
            raise exc.TypeError(action='update', t1=self.__class__,
                                t2=model.__class__)
        for name, prop in self._get_properties():
            if not (skip_read_only and prop.is_read_only()):
                setattr(self, name, getattr(model, name))

    def get_uri(self):
        return self.__uri__ + self.uuid

    @classmethod
    def get_relationship_name(cls, model):
        target = None
        searcher = PropertySearcher(cls)
        for name, prop in searcher.search_all(relationship.BaseRelationship):
            if prop.is_compatible(model) and not target:
                target = name
            elif prop.is_compatible(model) and target:
                # TODO(Eugene Frolov): TBD
                raise
        if not target:
            # TODO(Eugene Frolov): TBD
            raise
        return target


class SimpleModel(BaseModel):

    uuid = properties.Property(types.UUIDType, read_only=True,
                               default=lambda: str(uuid.uuid4()))

    def __init__(self, **kwargs):
        super(SimpleModel, self).__init__(**kwargs)
