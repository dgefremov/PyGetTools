import logging
from dataclasses import dataclass

from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DPCSignal:
    """
    Класс хранения двухпозицонного сигнала
    """
    signal_part: str | None
    signal_part_dupl: tuple[str, str] | None
    command_part: str | None
    command_part_dupl: tuple[str, str] | None

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
    command_part_dupl: tuple[str, str] | None

    def is_command(self, value: str) -> bool:
        return value.upper() in (command_part.upper() for command_part in self.command_part_dupl)

    def is_signal(self, value: str) -> bool:
        return value.upper() == self.signal_part


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
    path: str
    iec_table_name: str
    ied_table_name: str
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

    dpc_container: dict[DPCSignal, dict[str, str]]
    bsc_container: dict[BSCSignal, dict[str, str]]
    dataset_container: list[DatasetDescription]
    dataset_descriptions: DatasetDescriptionList | None

    MV_PREFIX = 'Device/GGIO1.AnIn'
    MV_POSTFIX = '.mag.f'

    SPS_PREFIX = 'Device/GGIO1.Alm'
    SPS_POSTFIX = '.stVal'

    SPC_PREFIX = 'Device/GGIO1.SPCSO'
    SPC_POSTFIX = '.Oper'

    BSC_PREFIX = 'Device/ATCC'
    BSC_COMMAND_POSTFIX = '.TapChg.Oper'
    BSC_POS_POSTFIX = '.TapChg.valWTr.posVal'

    DPS_PREFIX = 'Device/GGIO1.DPCSO'
    DPS_COMMAND_POSTFIX = '.Oper'
    DPS_POS_POSTFIX = '.stVal'

    def __init__(self, kksp: str, dpc_signals: list[DPCSignal],
                 bsc_signals: list[BSCSignal], dataset_descriptions: DatasetDescriptionList):
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
        for value in values:
            kks: str = value['KKS']
            part: str = value['PART']
            mms_path: str = mms_generator.get_mms(kks=kks,
                                                  part=part)
            mms: str = ''
            mms_pos: str = ''
            mms_com: str = ''
            if part.startswith('XL') or part.startswith('XA'):
                mms_com = mms_path
            elif part.upper().startswith('XB'):
                mms_pos = mms_path
            else:
                mms = mms_path
            self._access_base.update_field(table_name=self._options.iec_table_name,
                                           fields=['MMS', 'MMS_POS', 'MMS_COM'],
                                           values=[mms, mms_pos, mms_com],
                                           key_names=['KKS', 'PART'],
                                           key_values=[kks, part])
            ProgressBar.update_progress()
        if self._options.datasets is not None and len(mms_generator.dataset_container) > 0:
            self._add_ied_record(mms_generator=mms_generator)
        self._access_base.commit()

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
                                         values=[mms_generator.ied_name, dataset_list, rb_master_list, rb_slave_list])

    def _fill_mms(self) -> None:
        """
        Основная функция генерации таблиц
        :return: None
        """
        max_value: int = self._access_base.get_row_count(self._options.iec_table_name)
        logging.info('Заполнение адресов MMS...')
        ProgressBar.config(max_value=max_value, step=1, prefix='Обработка MMS адресов', suffix='Завершено', length=50)
        kksp_list: list[str] = self._get_kksp_list()
        for kksp in kksp_list:
            self._generate_mms_for_kksp(kksp=kksp)

        logging.info('Завершено')

    @staticmethod
    def run(options: FillMMSAddressOptions) -> None:
        """
        Запуск скрипта
        :param options: Настройки для скрипта
        :return: None
        """
        logging.info('Запуск скрипта...')
        with Connection.connect_to_mdb(options.path) as access_base:
            fill_mms_class: FillMMSAdress = FillMMSAdress(options=options,
                                                          access_base=access_base)
            fill_mms_class._fill_mms()
        logging.info('Выпонение завершено.')
