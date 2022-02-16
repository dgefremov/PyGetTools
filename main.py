import logging

from tools.generate_tables import GenerateTables, GenerateTableOptions, DoublePointSignal, SWTemplate

from tools.fill_mms_address import FillMMSAdress, FillMMSAddressOptions, DPCSignal, BSCSignal, DatasetDescriptionList, \
    DatasetDescription, SignalRange

from tools.copy_cid import CopyCid, CopyCidOptions

from tools.fill_ref import VirtualTemplate, TemplateVariant, FillRef, FillRefOptions

from tools.find_schemas import FindSchemas, FindSchemasOptions, Schema

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s - %(message)s')


def fill_mms():
    dps_signal_cb = DPCSignal(signal_part='XB00',
                              signal_part_dupl=('XB01', 'XB02'),
                              command_part='XL00',
                              command_part_dupl=('XL01', 'XL02'))

    dps_signal_alt = DPCSignal(signal_part='XB20',
                               signal_part_dupl=('XB21', 'XB22'),
                               command_part='XL20',
                               command_part_dupl=('XL21', 'XL22'))

    dps_signal_gb = DPCSignal(signal_part='XB30',
                              signal_part_dupl=('XB31', 'XB32'),
                              command_part=None,
                              command_part_dupl=None)

    dps_signal_cb2 = DPCSignal(signal_part=None,
                               signal_part_dupl=None,
                               command_part=None,
                               command_part_dupl=('XA01', 'XA02'))

    bsc_signal = BSCSignal(signal_part='XB10',
                           command_part='XL10',
                           command_part_dupl=('XL11', 'XL12'))

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

    dpc_signals: list[DPCSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb]

    FillMMSAdress.run(FillMMSAddressOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.07.accdb',
                                            iec_table_name='[МЭК 61850]',
                                            ied_table_name='[IED]',
                                            dpc_signals=dpc_signals,
                                            bsc_signals=[bsc_signal],
                                            datasets=DatasetDescriptionList([dataset_1, dataset_2, dataset_3])))


def fill_tables():
    signal1: DoublePointSignal = DoublePointSignal(single_part='XB00',
                                                   on_part='XB01',
                                                   off_part='XB02')
    signal2: DoublePointSignal = DoublePointSignal(single_part='XL00',
                                                   on_part='XL01',
                                                   off_part='XL02')
    signal3: DoublePointSignal = DoublePointSignal(single_part='XB20',
                                                   on_part='XB21',
                                                   off_part='XB22')
    signal4: DoublePointSignal = DoublePointSignal(single_part='XL20',
                                                   on_part='XL21',
                                                   off_part='XL22')
    signal5: DoublePointSignal = DoublePointSignal(single_part='XB30',
                                                   on_part='XB31',
                                                   off_part='XB32')
    signal6: DoublePointSignal = DoublePointSignal(single_part='XL10',
                                                   on_part='XL11',
                                                   off_part='XL12')
    signal7: DoublePointSignal = DoublePointSignal(single_part=None,
                                                   on_part='XA01',
                                                   off_part='XA02')
    GenerateTables.run(GenerateTableOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.07.accdb',
                                            network_data_table_name='[Network Data]',
                                            controller_data_table_name='TPTS',
                                            aep_table_name='[Сигналы и механизмы АЭП]',
                                            sim_table_name='[Сигналы и механизмы]',
                                            iec_table_name='[МЭК 61850]',
                                            ied_table_name='[IED]',
                                            ref_table_name='[REF]',
                                            sign_table_name='[DIAG]',
                                            skip_duplicate_prefix=['00BCE'],
                                            dps_signals=[signal1, signal2, signal3, signal4, signal5, signal6, signal7],
                                            sw_templates=[SWTemplate('SW_1623_1', ['XF27']),
                                                          SWTemplate('SW_1623_2', ['XK52'])])
                       )


def copy_cid():
    CopyCid.run(CopyCidOptions(base_path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.07.accdb',
                               source_cid='c:\\User data\\All_in_one.cid',
                               target_path='c:\\User data\\2\\',
                               mask='255.255.255.0'))


