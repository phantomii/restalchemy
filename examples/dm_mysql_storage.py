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

from restalchemy.dm import models
from restalchemy.dm import properties
from restalchemy.dm import relationships
from restalchemy.dm import types
from restalchemy.storage.sql import engines
from restalchemy.storage.sql import orm


# CREATE TABLE `foos` (
#      `uuid` CHAR(36) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL ,
#      `foo_field1` INT NOT NULL ,
#      `foo_field2` VARCHAR(255) NOT NULL ,
# PRIMARY KEY (`uuid`(36)) USING HASH)
# ENGINE = InnoDB;
class FooModel(models.ModelWithUUID, orm.SQLStorableMixin):
    __tablename__ = "foos"
    foo_field1 = properties.property(types.Integer, required=True)
    foo_field2 = properties.property(types.String, default="foo_str")


# CREATE TABLE `test`.`bars` (
#     `uuid` CHAR(36) CHARACTER SET utf32 COLLATE utf32_unicode_ci NOT NULL ,
#     `bar_field1` VARCHAR(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci
#         NOT NULL ,
#     `foo` CHAR(36) CHARACTER SET utf32 COLLATE utf32_unicode_ci NOT NULL ,
# PRIMARY KEY (`uuid`(36)) USING HASH,
# INDEX `rlfoo` (`foo`(36)) USING HASH)
# ENGINE = InnoDB;

# ALTER TABLE `bars` ADD CONSTRAINT `_idx_foo` FOREIGN KEY (`foo`)
# REFERENCES `foos`(`uuid`) ON DELETE RESTRICT ON UPDATE RESTRICT;
class BarModel(models.ModelWithUUID, orm.SQLStorableMixin):
    __tablename__ = "bars"
    bar_field1 = properties.property(types.String(min_length=1, max_length=10))
    foo = relationships.relationship(FooModel)


engines.engine_factory.configure_factory(
    db_url="mysql://test:OyO83AdIn9hbK3uz@cameron.synapse.net.ru/test")


# Create new foo object and store it
foo1 = FooModel(foo_field1=10)
foo1.save()

bar1 = BarModel(bar_field1="test", foo=foo1)
bar1.save()

print list(BarModel.objects.get_all())
print BarModel.objects.get_one(filters={"uuid": bar1.get_id()})
print list(BarModel.objects.get_all(filters={"foo": foo1}))

bar1.delete()

foo2 = FooModel(foo_field1=11,
                foo_field2="some text")
foo2.save()

foos = list(FooModel.objects.get_all())
print foos

print FooModel.objects.get_one(filters={'foo_field1': 10})

# Modify foo_field2 and update it in storage
foo2.foo_field2 = 'xxx2 asdad asdasd'
foo2.save()

# Delete foo object from storage
for foo in foos:
    foo.delete()
