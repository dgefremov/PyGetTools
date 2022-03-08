import logging
from dataclasses import dataclass

from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TemplateVariant:
    """
    Класс хранения данных по вариантам схемы
    """
    name: str
    signal_parts: dict[str, tuple[str, str, str | None]]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class VirtualTemplate:
    """
    Класс хранения данных по шаблону для виртаульных схем
    """
    name: str
    has_channel: bool
    commands_parts_list: dict[str, dict[str, str]]
    variants: list[TemplateVariant]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FillRefOptions:
    """
    Класс для хранения настроек
    """
    sim_table_name: str
    ref_table_name: str
    virtual_schemas_table_name: str
    virtual_templates: list[VirtualTemplate]
    sign_table_name: str
    vs_sign_table_name: str
    wired_template_variants: list[TemplateVariant]


class FillRef:
    """
    Основной класс расстановки ссылок
    """
    _options: FillRefOptions
    _access: Connection

    def __init__(self, options: FillRefOptions, access: Connection):
        self._options = options
        self._access = access

    def _get_part_list(self, kks: str, kksp: str, cabinet: str, kks_shemas: list[str]) -> dict[str, str]:
        """
        Функция получения списка part для использования их в поиске схемы управления. Поиск осуществляется сначала
        по ККС, потом по KKSp.
        :param kks: ККС, для которого осуществляется поиск Part
        :param kksp: KKSp для которого осуществляется поиск Part
        :param cabinet: Имя шкафа для сужения поиска
        :param kks_shemas: Список ККС для схем управления. Part с такими ККС игнорируются (для исключения пересечений
        при наличии в пределах KKSp двух схем управления
        :return: Список PART с их KKS
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

        return parts_dict

    @staticmethod
    def _get_template_variant(template: VirtualTemplate, parts: dict[str, str], kks: str) -> TemplateVariant:
        """
        Фунция поиска варианты схемы
        :param template: Шаблон, для которого ищутся варианты схемы
        :param parts: Список PART для текущего ККС и KKSp
        :param kks: ККС для даннной схемы управления
        :return: Вариант схемы
        """
        for template_variant in sorted(template.variants, key=lambda item: len(item.signal_parts.keys()), reverse=True):
            parts_in_template: list[str] = list(template_variant.signal_parts.keys())
            if all(item in parts.keys() for item in parts_in_template):
                return template_variant
        logging.error(f'Не найдена схема {template.name} для KKS:{kks}')
        raise Exception('TemplateVariantNotFound')

    def _update_ref(self, ref: str, unrel_ref: str | None, kks: str, part: str) -> None:
        """
        Функция добавление записи в таблицу REF с учетом проверки существования записи
        :param ref: Ссылка
        :param unrel_ref: Ссылка сигнала недостоверности
        :param kks: ККС источника сигнала
        :param part: PART источника сигнала
        :return: None
        """
        exist_data: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.ref_table_name,
                                                                      fields=['REF', 'UNREL_REF'],
                                                                      key_names=['KKS', 'PART'],
                                                                      key_values=[kks, part])
        if len(exist_data) == 0:
            if unrel_ref is None:
                unrel_ref = ''
            self._access.insert_row(table_name=self._options.ref_table_name,
                                    column_names=['KKS', 'PART', 'REF', 'UNREL_REF'],
                                    values=[kks, part, ref, unrel_ref])

        elif len(exist_data) == 1:
            ref = '{0};{1}'.format(exist_data[0]['REF'], unrel_ref)
            if unrel_ref is None:
                unrel_ref = exist_data[0]['UNREL_REF']
            else:
                unrel_ref = '{0};{1}'.format(exist_data[0]['UNREL_REF'], unrel_ref)
            self._access.update_field(table_name=self._options.ref_table_name,
                                      fields=['REF', 'UNREL_REF'],
                                      values=[ref, unrel_ref],
                                      key_names=['KKS', 'PART'],
                                      key_values=[kks, part])
        if len(exist_data) > 1:
            logging.error('Неверный результат запроса')
            raise Exception('TooManyValues')

    def _fill_wired_ref(self) -> None:
        """
        Функция заполнения ссылок для проводных схем управления
        :return: None
        """
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                  fields=['KKS', 'PART', 'KKSp', 'SCHEMA'],
                                                                  key_names=['OBJECT_TYP'],
                                                                  key_values=['SW'])
        step: float = 100/3/len(values)
        for value in values:
            ProgressBar.update_progress_with_step(step)
            sw_kks: str = value['KKS']
            sw_part: str = value['PART']
            sw_kksp: str = value['KKSp']
            sw_schema: str = value['SCHEMA']
            wired_template_variant: TemplateVariant = next(
                (variant for variant in self._options.wired_template_variants
                 if variant.name.casefold() == sw_schema.casefold()), None)
            if wired_template_variant is None:
                logging.error('Не найдена схема для SW сигнала')
                raise Exception('SWTemplateNotFound')

            signals: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                       fields=['KKS', 'PART'],
                                                                       key_names=['KKSp'],
                                                                       key_values=[sw_kksp])
            for signal in signals:
                signal_part = signal['PART']
                signal_kks = signal['KKS']
                found_signals: int = 0
                if signal_part in wired_template_variant.signal_parts.keys():
                    found_signals += 1
                    page: str = wired_template_variant.signal_parts[signal_part][0]
                    cell: str = wired_template_variant.signal_parts[signal_part][1]
                    ref: str = f'{sw_kks}_{sw_part}\\{page}\\{cell}'
                    self._update_ref(ref, None, signal_kks, signal_part)
            self._access.commit()

    def _fill_sign_ref(self) -> None:
        """
        Функция копирования данных (ссылок и схем управления) для диагностических сигналов
        :return: None
        """
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sign_table_name,
                                                                  fields=['KKS', 'PART', 'REF'])
        step: float = 100/3/len(values)
        for value in values:
            ProgressBar.update_progress_with_step(step)
            kks: str = value['KKS']
            part: str = value['PART']
            ref: str = value['REF']
            if ref is None or ref == '':
                continue
            self._update_ref(kks=kks,
                             part=part,
                             ref=ref,
                             unrel_ref=None)
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.vs_sign_table_name,
                                                                  fields=['KKS', 'CABINET', 'SCHEMA',
                                                                          'CHANNEL', 'PART', 'DESCR',
                                                                          'REF'])
        for value in values:
            vs_kks: str = value['KKS']
            cabinet: str = value['CABINET']
            vs_schema: str = value['SCHEMA']
            vs_channel: int = int(value['CHANNEL'])
            vs_part: str = value['PART']
            descr: str = value['DESCR']
            vs_ref: str = value['REF']
            self._update_ref(kks=vs_kks,
                             unrel_ref=None,
                             part=vs_part,
                             ref=vs_ref)

            self._access.insert_row(table_name=self._options.virtual_schemas_table_name,
                                    column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR'],
                                    values=[vs_kks, cabinet, vs_schema, vs_channel, vs_part, descr])
        self._access.commit()

    def _fill_virtual_ref(self) -> None:
        """
        Функция заполнения ссылок и схем управления для виртуальных схем
        :return: None
        """
        channel_container: dict[str, int] = {}
        step: float = 100/3/len(self._options.virtual_templates)

        for template in self._options.virtual_templates:
            ProgressBar.update_progress_with_step(step)
            for schema_part in template.commands_parts_list:
                command_list: dict[str, str] = template.commands_parts_list[schema_part]
                values_list: list[dict[str, str]] = self._access.retrive_data_with_having(
                    table_name=self._options.sim_table_name,
                    fields=['KKS', 'CABINET', 'KKSp'],
                    key_column='PART',
                    key_values=list(command_list.keys()))

                kks_schemas_list: list[str] = [value['KKS'] for value in values_list]
                for value in values_list:
                    kks: str = value['KKS']
                    kksp: str = value['KKSp']
                    cabinet: str = value['CABINET']

                    current_channel: int = 0
                    if template.has_channel:
                        if cabinet in channel_container:
                            channel_container[cabinet] = channel_container[cabinet] + 1
                            current_channel = channel_container[cabinet]
                        else:
                            channel_container[cabinet] = 1
                            current_channel = 1

                    part_dict: dict[str, str] = self._get_part_list(kks=kks, kksp=kksp, cabinet=cabinet,
                                                                    kks_shemas=kks_schemas_list)
                    variant: TemplateVariant = self._get_template_variant(template=template, parts=part_dict,
                                                                          kks=kks)
                    self._fill_ref_for_virtaul_template_variant(variant=variant,
                                                                part_dict=part_dict,
                                                                template_kks=kks,
                                                                template_part=schema_part)
                    self._access.insert_row(table_name=self._options.virtual_schemas_table_name,
                                            column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART'],
                                            values=[kks, cabinet, variant.name, current_channel, schema_part])
                    command_ref: str = ';'.join([f'{command_list[command_part]}:{kks}_{command_part}'
                                                 for command_part in command_list])
                    self._update_ref(ref=command_ref,
                                     unrel_ref=None,
                                     kks=kks,
                                     part=schema_part)

        self._access.commit()

    def _fill_ref(self) -> None:
        """
        Функция запуска заполнения ссылок и схем управления
        :return: None
        """
        logging.info(f'Очистка таблицы {self._options.ref_table_name}...')
        self._access.clear_table(table_name=self._options.ref_table_name, drop_index=False)
        logging.info('Очистка завершена.')
        logging.info(f'Очистка таблицы {self._options.virtual_schemas_table_name}...')
        self._access.clear_table(table_name=self._options.virtual_schemas_table_name, drop_index=False)
        logging.info('Очистка завершена.')
        logging.info('Расстановка ссылок...')
        ProgressBar.config(max_value=100, step=1, prefix='Расстановка ссылок', suffix='Завершено', length=50)
        self._fill_virtual_ref()
        self._fill_wired_ref()
        self._fill_sign_ref()

    def _fill_ref_for_virtaul_template_variant(self, variant: TemplateVariant, part_dict: dict[str, str],
                                               template_kks: str, template_part: str) -> None:
        """
        Функция заполнения ссылок для варианта схемы
        :param variant: Вариант схемы
        :param part_dict: Список Part (с ККС) для данной схемы
        :param template_kks: ККС схемы
        :param template_part: PART схемы
        :return: None
        """
        for part in variant.signal_parts:
            kks: str = part_dict[part]
            page: str = variant.signal_parts[part][0]
            cell: str = variant.signal_parts[part][1]
            unrel_cell: str | None = variant.signal_parts[part][2]
            ref: str = f'{template_kks}_{template_part}\\{page}\\{cell}'
            unrel_ref: str | None = None
            if variant.signal_parts[part][2] is not None:
                unrel_ref: str = f'{template_kks}_{template_part}\\{page}\\{unrel_cell}'
            self._update_ref(ref=ref,
                             unrel_ref=unrel_ref,
                             kks=kks,
                             part=part)

    @staticmethod
    def run(options: FillRefOptions, base_path: str) -> None:
        logging.info('Запуск скрипта "Расстановка ссылок"...')
        with Connection.connect_to_mdb(base_path=base_path) as access:
            find_class: FillRef = FillRef(options=options,
                                          access=access)
            find_class._fill_ref()
        logging.info('Выпонение скрипта "Расстановка ссылок" завершено.')
        logging.info('')
