import re
from typing import List, Dict, Union, Set

from tools.utils.sql_utils import SQLUtils
from dataclasses import dataclass


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class GenerateTableOptions:
    path: str
    network_data_table_name: str
    controller_data_table_name: str
    aep_table_name: str
    sim_table_name: str
    iec_table_name: str
    dps_signals: List['DPSSignal']
    bsc_signals: List['BSCSignal']
    skip_duplicate_prefix: List[str]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DPSSignal:
    signal_part: Union[str, None]
    signals_part_dupl: List[str]
    command_part: Union[str, None]
    command_part_dupl: List[str]

    def is_command(self, value: str) -> bool:
        return value.upper() in (command_part.upper() for command_part in self.command_part_dupl)

    def is_signal(self, value: str) -> bool:
        return value.upper() in (signal_part.upper() for signal_part in self.signals_part_dupl)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class BSCSignal:
    signal_part: str
    command_part: str
    command_part_dupl: List[str]

    def is_command(self, value: str) -> bool:
        return value.upper() in (command_part.upper() for command_part in self.command_part_dupl)

    def is_signal(self, value: str) -> bool:
        return value.upper() == self.signal_part


@dataclass(init=False, repr=False, eq=False, order=False, frozen=False)
class Signal:
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


class GenerateTables:
    _options: 'GenerateTableOptions'
    _access_base: SQLUtils.Connection

    class MMSGenerator:
        sps_index: int
        spc_index: int
        dps_index: int
        mv_index: int
        bsc_index: int
        ied_name: str

        dps_container: Dict[DPSSignal, Dict[str, str]]
        bsc_container: Dict[BSCSignal, Dict[str, str]]

        MV_PREFIX = 'Device/GGIO1.AnIn'
        MV_POSTFIX = '.mag.f'

        SPS_PREFIX = 'Device/GGIO1.Alm'
        SPS_POSTFIX = '.stVal'

        SPC_PREFIX = 'Device/GGIO1.SPCSO'
        SPC_POSTFIX = '.Oper'

        BSC_PREFIX = 'Device/ATCC'
        BSC_COMMAND_POSTFIX = '.TapChg.Oper'
        BSC_POS_POSTFIX = 'TapChg.valWTr'

        DPS_PREFIX = 'Device/GGIO1.DPCSO'
        DPS_COMMAND_POSTFIX = '.Oper'
        DPS_POS_POSTFIX = '.stVal'

        # DPS_CB_CONST: List[str] = ['XB01', 'XB02', 'XL01', 'XL02']
        # DPS_ALT_CONST: List[str] = ['XB21', 'XB22', 'XL21', 'XL22']
        # BSC_CONST: List[str] = ['XB10', 'XL11', 'XL12']

        def __init__(self, kksp: str, dps_signals: List[DPSSignal],
                     bsc_signals: List[BSCSignal]):
            self.sps_index = 0
            self.spc_index = 0
            self.dps_index = 0
            self.mv_index = 0
            self.bsc_index = 0
            self.ied_name = 'IED_' + kksp.replace('-', '_')
            self.dps_container = {}
            self.bsc_container = {}
            for dps_signal in dps_signals:
                self.dps_container[dps_signal] = {}
            for bsc_signal in bsc_signals:
                self.bsc_container[bsc_signal] = {}

        def get_mms(self, kks: str, part: str):
            for dps_signal in self.dps_container:
                if dps_signal.is_signal(part) or dps_signal.is_command(part):
                    postfix: str = self.DPS_COMMAND_POSTFIX if dps_signal.is_command(part) else \
                        self.DPS_POS_POSTFIX
                    if kks not in self.dps_container[dps_signal]:
                        self.dps_index += 1
                        self.dps_container[dps_signal][kks] = self.DPS_PREFIX + str(self.dps_index)
                    return self.ied_name + self.dps_container[dps_signal][kks] + postfix

            for bsc_signal in self.bsc_container:
                if bsc_signal.is_signal(part) or bsc_signal.is_command(part):
                    postfix: str = self.BSC_COMMAND_POSTFIX if bsc_signal.is_command(part) else \
                        self.BSC_POS_POSTFIX
                    if kks not in self.bsc_container[bsc_signal]:
                        self.bsc_index += 1
                        self.bsc_container[bsc_signal][kks] = self.BSC_PREFIX + str(self.bsc_index)
                    return self.ied_name + self.bsc_container[bsc_signal][kks] + postfix

            if part.upper().startswith('XL'):
                self.sps_index += 1
                return self.ied_name + self.SPC_PREFIX + str(self.spc_index) + self.SPC_POSTFIX

            if part.upper().startswith('XQ'):
                self.mv_index += 1
                return self.ied_name + self.MV_PREFIX + str(self.mv_index) + self.MV_POSTFIX

            self.sps_index += 1
            return self.ied_name + self.SPS_PREFIX + str(self.sps_index) + self.SPS_POSTFIX

    def __init__(self, options: GenerateTableOptions, access_base: SQLUtils.Connection):
        self._options = options
        self._access_base = access_base

    def _get_kksp_list(self) -> List[str]:
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

    def _generate_tables(self, kksp: str):
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
        mms_generator: GenerateTables.MMSGenerator = GenerateTables.MMSGenerator(kksp=kksp,
                                                                                 dps_signals=self._options.dps_signals,
                                                                                 bsc_signals=self._options.bsc_signals)
        for value in values:
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
                self._process_digital_signal(signal=signal, mms_generator=mms_generator)

        self._access_base.commit()

    def _process_wired_signal(self, signal: Signal, sw_container: Dict[str, List[Signal]]):
        if signal.module == '1623' and signal.object_typ.casefold() == 'SW'.casefold():
            self._process_sw_signals(sw_container=sw_container,
                                     signal=signal)
        else:
            self._add_signal_to_sim_table(signal=signal)

    def _get_parts_to_duplicate(self) -> List[str]:
        output: List[str] = []
        for dps_signal in self._options.dps_signals:
            if dps_signal.signal_part is not None:
                output.append(dps_signal.signal_part)
            if dps_signal.command_part is not None:
                output.append(dps_signal.command_part)
        for bsc_signal in self._options.bsc_signals:
            output.append(bsc_signal.command_part)
        return output

    def _get_duplicated_parts(self) -> List[str]:
        output: List[str] = []
        for dps_signal in self._options.dps_signals:
            output.extend(dps_signal.signals_part_dupl)
            output.extend(dps_signal.command_part_dupl)
        for bsc_signal in self._options.bsc_signals:
            output.extend(bsc_signal.command_part_dupl)
        return output

    def _process_digital_signal(self, signal: Signal, mms_generator: MMSGenerator):
        if signal.part in self._get_duplicated_parts():
            signal.name_rus = self._sanitizate_signal_name(signal.name_rus)
            signal.full_name_rus = self._sanitizate_signal_name(signal.full_name_rus)
            signal.name_eng = self._sanitizate_signal_name(signal.name_eng)
            signal.full_name_eng = self._sanitizate_signal_name(signal.full_name_eng)

        if signal.part in self._get_parts_to_duplicate() and \
                not any(signal.kks.upper().startswith(item.upper()) for item in self._options.skip_duplicate_prefix):
            self._duplicate_signal(signal=signal, mms_generator=mms_generator)
        else:
            self._add_signal_to_iec_table(signal=signal, mms_generator=mms_generator)
            self._add_signal_to_sim_table(signal=signal)

    def _duplicate_signal(self, signal: Signal, mms_generator: MMSGenerator):
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

    def _process_sw_signals(self, sw_container: Dict[str, List[Signal]], signal: Signal):
        if signal.kks in sw_container:
            sw_signals: List[Signal] = sw_container[signal.kks]
            if len(sw_signals) < 6:
                sw_signals.append(signal)
            if len(sw_signals) == 6:
                parts_in_container: Set[str] = {item.part for item in sw_signals}
                parts_set: Set[str] = {'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'}
                if parts_set == parts_in_container:
                    sw_signal: Signal = signal.clone()
                    sw_signal.part = 'XA01'
                    sw_signal.name_rus = self._get_common_prefix(list(map(lambda item: item.name_rus, sw_signals)))
                    sw_signal.name_eng = self._get_common_prefix(list(map(lambda item: item.name_eng, sw_signals)))
                    sw_signal.full_name_rus = self._get_common_prefix(list(map(lambda item: item.full_name_rus,
                                                                               sw_signals)))
                    sw_signal.full_name_eng = self._get_common_prefix(list(map(lambda item: item.full_name_eng,
                                                                               sw_signals)))
                    self._add_signal_to_sim_table(sw_signal)
                    del sw_container[signal.kks]
                else:
                    print('Неверный набор сигналов в группе SW')
                    raise Exception('SignalGroupError')
        else:
            sw_container[signal.kks] = [signal]

    def _add_signal_to_sim_table(self, signal: Signal):
        column_names: List[str] = ['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF', 'FULL_NAME_RUS', 'NAME_RUS',
                                   'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL',
                                   'CABINET', 'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam', 'KKSp',
                                   'LOCATION_MP', 'SCHEMA']
        schema: Union[str, None] = '' if signal.module == '1691' else f'{signal.object_typ}_{signal.module}'
        values: List[str] = [signal.object_typ, signal.kks, signal.part, signal.module, signal.rednd_intf,
                             signal.full_name_rus, signal.name_rus, signal.full_name_eng, signal.name_eng,
                             signal.min, signal.max, signal.units_rus, signal.units_eng, signal.in_level,
                             signal.cabinet, signal.slot_mp, signal.channel, signal.connection, signal.sensr_typ,
                             signal.cat_nam, signal.kksp, signal.location_mp, schema]
        self._access_base.insert_row(table_name=self._options.sim_table_name,
                                     column_names=column_names,
                                     values=values)

    def _add_signal_to_iec_table(self, signal: Signal, mms_generator: 'GenerateTables.MMSGenerator'):
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
        if signal.part.upper().startswith('XL'):
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
            raise Exception('SignalNameCorrectionFailed')
        return out_string

    def generate(self):
        self._access_base.clear_table(self._options.sim_table_name)
        self._access_base.clear_table(self._options.iec_table_name)

        kksp_list: List[str] = self._get_kksp_list()
        for kksp in kksp_list:
            self._generate_tables(kksp=kksp)

    @staticmethod
    def run(options: GenerateTableOptions):
        with SQLUtils.Connection.connect_to_mdb(options.path) as access_base:
            generate_class: GenerateTables = GenerateTables(options=options,
                                                            access_base=access_base)
            generate_class.generate()
