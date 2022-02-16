import logging
from dataclasses import dataclass, field

from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class Schema:
    name: str
    command_parts: list[str] = field(compare=False)
    signal_parts: list[str] = field(compare=False)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FindSchemasOptions:
    database_path: str
    sim_table_name: str
    schemas: list[Schema]


class FindSchemas:
    _options: FindSchemasOptions
    _access: Connection

    def __init__(self, options: FindSchemasOptions, access: Connection):
        self._options = options
        self._access = access

    def find_schemas_variants(self) -> dict[Schema, list[list[bool]]]:
        schema_variants: dict[Schema, list[list[bool]]] = {}
        for schema in self._options.schemas:
            variants: list[list[bool]] = []
            values_list: list[dict[str, str]] = self._access.retrive_data_with_having(
                table_name=self._options.sim_table_name,
                fields=['KKS', 'CABINET', 'KKSp'],
                key_column='PART',
                key_values=schema.command_parts)
            for value in values_list:
                parts_list: list[str] = self._get_part_list(kks=value['KKS'],
                                                            kksp=value['KKSp'],
                                                            cabinet=value['CABINET'])
                new_variant: list[bool] = self._get_schema_variant(schema=schema, parts_list=parts_list)
                if not self._variant_exists(variants=variants, new_variant=new_variant):
                    variants.append(new_variant)
            schema_variants[schema] = variants
        return schema_variants

    @staticmethod
    def _variant_exists(variants: list[list[bool]], new_variant: list[bool]):
        for variant in variants:
            if next((False for item1, item2 in zip(variant, new_variant) if item1 != item2), True):
                return True
        return False

    def _get_part_list(self, kks: str, kksp: str, cabinet: str) -> list[str]:
        parts_list: list[str] = []
        values_from_kks: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                           fields=['PART'],
                                                                           key_names=['KKS', 'CABINET'],
                                                                           key_values=[kks, cabinet])
        for value in values_from_kks:
            if value['PART'] not in values_from_kks:
                parts_list.append(value['PART'])

        values_from_kksp: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                            fields=['PART'],
                                                                            key_names=['KKSp', 'CABINET'],
                                                                            key_values=[kksp, cabinet])
        for value in values_from_kksp:
            if value['PART'] not in values_from_kksp:
                parts_list.append(value['PART'])

        return parts_list

    @staticmethod
    def _print_schemas_variants(schemas_variants: dict[Schema, list[list[bool]]]) -> None:
        for schema in schemas_variants:
            logging.info(f'Схема {schema.name}')
            for index in range(len(schemas_variants[schema])):
                logging.info(f'Вариация {index + 1}')
                logging.info(
                    ','.join([part for part, part_presence in zip(schema.signal_parts, schemas_variants[schema][index])
                              if part_presence]))

    @staticmethod
    def _get_schema_variant(schema: Schema, parts_list: list[str]) -> list[bool]:
        schema_variant: list[bool] = []
        for signal_part in schema.signal_parts:
            schema_variant.append(signal_part in parts_list)
        return schema_variant

    @staticmethod
    def run(options: FindSchemasOptions) -> None:
        """
        Запуск скрипта
        :param options: Настройки для скрипта
        :return: None
        """
        logging.info('Запуск скрипта...')
        with Connection.connect_to_mdb(options.database_path) as access:
            find_class: FindSchemas = FindSchemas(options=options,
                                                  access=access)
            schema_variants: dict[Schema, list[list[bool]]] = find_class.find_schemas_variants()
            find_class._print_schemas_variants(schema_variants)
        logging.info('Выпонение завершено.')
