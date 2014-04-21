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


class RestAlchemyException(Exception):
    """Base REST Alchemy Exception.

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """

    message = "An unknown exception occurred."
    code = 0

    def __init__(self, **kwargs):
        self.msg = self.message % kwargs
        super(RestAlchemyException, self).__init__(self.msg)

    def __repr__(self):
        return "Code: %s, Message: %s" % (self.code, self.msg)


class ValueError(RestAlchemyException):

    message = "Invalid value for %(class_name)s with base: %(value)s"
    code = 400


class ValueRequiredError(RestAlchemyException):

    message = "Value is required"
    code = 400


class PropertyNotFoundError(RestAlchemyException):

    message = "'%(class_name)s' object has no property '%(property_name)s'"
    code = 400


class NotImplementedError(RestAlchemyException):

    message = "Not implemented"
    code = 400


class NotFoundError(RestAlchemyException):

    message = "Not Found"
    code = 400


# TODO(Eugene Frolov): TBD
class ReadOnlyPropertyError(RestAlchemyException):

    message = "One can't change a read only property"
    code = 400


class TypeError(RestAlchemyException):

    message = "Cannot %(action)s '%(t1)s' and '%(t2)s' objects"
    code = 400
