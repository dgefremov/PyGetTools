import logging
from dataclasses import dataclass

from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TemplateVariant:
    name: str
    signal_parts: dict[str, tuple[str, str, str | None]]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class VirtualTemplate:
    name: str
    part: str
    has_channel: bool
    commands_parts_list: dict[str, str]
    variants: list[TemplateVariant]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FillRefOptions:
    path: str
    sim_table_name: str
    ref_table_name: str
    virtual_schemas_table_name: str
    virtual_templates: list[VirtualTemplate]
    sign_table_name: str
    vs_sign_table_name: str
    wired_template_variants: list[TemplateVariant]


class FillRef:
    _options: FillRefOptions
    _access: Connection

    def __init__(self, options: FillRefOptions, access: Connection):
        self._options = options
        self._access = access

    def _get_part_list(self, kks: str, kksp: str, cabinet: str, kks_shemas: list[str]) -> dict[str, str]:
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
        for template_variant in sorted(template.variants, key=lambda item: len(item.signal_parts.keys()), reverse=True):
            parts_in_template: list[str] = list(template_variant.signal_parts.keys())
            if all(item in parts.keys() for item in parts_in_template):
                return template_variant
        logging.error(f'Не найдена схема {template.name} для KKS:{kks}')
        raise Exception('TemplateVariantNotFound')

    def _update_ref(self, ref: str, unrel_ref: str | None, kks: str, part: str):
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

    def _fill_wired_ref(self):
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                  fields=['KKS', 'PART', 'KKSp', 'SCHEMA'],
                                                                  key_names=['OBJECT_TYP'],
                                                                  key_values=['SW'])
        for value in values:
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

    def _fill_sign_ref(self):
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sign_table_name,
                                                                  fields=['KKS', 'PART', 'REF'])
        for value in values:
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
                                                                  fields=['VS_KKS', 'CABINET', 'VS_SCHEMA',
                                                                          'VS_CHANNEL', 'VS_PART', 'DESCR',
                                                                          'REF'])
        for value in values:
            vs_kks: str = value['VS_KKS']
            cabinet: str = value['CABINET']
            vs_schema: str = value['VS_SCHEMA']
            vs_channel: int = int(value['VS_CHANNEL'])
            vs_part: str = value['VS_PART']
            descr: str = value['DESCR']
            vs_ref: str = value['REF']
            self._update_ref(kks=vs_kks,
                             unrel_ref=None,
                             part=vs_part,
                             ref=vs_ref)

            self._access.insert_row(table_name=self._options.virtual_schemas_table_name,
                                    column_names=['VS_KKS', 'CABINET', 'VS_SCHEMA', 'VS_CHANNEL', 'VS_PART', 'DESCR'],
                                    values=[vs_kks, cabinet, vs_schema, vs_channel, vs_part, descr])
        self._access.commit()

    def _fill_virtual_ref(self):
        channel_container: dict[str, int] = {}
        for template in self._options.virtual_templates:
            values_list: list[dict[str, str]] = self._access.retrive_data_with_having(
                table_name=self._options.sim_table_name,
                fields=['KKS', 'CABINET', 'KKSp'],
                key_column='PART',
                key_values=list(template.commands_parts_list.keys()))

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
                self._fill_ref_for_variant(template=template,
                                           variant=variant,
                                           part_dict=part_dict,
                                           template_kks=kks,
                                           template_part=template.part)
                self._access.insert_row(table_name=self._options.virtual_schemas_table_name,
                                        column_names=['VS_KKS', 'CABINET', 'VS_SCHEMA', 'VS_CHANNEL', 'VS_PART'],
                                        values=[kks, cabinet, variant.name, current_channel, template.part])
            self._access.commit()

    def _fill_ref(self):
        logging.info(f'Очистка таблицы {self._options.ref_table_name}...')
        self._access.clear_table(table_name=self._options.ref_table_name, drop_index=False)
        logging.info('Очистка завершена.')
        logging.info(f'Очистка таблицы {self._options.virtual_schemas_table_name}...')
        self._access.clear_table(table_name=self._options.virtual_schemas_table_name, drop_index=False)
        logging.info('Очистка завершена.')
        logging.info('Расстановка ссылок...')
        self._fill_virtual_ref()
        self._fill_wired_ref()
        self._fill_sign_ref()

    def _fill_ref_for_variant(self, template: VirtualTemplate, variant: TemplateVariant, part_dict: dict[str, str],
                              template_kks: str, template_part: str):
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
            command_ref: str = ';'.join([f'{template.commands_parts_list[command_part]}:{template_kks}_{command_part}'
                                         for command_part in template.commands_parts_list])
            self._update_ref(ref=command_ref,
                             unrel_ref=None,
                             kks=template_kks,
                             part=template_part)

    @staticmethod
    def run(options: FillRefOptions) -> None:
        """
        Запуск скрипта
        :param options: Настройки для скрипта
        :return: None
        """
        logging.info('Запуск скрипта...')
        with Connection.connect_to_mdb(options.path) as access:
            find_class: FillRef = FillRef(options=options,
                                          access=access)
            find_class._fill_ref()
        logging.info('Выпонение завершено.')