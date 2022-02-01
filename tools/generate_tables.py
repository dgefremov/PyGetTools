import re
import logging
from typing import List, Dict, Union, Set, Tuple
from dataclasses import dataclass

from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class UncommonTemplate:
    """
    Класс хранения шаблонов для нетиповых сигналов
    """
    signal_kks: str
    signal_part: str
    template: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DPCSignal:
    """
    Класс хранения двухпозицонного сигнала
    """
    signal_part: Union[str, None]
    signal_part_dupl: Union[Tuple[str, str], None]
    command_part: Union[str, None]
    command_part_dupl: Union[Tuple[str, str], None]

    def is_command(self, value: str) -> bool:
        if self.command_part_dupl is None:
            return False
        return value.upper() in (command_part.upper() for command_part in self.command_part_dupl)

    def is_signal(self, value: str) -> bool:
        if self.signal_part_dupl is None:
            return False
        return value.upper() in (signal_part.upper() for signal_part in self.signal_part_dupl)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BSCSignal:
    """
    Класс хранения сигнала РПН типа BSC
    """
    signal_part: str
    command_part: str
    command_part_dupl: Union[Tuple[str, str], None]

    def is_command(self, value: str) -> bool:
        return value.upper() in (command_part.upper() for command_part in self.command_part_dupl)

    def is_signal(self, value: str) -> bool:
        return value.upper() == self.signal_part


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
    min: Union[float, None]
    max: Union[float, None]
    units_rus: str
    units_eng: str
    in_level: str
    cabinet: str
    slot_mp: Union[int, None]
    channel: Union[int, None]
    connection: str
    sensr_typ: str
    cat_nam: str
    location_mp: str
    dname: str
    kksp: str

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
        return new_signal


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class SignalRange:
    """
    Класс хранения диапазона MMS адресов для типа сигнала в CID файле
    """
    low: int
    high: int


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DatasetDescription:
    """
    Класс хранения описания Dataset в CID файле
    """
    name: str
    path: str
    rcb_main: str
    rcb_res: str
    spc_range: Union[SignalRange, None] = None
    sps_range: Union[SignalRange, None] = None
    dpc_range: Union[SignalRange, None] = None
    bsc_range: Union[SignalRange, None] = None
    mv_range: Union[SignalRange, None] = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=False)
class DatasetDescriptionList:
    """
    Класс хранения списков Dataset
    """
    dataset_list: List[DatasetDescription]

    def get_by_spc_index(self, spc_index) -> Union[DatasetDescription, None]:
        return next(
            (dataset for dataset in self.dataset_list if dataset.spc_range is not None and dataset.spc_range.low <=
             spc_index <= dataset.spc_range.high),
            None)

    def get_by_sps_index(self, sps_index) -> Union[DatasetDescription, None]:
        return next(
            (dataset for dataset in self.dataset_list if dataset.sps_range is not None and dataset.sps_range.low <=
             sps_index <= dataset.sps_range.high),
            None)

    def get_by_dpc_index(self, dpc_index) -> Union[DatasetDescription, None]:
        return next(
            (dataset for dataset in self.dataset_list if dataset.dpc_range is not None and dataset.dpc_range.low <=
             dpc_index <= dataset.dpc_range.high),
            None)

    def get_by_bsc_index(self, bsc_index) -> Union[DatasetDescription, None]:
        return next(
            (dataset for dataset in self.dataset_list if dataset.bsc_range is not None and dataset.bsc_range.low <=
             bsc_index <= dataset.bsc_range.high),
            None)

    def get_by_mv_index(self, mv_index) -> Union[DatasetDescription, None]:
        return next(
            (dataset for dataset in self.dataset_list if dataset.mv_range is not None and dataset.mv_range.low <=
             mv_index <= dataset.mv_range.high),
            None)


