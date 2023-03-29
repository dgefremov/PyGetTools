import logging
from dataclasses import dataclass

from tools.utils.progress_utils import ProgressBar
from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DPCSignal:
    """
    Класс хранения двухпозицонного сигнала
    """
    signal_part: tuple[str, str] | None
    command_part: tuple[str, str] | None

    def is_command(self, value: str) -> bool:
        if self.command_part is None:
            return False
        return value.upper() in (command_part.upper() for command_part in self.command_part)

    def is_signal(self, value: str) -> bool:
        if self.signal_part is None:
            return False
        return value.upper() in (signal_part.upper() for signal_part in self.signal_part)

    def get_signals_num(self):
        signals: int = 0
        if self.signal_part is not None:
            signals += 2
        if self.command_part is not None:
            signals += 2
        return signals


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BSCSignal:
    """
    Класс хранения сигнала РПН типа BSC
    """
    signal_part: str
    command_part: tuple[str, str]

    def is_command(self, value: str) -> bool:
        return value.upper() in (command_part.upper() for command_part in self.command_part)

    def is_signal(self, value: str) -> bool:
        return value.upper() == self.signal_part

    def get_signals_num(self):
        if self.command_part is not None:
            return 3
        return 1


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
    spc_range: SignalRange | None = None
    sps_range: SignalRange | None = None
    dpc_range: SignalRange | None = None
    bsc_range: SignalRange | None = None
    mv_range: SignalRange | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=False)
