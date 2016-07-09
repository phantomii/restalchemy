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

from restalchemy.storage.sql.dialect import base


class SQLiteProcessResult(base.AbstractProcessResult):

    def __init__(self, result):
        super(SQLiteProcessResult, self).__init__(result)
        self._rows = None

    def get_count(self):
        return self._result.rowcount

    def fetchall(self):
        for row in self._result:
            yield row

    @property
    def rows(self):
        if self._rows is None:
            self._rows = self._result.fetchall()
        return self._rows


class AbstractDialectCommand(base.AbstractDialectCommand):

    def execute(self, session):
        return SQLiteProcessResult(
            super(AbstractDialectCommand, self).execute(session))


class MySQLInsert(AbstractDialectCommand):

    def get_values(self):
        values = tuple()
        for column_name in self._table.get_column_names():
            values += (self._data[column_name],)
        return values

    def get_statement(self):
        column_names = self._table.get_column_names()
        return "INSERT INTO %s (%s) VALUES (%s)" % (
            self._table.name,
            ", ".join(column_names),
            ", ".join(['%s'] * len(column_names))
        )


class MySQLUpdate(AbstractDialectCommand):

    def __init__(self, table, ids, data):
        super(MySQLUpdate, self).__init__(table, data)
        self._ids = ids

    def get_values(self):
        values = tuple()
        column_names = self._table.get_column_names(with_pk=False)
        pk_names = self._table.get_pk_names()
        for column_name in column_names:
            values += (self._data[column_name],)
        for column_name in pk_names:
            values += (self._ids[column_name],)
        return values

    def get_statement(self):
        column_names = self._table.get_column_names(with_pk=False)
        pk_names = self._table.get_pk_names()
        return "UPDATE %s SET %s WHERE %s" % (
            self._table.name,
            ", ".join(["%s = %s" % (name, "%s") for name in column_names]),
            ", ".join(["%s = %s" % (name, "%s") for name in pk_names])
        )


class MySQLDelete(AbstractDialectCommand):

    def __init__(self, table, ids):
        super(MySQLDelete, self).__init__(table=table, data={})
        self._ids = ids

    def get_values(self):
        values = tuple()
        pk_names = self._table.get_pk_names()
        for column_name in pk_names:
            values += (self._ids[column_name],)
        return values

    def get_statement(self):
        pk_names = self._table.get_pk_names()
        return "DELETE FROM %s WHERE %s" % (
            self._table.name,
            ", ".join(["%s = %s" % (name, "%s") for name in pk_names])
        )


class MySQLSelect(AbstractDialectCommand):

    def __init__(self, table, filters):
        super(MySQLSelect, self).__init__(table=table, data={})
        self._check_filters(filters)
        self._filters = filters

    def _check_filters(self, filters):
        result = set(filters.keys()) - set(self._table.get_column_names())
        if result:
            raise ValueError("Unknown columns: %s. Filters is %s" % (
                result, filters))

    def get_values(self):
        return [self._filters[key] for key in sorted(self._filters.keys())]

    def get_statement(self):
        sql = "SELECT %s FROM %s" % (
            ", ".join(self._table.get_column_names()),
            self._table.name
        )
        filt = "AND".join(["%s = %s" % (param, "%s")
                           for param in sorted(self._filters.keys())])
        return sql + " WHERE %s" % filt if filt else sql


class MySQLDialect(base.AbstractDialect):

    def insert(self, table, data):
        return MySQLInsert(table, data)

    def update(self, table, ids, data):
        return MySQLUpdate(table, ids, data)

    def delete(self, table, ids):
        return MySQLDelete(table, ids)

    def select(self, table, filters):
        return MySQLSelect(table, filters)