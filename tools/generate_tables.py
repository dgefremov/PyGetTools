import logging
import re
from dataclasses import dataclass, field, fields

from tools.utils.progress_utils import ProgressBar
from tools.utils.sql_utils import Connection, BaseType


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class SignalModification:
    """
    Класс хранения шаблонов для нетиповых сигналов
    """
    signal_kks: str
    signal_part: str
    new_template: str | None = None
    new_name_rus: str | None = None
    new_full_name_rus: str | None = None
    new_name_eng: str | None = None
    new_full_name_eng: str | None = None
    new_part: str | None = None
    new_kks: str | None = None


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class SWTemplateVariant:
    schema_part: str
    schema: list[str]
    parts: list[str]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class SWTemplate:
    """
    Класс для хранения шаблонов для проводных сигналов управления
    """
    connection: str
    signals: set[str]
    variants: list[SWTemplateVariant]


@dataclass(init=False, repr=False, eq=False, order=False, frozen=False)
class Signal:
    """
    Класс хранения строки с сигналом
    """
    kks: str = field(metadata={'column_name': 'KKS'})
    part: str = field(metadata={'column_name': 'PART'})
    module: str = field(metadata={'column_name': 'MODULE'})
    slot_mp: int = field(metadata={'column_name': 'SLOT_MP'})
    location_mp: str = field(metadata={'column_name': 'LOCATION_MP'})
    kksp: str = field(metadata={'column_name': 'KKSp'})
    object_typ: str = field(metadata={'column_name': 'OBJECT_TYP'})
    rednd_intf: str | None = field(default=None, metadata={'column_name': 'REDND_INTF'})
    name_rus: str | None = field(default=None, metadata={'column_name': 'NAME_RUS'})
    full_name_rus: str | None = field(default=None, metadata={'column_name': 'FULL_NAME_RUS'})
    name_eng: str | None = field(default=None, metadata={'column_name': 'NAME_ENG'})
    full_name_eng: str | None = field(default=None, metadata={'column_name': 'FULL_NAME_ENG'})
    min: float | None = field(default=None, metadata={'column_name': 'MIN'})
    max: float | None = field(default=None, metadata={'column_name': 'MAX'})
    units_rus: str | None = field(default=None, metadata={'column_name': 'UNITS_RUS'})
    units_eng: str | None = field(default=None, metadata={'column_name': 'UNITS_ENG'})
    in_level: str | None = field(default=None, metadata={'column_name': 'IN_LEVEL'})
    cabinet: str | None = field(default=None, metadata={'column_name': 'CABINET'})
    channel: int | None = field(default=None, metadata={'column_name': 'CHANNEL'})
    connection: str = field(default=None, metadata={'column_name': 'CONNECTION'})
    sensr_typ: str = field(default=None, metadata={'column_name': 'SENSR_TYPE'})
    cat_nam: str = field(default=None, metadata={'column_name': 'CatNam'})
    dname: str | None = field(default=None, metadata={'column_name': 'DNAME'})
    template: str | None = field(default=None, metadata={'column_name': 'SCHEMA'})

    @staticmethod
    def create_from_row(value: dict[str, str], base_type: BaseType) -> 'Signal':
        signal: Signal = Signal()
        for dataclass_field in fields(signal):
            if 'column_name' in dataclass_field.metadata:
                if base_type == BaseType.ACCESS:
                    column_name: str = dataclass_field.metadata['column_name']
                elif base_type == BaseType.POSTGRES:
                    match dataclass_field.name:
                        case 'module':
                            column_name = 'module_name'
                        case 'template':
                            column_name = 'schema_name'
                        case 'connection':
                            column_name = 'conn'
                        case _:
                            column_name: str = str(dataclass_field.metadata['column_name']).lower()
                else:
                    raise Exception("Неподдерживаемый тип DBEngine")
                if column_name in value:
                    if value[column_name] is None:
                        setattr(signal, dataclass_field.name, None)
                    else:
                        field_type = dataclass_field.type
                        if field_type == str or field_type == str | None:
                            setattr(signal, dataclass_field.name, value[column_name])
                        elif field_type == int or field_type == int | None:
                            setattr(signal, dataclass_field.name, int(value[column_name]))
                        elif field_type == float or field_type == float | None:
                            setattr(signal, dataclass_field.name, float(value[column_name]))
                        else:
                            logging.error(f'Недопустимый тип для поля {dataclass_field.name}')
                            raise TypeError('Недопустимый тип')

        return signal

    def clone(self) -> 'Signal':
        new_signal: Signal = Signal()
        new_signal.kks = self.kks
        new_signal.object_typ = self.object_typ
        new_signal.part = self.part
        new_signal.module = self.module
        new_signal.rednd_intf = self.rednd_intf
        new_signal.full_name_rus = self.full_name_rus
        new_signal.name_rus = self.name_rus
        new_signal.full_name_eng = self.full_name_eng
        new_signal.name_eng = self.name_eng
        new_signal.min = self.min
        new_signal.max = self.max
        new_signal.units_rus = self.units_rus
        new_signal.units_eng = self.units_eng
        new_signal.in_level = self.in_level
        new_signal.cabinet = self.cabinet
        new_signal.slot_mp = self.slot_mp
        new_signal.channel = self.channel
        new_signal.connection = self.connection
        new_signal.sensr_typ = self.sensr_typ
        new_signal.cat_nam = self.cat_nam
        new_signal.location_mp = self.location_mp
        new_signal.dname = self.dname
        new_signal.kksp = self.kksp
        new_signal.template = self.template
        return new_signal