class DatasetDescriptionList:
    """
    Класс хранения списков Dataset
    """
    dataset_list: list[DatasetDescription]

    def get_by_spc_index(self, spc_index) -> DatasetDescription | None:
        return next(
            (dataset for dataset in self.dataset_list if dataset.spc_range is not None and dataset.spc_range.low <=
             spc_index <= dataset.spc_range.high),
            None)

    def get_by_sps_index(self, sps_index) -> DatasetDescription | None:
        return next(
            (dataset for dataset in self.dataset_list if dataset.sps_range is not None and dataset.sps_range.low <=
             sps_index <= dataset.sps_range.high),
            None)

    def get_by_dpc_index(self, dpc_index) -> DatasetDescription | None:
        return next(
            (dataset for dataset in self.dataset_list if dataset.dpc_range is not None and dataset.dpc_range.low <=
             dpc_index <= dataset.dpc_range.high),
            None)

    def get_by_bsc_index(self, bsc_index) -> DatasetDescription | None:
        return next(
            (dataset for dataset in self.dataset_list if dataset.bsc_range is not None and dataset.bsc_range.low <=
             bsc_index <= dataset.bsc_range.high),
            None)

    def get_by_mv_index(self, mv_index) -> DatasetDescription | None:
        return next(
            (dataset for dataset in self.dataset_list if dataset.mv_range is not None and dataset.mv_range.low <=
             mv_index <= dataset.mv_range.high),
            None)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FillMMSAddressOptions:
    iec_table_name: str
    ied_table_name: str
    mms_table_name: str
    dpc_signals: list[DPCSignal]
    bsc_signals: list[BSCSignal]
    datasets: None | DatasetDescriptionList = None


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
    kksp: str
    filename: str

    dpc_signals: list[DPCSignal]
    bsc_signals: list[BSCSignal]

    dpc_container: dict[str, list[str]]
    bsc_container: dict[str, list[str]]
    dataset_container: list[DatasetDescription]
    dataset_descriptions: DatasetDescriptionList

    MV_PREFIX = 'Device/GGIO1.AnIn'
    MV_POSTFIX = '.mag.f'

    SPS_PREFIX = 'Device/GGIO1.Alm'
    SPS_POSTFIX = '.stVal'

    SPC_PREFIX = 'Device/GGIO1.SPCSO'
    SPC_POSTFIX = '.Oper.ctlVal'

    BSC_PREFIX = 'Device/ATCC'
    BSC_COMMAND_POSTFIX = '.TapChg.Oper.ctlVal'
    BSC_POS_POSTFIX = '.TapChg.valWTr.posVal'

    DPC_PREFIX = 'Device/GGIO1.DPCSO'
    DPS_COMMAND_POSTFIX = '.Oper.ctlVal'
    DPC_POS_POSTFIX = '.stVal'

    def __init__(self, kksp: str, dpc_signals: list[DPCSignal],
                 bsc_signals: list[BSCSignal], dataset_descriptions: DatasetDescriptionList):
        self.sps_index = 0
        self.spc_index = 0
        self.dpc_index = 0
        self.mv_index = 0
        self.bsc_index = 0
        self.ied_name = 'IED_' + kksp.replace('-', '_')
        self.kksp = kksp
        self.dpc_signals = dpc_signals
        self.bsc_signals = bsc_signals
        self.dpc_container = {}
        self.bsc_container = {}
        self.dataset_container = []
        self.dataset_descriptions = dataset_descriptions
        self.filename = kksp

    def get_mms_for_dpc(self, kks: str, part: str) -> list[tuple[str, str, str]] | None:
        # Здесь обрабатываются только полные DPC сигналы
        for dpc_signal in self.dpc_signals:
            if dpc_signal.is_signal(part) or dpc_signal.is_command(part):
                if kks not in self.dpc_container:
                    self.dpc_container[kks] = [part]
                else:
                    self.dpc_container[kks].append(part)
                break
        for dpc_signal in self.dpc_signals:
            if dpc_signal.signal_part is None or dpc_signal.command_part is None:
                continue
            if set(dpc_signal.signal_part + dpc_signal.command_part).issubset(set(self.dpc_container[kks])):
                if set(dpc_signal.signal_part + dpc_signal.command_part) == set(self.dpc_container[kks]):
                    del self.dpc_container[kks]
                else:
                    self.dpc_container[kks] = list(set(self.dpc_container[kks]) -
                                                   set(dpc_signal.signal_part + dpc_signal.command_part))
                self.dpc_index += 1
                dataset: DatasetDescription | None = self.dataset_descriptions.get_by_dpc_index(self.dpc_index)
                if dataset is None:
                    logging.error(f'Не найден Dataset для DPC {self.bsc_index}')
                    raise Exception('DatasetError')
                if not self.dataset_container.__contains__(dataset):
                    self.dataset_container.append(dataset)
                command_address: str = self.ied_name + self.DPC_PREFIX + str(
                    self.dpc_index) + self.DPS_COMMAND_POSTFIX
                signal_address: str = self.ied_name + self.DPC_PREFIX + str(self.dpc_index) + self.DPC_POS_POSTFIX
                mms_addresses: list[tuple[str, str, str]] = [(kks, dpc_signal.signal_part[0], signal_address),
                                                             (kks, dpc_signal.signal_part[1], signal_address),
                                                             (kks, dpc_signal.command_part[0], command_address),
                                                             (kks, dpc_signal.command_part[1], command_address)]
                return mms_addresses
        return None

    def get_mms_for_bsc(self, kks: str, part: str) -> list[tuple[str, str, str]] | None:
        for bsc_signal in self.bsc_signals:
            if bsc_signal.is_signal(part) or bsc_signal.is_command(part):
                if kks not in self.bsc_container:
                    self.bsc_container[kks] = [part]
                    return None
                else:
                    self.bsc_container[kks].append(part)
                if set([bsc_signal.signal_part] + list(bsc_signal.command_part)).issubset(set(self.bsc_container[kks])):
                    if set([bsc_signal.signal_part] + list(bsc_signal.command_part)) == set(self.bsc_container[kks]):
                        del self.bsc_container[kks]
                    else:
                        self.bsc_container[kks] = list(set(self.bsc_container[kks]) -
                                                       set([bsc_signal.signal_part] + list(bsc_signal.command_part)))
                    self.bsc_index += 1
                    dataset: DatasetDescription | None = self.dataset_descriptions.get_by_bsc_index(self.bsc_index)
                    if dataset is None:
                        logging.error(f'Не найден Dataset для BSC {self.bsc_index}')
                        raise Exception('DatasetError')
                    if not self.dataset_container.__contains__(dataset):
                        self.dataset_container.append(dataset)
                    command_adress: str = self.ied_name + self.BSC_PREFIX + str(
                        self.bsc_index) + self.BSC_COMMAND_POSTFIX
                    signal_address: str = self.ied_name + self.BSC_PREFIX + str(self.bsc_index) + self.BSC_POS_POSTFIX
                    return [(kks, bsc_signal.signal_part, signal_address),
                            (kks, bsc_signal.command_part[0], command_adress),
                            (kks, bsc_signal.command_part[1], command_adress)]
        return None

    def get_mms_for_spc(self, kks: str, part: str) -> list[tuple[str, str, str]]:
        self.spc_index += 1
        dataset: DatasetDescription = self.dataset_descriptions.get_by_spc_index(self.spc_index)
        if dataset is None:
            logging.error(f'Не найден Dataset для SPC {self.spc_index}')
            raise Exception('DatasetError')
        if not self.dataset_container.__contains__(dataset):
            self.dataset_container.append(dataset)
        return [(kks, part, self.ied_name + self.SPC_PREFIX + str(self.spc_index) + self.SPC_POSTFIX)]

    def get_mms_for_mv(self, kks: str, part: str) -> list[tuple[str, str, str]]:
        self.mv_index += 1
        if self.dataset_descriptions is not None:
            dataset: DatasetDescription = self.dataset_descriptions.get_by_mv_index(self.mv_index)
            if dataset is None:
                logging.error(f'Не найден Dataset для MV {self.mv_index}')
                raise Exception('DatasetError')
            if not self.dataset_container.__contains__(dataset):
                self.dataset_container.append(dataset)
        return [(kks, part, self.ied_name + self.MV_PREFIX + str(self.mv_index) + self.MV_POSTFIX)]

    def get_mms_for_sps(self, kks: str, part: str) -> list[tuple[str, str, str]]:
        self.sps_index += 1
        if self.dataset_descriptions is not None:
            dataset: DatasetDescription = self.dataset_descriptions.get_by_sps_index(self.sps_index)
            if dataset is None:
                logging.error(f'Не найден Dataset для SPS {self.sps_index}')
                raise Exception('DatasetError')
            if not self.dataset_container.__contains__(dataset):
                self.dataset_container.append(dataset)
        return [(kks, part, self.ied_name + self.SPS_PREFIX + str(self.sps_index) + self.SPS_POSTFIX)]

    def get_mms(self, kks: str, part: str) -> list[tuple[str, str, str]] | None:
        if any(dpc_signal.is_signal(part) or dpc_signal.is_command(part) for dpc_signal in self.dpc_signals):
            return self.get_mms_for_dpc(kks=kks,
                                        part=part)
        if any(bsc_signal.is_signal(part) or bsc_signal.is_command(part) for bsc_signal in self.bsc_signals):
            return self.get_mms_for_bsc(kks=kks,
                                        part=part)
        if part.upper().startswith('XL') or part.upper().startswith('XA'):
            return self.get_mms_for_spc(kks=kks,
                                        part=part)
        if part.upper().startswith('XQ'):
            return self.get_mms_for_mv(kks=kks,
                                       part=part)
        return self.get_mms_for_sps(kks=kks,
                                    part=part)

    def add_undubled_signals(self) -> list[tuple[str, str, str]]:
        mms_addresses: list[tuple[str, str, str]] = []
        # Сначала ищем ККС в котором только команды
        for dpc_signal in self.dpc_signals:
            keys: list[str] = list(self.dpc_container)
            # Только для команд у которых есть и команды и сигналы
            if dpc_signal.signal_part is None or dpc_signal.command_part is None:
                continue
            commands_parts_set: set[str] = {part for part in dpc_signal.command_part}
            signals_parts_set: set[str] = {part for part in dpc_signal.signal_part}
            removed_keys: list[str] = []
            for kks_with_commands in keys:
                if kks_with_commands in removed_keys:
                    continue
                if commands_parts_set.issubset(set(self.dpc_container[kks_with_commands])):
                    # дальше пытаемся найти ККС в котором есть сигналы для данных команд
                    for kks_with_signals in keys:
                        if kks_with_signals in removed_keys:
                            continue
                        if signals_parts_set.issubset(set(self.dpc_container[kks_with_signals])) \
                                and kks_with_signals[:6] == kks_with_commands[:6]:
                            if signals_parts_set == set(self.dpc_container[kks_with_signals]):
                                del self.dpc_container[kks_with_signals]
                            else:
                                self.dpc_container[kks_with_signals] = list(set(self.dpc_container[kks_with_signals])
                                                                            - signals_parts_set)
                            if commands_parts_set == set(self.dpc_container[kks_with_commands]):
                                del self.dpc_container[kks_with_commands]
                            else:
                                self.dpc_container[kks_with_commands] = list(set(self.dpc_container[kks_with_commands])
                                                                             - commands_parts_set)
                            removed_keys.append(kks_with_signals)
                            removed_keys.append(kks_with_commands)
                            self.dpc_index += 1
                            dataset: DatasetDescription | None = self.dataset_descriptions.get_by_dpc_index(
                                self.dpc_index)
                            if dataset is None:
                                logging.error(f'Не найден Dataset для DPC {self.bsc_index}')
                                raise Exception('DatasetError')
                            if not self.dataset_container.__contains__(dataset):
                                self.dataset_container.append(dataset)
                            self.dpc_index += 1
                            command_adress: str = self.ied_name + self.DPC_PREFIX + str(
                                self.dpc_index) + self.DPS_COMMAND_POSTFIX
                            signal_address: str = self.ied_name + self.DPC_PREFIX + str(
                                self.dpc_index) + self.DPC_POS_POSTFIX

                            mms_addresses.append((kks_with_signals, dpc_signal.signal_part[0], signal_address))
                            mms_addresses.append((kks_with_signals, dpc_signal.signal_part[1], signal_address))
                            mms_addresses.append((kks_with_commands, dpc_signal.command_part[0], command_adress))
                            mms_addresses.append((kks_with_commands, dpc_signal.command_part[1], command_adress))
            if len(self.dpc_container) == 0:
                return mms_addresses
        # Следующий шаг: ищем ККС в которых есть только сигналы
        for dpc_signal in self.dpc_signals:
            keys: list[str] = list(self.dpc_container)
            removed_keys: list[str] = []
            if dpc_signal.command_part is not None:
                continue
            signals_parts_set: set[str] = {part for part in dpc_signal.signal_part}
            for kks_with_signals in keys:
                if kks_with_signals in removed_keys:
                    continue
                if set(signals_parts_set).issubset(set(self.dpc_container[kks_with_signals])):
                    if set(self.dpc_container[kks_with_signals]) == signals_parts_set:
                        del self.dpc_container[kks_with_signals]
                    else:
                        self.dpc_container[kks_with_signals] = list(set(self.dpc_container[kks_with_signals]) -
                                                                    signals_parts_set)
                    removed_keys.append(kks_with_signals)
                    self.dpc_index += 1
                    dataset: DatasetDescription | None = self.dataset_descriptions.get_by_dpc_index(
                        self.dpc_index)
                    if dataset is None:
                        logging.error(f'Не найден Dataset для DPC {self.bsc_index}')
                        raise Exception('DatasetError')
                    if not self.dataset_container.__contains__(dataset):
                        self.dataset_container.append(dataset)
                    signal_address: str = self.ied_name + self.DPC_PREFIX + str(
                        self.dpc_index) + self.DPC_POS_POSTFIX

                    mms_addresses.append((kks_with_signals, dpc_signal.signal_part[0], signal_address))
                    mms_addresses.append((kks_with_signals, dpc_signal.signal_part[1], signal_address))
        # Все оставшиеся сигналы классифицируются как SPC\SPS
        for kks in self.dpc_container:
            part_list: list[str] = self.dpc_container[kks]
            for part in part_list:
                if any(dpc_signal.is_signal(part) for dpc_signal in self.dpc_signals):
                    self.sps_index += 1
                    mms_addresses.append((kks, part, self.ied_name + self.SPS_PREFIX + str(self.sps_index) +
                                          self.SPS_POSTFIX))
                else:
                    self.spc_index += 1
                    mms_addresses.append((kks, part, self.ied_name + self.SPC_PREFIX + str(self.spc_index) +
                                          self.SPC_POSTFIX))
        return mms_addresses


