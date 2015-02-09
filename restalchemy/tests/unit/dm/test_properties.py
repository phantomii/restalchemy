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

import mock

from restalchemy.common import exceptions as exc
from restalchemy.dm import properties
from restalchemy.tests.unit import base


FAKE_VALUE = "fake value"


class FakeClass(object):

    fake_property1 = mock.Mock()
    fake_property2 = mock.Mock()

    def get_attr(self, name):
        return getattr(self, name)


class PropertySearcherTestCase(base.BaseTestCase):

    def _prepare(self, target):
        self.test_instance = properties.PropertySearcher(target)

    def test_is_property_for_class_positive(self):
        self._prepare(object())

        self.assertTrue(self.test_instance.is_property(object, object))

    def test_is_property_for_class_negative(self):
        self._prepare(object())

        self.assertFalse(self.test_instance.is_property(object, str))

    def test_is_property_for_instance_positive(self):
        self._prepare(object())

        self.assertTrue(self.test_instance.is_property(object(), object))

    def test_is_property_for_instance_negative(self):
        self._prepare(object())

        self.assertFalse(self.test_instance.is_property(object(), str))

    @mock.patch.object(properties.PropertySearcher, "is_property",
                       side_effect=[True, True, False])
    def test_search_all_return_properties(self, is_property_mock):
        self._prepare(FakeClass())

        self.assertListEqual(list(self.test_instance.search_all(mock.Mock)),
                             [('fake_property1', FakeClass.fake_property1),
                              ('fake_property2', FakeClass.fake_property2)])
        self.assertEqual(is_property_mock.call_count, 3)

    @mock.patch.object(properties.PropertySearcher, "is_property",
                       return_value=False)
    def test_search_all_return_empty(self, is_property_mock):
        self._prepare(FakeClass())

        self.assertListEqual(list(self.test_instance.search_all(mock.Mock)),
                             [])
        self.assertEqual(is_property_mock.call_count, 3)

    @mock.patch.object(properties.PropertySearcher, "is_property",
                       return_value=True)
    def test_get_roperty_positive(self, is_property_mock):
        self._prepare(FakeClass())

        self.assertEqual(
            self.test_instance.get_property('fake_property1', object),
            FakeClass.fake_property1)
        is_property_mock.assert_called_one_with(
            FakeClass.fake_property1, object)

    @mock.patch.object(properties.PropertySearcher, "is_property",
                       return_value=False)
    def test_get_roperty_raise_property_not_found(self, is_property_mock):
        self._prepare(FakeClass())

        self.assertRaises(
            exc.PropertyNotFoundError, self.test_instance.get_property,
            'fake_property1', object)


class PropertyBasedObjectTestCase(base.BaseTestCase):

    @mock.patch('restalchemy.dm.properties.PropertySearcher')
    def test_init(self, ps_mock):
        prop = [('fake_prop1', mock.Mock), ('fake_prop2', mock.Mock)]

        def side_effect(attr, *property_type):
            try:
                if attr.__name__ == "validate":
                    return False
                return True
            except Exception:
                return True

        ps_mock.configure_mock(**{
            'return_value.search_all.return_value': prop,
            'return_value.is_property.side_effect': side_effect})
        params = {
            'fake_prop1': 'fake_value1',
            'fake_prop2': 'fake_value2'}

        target = properties.PropertyBasedObject(
            properties.BaseProperty, **params)

        self.assertIsInstance(target, properties.PropertyBasedObject)
        self.assertEqual(target.fake_prop1, 'fake_value1')
        self.assertEqual(target.fake_prop2, 'fake_value2')

    def test_get_attr(self):
        target = properties.PropertyBasedObject(properties.BaseProperty)

        self.assertEqual(target.get_attr('get_attr'), target.get_attr)

    @mock.patch('restalchemy.dm.properties.PropertySearcher')
    def test__setattr__property(self, ps_mock):

        x_property = mock.Mock(name='x_property')

        def side_effect(attr, *property_type):
            try:
                if attr.__name__ == "validate":
                    return False
                return True
            except Exception:
                return True
        ps_mock.configure_mock(**{
            'return_value.is_property.side_effect': side_effect,
            'return_value.get_property.return_value': x_property})

        target = properties.PropertyBasedObject(properties.BaseProperty)

        self.assertIsNone(setattr(target, 'test_property', 'test_value'))
        self.assertEqual(x_property.value, 'test_value')

    @mock.patch('restalchemy.dm.properties.PropertySearcher')
    def test__setattr__value(self, ps_mock):

        ps_mock.configure_mock(**{
            'return_value.get_property.side_effect': (
                exc.PropertyNotFoundError(class_name='test',
                                          property_name='test')),
            'return_value.is_property.return_value': False})

        target = properties.PropertyBasedObject(properties.BaseProperty)

        self.assertIsNone(setattr(target, 'test_property', 'test_value'))
        self.assertEqual(target.test_property, 'test_value')


class PropertyTestCase(base.BaseTestCase):

    def setUp(self):
        super(PropertyTestCase, self).setUp()
        self.positive_fake_property_type = mock.MagicMock(
            **{'validate': mock.MagicMock(return_value=True)})
        self.negative_fake_property_type = mock.MagicMock(
            **{'validate': mock.MagicMock(return_value=False)})

    def test_default_value_incorect_raise_value_error(self):
        property_obj = properties.property(self.negative_fake_property_type,
                                           default=FAKE_VALUE)

        self.assertRaises(exc.ValueError, property_obj)
        self.negative_fake_property_type.validate.assert_called_with(
            FAKE_VALUE)

    def _set_property_value(self, obj, value):
        obj.value = value

    def test_set_corect_value(self):
        property_obj = properties.property(self.positive_fake_property_type)()

        self.assertIsNone(self._set_property_value(property_obj, FAKE_VALUE))
        self.positive_fake_property_type.validate.assert_called_with(
            FAKE_VALUE)

    def test_set_none_value(self):
        property_obj = properties.property(self.negative_fake_property_type)()

        self.assertIsNone(self._set_property_value(property_obj, None))

    def test_set_incorect_value(self):
        property_obj = properties.property(self.negative_fake_property_type)()

        self.assertRaises(exc.ValueError, self._set_property_value,
                          property_obj, FAKE_VALUE)
        self.negative_fake_property_type.validate.assert_called_with(
            FAKE_VALUE)

    def test_default_return_value(self):
        property_obj = properties.property(self.positive_fake_property_type,
                                           default=FAKE_VALUE)()

        self.assertEqual(property_obj.value, FAKE_VALUE)

    def test_check_pass_if_value_is_required(self):
        property_obj = properties.property(self.positive_fake_property_type,
                                           required=True)()
        property_obj.value = FAKE_VALUE

        self.assertEqual(property_obj.check(), None)

    def test_check_pass_if_value_is_required_and_default_is_set(self):
        property_obj = properties.property(self.positive_fake_property_type,
                                           required=True,
                                           default=FAKE_VALUE)()

        self.assertEqual(property_obj.check(), None)

    def test_check_pass_if_value_is_not_required(self):
        property_obj = properties.property(self.positive_fake_property_type,
                                           required=False)()

        self.assertEqual(property_obj.check(), None)

    def test_check_raise_if_value_is_required(self):
        property_obj = properties.property(self.positive_fake_property_type,
                                           required=True)()

        self.assertRaises(exc.ValueRequiredError, property_obj.check)
