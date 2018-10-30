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

import contextlib
import struct
import os
import hashlib
import math
import mmap
import multiprocessing as mp

import six

from restalchemy.storage.memory import atomics


def prepare_index_file(file, mode='w+b'):
    header = six.b('\x2f\x01')
    file.write(header)
    file.flush()
    return len(header)


class ConflictIndex(Exception):
    pass


def md5_hash_func(key):
    return six.b(hashlib.md5(six.b(key)).hexdigest())


class Index(object):
    """Multiprocess index

    :param path_to_index: path to index file on your disk.
    :param lock_areas_count: number of areas in a data array with parallel
                             locks. Should be 1, 16 or 256.
    :param index_length: index size which used for table. For example: index
                      size is 1 follow to table size is 16. Hash size 2 follow
                      to table size is 256 and so on.
    :param hash_func: A hash function to construct index hash and data hash.

    """

    # PID length in bites
    LPID = 2

    def __init__(self, path_to_index, index_length=2, lock_areas_count=1,
                 hash_func=md5_hash_func):
        super(Index, self).__init__()

        self._hash_func = hash_func

        # Construct locks
        if lock_areas_count not in [1, 16, 256]:
            raise ValueError("Lock areas count should be one of [1, 16, 256]")
        self._lock_areas = [mp.Lock() for lock in range(lock_areas_count)]

        self._index_length = index_length
        self._hash_length = len(self._hash_func('test_length'))
        # Calculate shared memory parameters
        # Record_size = record_pid_allocation + is_filled + hash_length
        #               + data_pointer + next_rec
        self._record_size = self.LPID + 1 + self._hash_length + 4 + 4
        self._record_format = "=H?%sLL" % ('%ds' % self._hash_length)
        self._table_size = (16 ** index_length) * self._record_size

        # Prepare shared memory and index file
        self._index_file = open(path_to_index, "w+b")
        self._table_offset = prepare_index_file(self._index_file)
        self._shm = mmap.mmap(self._index_file.fileno(), self._table_offset,
                              access=mmap.ACCESS_WRITE)
        self._shm_size = (self._table_offset +
                          (self._table_size * (16 ** index_length)))
        self._shm.resize(self._shm_size)

    def release(self):
        self._shm.close()
        self._index_file.close()

    @contextlib.contextmanager
    def _record_allocate(self, key_hash, offset):
        area = int(key_hash[:int(math.log(1, 16))] or '0', 16)
        lock = self._lock_areas[area]
        pid = os.getpid()
        while not atomics.compare_and_swap(
                memory_array=self._shm, lock=lock, offset=offset,
                ctype_str="H", from_val=0, to_val=pid):
            # TODO(efrolov): Detect infinity loop and raise exception
            pass
        try:
            yield
        finally:
            struct.pack_into('H', self._shm, offset, 0)

    def _recursive_find_and_insert(self, key, value, key_hash, offset):
        with self._record_allocate(key_hash, offset):
            pid, r_filled, r_hash, r_pointer, r_next = (
                struct.unpack_from(self._record_format, self._shm, offset))

            # Record is empty. Just write data.
            if not r_filled:
                struct.pack_into(self._record_format, self._shm, offset,
                                 pid, True, key_hash, value, 0)
                return offset

            # Record is not empty and record hash is equal key hash
            if r_hash == key_hash:
                raise ConflictIndex("Record with key %s exists" % key)

            if r_next == 0:
                next_record = self._recursive_find_and_insert(
                    key, value, key_hash, offset + self._record_size)
                struct.pack_into(self._record_format, self._shm, offset,
                                 pid, True, r_hash, r_pointer, next_record)
                return next_record

        # has next record and r_hash != key_hash
        return self._recursive_find_and_insert(key, value, key_hash, r_next)

    def insert(self, key, value):
        key_hash = self._hash_func(key)
        record_id = int(key_hash[:self._index_length], 16)
        offset = record_id * self._record_size + self._table_offset
        return self._recursive_find_and_insert(key, value, key_hash, offset)

    def delete(self, key):
        pass

    def get(self, key):
        pass
