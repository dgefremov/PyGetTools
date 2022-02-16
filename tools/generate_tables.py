import logging
import re
from dataclasses import dataclass

from tools.utils.progress_utils import ProgressBar
from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class UncommonTemplate:
    """
    Класс хранения шаблонов для нетиповых сигналов
    """
    signal_kks: str
    signal_part: str
    template: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class SWTemplate:
    """
    Класс для хранения шаблонов для проводных сигналов управления
    """
    name: str
    part_list: list[str]


@dataclass(init=False, repr=False, eq=False, order=False, frozen=False)
class Signal:
    """
    Класс хранения строки с сигналом
    """
    object_typ: str
    kks: str
    part: str
    module: str
    rednd_intf: str
    name_rus: str
    full_name_rus: str
    name_eng: str
    full_name_eng: str
    min: float | None
    max: float | None
    units_rus: str
    units_eng: str
    in_level: str
    cabinet: str
    slot_mp: int | None
    channel: int | None
    connection: str
    sensr_typ: str
    cat_nam: str
    location_mp: str
    dname: str | None
    kksp: str
    template: str | None

    @staticmethod
    def create_from_row(value: dict[str, str]) -> 'Signal':
        signal: Signal = Signal()
        signal.object_typ = value['OBJECT_TYP']
        signal.kks = value['KKS']
        signal.part = value['PART']
        signal.module = value['MODULE']
        signal.rednd_intf = value['REDND_INTF']
        signal.name_rus = value['NAME_RUS']
        signal.full_name_rus = value['FULL_NAME_RUS']
        signal.name_eng = value['NAME_ENG']
        signal.full_name_eng = value['FULL_NAME_ENG']
        signal.min = None if value['MIN'] is None else float(value['MIN'])
        signal.max = None if value['MAX'] is None else float(value['MAX'])
        signal.units_rus = value['UNITS_RUS']
        signal.units_eng = value['UNITS_ENG']
        signal.in_level = value['IN_LEVEL']
        signal.cabinet = value['CABINET']
        signal.slot_mp = None if value['SLOT_MP'] is None else int(value['SLOT_MP'])
        signal.channel = None if value['CHANNEL'] is None else int(value['CHANNEL'])
        signal.connection = value['CONNECTION']
        signal.sensr_typ = value['SENSR_TYPE']
        signal.cat_nam = value['CatNam']
        signal.location_mp = value['LOCATION_MP']
        if 'DNAME' in value:
            signal.dname = value['DNAME']
        else:
            signal.dname = None
        signal.kksp = value['KKSp']
        if 'SCHEMA' in value:
            signal.template = value['SCHEMA']
        else:
            signal.template = None
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
    path: str
    network_data_table_name: str
    controller_data_table_name: str
    aep_table_name: str
    sim_table_name: str
    iec_table_name: str
    ied_table_name: str
    ref_table_name: str
    sign_table_name: str
    skip_duplicate_prefix: list[str]
    dps_signals: list[DoublePointSignal]
    sw_templates: list[SWTemplate]
    uncommon_templates: None | list[UncommonTemplate] = None