class MMSGenerator:
    """
    Класс генератора MMS адресов для сигналов
    """
    sps_index: int
    spc_index: int
    dpc_index: int
    mv_index: int
    bsc_index: int
    ied_name: str

    dpc_container: Dict[DPCSignal, Dict[str, str]]
    bsc_container: Dict[BSCSignal, Dict[str, str]]
    dataset_container: List[DatasetDescription]
    dataset_descriptions: Union[DatasetDescriptionList, None]

    MV_PREFIX = 'Device/GGIO1.AnIn'
    MV_POSTFIX = '.mag.f'

    SPS_PREFIX = 'Device/GGIO1.Alm'
    SPS_POSTFIX = '.stVal'

    SPC_PREFIX = 'Device/GGIO1.SPCSO'
    SPC_POSTFIX = '.Oper'

    BSC_PREFIX = 'Device/ATCC'
    BSC_COMMAND_POSTFIX = '.TapChg.Oper'
    BSC_POS_POSTFIX = '.TapChg.valWTr'

    DPS_PREFIX = 'Device/GGIO1.DPCSO'
    DPS_COMMAND_POSTFIX = '.Oper'
    DPS_POS_POSTFIX = '.stVal'

    def __init__(self, kksp: str, dpc_signals: List[DPCSignal],
                 bsc_signals: List[BSCSignal], dataset_descriptions: DatasetDescriptionList):
        self.sps_index = 0
        self.spc_index = 0
        self.dpc_index = 0
        self.mv_index = 0
        self.bsc_index = 0
        self.ied_name = 'IED_' + kksp.replace('-', '_')
        self.dpc_container = {}
        self.bsc_container = {}
        self.dataset_container = []
        self.dataset_descriptions = dataset_descriptions
        for dpc_signal in dpc_signals:
            self.dpc_container[dpc_signal] = {}
        for bsc_signal in bsc_signals:
            self.bsc_container[bsc_signal] = {}

    def get_mms(self, kks: str, part: str):
        for dps_signal in self.dpc_container:
            if dps_signal.is_signal(part) or dps_signal.is_command(part):
                postfix: str = self.DPS_COMMAND_POSTFIX if dps_signal.is_command(part) else \
                    self.DPS_POS_POSTFIX
                if kks not in self.dpc_container[dps_signal]:
                    self.dpc_index += 1
                    self.dpc_container[dps_signal][kks] = self.DPS_PREFIX + str(self.dpc_index)
                    if self.dataset_descriptions is not None:
                        dataset: DatasetDescription = self.dataset_descriptions.get_by_dpc_index(self.dpc_index)
                        if dataset is None:
                            logging.error(f'Не найден Dataset для DPS {self.dpc_index}')
                            raise Exception('DatasetError')
                        if not self.dataset_container.__contains__(dataset):
                            self.dataset_container.append(dataset)
                return self.ied_name + self.dpc_container[dps_signal][kks] + postfix

        for bsc_signal in self.bsc_container:
            if bsc_signal.is_signal(part) or bsc_signal.is_command(part):
                postfix: str = self.BSC_COMMAND_POSTFIX if bsc_signal.is_command(part) else \
                    self.BSC_POS_POSTFIX
                if kks not in self.bsc_container[bsc_signal]:
                    self.bsc_index += 1
                    self.bsc_container[bsc_signal][kks] = self.BSC_PREFIX + str(self.bsc_index)
                    if self.dataset_descriptions is not None:
                        dataset: DatasetDescription = self.dataset_descriptions.get_by_bsc_index(self.bsc_index)
                        if dataset is None:
                            logging.error(f'Не найден Dataset для BSC {self.bsc_index}')
                            raise Exception('DatasetError')
                        if not self.dataset_container.__contains__(dataset):
                            self.dataset_container.append(dataset)
                return self.ied_name + self.bsc_container[bsc_signal][kks] + postfix

        if part.upper().startswith('XL'):
            self.spc_index += 1
            if self.dataset_descriptions is not None:
                dataset: DatasetDescription = self.dataset_descriptions.get_by_spc_index(self.spc_index)
                if dataset is None:
                    logging.error(f'Не найден Dataset для SPC {self.spc_index}')
                    raise Exception('DatasetError')
                if not self.dataset_container.__contains__(dataset):
                    self.dataset_container.append(dataset)
            return self.ied_name + self.SPC_PREFIX + str(self.spc_index) + self.SPC_POSTFIX

        if part.upper().startswith('XQ'):
            self.mv_index += 1
            if self.dataset_descriptions is not None:
                dataset: DatasetDescription = self.dataset_descriptions.get_by_mv_index(self.mv_index)
                if dataset is None:
                    logging.error(f'Не найден Dataset для MV {self.mv_index}')
                    raise Exception('DatasetError')
                if not self.dataset_container.__contains__(dataset):
                    self.dataset_container.append(dataset)
            return self.ied_name + self.MV_PREFIX + str(self.mv_index) + self.MV_POSTFIX

        self.sps_index += 1
        if self.dataset_descriptions is not None:
            dataset: DatasetDescription = self.dataset_descriptions.get_by_sps_index(self.sps_index)
            if dataset is None:
                logging.error(f'Не найден Dataset для SPS {self.sps_index}')
                raise Exception('DatasetError')
            if not self.dataset_container.__contains__(dataset):
                self.dataset_container.append(dataset)
        return self.ied_name + self.SPS_PREFIX + str(self.sps_index) + self.SPS_POSTFIX


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
    dpc_signals: List[DPCSignal]
    bsc_signals: List[BSCSignal]
    skip_duplicate_prefix: List[str]
    datasets: Union[None, DatasetDescriptionList] = None
    uncommon_templates: Union[None, List[UncommonTemplate]] = None


