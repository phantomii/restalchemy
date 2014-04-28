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

import __builtin__
import abc
import collections
import inspect

from restalchemy.common import exceptions as exc


class AbstractProperty(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def value(self):
        pass

    @abc.abstractmethod
    def check(self):
        pass


class BaseProperty(AbstractProperty):
    pass


def property(value_type, default=None, required=False, read_only=False):

    class Property(BaseProperty):

        def __init__(self):
            super(Property, self).__init__()
            self._value_type = (value_type() if inspect.isclass(value_type)
                                else value_type)
            self._default = self._safe_value(default()) if callable(
                default) else self._safe_value(default)
            self._value = None
            self._required = required
            self._read_only = read_only

        def _safe_value(self, value):
            if value is None or self._value_type.validate(value):
                return value
            else:
                raise exc.ValueError(class_name=self._value_type.__class__,
                                     value=value)

        @__builtin__.property
        def value(self):
            return self._value or self._default

        @value.setter
        def value(self, value):
            if self._read_only:
                raise exc.ReadOnlyPropertyError()
            self._value = self._safe_value(value)

        def restore_value(self, value):
            self._value = self._safe_value(value)

        def is_read_only(self):
            return self._read_only

        def check(self):
            if self._required and self.value is None:
                raise exc.ValueRequiredError()

    return Property


class PropertySearcher(object):

    def __init__(self, target):
        self._target = target

    def is_property(self, prop, *args):
        equal_func = issubclass if inspect.isclass(prop) else isinstance
        return equal_func(prop, args)

    def get_target_attr(self, name):
        if inspect.isclass(self._target):
            return getattr(self._target, name)
        else:
            return self._target.get_attr(name)

    def get_property(self, name, *args):
        try:
            prop = self.get_target_attr(name)
            if self.is_property(prop, *args):
                return prop
            else:
                raise AttributeError()
        except AttributeError:
            raise exc.PropertyNotFoundError(class_name=self._target.__class__,
                                            property_name=name)

    def search_all(self, *args):
        property_filter = lambda x: not x.startswith('__')
        for name in filter(property_filter, dir(self._target)):
            prop = self.get_target_attr(name)
            if self.is_property(prop, *args):
                yield name, prop


class PropertyBasedObject(collections.Mapping):

    def __init__(self, *args, **kwargs):
        ps = PropertySearcher(self)
        # TODO(Eugene Frolov): Fix recursion by other methods
        super(PropertyBasedObject, self).__setattr__('_ps', ps)
        super(PropertyBasedObject, self).__setattr__(
            '_property_type', args)
        for name, prop_class in ps.search_all(*args):
            prop = prop_class()
            super(PropertyBasedObject, self).__setattr__(name, prop)
            value = kwargs.pop(name, None)
            if value:
                prop.value = value
        super(PropertyBasedObject, self).__init__(**kwargs)

    @classmethod
    def restore(cls, *args, **kwargs):
        obj = cls()
        ps = PropertySearcher(obj)
        for name, prop in ps.search_all(*args):
            prop.restore_value(kwargs.pop(name, None))
        return obj

    def get_attr(self, name):
        return super(PropertyBasedObject, self).__getattribute__(name)

    def __getattribute__(self, name):
        attr = super(PropertyBasedObject, self).__getattribute__(name)
        try:
            ps = super(PropertyBasedObject, self).__getattribute__('_ps')
        except AttributeError:
            return attr
        property_type = super(PropertyBasedObject, self).__getattribute__(
            '_property_type')
        if ps.is_property(attr, *property_type):
            return attr.value
        return attr

    def __setattr__(self, name, value):
        try:
            try:
                ps = super(PropertyBasedObject, self).__getattribute__('_ps')
            except AttributeError:
                return super(PropertyBasedObject, self).__setattr__(name,
                                                                    value)
            property_type = super(PropertyBasedObject, self).__getattribute__(
                '_property_type')
            attr = ps.get_property(name, *property_type)
            attr.value = value
        except exc.PropertyNotFoundError:
            super(PropertyBasedObject, self).__setattr__(name, value)

    def update(self, values):
        for name, value in values.items():
            setattr(self, name, value)

    def check(self):
        for name, prop in self._ps.search_all(*self._property_type):
            prop.check()

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __iter__(self):
        for name, value in self._ps.search_all(*self._property_type):
            yield name

    def __len__(self):
        return len(list(self._ps.search_all(*self._property_type)))


class BaseContainer(BaseProperty):
    pass


def container(**kwargs):

    class Container(BaseContainer):

        def __init__(self):
            for k, v in kwargs.items():
                setattr(self, k, v())

        @__builtin__.property
        def value(self):
            result = {}
            for k, v in self._ps.search_all(BaseProperty):
                result[k] = v
            return result

        @value.setter
        def value(self, value):
            for k, v in value.items():
                getattr(self, k).value = v

        def check(self):
            for k, v in self._ps.search_all(BaseProperty):
                v.check()
