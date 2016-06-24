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

import abc
import urlparse

import six

from restalchemy.common import singletons


@six.add_metaclass(abc.ABCMeta)
class AbstractEngine(object):

    @abc.abstractproperty
    def URL_SCHEMA(self):
        raise NotImplementedError()

    def __init__(self, db_url):
        super(AbstractEngine, self).__init__()
        self._db_url = urlparse.urlparse(db_url)

    @abc.abstractproperty
    def db_name(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def db_username(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def db_password(self):
        raise NotImplementedError()


class EngineFactory(singletons.InheritSingleton):

    def __init__(self):
        super(EngineFactory, self).__init__()
        self._engine = None
        self._engines_map = {}

    def configure_factory(self, db_url, config=None):
        """Configure_factory

        @property db_url: str. For example driver://user:passwd@host:port/db
        """
        schema = db_url.split(':')[0]
        try:
            self._engine = self._engines_map[schema.lower()](db_url, config)
        except KeyError:
            raise ValueError("Can not find driver for schema %s" % schema)

    def get_engine(self):
        if self._engine:
            return self._engine
        raise ValueError("Can not return engine. Please configure "
                         "EngineFactory")


engine_factory = EngineFactory()
