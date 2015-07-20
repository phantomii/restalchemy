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
    code = 500

    def __init__(self, **kwargs):
        self.msg = self.message % kwargs
        super(RestAlchemyException, self).__init__(self.msg)

    def __repr__(self):
        return "Code: %s, Message: %s" % (self.code, self.msg)


class PropertyNotFoundError(RestAlchemyException):

    message = "'%(class_name)s' object has no property '%(property_name)s'"
    code = 400


class NotFoundError(RestAlchemyException):

    message = "Nothing is found on path '%(path)s'"
    code = 404


class NotImplementedError(NotFoundError):

    message = "Not implemented"


class UnsupportedHttpMethod(RestAlchemyException):
    message = "HTTP method '%(method)s' is not supported."
    code = 405


class UnsupportedMethod(NotFoundError):
    message = "Method '%(method)s' is not supported " \
              "for %(object_name)s"


class LocatorNotFound(NotFoundError):
    message = ("Locator is not found for URI %(uri)s. "
               "Thus resource could not be found. ")


class IncorrectRouteAttributeClass(NotFoundError):
    message = "Route %(route)s is of unacceptable class"


class IncorrectRouteAttribute(NotFoundError):
    message = "Route %(route)s doesn't have method %(attr)s"


class IncorrectActionCall(NotFoundError):
    message = "Action %(action)s is incorrectly called with HTTP method %(" \
              "method)s"


class ResourceNotFoundError(NotFoundError):

    message = "Resource '%(resource)s' is not found on path: %(path)s"


class CollectionNotFoundError(NotFoundError):

    message = "Collection '%(collection)s' is not found on path: %(path)s"


class PropertyException(RestAlchemyException, ValueError):

    def __init__(self, name=None, model=None):
        self.name = name or 'Unknown'
        self.model = model or 'Unknown'
        super(PropertyException, self).__init__(
            name=self.name,
            model=self.model
        )


class PropertyRequired(PropertyException):

    message = ("Value for property '%(name)s' for model %(model)s "
               "is required! Property should not be None value.")


class ReadOnlyProperty(PropertyException):

    message = ("Property '%(name)s' of model %(model)s is read only!")


class TypeError(RestAlchemyException, TypeError):

    message = "Invalid type value '%(value)s' for '%(property_type)s'"

    def __init__(self, value, property_type):
        self._value = value
        self._property_type = property_type
        super(TypeError, self).__init__(
            value=value, property_type=type(property_type).__name__)

    def get_value(self):
        return self._value

    def get_property_type(self):
        return self._property_type


class ModelTypeError(TypeError):

    message = ("Invalid type value '%(value)s'(%(value_type)s) for "
               "'%(model_name)s.%(property_name)s'(%(property_type)s)")

    def __init__(self, value, property_name, property_type, model):
        super(TypeError, self).__init__(
            value=value, value_type=type(value),
            property_type=type(property_type).__name__,
            model_name=type(model).__name__,
            property_name=property_name)


class RelationshipModelError(RestAlchemyException):

    message = ("Invalid model %(model)s for relationship. Must be inherited "
               "from dm.core.models.Model")
