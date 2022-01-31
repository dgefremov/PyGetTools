from typing import List

from tools.generate_tables import GenerateTables, DPCSignal, BSCSignal, GenerateTableOptions, DatasetDescriptionList, \
    DatasetDescription, SignalRange
from tools.copy_cid import CopyCid, CopyCidOptions


def fill_tables():
    dps_signal_cb = DPCSignal(signal_part='XB00',
                              signal_part_dupl=['XB01', 'XB02'],
                              command_part='XL00',
                              command_part_dupl=['XL01', 'XL02'])

    dps_signal_alt = DPCSignal(signal_part='XB20',
                               signal_part_dupl=['XB21', 'XB22'],
                               command_part='XL20',
                               command_part_dupl=['XL21', 'XL22'])

    dps_signal_gb = DPCSignal(signal_part='XB30',
                              signal_part_dupl=['XB31', 'XB32'],
                              command_part=None,
                              command_part_dupl=[])

    dps_signal_cb2 = DPCSignal(signal_part=None,
                               signal_part_dupl=[],
                               command_part=None,
                               command_part_dupl=['XA01', 'XA02'])

    bsc_signal = BSCSignal(signal_part='XB10',
                           command_part='XL10',
                           command_part_dupl=['XL11', 'XL12'])

    dataset_1: DatasetDescription = DatasetDescription(name='Dataset01',
                                                       sps_range=SignalRange(1, 50),
                                                       path='Device/LLN0.DataSet01',
                                                       rcb_main='Device/LLN0.RP.Report_A_DS1',
                                                       rcb_res='Device/LLN0.RP.Report_B_DS1')

    dataset_2: DatasetDescription = DatasetDescription(name='Dataset0',
                                                       sps_range=SignalRange(51, 75),
                                                       spc_range=SignalRange(1, 10),
                                                       dpc_range=SignalRange(1, 10),
                                                       bsc_range=SignalRange(1, 2),
                                                       path='Device/LLN0.DataSet02',
                                                       rcb_main='Device/LLN0.RP.Report_A_DS2',
                                                       rcb_res='Device/LLN0.RP.Report_B_DS2')

    dataset_3: DatasetDescription = DatasetDescription(name='Dataset03',
                                                       mv_range=SignalRange(1, 10),
                                                       path='Device/LLN0.DataSet03',
                                                       rcb_main='Device/LLN0.RP.Report_A_DS3',
                                                       rcb_res='Device/LLN0.RP.Report_B_DS3')

    dpc_signals: List[DPCSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb]

    GenerateTables.run(GenerateTableOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.06.accdb',
                                            network_data_table_name='[Network Data]',
                                            controller_data_table_name='TPTS',
                                            aep_table_name='[Сигналы и механизмы АЭП]',
                                            sim_table_name='[Сигналы и механизмы]',
                                            iec_table_name='[МЭК 61850]',
                                            ied_table_name='[IED]',
                                            skip_duplicate_prefix=['00BCE'],
                                            dpc_signals=dpc_signals,
                                            bsc_signals=[bsc_signal],
                                            datasets=DatasetDescriptionList([dataset_1, dataset_2, dataset_3])))


def copy_cid():
    CopyCid.run(CopyCidOptions(base_path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.06.accdb',
                               source_cid='c:\\User data\\All_in_one.cid',
                               target_path='c:\\User data\\2\\',
                               mask='255.255.255.0'))


if __name__ == '__main__':
    fill_tables()
    # copy_cid()