class GenerateTables:
    """
    Основной класс генерации таблиц
    """
    _options: 'GenerateTableOptions'
    _access_base: Connection

    def __init__(self, options: GenerateTableOptions, access_base: Connection):
        self._options = options
        self._access_base = access_base

    def _get_kksp_list(self) -> list[str]:
        """

        :return: Список KKSp
        """
        values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.aep_table_name,
                                                                       fields=['KKSp'],
                                                                       key_names=None,
                                                                       key_values=None,
                                                                       uniq_values=True,
                                                                       sort_by=None,
                                                                       key_operator=None)
        kksp_list: list[str] = []
        for value in values:
            kksp_list.append(value['KKSp'])
        return kksp_list

    def _generate_table_for_kksp(self, kksp: str) -> None:
        """
        Функция запуска генерации таблиц для одного KKSp
        :param kksp: KKSp для генерации
        :return: None
        """
        values: list[dict[str, str]] = \
            self._access_base.retrieve_data(table_name=self._options.aep_table_name,
                                            fields=['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF',
                                                    'FULL_NAME_RUS', 'NAME_RUS', 'FULL_NAME_ENG', 'NAME_ENG', 'MIN',
                                                    'MAX', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL', 'CABINET',
                                                    'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam',
                                                    'LOCATION_MP', 'DNAME', 'KKSp'],
                                            key_names=['KKSp'],
                                            key_values=[kksp])
        sw_container: dict[str, list[Signal]] = {}
        undubled_container: list[Signal] = []
        for value in values:
            ProgressBar.update_progress()
            signal: Signal = Signal.create_from_row(value)
            if signal.module == '1623' or signal.module == '1631' or signal.module == '1661':
                self._process_wired_signal(signal=signal, sw_container=sw_container)
            elif signal.module == '1691':
                self._process_digital_signal(signal=signal,
                                             undubled_signal_container=undubled_container)
        self._check_undubled_signals(undubled_signal_container=undubled_container)
        self._access_base.commit()

    def _process_wired_signal(self, signal: Signal, sw_container: dict[str, list[Signal]]) -> None:
        """
        Обработка проводного сигнала
        :param signal: Сигнал (строка таблицы)
        :param sw_container: Контейнер для хранения групп SW сигналов
        :return: None
        """
        if signal.module == '1623' and signal.object_typ.casefold() == 'SW'.casefold():
            self._process_sw_signals(sw_container=sw_container,
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

    def _check_undubled_signals(self, undubled_signal_container: list[Signal]) -> None:
        """
        Проверка пар для раздвоенных сигналов (которые изначально были в базе). Для сигналов без пары создается сигнал
        :param undubled_signal_container: Хранилище для раздвоенных сигналов
        :return: None
        """
        dict_with_status: dict[Signal, bool] = {signal: False for signal in undubled_signal_container}
        for signal in dict_with_status:
            if dict_with_status[signal]:
                continue
            paired_part: str = self._get_part_pair(signal.part)
            paired_signal: Signal = next((signal for signal in list(dict_with_status.keys())
                                          if signal.part.casefold() == paired_part.casefold()), None)
            if paired_signal is not None:
                dict_with_status[paired_signal] = True
                continue
            else:
                new_signal: Signal = signal.clone()
                new_signal.part = paired_part
                self._add_signal_to_iec_table(signal=new_signal)
                self._add_signal_to_sim_table(signal=new_signal)

    def _process_digital_signal(self, signal: Signal, undubled_signal_container: list[Signal]) -> None:
        """
        Обработка цифрового сигнала
        :param signal: Сигнал (строка из базы)
        :param undubled_signal_container: хранилище для раздвоенных сигналов (которые изначально были в базе)
        :return: None
        """
        if signal.part in list(sum([(dps_signal.on_part, dps_signal.off_part) for dps_signal in
                                    self._options.dps_signals], ())):
            signal.name_rus = self._sanitizate_signal_name(signal.name_rus)
            signal.full_name_rus = self._sanitizate_signal_name(signal.full_name_rus)
            signal.name_eng = self._sanitizate_signal_name(signal.name_eng)
            signal.full_name_eng = self._sanitizate_signal_name(signal.full_name_eng)
            undubled_signal_container.append(signal)

        if signal.part in [dps_signal.single_part for dps_signal in self._options.dps_signals
                           if dps_signal.single_part is not None] and \
                not any(signal.kks.upper().startswith(item.upper()) for item in self._options.skip_duplicate_prefix):
            self._duplicate_signal(signal=signal)
        else:
            self._add_signal_to_iec_table(signal=signal)
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
        self._add_signal_to_sim_table(signal=new_signal_1)
        self._add_signal_to_iec_table(signal=new_signal_2)
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

    def _process_sw_signals(self, sw_container: dict[str, list[Signal]], signal: Signal) -> None:
        """
        Обработка SW сигналов (объединения группы сигналов в один)
        :param sw_container: Хранилище для SW сигналов
        :param signal: Текущий SW сигнал
        :return: None
        """
        if signal.kks in sw_container:
            sw_signals: list[Signal] = sw_container[signal.kks]
            if len(sw_signals) < 6:
                sw_signals.append(signal)
            if len(sw_signals) == 6:
                parts_in_container: set[str] = {item.part for item in sw_signals}
                parts_set: set[str] = {'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'}
                if parts_set == parts_in_container:
                    sw_signal: Signal = signal.clone()
                    sw_signal.part = 'XA00'
                    sw_signal.name_rus = self._get_common_prefix(list(map(lambda item: item.name_rus, sw_signals)))
                    sw_signal.name_eng = self._get_common_prefix(list(map(lambda item: item.name_eng, sw_signals)))
                    sw_signal.full_name_rus = self._get_common_prefix(list(map(lambda item: item.full_name_rus,
                                                                               sw_signals)))
                    sw_signal.full_name_eng = self._get_common_prefix(list(map(lambda item: item.full_name_eng,
                                                                               sw_signals)))
                    sw_signal.template = self._get_sw_template(sw_signal.kksp, sw_signal.cabinet)
                    self._add_signal_to_sim_table(sw_signal)
                    del sw_container[signal.kks]
                else:
                    logging.error('Неверный набор сигналов в группе SW')
                    raise Exception('SignalGroupError')
        else:
            sw_container[signal.kks] = [signal]

    def _get_sw_template(self, kksp: str, cabinet: str) -> str:
        values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.aep_table_name,
                                                                       fields=['PART'],
                                                                       key_names=['KKSp', 'CABINET'],
                                                                       key_values=[kksp, cabinet])
        path_list: list[str] = [value['PART'] for value in values]
        for sw_template in self._options.sw_templates:
            if all(part in path_list for part in sw_template.part_list):
                return sw_template.name
        logging.error('Не найдена схема подключения для управления выключателем')
        raise Exception('SWTemplateNotFound')

    def _add_signal_to_sim_table(self, signal: Signal) -> None:
        """
        Добавление сигнала в таблицу СиМ
        :param signal: Сигнал для добавления в таблицу
        :return: None
        """
        column_names: list[str] = ['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF', 'FULL_NAME_RUS', 'NAME_RUS',
                                   'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL',
                                   'CABINET', 'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam', 'KKSp',
                                   'LOCATION_MP', 'SCHEMA']
        if signal.module == '1691':
            signal.template = ''
        else:
            if signal.template is None:
                uncommon_template: [UncommonTemplate, None] = None
                if self._options.uncommon_templates is not None:
                    uncommon_template = next(item for item in self._options.uncommon_templates if
                                             item.signal_kks == signal.kks and item.signal_part == signal.part)
                signal.template = f'{signal.object_typ}_{signal.module}' \
                    if uncommon_template is None else uncommon_template.template

        channel: int
        if signal.module == '1623' and signal.object_typ != 'SW':
            channel = signal.channel + 50
        else:
            channel = signal.channel
        values: list[str] = [signal.object_typ, signal.kks, signal.part, signal.module, signal.rednd_intf,
                             signal.full_name_rus, signal.name_rus, signal.full_name_eng, signal.name_eng,
                             signal.min, signal.max, signal.units_rus, signal.units_eng, signal.in_level,
                             signal.cabinet, signal.slot_mp, channel, signal.connection, signal.sensr_typ,
                             signal.cat_nam, signal.kksp, signal.location_mp, signal.template]
        self._access_base.insert_row(table_name=self._options.sim_table_name,
                                     column_names=column_names,
                                     values=values)

    def _add_signal_to_iec_table(self, signal: Signal) -> None:
        """
        Добавление сигнала в таблицу МЭК
        :param signal: Сигнал (запись в базе)
        :return: None
        """
        column_names: list[str] = ['KKS', 'PART', 'KKSp', 'MODULE', 'REDND_INTF', 'CABINET', 'SLOT_MP', 'LOCATION_MP',
                                   'FULL_NAME_RUS', 'NAME_RUS', 'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS',
                                   'UNITS_ENG', 'SENSR_TYPE', 'AREA', 'DNAME', 'IP', 'IED_NAME']
        ied_name: str = 'IED_' + signal.kksp.replace('-', '_')
        area: str = self._access_base.retrieve_data('TPTS', ['AREA'], ['CABINET'], [signal.cabinet])[0]['AREA']
        ip: str = self._access_base.retrieve_data('[Network data]', ['IP'], ['KKSp'], [signal.kksp])[0]['IP']
        values: list[str] = [signal.kks, signal.part, signal.kksp, signal.module, signal.rednd_intf, signal.cabinet,
                             signal.slot_mp, signal.location_mp, signal.full_name_rus, signal.name_rus,
                             signal.full_name_eng, signal.name_eng, signal.min, signal.max, signal.units_rus,
                             signal.units_eng, signal.sensr_typ, area, signal.dname, ip, ied_name]

        self._access_base.insert_row(table_name=self._options.iec_table_name,
                                     column_names=column_names,
                                     values=values)

    @staticmethod
    def _sanitizate_signal_name(signal_name: str) -> str:
        """
        Функция очистки имени сигнала (для раздвоенных изначально сигналов убирается признак сигнала, такой как: вкл,
        откл, ввод, вывод и пр.
        :param signal_name: Очищаемое имя сигнала
        :return: Очищенное имя сигнала
        """
        key_words: list = ['вкл', 'откл', 'замкн', 'разомкн', 'ввод', 'вывод', 'введ',
                           'close', 'trip', 'input', 'output', 'discon']
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
            self._access_base.retrieve_data(table_name=self._options.sign_table_name,
                                            fields=['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF',
                                                    'FULL_NAME_RUS', 'NAME_RUS', 'FULL_NAME_ENG', 'NAME_ENG', 'MIN',
                                                    'MAX', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL', 'CABINET',
                                                    'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam',
                                                    'LOCATION_MP', 'KKSp', 'SCHEMA', 'REF'],
                                            key_names=None,
                                            key_values=None)
        ProgressBar.config(max_value=len(values), length=50, step=1,
                           prefix=f'Добавление диагностических сигналов', suffix='Завершено')
        for value in values:
            signal: Signal = Signal.create_from_row(value)
            self._add_signal_to_sim_table(signal=signal)
            ProgressBar.update_progress()

    def generate(self) -> None:
        """
        Основная функция генерации таблиц
        :return: None
        """
        logging.info(f'Очистка таблицы {self._options.sim_table_name}...')
        self._access_base.clear_table(self._options.sim_table_name)
        logging.info('Завершено.')

        logging.info(f'Очистка таблицы {self._options.iec_table_name}...')
        self._access_base.clear_table(self._options.iec_table_name)
        logging.info('Завершено')

        max_value: int = self._access_base.get_row_count(self._options.aep_table_name)
        logging.info('Заполнение таблиц...')
        ProgressBar.config(max_value=max_value, step=1, prefix='Обработка таблицы АЭП', suffix='Завершено', length=50)
        kksp_list: list[str] = self._get_kksp_list()
        for kksp in kksp_list:
            self._generate_table_for_kksp(kksp=kksp)

        self._read_signalization_table()
        logging.info('Завершено')

    @staticmethod
    def run(options: GenerateTableOptions) -> None:
        """
        Запуск скрипта
        :param options: Настройки для скрипта
        :return: None
        """
        logging.info('Запуск скрипта...')
        with Connection.connect_to_mdb(options.path) as access_base:
            generate_class: GenerateTables = GenerateTables(options=options,
                                                            access_base=access_base)
            generate_class.generate()
        logging.info('Выпонение завершено.')