@dataclass(init=False, repr=False, eq=False, order=False, frozen=False)
class DigitalSignal:
    """
    Класс хранения строки с сигналом
    """
    kks: str = field(metadata={'column_name': 'KKS'})
    part: str = field(metadata={'column_name': 'PART'})
    module: str = field(metadata={'column_name': 'MODULE'})
    slot_mp: int = field(metadata={'column_name': 'SLOT_MP'})
    location_mp: str = field(metadata={'column_name': 'LOCATION_MP'})
    kksp: str = field(metadata={'column_name': 'KKSp'})
    rednd_intf: str | None = field(default=None, metadata={'column_name': 'REDND_INTF'})
    name_rus: str | None = field(default=None, metadata={'column_name': 'NAME_RUS'})
    full_name_rus: str | None = field(default=None, metadata={'column_name': 'FULL_NAME_RUS'})
    name_eng: str | None = field(default=None, metadata={'column_name': 'NAME_ENG'})
    full_name_eng: str | None = field(default=None, metadata={'column_name': 'FULL_NAME_ENG'})
    min: float | None = field(default=None, metadata={'column_name': 'MIN'})
    max: float | None = field(default=None, metadata={'column_name': 'MAX'})
    units_rus: str | None = field(default=None, metadata={'column_name': 'UNITS_RUS'})
    units_eng: str | None = field(default=None, metadata={'column_name': 'UNITS_ENG'})
    cabinet: str | None = field(default=None, metadata={'column_name': 'CABINET'})
    sensr_typ: str = field(default=None, metadata={'column_name': 'SENSR_TYPE'})
    dname: str | None = field(default=None, metadata={'column_name': 'DNAME'})
    ip: str | None = field(default=None, metadata={'column_name': 'IP'})
    area: str | None = field(default=None, metadata={'column_name': 'AREA'})
    cat_nam: str = field(default=None, metadata={'column_name': 'CatNam'})
    fake: bool | None = field(default=None, metadata={'column_name': 'FAKE'})

    @staticmethod
    def create_from_signal(signal: Signal) -> 'DigitalSignal':
        diginal_signal: DigitalSignal = DigitalSignal()
        diginal_signal.kks = signal.kks
        diginal_signal.part = signal.part
        diginal_signal.module = signal.module
        diginal_signal.slot_mp = signal.slot_mp
        diginal_signal.location_mp = signal.location_mp
        diginal_signal.kksp = signal.kksp
        diginal_signal.rednd_intf = signal.rednd_intf
        diginal_signal.name_rus = signal.name_rus
        diginal_signal.full_name_rus = signal.full_name_rus
        diginal_signal.name_eng = signal.name_eng
        diginal_signal.full_name_eng = signal.full_name_eng
        diginal_signal.min = signal.min
        diginal_signal.max = signal.max
        diginal_signal.units_rus = signal.units_rus
        diginal_signal.units_eng = signal.units_eng
        diginal_signal.cabinet = signal.cabinet
        diginal_signal.sensr_typ = signal.sensr_typ
        diginal_signal.dname = signal.dname
        diginal_signal.cat_nam = signal.cat_nam
        return diginal_signal


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DoublePointSignal:
    single_part: str | None
    on_part: str
    off_part: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class GenerateTableOptions:
    """
    Класс настроек
    """
    network_data_table_name: str
    controller_data_table_name: str
    aep_table_name: str
    sim_table_name: str
    iec_table_name: str
    ied_table_name: str
    ref_table_name: str
    sign_table_name: str
    ps_table_name: str
    fake_signals_table_name: str
    skip_duplicate_signals: list[tuple[str, str]]
    copy_ds_to_sim_table: bool
    dps_signals: list[DoublePointSignal]
    sw_templates: list[SWTemplate]
    signal_modifications: None | list[SignalModification] = None


