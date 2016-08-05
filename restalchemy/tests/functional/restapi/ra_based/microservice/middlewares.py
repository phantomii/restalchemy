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


from restalchemy.api import middlewares
from restalchemy.tests.functional.restapi.ra_based.microservice import (
    contexts)


class ContextMiddleware(middlewares.ContextMiddleware):

    def process_request(self, req):
        ctx = contexts.Context()
        req.context = ctx
        result = req.get_response(self.application)
        ctx.release()
        return result
