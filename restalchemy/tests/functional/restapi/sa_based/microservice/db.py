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

import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from restalchemy.tests.functional.restapi.sa_based.microservice import models

_engine = None
_session_maker = None


DB_CONNECTION = "sqlite:////tmp/restalchemy-%s.db" % uuid.uuid4()


def get_engine():
    global _engine
    if _engine is None:
        _engine = sa.create_engine(DB_CONNECTION, echo=True)
    return _engine


def get_session():
    return orm.sessionmaker(bind=get_engine())