class GenerateTables:
    """
    Основной класс генерации таблиц
    """
    _options: 'GenerateTableOptions'
    _connection: Connection
    _columns_list: dict[str, list[str]]

    def __init__(self, options: GenerateTableOptions, connection: Connection):
        self._options = options
        self._connection = connection
        self._columns_list = {}

    def _get_column_set(self, signal_type: dataclass) -> set[str]:
        columns: set[str] = set()
        for dataclass_field in fields(signal_type):
            if self._connection.get_base_type() == BaseType.ACCESS:
                if 'column_name' in dataclass_field.metadata:
                    columns.add(dataclass_field.metadata['column_name'])
            elif self._connection.get_base_type() == BaseType.POSTGRES:
                match dataclass_field.name:
                    case 'template':
                        columns.add('schema_name')
                    case 'connection':
                        columns.add('conn')
                    case 'module':
                        columns.add('module_name')
                    case _:
                        columns.add(str(dataclass_field.metadata['column_name']).lower())
            else:
                raise Exception("Неподдерживаемый тип DBEngine")
        return columns

    def _get_columns_and_values(self, signal: dataclass, columns_from_table: list[str]) -> tuple[list[str], list[str]]:
        columns: list[str] = []
        values: list[str] = []
        for dataclass_field in fields(signal):
            if 'column_name' in dataclass_field.metadata:
                column_name: str
                if self._connection.get_base_type() == BaseType.ACCESS:
                    column_name = dataclass_field.metadata['column_name']
                elif self._connection.get_base_type() == BaseType.POSTGRES:
                    match dataclass_field.name:
                        case 'template':
                            column_name = 'schema_name'
                        case 'module':
                            column_name = 'module_name'
                        case 'connection':
                            column_name = 'conn'
                        case _:
                            column_name = str(dataclass_field.metadata['column_name']).lower()
                else:
                    raise Exception("Неподдерживаемый тип DBEngine")
                if column_name in columns_from_table:
                    columns.append(dataclass_field.metadata['column_name'])
                    values.append(getattr(signal, dataclass_field.name))
        return columns, values

    def _get_kksp_list(self) -> list[str]:
        """
        Функция получения списка KKSp
        :return: Список KKSp
        """
        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.aep_table_name,
                                                                      fields=['KKSp'],
                                                                      key_names=None,
                                                                      key_values=None,
                                                                      uniq_values=True,
                                                                      sort_by=None,
                                                                      key_operator=None)
        kksp_list: list[str] = []
        for value in values:
            kksp_list.append(value[self.get_column_name(self._connection.modify_column_name('KKSp'))])
        return kksp_list

    def _generate_table_for_kksp(self, kksp: str) -> None:
        """
        Функция запуска генерации таблиц для одного KKSp
        :param kksp: KKSp для генерации
        :return: None
        """

        values: list[dict[str, str]] = \
            self._connection.retrieve_data(table_name=self._options.aep_table_name,
                                           fields=self._columns_list[self._options.aep_table_name],
                                           key_names=['KKSp'],
                                           key_values=[kksp])
        sw_containers: dict[SWTemplate, dict[str, list[Signal]]] = {}
        for sw_template in self._options.sw_templates:
            sw_containers[sw_template] = {}
        for value in values:
            ProgressBar.update_progress()
            signal: Signal = Signal.create_from_row(value=value,
                                                    base_type=self._connection.get_base_type())

            if signal.module in ['1623', '1631', '1661', '1662', '1671', '1673']:
                self._process_wired_signal(signal=signal, sw_containers=sw_containers)
            elif signal.module == '1691':
                self._process_digital_signal(signal=signal)
        self._flush_sw_container(sw_containers=sw_containers)
        self._connection.commit()

    def _process_wired_signal(self, signal: Signal, sw_containers: dict[SWTemplate, dict[str, list[Signal]]]) -> None:
        """
        Обработка проводного сигнала
        :param signal: Сигнал (строка таблицы)
        :param sw_containers: Контейнер для хранения групп SW сигналов
        :return: None
        """
        if (signal.module == '1623' or signal.module == '1673') and signal.object_typ.casefold() == 'SW'.casefold():
            self._process_sw_signal(sw_containers=sw_containers,
                                    signal=signal)
        else:
            self._add_signal_to_sim_table(signal=signal)

    def _get_part_pair(self, part: str) -> str:
        """
        Получение ответный part для раздвоенных сигналов
        :param part: Part, для которой ищется пара
        :return: Ответный part для развдоенного сигнала
        """
        found_signal: DoublePointSignal = next((dps_signal for dps_signal in self._options.dps_signals if
                                                dps_signal.on_part.casefold() == part.casefold()), None)
        if found_signal is not None:
            return found_signal.off_part
        else:
            return next(dps_signal.on_part for dps_signal in self._options.dps_signals
                        if dps_signal.off_part.casefold() == part.casefold())

    def _process_digital_signal(self, signal: Signal) -> None:
        """
        Обработка цифрового сигнала
        :param signal: Сигнал (строка из базы)
        :return: None
        """
        if signal.part in [dps_signal.single_part for dps_signal in self._options.dps_signals
                           if dps_signal.single_part is not None] and \
                not any(signal.kks.upper().startswith(item_kks.upper()) and signal.part.upper() == item_part.upper()
                        for (item_kks, item_part) in self._options.skip_duplicate_signals):
            self._duplicate_signal(signal=signal)
        else:
            self._add_signal_to_iec_table(signal=signal)
            if self._options.copy_ds_to_sim_table:
                self._add_signal_to_sim_table(signal=signal)

    def _duplicate_signal(self, signal: Signal) -> None:
        """
        Раздвоение сигнала
        :param signal: Исходный сигнал
        :return: None
        """
        part_num_string: str = signal.part[2:]
        part_num: int = int(part_num_string)
        new_signal_1: Signal = signal.clone()
        new_signal_1.part = signal.part[:2] + str(part_num + 1).rjust(2, '0')
        new_signal_2: Signal = signal.clone()
        new_signal_2.part = signal.part[:2] + str(part_num + 2).rjust(2, '0')
        self._add_signal_to_iec_table(signal=new_signal_1)
        self._add_signal_to_iec_table(signal=new_signal_2)
        if self._options.copy_ds_to_sim_table:
            self._add_signal_to_sim_table(signal=new_signal_1)
            self._add_signal_to_sim_table(signal=new_signal_2)

    @staticmethod
    def _get_common_prefix(strings: list[str]) -> str:
        """
        Класс выделения общей части для группы строк
        :param strings: Группа строк
        :return: Общая часть группы строк
        """
        min_length: int = len(min(strings, key=len))
        stop_flag: bool = False
        common_index: int = 0
        for char_index in range(min_length):
            for string_index in range(1, len(strings)):
                if strings[string_index][char_index].upper() != strings[0][char_index].upper():
                    stop_flag = True
                    break
            if stop_flag:
                common_index = char_index
                break
        if not stop_flag:
            common_index = min_length
        return strings[0][:common_index].rstrip()

    def _flush_sw_container(self, sw_containers: dict[SWTemplate, dict[str, list[Signal]]]):
        for signal_dict in sw_containers.values():
            for signal_list in signal_dict.values():
                for signal in signal_list:
                    self._add_signal_to_sim_table(signal)

    def _process_sw_signal(self, sw_containers: dict[SWTemplate, dict[str, list[Signal]]], signal: Signal) -> None:
        """
        Обработка SW сигналов (объединения группы сигналов в один)
        :param sw_containers: Хранилище для SW сигналов
        :param signal: Текущий SW сигнал
        :return: None
        """
        sw_template: SWTemplate = next((template for template in self._options.sw_templates if template.connection ==
                                        signal.connection), None)
        if sw_template is None:
            logging.error('Не найдена схема для проводного сигнала')
            raise Exception('SWConnectionNotFound')

        sw_signals: list[Signal]
        if signal.kksp in sw_containers[sw_template]:
            sw_signals = sw_containers[sw_template][signal.kksp]
        else:
            sw_signals = []
            sw_containers[sw_template][signal.kksp] = sw_signals
        sw_signals.append(signal)
        if len(sw_signals) == len(sw_template.signals):
            parts_in_container: set[str] = {item.part for item in sw_signals}
            parts_set: set[str] = sw_template.signals
            if parts_set == parts_in_container:
                sw_signal: Signal = signal.clone()
                if any([signal.name_rus is None for signal in sw_signals]):
                    sw_signal.name_rus = None
                else:
                    sw_signal.name_rus = self._get_common_prefix(list(map(lambda item: item.name_rus, sw_signals)))

                if any([signal.name_eng is None for signal in sw_signals]):
                    sw_signal.name_eng = None
                else:
                    sw_signal.name_eng = self._get_common_prefix(list(map(lambda item: item.name_eng, sw_signals)))

                if any([signal.full_name_rus is None for signal in sw_signals]):
                    sw_signal.full_name_rus = None
                else:
                    sw_signal.full_name_rus = self._get_common_prefix(list(map(lambda item: item.full_name_rus,
                                                                               sw_signals)))
                if any([signal.full_name_eng is None for signal in sw_signals]):
                    sw_signal.full_name_eng = None
                else:
                    sw_signal.full_name_eng = self._get_common_prefix(list(map(lambda item: item.full_name_eng,
                                                                               sw_signals)))
                sw_signal.template, sw_signal.part = self._get_sw_template(kks=sw_signal.kks,
                                                                           kksp=sw_signal.kksp,
                                                                           cabinet=sw_signal.cabinet,
                                                                           sw_template=sw_template)
                if self._options.signal_modifications is not None:
                    sw_signal = self._modificate_signal(signal=sw_signal)

                self._add_signal_to_sim_table(sw_signal)
                del sw_containers[sw_template]
            else:
                logging.error('Неверный набор сигналов в группе SW')
                raise Exception('SignalGroupError')

    def _get_sw_template(self, kks: str, kksp: str, cabinet: str, sw_template: SWTemplate) -> tuple[str, str]:
        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.aep_table_name,
                                                                      fields=['PART'],
                                                                      key_names=['KKSp', 'CABINET'],
                                                                      key_values=[kksp, cabinet])
        path_list: list[str] = [value[self.get_column_name('PART')] for value in values]
        for sw_template in sorted(sw_template.variants, key=lambda item: len(item.parts), reverse=True):
            if len(sw_template.parts) == 0 or all(part in path_list for part in sw_template.parts):
                values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.ps_table_name,
                                                                              fields=['SCHEMA'],
                                                                              key_names=['KKS', 'PART', 'CABINET'],
                                                                              key_values=[kks, sw_template.schema_part,
                                                                                          cabinet])
                if len(values) != 1:
                    raise Exception('Ошибка получения схемы для SW')
                if values[0][self.get_column_name('SCHEMA')] not in sw_template.schema:
                    raise Exception('Ошибка получения схемы для SW')
                return values[0][self.get_column_name('SCHEMA')], sw_template.schema_part
        logging.error('Не найдена схема подключения для управления')
        raise Exception('SWTemplateNotFound')

    def _modificate_signal(self, signal: Signal) -> Signal:
        signal_modification: SignalModification | None = \
            next((item for item in self._options.signal_modifications
                  if re.search(item.signal_kks, signal.kks) and re.search(item.signal_part, signal.part)), None)
        if signal_modification is not None:
            if signal_modification.new_template is not None:
                signal.template = signal_modification.new_template
            if signal_modification.new_name_rus is not None:
                signal.name_rus = signal_modification.new_name_rus
            if signal_modification.new_full_name_rus is not None:
                signal.full_name_rus = signal_modification.new_full_name_rus
            if signal_modification.new_name_eng is not None:
                signal.name_eng = signal_modification.new_name_eng
            if signal_modification.new_full_name_eng is not None:
                signal.full_name_eng = signal_modification.new_full_name_eng
            if signal_modification.new_part is not None:
                signal.part = signal_modification.new_part
            if signal_modification.new_kks is not None:
                signal.kks = signal_modification.new_kks
        return signal

    def _add_signal_to_sim_table(self, signal: Signal) -> None:
        """
        Добавление сигнала в таблицу СиМ
        :param signal: Сигнал для добавления в таблицу
        :return: None
        """
        if signal.module == '1691':
            signal.template = ''
        else:
            if signal.template is None or signal.template == '':
                signal.template = f'{signal.object_typ}_{signal.module}'

            if self._options.signal_modifications is not None:
                signal = self._modificate_signal(signal=signal)
        channel: int
        if signal.module == '1623' and signal.object_typ != 'SW' and signal.channel < 50:
            signal.channel = signal.channel + 50
        else:
            signal.channel = signal.channel
        columns, values = self._get_columns_and_values(signal=signal,
                                                       columns_from_table=self._columns_list[
                                                           self._options.sim_table_name])
        self._connection.insert_row(table_name=self._options.sim_table_name,
                                    column_names=columns,
                                    values=values)

    def _update_fake_signal_data(self, signal: Signal):
        self._connection.update_field(table_name=self._options.fake_signals_table_name,
                                      fields=['DESCR_RUS', 'DESCR_ENG', 'CABINET', 'KKSP', 'CatNam'],
                                      values=[signal.name_rus, signal.name_eng,
                                              signal.cabinet, signal.kksp, signal.cat_nam],
                                      key_names=['KKS', 'PART'],
                                      key_values=[signal.kks, signal.part])

    def _add_signal_to_iec_table(self, signal: Signal) -> None:
        """
        Добавление сигнала в таблицу МЭК
        :param signal: Сигнал (запись в базе)
        :return: None
        """
        fake: bool = False
        if (self._connection.contains_value(table_name=self._options.fake_signals_table_name,
                                            key_names=['KKS', 'PART'],
                                            key_values=[signal.kks, signal.part])):
            self._update_fake_signal_data(signal=signal)
            fake = True
        digital_signal: DigitalSignal = DigitalSignal.create_from_signal(signal=signal)
        digital_signal.area = self._connection.retrieve_data(
            'TPTS', ['AREA'],
            ['CABINET'],
            [signal.cabinet])[0][self._connection.modify_column_name('AREA')]
        digital_signal.ip = self._connection.retrieve_data(
            self._options.network_data_table_name,
            ['IP'], ['KKSp'],
            [signal.kksp])[0][
            self._connection.modify_column_name('IP')]
        digital_signal.fake = fake
        columns, values = self._get_columns_and_values(signal=digital_signal,
                                                       columns_from_table=self._columns_list[
                                                           self._options.iec_table_name])
        self._connection.insert_row(table_name=self._options.iec_table_name,
                                    column_names=columns,
                                    values=values)

    @staticmethod
    def _sanitizate_signal_name(signal_name: str) -> str:
        """
        Функция очистки имени сигнала (для раздвоенных изначально сигналов убирается признак сигнала, такой как: вкл,
        откл, ввод, вывод и пр.
        :param signal_name: Очищаемое имя сигнала
        :return: Очищенное имя сигнала
        """
        key_words: list = ['вкл', 'откл', 'замкн', 'разомкн', 'ввод', 'вывод', 'введ', 'вывед',
                           'close', 'trip', 'input', 'output', 'discon', 'enabl', 'remov']
        key_word: str | None = next((key for key in key_words if key.upper() in signal_name.upper()), None)
        out_string: str
        if key_word is not None:
            start_index: int = signal_name.upper().find(key_word.upper())
            end_index: int = next(
                (index for index in range(start_index, len(signal_name)) if not signal_name[index].isalpha()),
                start_index)
            if (key_word == 'откл' or key_word == 'вкл') and \
                    signal_name[start_index - 3: start_index].casefold() == 'на '.casefold():
                start_index = start_index - 3
            if start_index == end_index:
                out_string = signal_name[:start_index]
            else:
                out_string = signal_name.replace(signal_name[start_index: end_index], '')
        else:
            out_string = signal_name
        out_string = re.sub('(^on|on$|is on |is on$)', '', out_string, flags=re.I)
        out_string = re.sub('(^off|off$|is off |is off$)', '', out_string, flags=re.I)
        out_string = re.sub('( on | off )', ' ', out_string, flags=re.I)
        out_string = out_string.replace('""', '').replace('  ', ' ')
        if out_string.casefold() == signal_name.casefold():
            logging.error(f'Не удалось очистить строку {signal_name}')
            raise Exception('SignalNameCorrectionFailed')
        return out_string

    def _read_signalization_table(self) -> None:
        """
        Функция чтения строк таблицы DIAG и запись в таблицу СиМ
        :return: None
        """
        values: list[dict[str, str]] = \
            self._connection.retrieve_data(table_name=self._options.sign_table_name,
                                           fields=self._columns_list[self._options.sign_table_name],
                                           key_names=None,
                                           key_values=None)
        ProgressBar.config(max_value=len(values), length=50, step=1,
                           prefix=f'Добавление диагностических сигналов', suffix='Завершено')
        for value in values:
            values_to_add: list[str] = []
            for column in self._columns_list[self._options.sign_table_name]:
                values_to_add.append(value[column])
            self._connection.insert_row(table_name=self._options.sim_table_name,
                                        column_names=self._columns_list[self._options.sign_table_name],
                                        values=values_to_add)
            ProgressBar.update_progress()
        self._connection.commit()

    def _get_table_columns(self):
        columns_from_signal: set[str] = self._get_column_set(signal_type=Signal)
        columns_from_digital_signal: set[str] = self._get_column_set(signal_type=DigitalSignal)
        columns_from_table_aep: set[str] = self._connection.get_column_names(table_name=self._options.aep_table_name)
        columns_from_table_sim: set[str] = self._connection.get_column_names(table_name=self._options.sim_table_name)
        columns_from_table_iec: set[str] = self._connection.get_column_names(table_name=self._options.iec_table_name)
        columns_from_table_sign: set[str] = self._connection.get_column_names(table_name=self._options.sign_table_name)
        excluded_columns: set[str] = columns_from_signal.difference(columns_from_table_aep)
        if len(excluded_columns) > 0:
            logging.info('Следующие поля не будут загружены: {}'.format(','.join(excluded_columns)))

        self._columns_list[self._options.aep_table_name] = list(
            columns_from_signal.intersection(columns_from_table_aep))
        self._columns_list[self._options.sim_table_name] = list(
            columns_from_signal.intersection(columns_from_table_sim))
        self._columns_list[self._options.iec_table_name] = list(
            columns_from_digital_signal.intersection(columns_from_table_iec))
        self._columns_list[self._options.sign_table_name] = list(
            columns_from_table_sign.intersection(columns_from_table_sim))

    def get_column_name(self, column_name: str) -> str:
        return self._connection.modify_column_name(column_name)

    def generate(self) -> None:
        """
        Основная функция генерации таблиц
        :return: None
        """
        logging.info(f'Очистка таблицы {self._options.sim_table_name}...')
        self._connection.clear_table(self._options.sim_table_name)
        logging.info('Завершено.')

        logging.info(f'Очистка таблицы {self._options.iec_table_name}...')
        self._connection.clear_table(self._options.iec_table_name)
        logging.info('Завершено')

        self._get_table_columns()

        max_value: int = self._connection.get_row_count(self._options.aep_table_name)
        logging.info('Заполнение таблиц...')
        ProgressBar.config(max_value=max_value, step=1, prefix='Обработка таблицы АЭП', suffix='Завершено', length=50)
        kksp_list: list[str] = self._get_kksp_list()
        for kksp in kksp_list:
            self._generate_table_for_kksp(kksp=kksp)
            self._connection.commit()

        self._read_signalization_table()
        logging.info('Завершено')

    @staticmethod
    def run(options: GenerateTableOptions, connection: Connection) -> None:
        logging.info('Запуск скрипта "Заполнение таблиц"...')
        with connection:
            generate_class: GenerateTables = GenerateTables(options=options,
                                                            connection=connection)
            generate_class.generate()
        logging.info('Выпонение скрипта "Заполнение таблиц" завершено.')
        logging.info('')
