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
from restalchemy.orm import properties
from restalchemy.tests.unit import base


FAKE_VALUE = "fake value"


class PropertyTestCase(base.BaseTestCase):

    def setUp(self):
        super(PropertyTestCase, self).setUp()
        self.positive_fake_property_type = mock.MagicMock(
            **{'validate': mock.MagicMock(return_value=True)})
        self.negative_fake_property_type = mock.MagicMock(
            **{'validate': mock.MagicMock(return_value=False)})

    def test_default_value_incorect_raise_value_error(self):
        property_obj = properties.Property(self.negative_fake_property_type,
                                           default=FAKE_VALUE)

        self.assertRaises(exc.ValueError, property_obj)
        self.negative_fake_property_type.validate.assert_called_with(
            FAKE_VALUE)

    def _set_property_value(self, obj, value):
        obj.value = value

    def test_set_corect_value(self):
        property_obj = properties.Property(self.positive_fake_property_type)()

        self.assertIsNone(self._set_property_value(property_obj, FAKE_VALUE))
        self.positive_fake_property_type.validate.assert_called_with(
            FAKE_VALUE)

    def test_set_incorect_value(self):
        logic_mock = mock.MagicMock(
            **{'validate': mock.MagicMock(side_effect=[True, False])})

        property_obj = properties.Property(logic_mock)()

        self.assertRaises(exc.ValueError, self._set_property_value,
                          property_obj, FAKE_VALUE)
        logic_mock.validate.assert_called_with(FAKE_VALUE)

    def test_default_return_value(self):
        property_obj = properties.Property(self.positive_fake_property_type,
                                           default=FAKE_VALUE)()

        self.assertEqual(property_obj.value, FAKE_VALUE)

    def test_check_pass_if_value_is_required(self):
        property_obj = properties.Property(self.positive_fake_property_type,
                                           required=True)()
        property_obj.value = FAKE_VALUE

        self.assertEqual(property_obj.check(), None)

    def test_check_pass_if_value_is_required_and_default_is_set(self):
        property_obj = properties.Property(self.positive_fake_property_type,
                                           required=True,
                                           default=FAKE_VALUE)()

        self.assertEqual(property_obj.check(), None)

    def test_check_pass_if_value_is_not_required(self):
        property_obj = properties.Property(self.positive_fake_property_type,
                                           required=False)()

        self.assertEqual(property_obj.check(), None)

    def test_check_raise_if_value_is_required(self):
        property_obj = properties.Property(self.positive_fake_property_type,
                                           required=True)()

        self.assertRaises(exc.ValueRequiredError, property_obj.check)
