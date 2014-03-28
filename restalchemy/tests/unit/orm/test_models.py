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

from restalchemy.orm import models
from restalchemy.tests.unit import base


class BaseModelTestCase(base.BaseTestCase):

    #TODO(Eugene Frolov): Write tests
    pass


class SimpleModelTestCase(base.BaseTestCase):

    def test_uuid_default_value(self):
        test_instance = models.SimpleModel()

        self.assertIsNotNone(re.match(
            "^[a-f0-9]{8,8}-([a-f0-9]{4,4}-){3,3}[a-f0-9]{12,12}$",
            test_instance.uuid))
