# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014 Eugene Frolov <eugene@frolov.net.ru>
# Copyright 2014 Mirantis Inc
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

import collections
import six


class ReadOnlyDictProxy(collections.Mapping):
    """A hashable, immutable dict proxy.

    Return a proxy object for a mapping which enforces read-only behavior.
    This is normally used to create a proxy to prevent modification of the
    dictionary for non-dynamic class types.
    """

    def __init__(self, d):
        self._d = d
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for key, value in six.iteritems(self):
                self._hash ^= hash(key)
                self._hash ^= hash(value)

        return self._hash

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._d)


class classproperty(property):
    """Property for classes

    Standard property cannot be used on classes only on instances.
    This one was created to overcome this problem. The only limitation
    is that setter is not working for classes, only getter.

    This property could be used as:
        class A(object):
            @classproperty
            def test(cls):
                ...some cls processing...
                return result

        test = A.test  # method 'test' will be called with A class argument
    """

    def __get__(self, obj, cls):
            # Calls property function
        return self.fget(cls)