class FillMMSAdress:
    _options: FillMMSAddressOptions
    _access_base: Connection

    def __init__(self, options: FillMMSAddressOptions, access_base: Connection):
        self._options = options
        self._access_base = access_base

    def _get_kksp_list(self) -> list[str]:
        """
        Функция загрузки списка KKSp из БД
        :return: Список KKSp
        """
        values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.iec_table_name,
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

    def _write_mms(self, kks: str, part: str, mms_address: str, ied_name: str):
        mms: str = ''
        mms_pos: str = ''
        mms_com: str = ''
        if part.startswith('XL') or part.startswith('XA'):
            mms_com = mms_address
        elif part.upper().startswith('XB'):
            mms_pos = mms_address
        else:
            mms = mms_address
        self._access_base.update_field(table_name=self._options.iec_table_name,
                                       fields=['MMS', 'MMS_POS', 'MMS_COM', 'IED_NAME'],
                                       values=[mms, mms_pos, mms_com, ied_name],
                                       key_names=['KKS', 'PART'],
                                       key_values=[kks, part])

    def _generate_mms_for_kksp(self, kksp: str):
        mms_generator: MMSGenerator = MMSGenerator(kksp=kksp,
                                                   dpc_signals=self._options.dpc_signals,
                                                   bsc_signals=self._options.bsc_signals,
                                                   dataset_descriptions=self.
                                                   _options.datasets)
        values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.iec_table_name,
                                                                       fields=['KKS', 'PART'],
                                                                       key_names=['KKSp'],
                                                                       key_values=[kksp])
        mms_addresses: list[tuple[str, str, str]] = []
        for value in values:
            kks: str = value['KKS']
            part: str = value['PART']
            result: tuple[str, str, str] | None = mms_generator.get_mms(kks=kks,
                                                                        part=part)
            if result is not None:
                mms_addresses += result
        mms_addresses += mms_generator.add_undubled_signals()
        ied_name: str = 'IED_' + kksp.replace('-', '_')
        for kks, part, mms_address in mms_addresses:
            self._write_mms(kks=kks,
                            part=part,
                            mms_address=mms_address,
                            ied_name=ied_name)
            ProgressBar.update_progress()
        if self._options.datasets is not None and len(mms_generator.dataset_container) > 0:
            self._add_emulator_ied_record(mms_generator=mms_generator)
        self._access_base.commit()

    def _add_emulator_ied_record(self, mms_generator: MMSGenerator) -> None:
        """
        Функция добавления (редактирования) записи в таблице IED
        :param mms_generator: Экземпляр класса генератора MMS сигналов (в нем хранятся Dataset)
        :return: None
        """
        dataset_list: str = ';'.join([dataset.path for dataset in mms_generator.dataset_container])
        rb_master_list: str = ';'.join([dataset.rcb_main for dataset in mms_generator.dataset_container])
        rb_slave_list: str = ';'.join([dataset.rcb_res for dataset in mms_generator.dataset_container])
        self._access_base.insert_row(table_name=self._options.ied_table_name,
                                     column_names=['IED_NAME', 'DATASET', 'RB_MASTER', 'RB_SLAVE', 'KKSp', 'ICD_PATH',
                                                   'EMULATOR'],
                                     values=[mms_generator.ied_name, dataset_list, rb_master_list, rb_slave_list,
                                             mms_generator.kksp, mms_generator.filename, True])

    def _add_real_ied_record(self, kksp: str, ied_name: str, file_name: str, dataset_list: list[str],
                             rb_master_list: list[str], rb_slave_list: list[str]) -> None:
        dataset_list: str = ';'.join(dataset_list)
        rb_master_list: str = ';'.join(rb_master_list)
        rb_slave_list: str = ';'.join(rb_slave_list)
        self._access_base.insert_row(table_name=self._options.ied_table_name,
                                     column_names=['IED_NAME', 'DATASET', 'RB_MASTER', 'RB_SLAVE', 'KKSp', 'ICD_PATH',
                                                   'EMULATOR'],
                                     values=[ied_name, dataset_list, rb_master_list, rb_slave_list,
                                             kksp, file_name, False])

    def _is_emulator(self, kksp: str) -> bool:
        values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.mms_table_name,
                                                                       fields=['IED_NAME'],
                                                                       key_names=['KKSp'],
                                                                       key_values=[kksp],
                                                                       uniq_values=True)
        if len(values) == 0:
            return True
        if len(values) == 1:
            return False
        raise Exception(f'Множественные значения в таблице {self._options.ied_table_name} для kksp {kksp}')

    def _copy_mms_for_kksp(self, kksp: str):
        mms_values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.mms_table_name,
                                                                           fields=['KKS', 'PART', 'MMS_address',
                                                                                   'Dataset', 'Report_Master',
                                                                                   'Report_Slave', 'IED_NAME',
                                                                                   'Filename'],
                                                                           key_names=['KKSp'],
                                                                           key_values=[kksp])
        mms_storage: dict[tuple[str, str], str] = dict([((value['KKS'], value['PART']), value['MMS_address'])
                                                        for value in mms_values])
        signal_values: list[dict[str, str]] = self._access_base.retrieve_data(table_name=self._options.iec_table_name,
                                                                              fields=['KKS', 'PART'],
                                                                              key_names=['KKSp'],
                                                                              key_values=[kksp])
        dataset_list: list[str] = list({value['Dataset'] for value in mms_values if value['Dataset'] is not None
                                        and value['Dataset'] != ''})
        report_master_list: list[str] = list({value['Report_Master'] for value in mms_values if value['Report_Master']
                                              is not None and value['Report_Master'] != ''})
        report_slave_list: list[str] = list({value['Report_Slave'] for value in mms_values if value['Report_Slave']
                                             is not None and value['Report_Slave'] != ''})
        ied_name_list: list[str] = list({value['IED_NAME'] for value in mms_values})
        if len(ied_name_list) > 1:
            logging.error(f'Для одного kksp {kksp} найдено несколько имен IED')
            raise Exception('IedNameError')
        filename_list: list[str] = list({value['Filename'] for value in mms_values})
        if len(filename_list) > 1:
            logging.error(f'Для одного IED {ied_name_list[0]} найдено несколько имен файлов')
            raise Exception('CidFileNameError')
        self._add_real_ied_record(ied_name=ied_name_list[0],
                                  kksp=kksp,
                                  file_name=filename_list[0],
                                  dataset_list=dataset_list,
                                  rb_master_list=report_master_list,
                                  rb_slave_list=report_slave_list)

        for signal in signal_values:
            kks: str = signal['KKS']
            part: str = signal['PART']
            mms: str | None = mms_storage.get((kks, part), None)
            ied_name: str = ied_name_list[0]
            if mms == '' or mms is None:
                logging.info(f'Для KKSp {kksp} для сигнала {kks}_{part} не найден адрес в таблице '
                             f'{self._options.mms_table_name}')
                if mms is None:
                    mms = ''
            self._write_mms(kks=kks,
                            part=part,
                            mms_address=mms,
                            ied_name=ied_name)
            ProgressBar.update_progress()
        self._access_base.commit()

    def _fill_mms(self) -> None:
        """
        Основная функция генерации таблиц
        :return: None
        """
        max_value: int = self._access_base.get_row_count(self._options.iec_table_name)
        logging.info('Очистка таблицы IED...')
        self._access_base.clear_table(table_name=self._options.ied_table_name)
        logging.info('Завершено.')
        logging.info('Заполнение адресов MMS...')
        ProgressBar.config(max_value=max_value, step=1, prefix='Обработка MMS адресов', suffix='Завершено', length=50)
        kksp_list: list[str] = self._get_kksp_list()
        for kksp in kksp_list:
            if self._is_emulator(kksp=kksp):
                self._generate_mms_for_kksp(kksp=kksp)
            else:
                self._copy_mms_for_kksp(kksp=kksp)

        logging.info('Завершено')

    @staticmethod
    def run(options: FillMMSAddressOptions, base_path: str) -> None:
        logging.info('Запуск скрипта "Заполнение MMS адресов"...')
        with Connection.connect_to_mdb(base_path=base_path) as access_base:
            fill_mms_class: FillMMSAdress = FillMMSAdress(options=options,
                                                          access_base=access_base)
            fill_mms_class._fill_mms()
        logging.info('Выпонение скрипта "Заполнение MMS адресов" завершено.')
        logging.info('')
