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

import re
import uuid

import mock

from restalchemy.orm import types
from restalchemy.tests.unit import base


TEST_VALUE = "test_value :)"


@mock.patch("re.compile", return_value=mock.MagicMock(), autospec=True)
class BaseTypeTestCase(base.BaseTestCase):

    def _prepare_mock(self, re_mock, return_value):
        self.re_match_mock = mock.MagicMock(**{
            'match': mock.MagicMock(return_value=return_value)})
        re_mock.return_value = self.re_match_mock

    def test_correct_value_if_value_is_not_none(self, re_mock):
        self._prepare_mock(re_mock, re.match("a", "a"))

        test_instance = types.BaseType("")

        self.assertTrue(test_instance.validate(TEST_VALUE))
        self.re_match_mock.match.assert_called_once_with(TEST_VALUE)

    def test_correct_value_if_value_is_none(self, re_mock):
        self._prepare_mock(re_mock, None)

        test_instance = types.BaseType("")

        self.assertTrue(test_instance.validate(None))

    def test_incorect_value(self, re_mock):
        self._prepare_mock(re_mock, None)

        test_instance = types.BaseType("")

        self.assertFalse(test_instance.validate(TEST_VALUE))
        self.re_match_mock.match.assert_called_once_with(TEST_VALUE)


class UUIDType(base.BaseTestCase):

    def setUp(self):
        super(UUIDType, self).setUp()
        self.test_instance = types.UUIDType()

    def test_uuid_correct_value(self):

        self.assertTrue(self.test_instance.validate(
            str(uuid.uuid4())))

    def test_uuid_incorrect_value(self):
        incorrect_uuid = '4a775g98-eg85-4a0e-a0g0-639f0a16f4c3'

        self.assertFalse(self.test_instance.validate(
            incorrect_uuid))
