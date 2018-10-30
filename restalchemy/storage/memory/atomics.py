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

import struct


def compare_and_swap(memory_array, lock, offset, ctype_str, from_val, to_val):
    """Compare value in memory array and change it. Atomic operation

    The target value does not apply if other process or thread fill to array
    cell new value. The lock will be released for minimal time as it possible.

    :param memory_array: the shared memory array.
    :param lock: the lock for atomic operation.
    :param offset: the offset in memory array.
    :param ctype_str: the ctype in string format. see struct module for more
                      information.
    :param from_val: memory_array[offset] should be equivalent to from_val.
    :param to_val: the target value.

    """
    if struct.unpack_from(ctype_str, memory_array, offset)[0] != from_val:
        return False
    with lock:
        if struct.unpack_from(ctype_str, memory_array, offset)[0] != from_val:
            return False
        struct.pack_into(ctype_str, memory_array, offset, to_val)
    return True
