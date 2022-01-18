from typing import List, Dict, Union

from tools.utils.sql_utils import SQLUtils
from dataclasses import dataclass


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class GenerateTableOptions:
    path: str
    network_data_table_name: str
    controller_data_table_name: str
    aep_table_name: str
    sim_table_name: str
    iec_talbe_name: str


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
    units: str
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


@dataclass(init=False, repr=False, eq=False, order=False, frozen=False)
class MMSDataContainer:
    sp_index: int
    dp_index: int


def _get_kksp_list(options: GenerateTableOptions, access_base: SQLUtils.Connection) -> List[str]:
    values: List[Dict[str, str]] = access_base.retrieve_data(table_name=options.aep_table_name,
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


def _get_data_for_kksp(options: GenerateTableOptions, access_base: SQLUtils.Connection, kksp_list: List[str]):
    for kksp in kksp_list:
        values: list[dict[str, str]] = access_base.retrieve_data(table_name=options.aep_table_name,
                                                                 fields=['OBJECT_TYP', 'KKS', 'PART', 'MODULE',
                                                                          'REDND_INTF', 'FULL_NAME_RUS', 'NAME_RUS',
                                                                          'FULL_NAME_ENG', 'NAME_ENG', 'MIN', 'MAX',
                                                                          'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL',
                                                                          'CABINET', 'SLOT_MP', 'CHANNEL', 'CONNECTION',
                                                                          'SENSR_TYPE', 'CatNam', 'LOCATION_MP',
                                                                          'DNAME'],
                                                                 key_names=['KKSp'],
                                                                 key_values=[kksp])
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
            signal.units = value['UNITS_RUS']
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

            add_signal_to_sim_table(options=options, signal=signal, access_table=access_base)
        access_base.commit()


def add_signal_to_sim_table(options: GenerateTableOptions, access_table: SQLUtils.Connection, signal: Signal):
    column_names: List[str] = ['OBJECT_TYP', 'KKS', 'PART', 'MODULE', 'REDND_INTF', 'FULL_NAME_RUS', 'NAME_RUS',
                               'FULL_NAME_ENG', 'NAME_ENG', 'Min', 'Max', 'UNITS_RUS', 'UNITS_ENG', 'IN_LEVEL',
                               'CABINET', 'SLOT_MP', 'CHANNEL', 'CONNECTION', 'SENSR_TYPE', 'CatNam', 'KKSp',
                               'LOCATION_MP', 'SCHEMA']
    schema: Union[str, None] = '' if signal.module == '1691' else f'{signal.object_typ}_{signal.module}'
    values: List[str] = [signal.object_typ, signal.kks, signal.part, signal.module, signal.rednd_intf,
                         signal.full_name_rus, signal.name_rus, signal.full_name_eng, signal.name_eng,
                         signal.min, signal.max, signal.units, signal.units_eng, signal.in_level,
                         signal.cabinet, signal.slot_mp, signal.channel, signal.connection, signal.sensr_typ,
                         signal.cat_nam, signal.kksp, signal.location_mp, schema]
    access_table.insert_row(table_name=options.sim_table_name,
                            column_names=column_names,
                            values=values)


def run(options: GenerateTableOptions):
    with SQLUtils.Connection.connect_to_mdb(options.path) as access_base:
        access_base.clear_table(options.sim_table_name)
        kssp_list: List[str] = _get_kksp_list(options=options,
                                              access_base=access_base)
        _get_data_for_kksp(options=options,
                           access_base=access_base,
                           kksp_list=kssp_list)