def find_schemas():
    schema1: Schema = Schema(name="Управление выключателем",
                             command_parts=['XL01', 'XL02'],
                             signal_parts=['XB01', 'XB02', 'XB07', 'XB08', 'XF19', 'XF27'])
    FindSchemas.run(FindSchemasOptions(database_path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.07.accdb',
                                       sim_table_name='[Сигналы и механизмы]',
                                       schemas=[schema1]))


def fill_ref():
    template1: VirtualTemplate = VirtualTemplate(name='Управление выключателем',
                                                 part='XA00',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL01': 'Port1', 'XL02': 'Port2'}],
                                                 variants=[TemplateVariant(name='DSW1',
                                                                           signal_parts={'XB01': ('3', '3', '15'),
                                                                                         'XB02': ('3', '4', None)}),
                                                           TemplateVariant(name='DSW2',
                                                                           signal_parts={'XB01': ('3', '3', '15'),
                                                                                         'XB02': ('3', '4', None),
                                                                                         'XB07': ('3', '5', '16'),
                                                                                         'XB08': ('3', '6', '17')}),
                                                           TemplateVariant(name='DSW3',
                                                                           signal_parts={'XB01': ('3', '3', '15'),
                                                                                         'XB02': ('3', '4', None),
                                                                                         'XB07': ('3', '5', '16'),
                                                                                         'XB08': ('3', '6', '17'),
                                                                                         'XF19': ('3', '7', '18')}),
                                                           TemplateVariant(name='DSW4',
                                                                           signal_parts={'XB01': ('3', '3', '15'),
                                                                                         'XB02': ('3', '4', None),
                                                                                         'XB07': ('3', '5', '16'),
                                                                                         'XB08': ('3', '6', '17'),
                                                                                         'XF27': ('3', '8', '19')}),
                                                           ])
    template2: VirtualTemplate = VirtualTemplate(name='Управление АВР',
                                                 part='XA10',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL21': 'Port1', 'XL22': 'Port2'}],
                                                 variants=[TemplateVariant(name='DAVR',
                                                                           signal_parts={'XB21': ('3', '3', '15'),
                                                                                         'XB22': ('3', '4', None)}),
                                                           ])
    template3: VirtualTemplate = VirtualTemplate(name='Управление РПН',
                                                 part='XA20',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL11': 'Port1', 'XL12': 'Port2'}],
                                                 variants=[TemplateVariant(name='DLTC',
                                                                           signal_parts={'XB10': ('3', '3', '7')}),
                                                           ])
    template4: VirtualTemplate = VirtualTemplate(name='Пуск ДГ',
                                                 part='XA30',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL04': 'Port1'}],
                                                 variants=[TemplateVariant(name='DDGS',
                                                                           signal_parts={}),
                                                           ])
    template5: VirtualTemplate = VirtualTemplate(name='Пуск АСП',
                                                 part='XA40',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL08': 'Port1'}],
                                                 variants=[TemplateVariant(name='DACNPS',
                                                                           signal_parts={}),
                                                           ])
    template6: VirtualTemplate = VirtualTemplate(name='Квитирование сигнализации',
                                                 part='XA50',
                                                 has_channel=True,
                                                 commands_parts_list=[{'XL50': 'Port1'},
                                                                      {'XL51': 'Port1'}],
                                                 variants=[TemplateVariant(name='DSIGN',
                                                                           signal_parts={}),
                                                           ])
    wired_template_1: TemplateVariant = TemplateVariant(name='SW_1623_1',
                                                        signal_parts={'XF27': ('3', '10', None)})
    wired_template_2: TemplateVariant = TemplateVariant(name='SW_1623_2',
                                                        signal_parts={'XK52': ('3', '11', None)})
    FillRef.run(FillRefOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.07.accdb',
                               sim_table_name='[Сигналы и механизмы]',
                               ref_table_name='[REF]',
                               sign_table_name='DIAG',
                               vs_sign_table_name='[DIAG_VS]',
                               virtual_templates=[template1, template2, template3, template4, template5, template6],
                               virtual_schemas_table_name='[VIRTUAL SCHEMAS]',
                               wired_template_variants=[wired_template_1, wired_template_2]))


if __name__ == '__main__':
    fill_tables()
    # fill_mms()
    # copy_cid()
    # find_schemas()
    fill_ref()