class GenerateTables:
    """
    Основной класс генерации таблиц
    """
    _options: 'GenerateTableOptions'
    _access_base: Connection

    def __init__(self, options: GenerateTableOptions, access_base: Connection):
        self._options = options
        self._access_base = access_base

    def _get_kksp_list(self) -> List[str]:
        """
        Функция загрузки списка KKSp из БД
        :return: Список KKSp
        """
        values: List[Dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.aep_table_name,
                                                                       fields=['KKSp'],
                                                                       key_names=None,
                                                                       key_values=None,
                                                                       uniq_values=True,
                                                                       sort_by=None,
                                                                       key_operator=None)
        kksp_list: List[str] = []
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
                                                    'LOCATION_MP', 'DNAME'],
                                            key_names=['KKSp'],
                                            key_values=[kksp])
        sw_container: Dict[str, List[Signal]] = {}
        undubled_container: List[Signal] = []
        mms_generator: MMSGenerator = MMSGenerator(kksp=kksp,
                                                   dpc_signals=self._options.dpc_signals,
                                                   bsc_signals=self._options.bsc_signals,
                                                   dataset_descriptions=self.
                                                   _options.datasets)
        for value in values:
            ProgressBar.update_progress()
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
            signal.dname = value['DNAME']
            signal.kksp = kksp

            if signal.module == '1623' or signal.module == '1631' or signal.module == '1661':
                self._process_wired_signal(signal=signal, sw_container=sw_container)
            elif signal.module == '1691':
                self._process_digital_signal(signal=signal, mms_generator=mms_generator,
                                             undubled_signal_container=undubled_container)
        if self._options.datasets is not None and len(mms_generator.dataset_container) > 0:
            self._add_ied_record(mms_generator=mms_generator)
        self._check_undubled_signals(undubled_signal_container=undubled_container, mms_generator=mms_generator)
        self._access_base.commit()

    def _process_wired_signal(self, signal: Signal, sw_container: Dict[str, List[Signal]]) -> None:
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

    def _add_ied_record(self, mms_generator: MMSGenerator):
        """
        Функция добавления (редактирования) записи в таблице IED
        :param mms_generator: Экземпляр класса генератора MMS сигналов (в нем хранятся Dataset)
        :return:
        """
        ied_record_exists: bool = len(self._access_base.retrieve_data(table_name=self._options.ied_table_name,
                                                                      fields=['IED_NAME'],
                                                                      key_names=['IED_NAME'],
                                                                      key_values=[mms_generator.ied_name])) == 1
        dataset_list: str = ';'.join([dataset.path for dataset in mms_generator.dataset_container])
        rb_master_list: str = ';'.join([dataset.rcb_main for dataset in mms_generator.dataset_container])
        rb_slave_list: str = ';'.join([dataset.rcb_res for dataset in mms_generator.dataset_container])
        if ied_record_exists:
            self._access_base.update_field(table_name=self._options.ied_table_name,
                                           fields=['DATASET', 'RB_MASTER', 'RB_SLAVE'],
                                           values=[dataset_list, rb_master_list, rb_slave_list],
                                           key_names=['IED_NAME'],
                                           key_values=[mms_generator.ied_name])
        else:
            self._access_base.insert_row(table_name=self._options.ied_table_name,
                                         column_names=['IED_NAME', 'DATASET', 'RB_MASTER', 'RB_SLAVE'],
                                         values=[dataset_list, rb_master_list, rb_slave_list])

    def _get_parts_to_duplicate(self) -> List[str]:
        """
        Получение списка PART для сигналов, которые требуется раздвоить
        :return: Список PART для сигналов, которые требуется раздвоить
        """
        output: List[str] = []
        for dps_signal in self._options.dpc_signals:
            if dps_signal.signal_part is not None:
                output.append(dps_signal.signal_part)
            if dps_signal.command_part is not None:
                output.append(dps_signal.command_part)
        for bsc_signal in self._options.bsc_signals:
            output.append(bsc_signal.command_part)
        return output

    def _get_duplicated_parts(self) -> List[str]:
        """
        Получение списка PART для раздвоенных сигналов
        :return: Список PART для раздвоенных сигналов
        """
        output: List[str] = []
        for dpc_signal in self._options.dpc_signals:
            if dpc_signal.signal_part_dupl is not None:
                output.extend(dpc_signal.signal_part_dupl)
            if dpc_signal.command_part_dupl is not None:
                output.extend(dpc_signal.command_part_dupl)
        for bsc_signal in self._options.bsc_signals:
            if bsc_signal.command_part_dupl is not None:
                output.extend(bsc_signal.command_part_dupl)
        return output

    def _get_part_pair(self, part: str) -> str:
        """
        Получение ответный part для раздвоенных сигналов
        :param part: Part, для которой ищется пара
        :return: Ответный part для развдоенного сигнала
        """
        for dpc_signal in self._options.dpc_signals:
            if dpc_signal.signal_part_dupl is not None:
                if dpc_signal.signal_part_dupl[0].casefold() == part.casefold():
                    return dpc_signal.signal_part_dupl[1]
                if dpc_signal.signal_part_dupl[1].casefold() == part.casefold():
                    return dpc_signal.signal_part_dupl[0]
            if dpc_signal.command_part_dupl is not None:
                if dpc_signal.command_part_dupl[0].casefold() == part.casefold():
                    return dpc_signal.command_part_dupl[1]
                if dpc_signal.command_part_dupl[1].casefold() == part.casefold():
                    return dpc_signal.command_part_dupl[0]
        for bsc_signal in self._options.bsc_signals:
            if bsc_signal.command_part_dupl is not None:
                if bsc_signal.command_part_dupl[0].casefold() == part.casefold():
                    return bsc_signal.command_part_dupl[1]
                if bsc_signal.command_part_dupl[1].casefold() == part.casefold():
                    return bsc_signal.command_part_dupl[0]

    def _check_undubled_signals(self, undubled_signal_container: List[Signal], mms_generator: MMSGenerator) -> None:
        """
        Проверка пар для раздвоенных сигналов (которые изначально были в базе). Для сигналов без пары создается сигнал
        :param undubled_signal_container: Хранилище для раздвоенных сигналов
        :param mms_generator: Экземпляр класса генератора MMS адресов
        :return: None
        """
        dict_with_status: Dict[Signal, bool] = {signal: False for signal in undubled_signal_container}
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
                self._add_signal_to_iec_table(signal=new_signal, mms_generator=mms_generator)
                self._add_signal_to_sim_table(signal=new_signal)

    def _process_digital_signal(self, signal: Signal, mms_generator: MMSGenerator,
                                undubled_signal_container: List[Signal]) -> None:
        """
        Обработка цифрового сигнала
        :param signal: Сигнал (строка из базы)
        :param mms_generator: Экземпляр для класса генератора MMS адресов
        :param undubled_signal_container: хранилище для раздвоенных сигналов (которые изначально были в базе)
        :return: None
        """
        if signal.part in self._get_duplicated_parts():
            signal.name_rus = self._sanitizate_signal_name(signal.name_rus)
            signal.full_name_rus = self._sanitizate_signal_name(signal.full_name_rus)
            signal.name_eng = self._sanitizate_signal_name(signal.name_eng)
            signal.full_name_eng = self._sanitizate_signal_name(signal.full_name_eng)
            undubled_signal_container.append(signal)

        if signal.part in self._get_parts_to_duplicate() and \
                not any(signal.kks.upper().startswith(item.upper()) for item in self._options.skip_duplicate_prefix):
            self._duplicate_signal(signal=signal, mms_generator=mms_generator)
        else:
            self._add_signal_to_iec_table(signal=signal, mms_generator=mms_generator)
            self._add_signal_to_sim_table(signal=signal)

    def _duplicate_signal(self, signal: Signal, mms_generator: MMSGenerator) -> None:
        """
        Раздвоение сигнала
        :param signal: Исходный сигнал
        :param mms_generator: Экземпляр для класса генератора MMS адреса
        :return: None
        """
        part_num_string: str = signal.part[2:]
        part_num: int = int(part_num_string)
        new_signal_1: Signal = signal.clone()
        new_signal_1.part = signal.part[:2] + str(part_num + 1).rjust(2, '0')
        new_signal_2: Signal = signal.clone()
        new_signal_2.part = signal.part[:2] + str(part_num + 2).rjust(2, '0')
        self._add_signal_to_iec_table(signal=new_signal_1, mms_generator=mms_generator)
        self._add_signal_to_sim_table(signal=new_signal_1)
        self._add_signal_to_iec_table(signal=new_signal_2, mms_generator=mms_generator)
        self._add_signal_to_sim_table(signal=new_signal_2)

    @staticmethod
    def _get_common_prefix(strings: List[str]) -> str:
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

    def _process_sw_signals(self, sw_container: Dict[str, List[Signal]], signal: Signal) -> None:
        """
        Обработка SW сигналов (объединения группы сигналов в один)
        :param sw_container: Хранилище для SW сигналов
        :param signal: Текущий SW сигнал
        :return: None
        """
        if signal.kks in sw_container:
            sw_signals: List[Signal] = sw_container[signal.kks]
            if len(sw_signals) < 6:
                sw_signals.append(signal)
            if len(sw_signals) == 6:
                parts_in_container: Set[str] = {item.part for item in sw_signals}
                parts_set: Set[str] = {'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'}
                if parts_set == parts_in_container:
                    sw_signal: Signal = signal.clone()
                    sw_signal.part = 'XA00'
                    sw_signal.name_rus = self._get_common_prefix(list(map(lambda item: item.name_rus, sw_signals)))
                    sw_signal.name_eng = self._get_common_prefix(list(map(lambda item: item.name_eng, sw_signals)))
                    sw_signal.full_name_rus = self._get_common_prefix(list(map(lambda item: item.full_name_rus,
                                                                               sw_signals)))
                    sw_signal.full_name_eng = self._get_common_prefix(list(map(lambda item: item.full_name_eng,
                                                                               sw_signals)))
                    self._add_signal_to_sim_table(sw_signal)
                    del sw_container[signal.kks]
                else:
                    logging.error('Неверный набор сигналов в группе SW')
                    raise Exception('SignalGroupError')
        else:
            sw_container[signal.kks] = [signal]

    def _add_signal_to_sim_table(self, signal: Signal) -> None:
        """
        Добавление сигнала в таблицу СиМ
        :param signal: Сигнал для добавления в таблицу
        :return: None
        """
        column_names: List[str] = ['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF', 'FULL_NAME_RUS', 'NAME_RUS',
                                   'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL',
                                   'CABINET', 'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam', 'KKSp',
                                   'LOCATION_MP', 'SCHEMA']
        template: str
        if signal.module == '1691':
            template = ''
        else:
            uncommon_template: [UncommonTemplate, None] = None
            if self._options.uncommon_templates is not None:
                uncommon_template = next(item for item in self._options.uncommon_templates if
                                         item.signal_kks == signal.kks and item.signal_part == signal.part)
            template: Union[str, None] = f'{signal.object_typ}_{signal.module}' \
                if uncommon_template is None else uncommon_template.template

        channel: int
        if signal.module == '1623' and signal.object_typ != 'SW':
            channel = signal.channel + 50
        else:
            channel = signal.channel
        values: List[str] = [signal.object_typ, signal.kks, signal.part, signal.module, signal.rednd_intf,
                             signal.full_name_rus, signal.name_rus, signal.full_name_eng, signal.name_eng,
                             signal.min, signal.max, signal.units_rus, signal.units_eng, signal.in_level,
                             signal.cabinet, signal.slot_mp, channel, signal.connection, signal.sensr_typ,
                             signal.cat_nam, signal.kksp, signal.location_mp, template]
        self._access_base.insert_row(table_name=self._options.sim_table_name,
                                     column_names=column_names,
                                     values=values)

    def _add_signal_to_iec_table(self, signal: Signal, mms_generator: MMSGenerator) -> None:
        """
        Добавление сигнала в таблицу МЭК
        :param signal: Сигнал (запись в базе)
        :param mms_generator: Экземпляр класса генератора MMS адресов
        :return: None
        """
        column_names: List[str] = ['KKS', 'PART', 'KKSp', 'MODULE', 'REDND_INTF', 'CABINET', 'SLOT_MP', 'LOCATION_MP',
                                   'FULL_NAME_RUS', 'NAME_RUS', 'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS',
                                   'UNITS_ENG', 'SENSR_TYPE', 'AREA', 'DNAME', 'IP', 'IED_NAME', 'MMS', 'MMS_POS',
                                   'MMS_COM']
        ied_name: str = 'IED_' + signal.kksp.replace('-', '_')
        area: str = self._access_base.retrieve_data('TPTS', ['AREA'], ['CABINET'], [signal.cabinet])[0]['AREA']
        ip: str = self._access_base.retrieve_data('[Network data]', ['IP'], ['KKSp'], [signal.kksp])[0]['IP']
        mms_path: str = mms_generator.get_mms(signal.kks, signal.part)
        mms: str = ''
        mms_pos: str = ''
        mms_com: str = ''
        if signal.part.upper().startswith('XL') or signal.part.startswith('XA'):
            mms_com = mms_path
        elif signal.part.upper().startswith('XB'):
            mms_pos = mms_path
        else:
            mms = mms_path
        values: List[str] = [signal.kks, signal.part, signal.kksp, signal.module, signal.rednd_intf, signal.cabinet,
                             signal.slot_mp, signal.location_mp, signal.full_name_rus, signal.name_rus,
                             signal.full_name_eng, signal.name_eng, signal.min, signal.max, signal.units_rus,
                             signal.units_eng, signal.sensr_typ, area, signal.dname, ip, ied_name, mms, mms_pos,
                             mms_com]

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
        key_words: List = ['вкл', 'откл', 'замкн', 'разомкн', 'ввод', 'вывод', 'введ',
                           'close', 'trip', 'input', 'output', 'discon']
        key_word: Union[str, None] = next((key for key in key_words if key.upper() in signal_name.upper()), None)
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
            logging.error('')
            raise Exception('SignalNameCorrectionFailed')
        return out_string

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
        ProgressBar.config(max_value=max_value, step=1, prefix='Обработка таблиц', suffix='Завершено', length=50)
        kksp_list: List[str] = self._get_kksp_list()
        for kksp in kksp_list:
            self._generate_table_for_kksp(kksp=kksp)
        logging.info('Завершено.')

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
