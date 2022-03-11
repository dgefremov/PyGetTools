import logging
from dataclasses import dataclass, field

from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class SchemaVariant:
    parts: list[bool]
    kks: list[str]


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class Schema:
    """
    Класс хранения описания схемы
    """
    name: str
    command_parts: list[str] = field(compare=False)
    signal_parts: list[str] = field(compare=False)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FindSchemasOptions:
    """
    Класс хранения настроек
    """
    sim_table_name: str
    schemas: list[Schema]


class FindSchemas:
    """
    Основной класс для поиска вариантов схем управления
    """
    _options: FindSchemasOptions
    _access: Connection

    def __init__(self, options: FindSchemasOptions, access: Connection):
        self._options = options
        self._access = access

    def find_schemas_variants(self) -> dict[Schema, list[SchemaVariant]]:
        """
        Функция поиска схем вариантов управления
        :return: Список схем с набором используемых сигналов
        """
        schema_variants: dict[Schema, list[SchemaVariant]] = {}
        for schema in self._options.schemas:
            variants: list[SchemaVariant] = []
            values_list: list[dict[str, str]] = self._access.retrive_data_with_having(
                table_name=self._options.sim_table_name,
                fields=['KKS', 'CABINET', 'KKSp'],
                key_column='PART',
                key_values=schema.command_parts)
            kks_schemas_list: list[str] = [value['KKS'] for value in values_list]
            for value in values_list:
                parts_list: list[str] = self._get_part_list(kks=value['KKS'],
                                                            kksp=value['KKSp'],
                                                            cabinet=value['CABINET'],
                                                            kks_shemas=kks_schemas_list)
                new_variant_parts: list[bool] = self._get_schema_variant(schema=schema, parts_list=parts_list)
                schema_variant: SchemaVariant = self._get_variant(variants=variants, new_variant=new_variant_parts)
                if schema_variant is None:
                    variants.append(SchemaVariant(parts=new_variant_parts, kks=[value['KKS']]))
                else:
                    schema_variant.kks.append(value['KKS'])
            schema_variants[schema] = variants
        return schema_variants

    @staticmethod
    def _get_variant(variants: list[SchemaVariant], new_variant: list[bool]) -> SchemaVariant | None:
        """
        Сравнение двух наборов сигналов
        :param variants:
        :param new_variant:
        :return:
        """
        for variant in variants:
            if next((False for item1, item2 in zip(variant.parts, new_variant) if item1 != item2), True):
                return variant
        return None

    def _get_part_list(self, kks: str, kksp: str, cabinet: str, kks_shemas: list[str]) -> list[str]:
        """
        Функция поиска PART для данного ККС и KKSp
        :param kks: ККС сигналов управления
        :param kksp: KKSp сигналов управления
        :param cabinet: Имя шкафа для сужения поиска
        :return: Список Part
        """
        parts_dict: dict[str] = {}
        values_from_kks: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                           fields=['PART'],
                                                                           key_names=['KKS', 'CABINET'],
                                                                           key_values=[kks, cabinet])
        for value in values_from_kks:
            if value['PART'] not in values_from_kks:
                parts_dict[value['PART']] = kks

        values_from_kksp: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                            fields=['PART', 'KKS'],
                                                                            key_names=['KKSp', 'CABINET'],
                                                                            key_values=[kksp, cabinet])
        for value in values_from_kksp:
            # Если ККС относится к схеме, которая есть в списке схем - пропускаем
            if value['KKS'] in kks_shemas:
                continue

            if value['PART'] not in values_from_kksp:
                parts_dict[value['PART']] = value['KKS']
            else:
                if value['KKS'].casefold() == kks:
                    parts_dict[value['PART']] = value['KKS']

        return list(parts_dict.keys())

    @staticmethod
    def _print_schemas_variants(schemas_variants: dict[Schema, list[SchemaVariant]]) -> None:
        """
        Вывод на экран списков вариантов схем
        :param schemas_variants:
        :return: None
        """
        for schema in schemas_variants:
            logging.info(f'Схема {schema.name}')
            for index in range(len(schemas_variants[schema])):
                logging.info(f'Вариация {index + 1}')
                logging.info(
                    ','.join([part for part, part_presence in
                              zip(schema.signal_parts, schemas_variants[schema][index].parts)
                              if part_presence]))
                logging.info('KKS вариации:')
                logging.info(
                    ','.join(schemas_variants[schema][index].kks)
                )

    @staticmethod
    def _get_schema_variant(schema: Schema, parts_list: list[str]) -> list[bool]:
        """
        Функция поиска вариантов схемы
        :param schema: Схема, для которой ищутся варианты
        :param parts_list: Список Part, на основе которых определяется вариант схемы
        :return: Список найденных сигналов для данной схемы
        """
        schema_variant: list[bool] = []
        for signal_part in schema.signal_parts:
            schema_variant.append(signal_part in parts_list)
        return schema_variant

    @staticmethod
    def run(options: FindSchemasOptions, base_path: str) -> None:
        logging.info('Запуск скрипта "Поиск схем"...')
        with Connection.connect_to_mdb(base_path=base_path) as access:
            find_class: FindSchemas = FindSchemas(options=options,
                                                  access=access)
            schema_variants: dict[Schema, list[SchemaVariant]] = find_class.find_schemas_variants()
            find_class._print_schemas_variants(schema_variants)
        logging.info('Выпонение скрипта "Поиск схем" завершено.')
