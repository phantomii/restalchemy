# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2018 Eugene Frolov <eugene@frolov.net.ru>
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

import six


@six.add_metaclass(abc.ABCMeta)
class AbstractExpression(object):

    def __init__(self, value):
        super(AbstractExpression, self).__init__()
        self._value = value

    @property
    def value(self):
        return self._value

    @abc.abstractmethod
    def construct_expression(self, name):
        raise NotImplementedError()


class EQ(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` = " % name) + "%s"


class NE(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` <> " % name) + "%s"


class GT(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` > " % name) + "%s"


class GE(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` >= " % name) + "%s"


class LT(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` < " % name) + "%s"


class LE(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` <= " % name) + "%s"


class Is(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` IS " % name) + "%s"


class IsNot(AbstractExpression):

    def construct_expression(self, name):
        return ("`%s` IS NOT " % name) + "%s"
