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
import tempfile
import struct
import unittest
import os
import random
import multiprocessing as mp

import six

from restalchemy.storage.memory import indexes

# P_COUNT = 1000
# INC_COUNT = 1000

# k1 = mp.Value('i', 0)
# kl = mp.Lock()

# z = mp.Value('i', 0)


# def lock_inc(z):
#     pid = os.getpid()
#     while True:
#         if k1.value == 0:
#             with kl:
#                 if k1.value != 0:
#                     continue
#                 k1.value = pid
#             z.value += 1
#             k1.value = 0
#             break


# def inc(z):
#     for i in range(INC_COUNT):
#         lock_inc(z)

class TestIndex(unittest.TestCase):

    RECORD_FORMAT = '=H?32sLL'

    def setUp(self):
        self._instance = indexes.Index(
            path_to_index=tempfile.mktemp(),
            index_length=1,
            lock_areas_count=1,
            hash_func=self._hash_func)

    def tearDown(self):
        self._instance.release()

    def _hash_func(self, data):
        return six.b("{:0<32}".format(data))

    def test_insert_in_empty_record_no_collisions(self):
        # from nose import tools
        # tools.set_trace()
        FAKE_KEY = "000"
        FAKE_VALUE = 1

        offset = self._instance.insert(key=FAKE_KEY, value=FAKE_VALUE)
        pid, r_filled, r_hash, r_pointer, r_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm, 2))

        self.assertEqual(offset, 2)  # 2 - the first record after index header
        self.assertEqual(pid, 0)  # Not locked
        self.assertTrue(r_filled)
        self.assertEqual(r_hash, self._hash_func(FAKE_KEY))
        self.assertEqual(r_pointer, FAKE_VALUE)
        self.assertEqual(r_next, 0)  # No next records

    def test_insert_conflict_record_no_collisions(self):
        FAKE_KEY = "000"
        FAKE_VALUE_1 = 1
        FAKE_VALUE_2 = 2
        OFFSET = 2
        # Insert test record to shm
        # 1. RECORD FORMAT
        # 2. SHM
        # 3. value is 2 - offset
        # 4. value is 0 - record allocated to pid
        # 5. value is 1 - record filled
        # 6. Record hash
        # 7. Record value
        # 8. Next record if collision
        struct.pack_into(self.RECORD_FORMAT, self._instance._shm, OFFSET,
                         0, 1, self._hash_func(FAKE_KEY), FAKE_VALUE_1, 0)

        self.assertRaises(indexes.ConflictIndex, self._instance.insert,
                          key=FAKE_KEY, value=FAKE_VALUE_2)
        pid, r_filled, r_hash, r_pointer, r_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm,
                               OFFSET))

        self.assertEqual(pid, 0)  # Not locked
        self.assertTrue(r_filled)
        self.assertEqual(r_hash, self._hash_func(FAKE_KEY))
        self.assertEqual(r_pointer, FAKE_VALUE_1)
        self.assertEqual(r_next, 0)  # No next records

    def test_insert_record_with_one_collisions(self):
        # from nose import tools
        # tools.set_trace()
        FAKE_KEY_1 = "000"
        FAKE_KEY_2 = "001"
        FAKE_VALUE_1 = 1
        FAKE_VALUE_2 = 2
        OFFSET_RECORD_1 = 2
        OFFSET_RECORD_2 = 45

        # See test_insert_conflict_record_no_collisions
        struct.pack_into(self.RECORD_FORMAT, self._instance._shm,
                         OFFSET_RECORD_1, 0, 1, self._hash_func(FAKE_KEY_1),
                         FAKE_VALUE_1, 0)

        offset = self._instance.insert(key=FAKE_KEY_2, value=FAKE_VALUE_2)
        r1_pid, r1_filled, r1_hash, r1_pointer, r1_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm,
                               OFFSET_RECORD_1))
        r2_pid, r2_filled, r2_hash, r2_pointer, r2_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm,
                               OFFSET_RECORD_2))

        self.assertEqual(offset, OFFSET_RECORD_2)
        # First record
        self.assertEqual(r1_pid, 0)  # Not locked
        self.assertTrue(r1_filled)
        self.assertEqual(r1_hash, self._hash_func(FAKE_KEY_1))
        self.assertEqual(r1_pointer, FAKE_VALUE_1)
        self.assertEqual(r1_next, OFFSET_RECORD_2)
        # Second record
        self.assertEqual(r2_pid, 0)  # Not locked
        self.assertTrue(r2_filled)
        self.assertEqual(r2_hash, self._hash_func(FAKE_KEY_2))
        self.assertEqual(r2_pointer, FAKE_VALUE_2)
        self.assertEqual(r2_next, 0)

    def test_insert_conflict_record_with_one_collisions(self):
        # from nose import tools
        # tools.set_trace()
        FAKE_KEY_1 = "000"
        FAKE_KEY_2 = "001"
        FAKE_VALUE_1 = 1
        FAKE_VALUE_2 = 2
        FAKE_VALUE_3 = 3
        OFFSET_RECORD_1 = 2
        OFFSET_RECORD_2 = 45

        # See test_insert_conflict_record_no_collisions
        struct.pack_into(self.RECORD_FORMAT, self._instance._shm,
                         OFFSET_RECORD_1, 0, 1, self._hash_func(FAKE_KEY_1),
                         FAKE_VALUE_1, OFFSET_RECORD_2)
        struct.pack_into(self.RECORD_FORMAT, self._instance._shm,
                         OFFSET_RECORD_2, 0, 1, self._hash_func(FAKE_KEY_2),
                         FAKE_VALUE_2, 0)

        self.assertRaises(indexes.ConflictIndex, self._instance.insert,
                          key=FAKE_KEY_2, value=FAKE_VALUE_3)
        r1_pid, r1_filled, r1_hash, r1_pointer, r1_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm,
                               OFFSET_RECORD_1))
        r2_pid, r2_filled, r2_hash, r2_pointer, r2_next = (
            struct.unpack_from(self.RECORD_FORMAT, self._instance._shm,
                               OFFSET_RECORD_2))

        # First record
        self.assertEqual(r1_pid, 0)  # Not locked
        self.assertTrue(r1_filled)
        self.assertEqual(r1_hash, self._hash_func(FAKE_KEY_1))
        self.assertEqual(r1_pointer, FAKE_VALUE_1)
        self.assertEqual(r1_next, OFFSET_RECORD_2)
        # Second record
        self.assertEqual(r2_pid, 0)  # Not locked
        self.assertTrue(r2_filled)
        self.assertEqual(r2_hash, self._hash_func(FAKE_KEY_2))
        self.assertEqual(r2_pointer, FAKE_VALUE_2)
        self.assertEqual(r2_next, 0)

    def test_lock(self):
        pass
        # from nose import tools
        # tools.set_trace()
        # inc(z)
        # p = [mp.Process(target=inc, args=(z,)) for i in range(P_COUNT)]
        # [i.start() for i in p]
        # [i.join() for i in p]
        # self.assertEqual(z.value, P_COUNT * INC_COUNT)
