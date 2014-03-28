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

from restalchemy.common import exceptions as exc


class RestfulObject(object):

    def __init__(self):
        super(RestfulObject, self).__init__()

    def _get_worker_method(self, worker_name):
        try:
            return getattr(self, worker_name)
        except AttributeError:
            raise exc.NotImplementedError()

    def _result_processing(self, result, status_code=200, headers={},
                           add_location=False):

        def correct(body, c=status_code, h={}, *args):
            if add_location:
                headers['Location'] = body.get_uri()
            headers.update(h)
            return body, c, headers

        if type(result) == tuple:
            return correct(*result)
        return correct(result)
