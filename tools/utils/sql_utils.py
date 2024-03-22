import pyodbc
import psycopg
from enum import IntEnum


class BaseType(IntEnum):
    ACCESS = 0
    POSTGRES = 1


class Connection:
    _connection: pyodbc.Connection | psycopg.Connection
    _cursor: pyodbc.Cursor | psycopg.Cursor
    _connection_string: str
    _base_type: BaseType

    def __init__(self, connection_string: str):
        self._connection_string: str = connection_string

    def __enter__(self):
        if self._base_type == BaseType.ACCESS:
            self._connection = pyodbc.connect(self._connection_string)
            self._cursor = self._connection.cursor()
        elif self._base_type == BaseType.POSTGRES:
            self._connection = psycopg.connect(self._connection_string)
            self._cursor = self._connection.cursor()
        else:
            raise Exception("Неподдерживаемый тип DBEngine")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.close()
        self._connection.close()

    def retrieve_data(self, table_name: str, fields: list[str],
                      key_names: list[str] | None = None,
                      key_values: list[str | int | bool | None] | None = None,
                      uniq_values: bool = False,
                      sort_by: list[str] | None = None,
                      key_operator: list[str] | None = None) -> list[dict[str, str]]:
        table_name = self.modify_table_name(table_name)
        fields = self.modify_column_names(fields)
        key_names = self.modify_column_names(key_names)
        sort_by = self.modify_column_names(sort_by)

        distinct_placeholder: str = ' DISTINCT ' if uniq_values else ''
        sort_by_placeholder: str = ' ORDER BY ' + ' ,'.join(sort_by) + ' ASC' if sort_by is not None else ''
        if key_names is None and key_values is None:
            query = 'SELECT {0}{1} FROM {2}{3}'.format(distinct_placeholder, ','.join(fields), table_name,
                                                       sort_by_placeholder)
            self._cursor.execute(query)
        elif key_names is not None and key_values is not None:
            if len(key_values) != len(key_names):
                print('Несоответствие названий ключевых полей и их значений')
                raise Exception("AccessError")

            key_column_placeholder: str = ''
            key_values_for_query: list[str | int | bool] = []
            for index in range(len(key_values)):
                if key_values[index] is None:
                    part_string = '{0} {1} NULL'.format(key_names[index],
                                                        'IS' if key_operator is None else key_operator[index])
                else:
                    if self._base_type == BaseType.ACCESS:
                        part_string = '{0} {1} ?'.format(key_names[index],
                                                         '=' if key_operator is None else key_operator[index])
                    elif self._base_type == BaseType.POSTGRES:

                        part_string = '{0} {1} %s'.format(key_names[index],
                                                          '=' if key_operator is None else key_operator[index])
                    else:
                        raise Exception("Неподдерживаемый тип DBEngine")
                    key_values_for_query.append(key_values[index])
                key_column_placeholder = part_string if key_column_placeholder == '' else \
                    key_column_placeholder + ' AND ' + part_string

            query = 'SELECT {0}{1} FROM {2} WHERE {3}{4}'.format(distinct_placeholder, ', '.join(fields),
                                                                 table_name, key_column_placeholder,
                                                                 sort_by_placeholder)
            self._cursor.execute(query, key_values_for_query)
        else:
            print('Несоответствие названий ключевых полей и их значений')
            raise Exception("AccessError")

        out_list = []
        for row in self._cursor.fetchall():
            out_row = {}
            for column_index in range(len(fields)):
                out_row[fields[column_index]] = None if row[column_index] is None else str(row[column_index])
            out_list.append(out_row)
        return out_list

    def get_column_names(self, table_name: str) -> set[str]:
        table_name = self.modify_table_name(table_name)
        if self._base_type == BaseType.ACCESS:
            return set([row.column_name for row in self._cursor.columns(table=table_name.strip('[]'))])
        elif self._base_type == BaseType.POSTGRES:
            self._cursor.execute(f'Select * FROM {table_name} LIMIT 0')
            return set([desc[0] for desc in self._cursor.description])
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    def contains_value(self, table_name: str,
                       key_names: list[str] | None,
                       key_values: list[str],
                       key_operator: list[str] | None = None) -> bool:
        table_name = self.modify_table_name(table_name)
        key_names = self.modify_column_names(key_names)

        return self.count_values(table_name=table_name,
                                 key_names=key_names,
                                 key_values=key_values,
                                 key_operator=key_operator) > 0

    def count_values(self, table_name: str,
                     key_names: list[str] | None,
                     key_values: list[str],
                     key_operator: list[str] | None = None) -> int:
        if len(key_values) != len(key_names):
            print("Несоответствие названий ключевых полей и их значений")
            raise Exception("AccessError")

        table_name = self.modify_table_name(table_name)
        key_names = self.modify_column_names(key_names)

        key_column_placeholder: str = ''
        key_values_for_query: list[str | int | bool] = []
        for index in range(len(key_values)):
            if key_values[index] is None:
                part_string = '{0} {1} NULL'.format(key_names[index],
                                                    'IS' if key_operator is None else key_operator[index])
            else:
                if self._base_type == BaseType.ACCESS:
                    part_string = '{0} {1} ?'.format(key_names[index],
                                                     '=' if key_operator is None else key_operator[index])
                elif self._base_type == BaseType.POSTGRES:
                    part_string = '{0} {1} %s'.format(key_names[index],
                                                      '=' if key_operator is None else key_operator[index])
                else:
                    raise Exception("Неподдерживаемый тип DBEngine")

                key_values_for_query.append(key_values[index])
            key_column_placeholder = part_string if key_column_placeholder == '' else \
                key_column_placeholder + ' AND ' + part_string

        query = 'SELECT COUNT(*) FROM {0} WHERE {1}'.format(table_name, key_column_placeholder)
        self._cursor.execute(query, key_values_for_query)
        return int(self._cursor.fetchall()[0][0])

    def retrieve_data_from_joined_table(self, table_name1: str, table_name2,
                                        joined_fields: list[str],
                                        fields: list[str],
                                        key_names: list[str] | None,
                                        key_values: list[str] | None,
                                        uniq_values: bool = False,
                                        sort_by: list[str] | None = None,
                                        key_operator: str = '=') -> list[dict[str, str]]:
        table_name1 = self.modify_table_name(table_name1)
        table_name2 = self.modify_table_name(table_name2)
        fields = self.modify_column_names(fields)
        key_names = self.modify_column_names(key_names)
        sort_by = self.modify_column_names(sort_by)

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

    def remove_row(self, table_name: str, key_names: list[str], key_values: list[str]) -> None:
        table_name = self.modify_table_name(table_name)
        key_names = self.modify_column_names(key_names)
        param_place_holder: str
        if self._base_type == BaseType.ACCESS:
            param_place_holder = '?'
        elif self._base_type == BaseType.POSTGRES:
            param_place_holder = '%s'
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

        key_column_placeholder = ['{0} = {1}'.format(item, param_place_holder) for item in key_names]
        if len(key_values) != len(key_names):
            print("Неверное число значений ключевых полей")
            raise Exception("AccessError")

        query = 'DELETE FROM {0} WHERE {1}'.format(table_name, ' AND '.join(key_column_placeholder))
        self._cursor.execute(query, key_values)

    def update_field(self, table_name: str, fields: list[str], values: list[str], key_names: list[str],
                     key_values: list[str]) -> None:
        table_name = self.modify_table_name(table_name)
        fields = self.modify_column_names(fields)
        key_names = self.modify_column_names(key_names)

        param_place_holder: str
        if self._base_type == BaseType.ACCESS:
            param_place_holder = '?'
        elif self._base_type == BaseType.POSTGRES:
            param_place_holder = '%s'
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

        if len(key_values) != len(key_names):
            print("Несоответствие названий ключевых полей и их значений")
            raise Exception("AccessError")
        if len(fields) != len(values):
            print("Несоответствие названий обновляемых полей и их значений")
            raise Exception("AccessError")

        values_placeholder: str = ','.join(
            ['{0}={1}'.format(fields[index], param_place_holder) for index in range(len(fields))])
        param_place_holder: str
        if self._base_type == BaseType.ACCESS:
            param_place_holder = '?'
        elif self._base_type == BaseType.POSTGRES:
            param_place_holder = '%s'
        else:
            raise Exception("Неподдерживаемый тип DBEngine")
        key_column_placeholder = ['{0} = {1}'.format(item, param_place_holder) for item in key_names]

        query = 'UPDATE {0} SET {1} WHERE {2}'.format(table_name, values_placeholder,
                                                      ' AND '.join(key_column_placeholder))
        self._cursor.execute(query, values + key_values)

    def retrive_data_with_having(self, table_name: str, fields: list[str], key_column: str,
                                 key_values: list[str]):
        table_name = self.modify_table_name(table_name)
        fields = self.modify_column_names(fields)

        condition_placeholder: str = ' OR '.join([f"{table_name}.{key_column} = ?" for _ in range(len(key_values))])
        fields_placeholder: str = ', '.join([f'{table_name}.{field}' for field in fields])
        having_placeholder: str = 'COUNT({0}.{1})={2}'.format(table_name, key_column, len(key_values))
        query = 'SELECT {0} FROM {1} WHERE {2} GROUP BY {0} HAVING {3}'.format(fields_placeholder,
                                                                               table_name,
                                                                               condition_placeholder,
                                                                               having_placeholder)

        self._cursor.execute(query, key_values)
        out_list = []
        for row in self._cursor.fetchall():
            out_row = {}
            for column_index in range(len(fields)):
                out_row[fields[column_index]] = None if row[column_index] is None else str(row[column_index])
            out_list.append(out_row)
        return out_list

    def clear_table(self, table_name: str, drop_index: bool = False) -> None:
        table_name = self.modify_table_name(table_name)

        if self._base_type == BaseType.ACCESS:
            self._cursor.execute(f'DELETE * From {table_name}')
            if drop_index:
                self._cursor.execute(f'ALTER TABLE {table_name} ALTER COLUMN ID COUNTER(1,1)')
        elif self._base_type == BaseType.POSTGRES:
            self._cursor.execute(f'DELETE From {table_name}')
        else:
            raise Exception("Неподдерживаемый тип DBEngine")
        self.commit()

    def insert_row(self, table_name: str, column_names: list[str], values: list[str | int | float | None]) -> None:
        table_name = self.modify_table_name(table_name)
        column_names = self.modify_column_names(column_names)

        if len(column_names) != len(values):
            print("Несоответствие количества столбцов количеству значений")
            raise Exception("SQLError")
        column_name_placeholder: str = ','.join(column_names)
        values_placeholder: str = ','.join(
            [self.get_string_value(item) for item in values])
        query: str = 'INSERT INTO {0} ({1}) VALUES ({2})'.format(table_name, column_name_placeholder,
                                                                 values_placeholder)
        self._cursor.execute(query)

    def get_row_count(self, table_name: str) -> int:
        table_name = self.modify_table_name(table_name)
        queury: str = f'SELECT COUNT(*) FROM {table_name}'
        self._cursor.execute(queury)
        if self._base_type == BaseType.ACCESS:
            return int(self._cursor.fetchval())
        elif self._base_type == BaseType.POSTGRES:
            return int(self._cursor.fetchone()[0])
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    def commit(self):
        if self._base_type == BaseType.ACCESS:
            self._cursor.commit()
        elif self._base_type == BaseType.POSTGRES:
            self._connection.commit()
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    def modify_column_names(self, columns: list[str]) -> list[str] | None:
        if columns is None:
            return None
        if self._base_type == BaseType.ACCESS:
            return columns
        elif self._base_type == BaseType.POSTGRES:
            return [self.modify_column_name(column) for column in columns]
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    def modify_column_name(self, column: str) -> str | None:
        if column is None:
            return None
        if self._base_type == BaseType.ACCESS:
            return column
        elif self._base_type == BaseType.POSTGRES:
            if column == 'REF':
                return 'refer'
            elif column == 'ТАБЛО':
                return 'indicator_name'
            elif column == 'TYPE':
                return 'type_name'
            elif column == 'SCHEMA':
                return 'schema_name'
            elif column == 'COMMENT':
                return 'comm'
            elif column == 'GROUP':
                return 'group_name'
            elif column == 'MODULE':
                return 'module_name'
            elif column == 'SET':
                return 'set_val'
            elif column == 'CONNECTION':
                return 'conn'
            else:
                return column.lower()
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    def get_base_type(self):
        return self._base_type

    def modify_table_name(self, table_name: str) -> str:
        if self._base_type == BaseType.ACCESS:
            return f'[{table_name}]'
        elif self._base_type == BaseType.POSTGRES:
            match table_name:
                case 'Логика ТС ОДУ':
                    return 'ts_odu_logic'
                case 'Модули связи с процессом':
                    return 'process_modules'
                case 'МЭК 61850':
                    return 'iec_61850'
                case 'Периферийное оборудование':
                    return 'extern_devices'
                case 'Сигналы и механизмы':
                    return 'signals_and_mechanisms'
                case 'Сигналы и механизмы АЭП':
                    return 'signals_and_mechanisms_aep'
                case 'Сигналы и механизмы ТС ОДУ':
                    return 'ts_odu_signals_and_mechanisms'
                case 'REF':
                    return 'refs'
                case _:
                    return f'{table_name.lower().replace(" ", "_")}'
        else:
            raise Exception("Неподдерживаемый тип DBEngine")

    @staticmethod
    def get_string_value(value: str | float | int | None) -> str:
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
        connection._base_type = BaseType.ACCESS
        return connection

    @staticmethod
    def connect_to_postgres(database: str, user: str, password: str, server: str, port: int):
        connection_string = f'host={server} port={port} dbname={database} user={user} password={password}'
        connection: Connection = Connection(connection_string)
        connection._base_type = BaseType.POSTGRES
        return connection
