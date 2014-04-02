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


TEST_STR_VALUE = 'test_value :)'
TEST_INT_VALUE = 5
TEST_TYPE = 'FAKE TYPE'
INCORECT_UUID = '4a775g98-eg85-4a0e-a0g0-639f0a16f4c3'


@mock.patch("re.compile", return_value=mock.MagicMock(), autospec=True)
class BaseTypeTestCase(base.BaseTestCase):

    def _prepare_mock(self, re_mock, return_value):
        self.re_match_mock = mock.MagicMock(**{
            'match': mock.MagicMock(return_value=return_value)})
        re_mock.return_value = self.re_match_mock

    def test_correct_value_if_value_is_not_none(self, re_mock):
        self._prepare_mock(re_mock, re.match("a", "a"))

        test_instance = types.BaseType("")

        self.assertTrue(test_instance.validate(TEST_STR_VALUE))
        self.re_match_mock.match.assert_called_once_with(TEST_STR_VALUE)

    def test_correct_value_if_value_is_none(self, re_mock):
        self._prepare_mock(re_mock, None)

        test_instance = types.BaseType("")

        self.assertTrue(test_instance.validate(None))

    def test_incorect_value(self, re_mock):
        self._prepare_mock(re_mock, None)

        test_instance = types.BaseType("")

        self.assertFalse(test_instance.validate(TEST_STR_VALUE))
        self.re_match_mock.match.assert_called_once_with(TEST_STR_VALUE)


class BaseTestCase(base.BaseTestCase):

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)
        self.test_instance = mock.MagicMock()

    def test_correct_none_value(self):
        self.assertTrue(self.test_instance.validate(None))


class UUIDTypeTestCase(BaseTestCase):

    def setUp(self):
        super(UUIDTypeTestCase, self).setUp()
        self.test_instance = types.UUIDType()

    def test_uuid_correct_value(self):

        self.assertTrue(self.test_instance.validate(
            str(uuid.uuid4())))

    def test_uuid_incorrect_value(self):
        self.assertFalse(self.test_instance.validate(
            INCORECT_UUID))


class StringTypeTestCase(BaseTestCase):

    def setUp(self):
        super(StringTypeTestCase, self).setUp()
        self.test_instance = types.StringType(min_length=5, max_length=8)

    def test_correct_value(self):
        self.assertTrue(self.test_instance.validate(self.string_generator()))

    def test_correct_min_value(self):
        self.assertTrue(self.test_instance.validate(self.string_generator(5)))

    def test_correct_max_value(self):
        self.assertTrue(self.test_instance.validate(self.string_generator(8)))

    def test_incorrect_min_value(self):
        self.assertFalse(self.test_instance.validate(self.string_generator(4)))

    def test_incorrect_max_value(self):
        self.assertFalse(self.test_instance.validate(self.string_generator(9)))


class UriTypeTestCase(BaseTestCase):

    def setUp(self):
        super(UriTypeTestCase, self).setUp()
        self.test_instance = types.UriType()

    def test_correct_value(self):
        self.assertTrue(self.test_instance.validate(
            '/fake/fake/' + str(uuid.uuid4())))

    def test_incorect_uuid_value(self):
        self.assertFalse(self.test_instance.validate(
            '/fake/fake/' + INCORECT_UUID))

    def test_incorect_start_char_value(self):
        self.assertFalse(self.test_instance.validate(
            'fake/fake/' + str(uuid.uuid4())))

    def test_incorect_start_end_value(self):
        self.assertFalse(self.test_instance.validate(
            '/fake/fake' + str(uuid.uuid4())))


class MacTypeTestCase(BaseTestCase):

    def setUp(self):
        super(MacTypeTestCase, self).setUp()
        self.test_instance = types.MacType()

    def test_correct_value(self):
        self.assertTrue(self.test_instance.validate("05:06:07:08:ab:ff"))

    def test_incorrect_cahar_value(self):
        self.assertFalse(self.test_instance.validate("05:06:0k:08:ab:ff"))

    def test_incorrect_length_value(self):
        self.assertFalse(self.test_instance.validate("05:06:08:ab:ff"))


class BasePythonTypeTestCase(base.BaseTestCase):

    def setUp(self):
        super(BasePythonTypeTestCase, self).setUp()

        self.test_instance = types.BasePythonType(int)

    def test_validate_correct_value(self):
        self.assertTrue(self.test_instance.validate(TEST_INT_VALUE))

    def test_validate_incorrect_value(self):
        self.assertFalse(self.test_instance.validate(TEST_STR_VALUE))


class IntegerTypeTestCase(base.BaseTestCase):

    def setUp(self):
        super(IntegerTypeTestCase, self).setUp()

        self.test_instance = types.IntegerType(0, 55)

    def test_validate_correct_value(self):
        self.assertTrue(self.test_instance.validate(TEST_INT_VALUE))

    def test_validate_correct_max_value(self):
        self.assertTrue(self.test_instance.validate(55))

    def test_validate_correct_min_value(self):
        self.assertTrue(self.test_instance.validate(0))

    def test_validate_incorrect_value(self):
        self.assertFalse(self.test_instance.validate(TEST_STR_VALUE))

    def test_validate_incorrect_max_value(self):
        self.assertFalse(self.test_instance.validate(56))

    def test_validate_incorrect_min_value(self):
        self.assertFalse(self.test_instance.validate(-1))


class DictTypeTestCase(base.BaseTestCase):

    def setUp(self):
        super(DictTypeTestCase, self).setUp()

        self.test_instance = types.DictType()

    def test_validate_correct_value(self):
        self.assertTrue(self.test_instance.validate(dict()))

    def test_validate_incorrect_value(self):
        self.assertFalse(self.test_instance.validate(TEST_STR_VALUE))


class EnumTypeTestCase(base.BaseTestCase):

    def setUp(self):
        super(EnumTypeTestCase, self).setUp()

        self.test_instance = types.EnumType([1, 2, 3])

    def test_validate_correct_value(self):
        self.assertTrue(self.test_instance.validate(1))

    def test_validate_incorrect_value(self):
        self.assertFalse(self.test_instance.validate(4))
