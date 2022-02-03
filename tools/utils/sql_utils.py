import pyodbc
from typing import List, Dict, Union
from enum import IntEnum


class _BaseType(IntEnum):
    ACCESS = 0
    POSTGRES = 1


class Connection:
    _connection: pyodbc.Connection
    _cursor: pyodbc.Cursor
    _connection_string: str
    _base_type: _BaseType

    def __init__(self, connection_string: str):
        self._connection_string: str = connection_string

    def __enter__(self):
        self._connection = pyodbc.connect(self._connection_string)
        self._cursor = self._connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.close()
        self._connection.close()

    def retrieve_data(self, table_name: str, fields: List[str],
                      key_names: Union[List[str], None],
                      key_values: Union[List[str], None],
                      uniq_values: bool = False,
                      sort_by: Union[List[str], None] = None,
                      key_operator: Union[List[str], None] = None) -> List[Dict[str, str]]:

        distinct_placeholder: str = ' DISTINCT ' if uniq_values else ''
        sort_by_placeholder: str = ' ORDER BY ' + ' ,'.join(sort_by) + ' ASC' if sort_by is not None else ''
        if key_names is None and key_values is None:
            query = 'SELECT {0}{1} FROM {2}{3}'.format(distinct_placeholder, ','.join(fields), table_name,
                                                       sort_by_placeholder)
            self._cursor.execute(query)
        elif key_names is not None and key_values is not None:
            if len(key_values) != len(key_names):
                print("Несоответствие названий ключевых полей и их значений")
                raise Exception("AccessError")

            key_column_placeholder: str = ''
            key_values_for_query = []
            for index in range(len(key_values)):
                if key_values[index].casefold() == 'null'.casefold():
                    part_string = '{0} {1} NULL'.format(key_names[index],
                                                        'IS' if key_operator is None else key_operator[index])
                else:
                    part_string = '{0} {1} ?'.format(key_names[index],
                                                     '=' if key_operator is None else key_operator[index])
                    key_values_for_query.append(key_values[index])
                key_column_placeholder = part_string if key_column_placeholder == '' else \
                    key_column_placeholder + ' AND ' + part_string

            query = 'SELECT {0}{1} FROM {2} WHERE {3}{4}'.format(distinct_placeholder, ', '.join(fields),
                                                                 table_name, key_column_placeholder,
                                                                 sort_by_placeholder)
            self._cursor.execute(query, key_values_for_query)
        else:
            print("Несоответствие названий ключевых полей и их значений")
            raise Exception("AccessError")

        out_list = []
        for row in self._cursor.fetchall():
            out_row = {}
            for column_index in range(len(fields)):
                out_row[fields[column_index]] = None if row[column_index] is None else str(row[column_index])
            out_list.append(out_row)
        return out_list

    def retrieve_data_from_joined_table(self, table_name1: str, table_name2,
                                        joined_fields: List[str],
                                        fields: List[str],
                                        key_names: Union[List[str], None],
                                        key_values: Union[List[str], None],
                                        uniq_values: bool = False,
                                        sort_by: Union[List[str], None] = None,
                                        key_operator: str = '=') -> List[Dict[str, str]]:
        join_placeholder: str = ','.join(
            ['{0}.{2} = {1}.{2}'.format(table_name1, table_name2, field) for field in joined_fields])
        distinct_placeholder: str = ' DISTINCT ' if uniq_values else ''
        sort_by_placeholder: str = ' ORDER BY ' + ' ,'.join(sort_by) + ' ASC' if sort_by is not None else ''

        if key_names is None and key_values is None:
            query = 'SELECT {0}{1} FROM {2} INNER JOIN {3} ON {4}{5}'.format(distinct_placeholder, ','.join(fields),
                                                                             table_name1, table_name2,
                                                                             join_placeholder,
                                                                             sort_by_placeholder)
            self._cursor.execute(query)
        elif key_names is not None and key_values is not None:
            if len(key_values) != len(key_names):
                print("Несоответствие названий ключевых полей и их значений")
                raise Exception("AccessError")
            key_column_placeholder = ['{0} {1} ?'.format(item, key_operator) for item in key_names]
            query = 'SELECT {0}{1} FROM {2} INNER JOIN {3} ON {4} WHERE {5}{6}'.format(
                distinct_placeholder, ','.join(fields), table_name1, table_name2, join_placeholder,
                ' AND '.join(key_column_placeholder), sort_by_placeholder)
            self._cursor.execute(query, key_values)
        else:
            print("Несоответствие названий ключевых полей и их значений")
            raise Exception("AccessError")
        out_list = []
        for row in self._cursor.fetchall():
            out_row = {}
            for column_index in range(len(fields)):
                out_row[fields[column_index]] = None if row[column_index] is None else str(row[column_index])
            out_list.append(out_row)
        return out_list

    def remove_row(self, table_name: str, key_names: List[str], key_values: List[str]) -> None:
        key_column_placeholder = ['{0} = ?'.format(item) for item in key_names]
        if len(key_values) != len(key_names):
            print("Неверное число значений ключевых полей")
            raise Exception("AccessError")

        query = 'DELETE FROM {0} WHERE {1}'.format(table_name, ' AND '.join(key_column_placeholder))
        self._cursor.execute(query, key_values)

    def update_field(self, table_name: str, fields: List[str], values: List[str], key_names: List[str],
                     key_values: List[str]) -> None:
        if len(key_values) != len(key_names):
            print("Несоответствие названий ключевых полей и их значений")
            raise Exception("AccessError")
        if len(fields) != len(values):
            print("Несоответствие названий обновляемых полей и их значений")
            raise Exception("AccessError")

        values_placeholder: str = ','.join(['{0}=?'.format(fields[index]) for index in range(len(fields))])

        key_column_placeholder = ['{0} = ?'.format(item) for item in key_names]

        query = 'UPDATE {0} SET {1} WHERE {2}'.format(table_name, values_placeholder,
                                                      ' AND '.join(key_column_placeholder))
        self._cursor.execute(query, values + key_values)

    def commit(self):
        self._connection.commit()

    def is_table_exists(self, table_name: str) -> bool:
        if self._base_type == _BaseType.ACCESS:
            values: List = self.retrieve_data(table_name='MSysObject',
                                              fields=['Name'],
                                              key_names=['Name', 'Type'],
                                              key_values=[table_name, '(1,4,6)'],
                                              key_operator=['=', 'IN'])
            if len(values) == 0:
                return False
            else:
                return True

        elif self._base_type == _BaseType.POSTGRES:
            raise Exception('Неподдерживаемый тип базы')

    def clear_table(self, table_name: str, drop_index: bool = False) -> None:
        self._cursor.execute(f'DELETE * From {table_name}')
        if self._base_type == _BaseType.ACCESS and drop_index:
            self._cursor.execute(f'ALTER TABLE {table_name} ALTER COLUMN ID COUNTER(1,1)')
        self._cursor.commit()

    def insert_row(self, table_name: str, column_names: List[str], values: List[Union[str, int, float]]) -> None:
        if len(column_names) != len(values):
            print("Несоответствие количества столбцов количеству значений")
            raise Exception("SQLError")
        column_name_placeholder: str = ','.join(column_names)
        values_placeholder: str = ','.join(
            [self.get_string_value(item) for item in values])
        query: str = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table_name, column_name_placeholder,
                                                                 values_placeholder)
        self._cursor.execute(query)
        self._cursor.commit()

    def get_row_count(self, table_name: str) -> int:
        queury: str = f'SELECT COUNT(*) FROM {table_name}'
        self._cursor.execute(queury)
        return int(self._cursor.fetchval())

    @staticmethod
    def get_string_value(value: Union[str, float, int]) -> str:
        if isinstance(value, int) or isinstance(value, float):
            return f'{value}'
        if isinstance(value, str):
            return f"'{value}'"
        if value is None:
            return 'NULL'

    @staticmethod
    def connect_to_mdb(base_path):
        connection_string: str = 'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0};'. \
            format(base_path)
        connection: Connection = Connection(connection_string)
        connection._base_type = _BaseType.ACCESS
        return connection

    @staticmethod
    def connect_to_postgre(database: str, user: str, password: str, server: str, port: int):
        connection_string = "DRIVER={{PostgreSQL Unicode}};DATABASE={0};UID={1};PWD={2};SERVER={3};PORT={4};". \
            format(database, user, password, server, port)
        connection: Connection = Connection(connection_string)
        connection._base_type = _BaseType.POSTGRES
        return connection
