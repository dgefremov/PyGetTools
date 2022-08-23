from tools.generate_tables import GenerateTableOptions, DoublePointSignal, SWTemplate, SignalModification, \
    SWTemplateVariant
from tools.fill_mms_address import FillMMSAddressOptions, DPCSignal, DatasetDescription, DatasetDescriptionList, \
    BSCSignal, SignalRange
from tools.fill_ref import FillRefOptions, VirtualTemplate, TemplateVariant, DefinedVariant
from tools.fill_ref2 import FillRef2Options, InputPort, OutputPort, Template, TSODUPanel
from tools.find_schemas import FindSchemasOptions, Schema

from dataclasses import dataclass


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class Options:
    generate_table_options: GenerateTableOptions
    fill_mms_address_options: FillMMSAddressOptions
    fill_ref_options: FillRefOptions
    fill_ref2_options: FillRef2Options
    find_schemas_options: FindSchemasOptions

    @staticmethod
    def load_ruppur() -> 'Options':
        # <-------------------------------generate_table_options------------------------------------------------------->
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
        sw_template1: SWTemplate = SWTemplate(name='XA00',
                                              connection='NTSW0113',
                                              signals={'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'},
                                              variants=[SWTemplateVariant(schema='SW_1623_1',
                                                                          parts=['XF27']),
                                                        SWTemplateVariant(schema='SW_1623_2',
                                                                          parts=['XK52'])])
        sw_template2: SWTemplate = SWTemplate(name='XA10',
                                              connection='NTSW0114',
                                              signals={'XB21', 'XB22', 'XL21', 'XL22'},
                                              variants=[SWTemplateVariant(schema='SW_1623_AVR',
                                                                          parts=[])])
        signal_modification1 = SignalModification(signal_kks='10BBG01GS001',
                                                  signal_part='XB17',
                                                  new_template='BI_1623_INV',
                                                  new_name_rus='Нерабочее положение',
                                                  new_full_name_rus='Нерабочее положение тележки выкатного элемента',
                                                  new_name_eng='Truck non-work pos',
                                                  new_full_name_eng='Non-working position of roll-out element truck')
        signal_modification2 = SignalModification(signal_kks='10BBG03GS001',
                                                  signal_part='XB17',
                                                  new_template='BI_1623_INV',
                                                  new_name_rus='Нерабочее положение',
                                                  new_full_name_rus='Нерабочее положение тележки выкатного элемента',
                                                  new_name_eng='Truck non-work pos',
                                                  new_full_name_eng='Non-working position of roll-out element truck')

        generate_option: GenerateTableOptions = GenerateTableOptions(network_data_table_name='[Network Data]',
                                                                     controller_data_table_name='TPTS',
                                                                     aep_table_name='[Сигналы и механизмы АЭП]',
                                                                     sim_table_name='[Сигналы и механизмы]',
                                                                     iec_table_name='[МЭК 61850]',
                                                                     ied_table_name='[IED]',
                                                                     ref_table_name='[REF]',
                                                                     sign_table_name='[DIAG]',
                                                                     skip_signals=[('00BCE', 'XB20')],
                                                                     dps_signals=[signal1, signal2, signal3, signal4,
                                                                                  signal5, signal6, signal7],
                                                                     sw_templates=[sw_template1, sw_template2],
                                                                     signal_modifications=[signal_modification1,
                                                                                           signal_modification2],
                                                                     copy_ds_to_sim_table=True)
        # <-------------------------------generate_table_options------------------------------------------------------->

        # <-------------------------------fill_mms_address_options----------------------------------------------------->
        dps_signal_cb = DPCSignal(signal_part_dupl=('XB01', 'XB02'),
                                  command_part_dupl=('XL01', 'XL02'))

        dps_signal_alt = DPCSignal(signal_part_dupl=('XB21', 'XB22'),
                                   command_part_dupl=('XL21', 'XL22'))

        dps_signal_gb = DPCSignal(signal_part_dupl=('XB31', 'XB32'),
                                  command_part_dupl=None)

        dps_signal_cb2 = DPCSignal(signal_part_dupl=('XB01', 'XB02'),
                                   command_part_dupl=('XA01', 'XA02'))

        bsc_signal = BSCSignal(signal_part='XB10',
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
                                                           mv_range=SignalRange(1, 25),
                                                           path='Device/LLN0.DataSet03',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS3',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS3')

        dpc_signals: list[DPCSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb]

        fill_mms_options: FillMMSAddressOptions = FillMMSAddressOptions(iec_table_name='[МЭК 61850]',
                                                                        ied_table_name='[IED]',
                                                                        dpc_signals=dpc_signals,
                                                                        bsc_signals=[bsc_signal],
                                                                        datasets=DatasetDescriptionList(
                                                                            [dataset_1, dataset_2, dataset_3]))
        # <-------------------------------fill_mms_address_options----------------------------------------------------->

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->
        template_dsw1_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None)]
        template_dsw1_output_ports_1: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XL01'),
                                                          OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                     part='XL02')]
        template_dsw1_output_ports_2: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XA01'),
                                                          OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                     part='XA02')]
        template_dsw1: Template = Template(name='DSW1',
                                           input_ports={'XA00': template_dsw1_input_ports,
                                                        'XA70': template_dsw1_input_ports},
                                           output_ports={'XA00': template_dsw1_output_ports_1,
                                                         'XA70': template_dsw1_output_ports_2})

        template_dsw2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17)]
        template_dsw2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw2: Template = Template(name='DSW2',
                                           input_ports={'XA00': template_dsw2_input_ports},
                                           output_ports={'XA00': template_dsw2_output_ports})

        template_dsw3_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17),
                                                      InputPort(page=3, cell_num=7, kks=None, part='XF19',
                                                                unrel_ref_cell_num=18)]
        template_dsw3_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw3: Template = Template(name='DSW3',
                                           input_ports={'XA00': template_dsw3_input_ports},
                                           output_ports={'XA00': template_dsw3_output_ports})

        template_dsw4_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17),
                                                      InputPort(page=3, cell_num=7, kks=None, part='XF27',
                                                                unrel_ref_cell_num=18)]
        template_dsw4_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw4: Template = Template(name='DSW4',
                                           input_ports={'XA00': template_dsw4_input_ports},
                                           output_ports={'XA00': template_dsw4_output_ports})

        template_davr2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB21',
                                                                 unrel_ref_cell_num=12),
                                                       InputPort(page=3, cell_num=4, kks=None, part='XB22',
                                                                 unrel_ref_cell_num=None)]
        template_davr2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL21'),
                                                         OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                    part='XL22')]
        template_davr2: Template = Template(name='DAVR2',
                                            input_ports={'XA10': template_davr2_input_ports},
                                            output_ports={'XA10': template_davr2_output_ports})

        template_dltc2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks='10BBT0_EK001', part='XB10',
                                                                 unrel_ref_cell_num=16),
                                                       InputPort(page=3, cell_num=4, kks='10BBT0_EK001', part='XN10',
                                                                 unrel_ref_cell_num=17),
                                                       InputPort(page=3, cell_num=5, kks='10BBT0_EK001', part='XF34',
                                                                 unrel_ref_cell_num=18),
                                                       InputPort(page=3, cell_num=6, kks='10BBT0_EK001', part='XB14',
                                                                 unrel_ref_cell_num=19),
                                                       InputPort(page=3, cell_num=7, kks='10BBT0_EK002', part='XM30',
                                                                 unrel_ref_cell_num=20),
                                                       InputPort(page=3, cell_num=8, kks='10BBT0_EK002', part='XM29',
                                                                 unrel_ref_cell_num=21),
                                                       InputPort(page=3, cell_num=9, kks='10BBT0_GH103', part='XF24',
                                                                 unrel_ref_cell_num=22),
                                                       InputPort(page=3, cell_num=10, kks='10BBT0_GH103', part='XF35',
                                                                 unrel_ref_cell_num=23),
                                                       InputPort(page=3, cell_num=11, kks='10BBT0_GH103', part='XF15',
                                                                 unrel_ref_cell_num=24)]
        template_dltc2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL11'),
                                                         OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                    part='XL12')]
        template_dltc2: Template = Template(name='DLTС2',
                                            input_ports={'XA20': template_dltc2_input_ports},
                                            output_ports={'XA20': template_dltc2_output_ports})
        template_ddgs_input_ports: list[InputPort] = []
        template_ddgs_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL04')]
        template_ddgs: Template = Template(name='DDGS',
                                           input_ports={'XA30': template_ddgs_input_ports},
                                           output_ports={'XA30': template_ddgs_output_ports})

        template_dacnps_input_ports: list[InputPort] = []
        template_dacnps_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XL08')]
        template_dacnps: Template = Template(name='DACNPS',
                                             input_ports={'XA40': template_dacnps_input_ports},
                                             output_ports={'XA40': template_dacnps_output_ports})

        template_dsync_input_ports: list[InputPort] = []
        template_dsync_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL03')]
        template_dsync: Template = Template(name='DSYNC',
                                            input_ports={'XA60': template_dsync_input_ports},
                                            output_ports={'XA60': template_dsync_output_ports})

        wired_template_dsw1_input_ports: list[InputPort] = [InputPort(page=3, cell_num=11, kks=None, part='XF27',
                                                                      unrel_ref_cell_num=None)]
        wired_template_dsw1_output_ports: list[OutputPort] = []
        wired_template_dsw1: Template = Template(name='SW_1623_1',
                                                 input_ports={'XA00': wired_template_dsw1_input_ports},
                                                 output_ports={'XA00': wired_template_dsw1_output_ports})

        wired_template_dsw2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=9, kks=None, part='XK52',
                                                                      unrel_ref_cell_num=None)]
        wired_template_dsw2_output_ports: list[OutputPort] = []
        wired_template_dsw2: Template = Template(name='SW_1623_2',
                                                 input_ports={'XA00': wired_template_dsw2_input_ports},
                                                 output_ports={'XA00': wired_template_dsw2_output_ports})

        wired_template_avr_input_ports: list[InputPort] = [InputPort(page=3, cell_num=9, kks=None, part='XK52',
                                                                     unrel_ref_cell_num=None)]
        wired_template_avr_output_ports: list[OutputPort] = []
        wired_template_avr: Template = Template(name='SW_1623_AVR',
                                                input_ports={'XA00': wired_template_avr_input_ports},
                                                output_ports={'XA00': wired_template_avr_output_ports})
        ts_odu_panel1: TSODUPanel = TSODUPanel(name='10CWG09',
                                               confirm_part='XA1',
                                               abonent=321)
        ts_odu_panel2: TSODUPanel = TSODUPanel(name='10CWG10',
                                               confirm_part='XA1',
                                               abonent=321)
        ts_odu_panel3: TSODUPanel = TSODUPanel(name='10CWB40',
                                               confirm_part='XA1',
                                               abonent=321)

        fill_ref2_options: FillRef2Options = FillRef2Options(control_schemas_table='[VIRTUAL SCHEMAS]',
                                                             predifend_control_schemas_table='[PREDEFINED SCHEMAS]',
                                                             ref_table='[REF]',
                                                             sim_table='[Сигналы и механизмы]',
                                                             iec_table='[МЭК 61850]',
                                                             templates=[template_dsw1, template_dsw2, template_dsw3,
                                                                        template_dsw4, template_davr2, template_dltc2,
                                                                        template_ddgs, template_dacnps,
                                                                        template_dsync, wired_template_dsw1,
                                                                        wired_template_dsw2, wired_template_avr],
                                                             wired_signal_input_page=2,
                                                             wired_signal_input_cell=5,
                                                             ts_odu_algorithm='TS_ODU_LOGIC',
                                                             ts_odu_table='Сигналы и механизмы ТС ОДУ',
                                                             ts_odu_panels=[ts_odu_panel1, ts_odu_panel2,
                                                                            ts_odu_panel3],
                                                             abonent_table='TPTS',
                                                             wired_signal_input_port='Port1')

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->

        # <-------------------------------fill_ref_options------------------------------------------------------------->
        template1: VirtualTemplate = VirtualTemplate(name='Управление выключателем',
                                                     has_channel=True,
                                                     commands_parts_list={'XA00': {'XL01': 'Port1', 'XL02': 'Port2'}},
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
                                                                                             'XF27': ('3', '8', '19')})
                                                               ])
        template2: VirtualTemplate = VirtualTemplate(name='Управление АВР',
                                                     has_channel=True,
                                                     commands_parts_list={'XA10': {'XL21': 'Port1', 'XL22': 'Port2'}},
                                                     variants=[TemplateVariant(name='DAVR2',
                                                                               signal_parts={'XB21': ('3', '3', '13'),
                                                                                             'XB22': ('3', '4', None)})
                                                               ])
        dltc_var: DefinedVariant = DefinedVariant(name='DLTС2',
                                                  signal_list=[('10BBT0#EK001', 'XB10', '3', '3', '16'),
                                                               ('10BBT0#EK001', 'XN10', '3', '4', '17'),
                                                               ('10BBT0#EK001', 'XF34', '3', '5', '18'),
                                                               ('10BBT0#EK001', 'XB14', '3', '6', '19'),
                                                               ('10BBT0#EK002', 'XM30', '3', '7', '20'),
                                                               ('10BBT0#EK002', 'XM29', '3', '8', '21'),
                                                               ('10BBT0#GH103', 'XF24', '3', '9', '22'),
                                                               ('10BBT0#GH103', 'XF35', '3', '10', '23'),
                                                               ('10BBT0#GH103', 'XF15', '3', '11', '24')])

        template3: VirtualTemplate = VirtualTemplate(name='Управление РПН',
                                                     has_channel=True,
                                                     commands_parts_list={'XA20': {'XL11': 'Port1', 'XL12': 'Port2'}},
                                                     variants=[dltc_var
                                                               ])

        template4: VirtualTemplate = VirtualTemplate(name='Пуск ДГ',
                                                     has_channel=True,
                                                     commands_parts_list={'XA30': {'XL04': 'Port1'}},
                                                     variants=[TemplateVariant(name='DDGS',
                                                                               signal_parts={})
                                                               ])
        template5: VirtualTemplate = VirtualTemplate(name='Пуск АСП',
                                                     has_channel=True,
                                                     commands_parts_list={'XA40': {'XL08': 'Port1'}},
                                                     variants=[TemplateVariant(name='DACNPS',
                                                                               signal_parts={})
                                                               ])
        template6: VirtualTemplate = VirtualTemplate(name='Квитирование сигнализации',
                                                     has_channel=True,
                                                     commands_parts_list={'XA50': {'XL50': 'Port1'},
                                                                          'XA51': {'XL51': 'Port1'}},
                                                     variants=[TemplateVariant(name='DSIGN',
                                                                               signal_parts={})
                                                               ])
        template7: VirtualTemplate = VirtualTemplate(name='Вкл при ручной синхронизации',
                                                     has_channel=True,
                                                     commands_parts_list={'XA60': {'XL03': 'Port1'}},
                                                     variants=[TemplateVariant(name='DSYNC',
                                                                               signal_parts={})
                                                               ])
        template8: VirtualTemplate = VirtualTemplate(name='Управление выключателем 2',
                                                     has_channel=True,
                                                     commands_parts_list={'XA70': {'XA01': 'Port1', 'XA02': 'Port2'}},
                                                     variants=[TemplateVariant(name='DSW1',
                                                                               signal_parts={'XB01': ('3', '3', '15'),
                                                                                             'XB02': ('3', '4', None)})
                                                               ])
        wired_template_1: TemplateVariant = TemplateVariant(name='SW_1623_1',
                                                            signal_parts={'XF27': ('3', '11', None)})
        wired_template_2: TemplateVariant = TemplateVariant(name='SW_1623_2',
                                                            signal_parts={'XK52': ('3', '9', None)})
        wired_template_3: TemplateVariant = TemplateVariant(name='SW_1623_AVR',
                                                            signal_parts={})
        fill_ref_options: FillRefOptions = FillRefOptions(sim_table_name='[Сигналы и механизмы]',
                                                          ref_table_name='[REF]',
                                                          sign_table_name='[DIAG]',
                                                          vs_sign_table_name='[DIAG_VS]',
                                                          virtual_templates=[template1, template2, template3, template4,
                                                                             template5, template6, template7,
                                                                             template8],
                                                          virtual_schemas_table_name='[VIRTUAL SCHEMAS]',
                                                          wired_template_variants=[wired_template_1, wired_template_2,
                                                                                   wired_template_3])
        # <-------------------------------fill_ref_options------------------------------------------------------------->

        # <-------------------------------find_schemas_options--------------------------------------------------------->

        schema1: Schema = Schema(name="Управление выключателем",
                                 command_parts=['XL01', 'XL02'],
                                 signal_parts=['XB01', 'XB02', 'XB07', 'XB08', 'XF26', 'XF27', 'XF03', 'XF02', 'XF19',
                                               'XF06', 'XF07'])
        find_schemas_options = FindSchemasOptions(sim_table_name='[Сигналы и механизмы]',
                                                  schemas=[schema1])
        # <-------------------------------find_schemas_options--------------------------------------------------------->

        return Options(generate_table_options=generate_option, fill_ref_options=fill_ref_options,
                       fill_mms_address_options=fill_mms_options, find_schemas_options=find_schemas_options,
                       fill_ref2_options=fill_ref2_options)

    @staticmethod
    def load_kursk() -> 'Options':
        # <-------------------------------generate_table_options------------------------------------------------------->
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
        sw_template1: SWTemplate = SWTemplate(name='XA00',
                                              connection='NTSW0113',
                                              signals={'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'},
                                              variants=[SWTemplateVariant(schema='SW_1623_1',
                                                                          parts=['XF27']),
                                                        SWTemplateVariant(schema='SW_1623_2',
                                                                          parts=['XK52'])])
        sw_template2: SWTemplate = SWTemplate(name='XA10',
                                              connection='NTSW0114',
                                              signals={'XB21', 'XB22', 'XL21', 'XL22'},
                                              variants=[SWTemplateVariant(schema='SW_1623_AVR',
                                                                          parts=[])])

        generate_option: GenerateTableOptions = GenerateTableOptions(network_data_table_name='[Network Data]',
                                                                     controller_data_table_name='TPTS',
                                                                     aep_table_name='[Сигналы и механизмы АЭП]',
                                                                     sim_table_name='[Сигналы и механизмы]',
                                                                     iec_table_name='[МЭК 61850]',
                                                                     ied_table_name='[IED]',
                                                                     ref_table_name='[REF]',
                                                                     sign_table_name='[DIAG]',
                                                                     skip_signals=[('00BCE', 'XB20')],
                                                                     dps_signals=[signal1, signal2, signal3, signal4,
                                                                                  signal5, signal6, signal7],
                                                                     sw_templates=[sw_template1, sw_template2],
                                                                     copy_ds_to_sim_table=False)
        # <-------------------------------generate_table_options------------------------------------------------------->

        # <-------------------------------fill_mms_address_options----------------------------------------------------->
        dps_signal_cb = DPCSignal(signal_part_dupl=('XB01', 'XB02'),
                                  command_part_dupl=('XL01', 'XL02'))

        dps_signal_alt = DPCSignal(signal_part_dupl=('XB21', 'XB22'),
                                   command_part_dupl=('XL21', 'XL22'))

        dps_signal_gb = DPCSignal(signal_part_dupl=('XB31', 'XB32'),
                                  command_part_dupl=None)

        dps_signal_cb2 = DPCSignal(signal_part_dupl=None,
                                   command_part_dupl=('XA01', 'XA02'))

        bsc_signal = BSCSignal(signal_part='XB10',
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
                                                           mv_range=SignalRange(1, 25),
                                                           path='Device/LLN0.DataSet03',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS3',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS3')

        dpc_signals: list[DPCSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb]

        fill_mms_options: FillMMSAddressOptions = FillMMSAddressOptions(iec_table_name='[МЭК 61850]',
                                                                        ied_table_name='[IED]',
                                                                        dpc_signals=dpc_signals,
                                                                        bsc_signals=[bsc_signal],
                                                                        datasets=DatasetDescriptionList(
                                                                            [dataset_1, dataset_2, dataset_3]))
        # <-------------------------------fill_mms_address_options----------------------------------------------------->

        # <-------------------------------fill_ref_options------------------------------------------------------------->
        template1: VirtualTemplate = VirtualTemplate(name='Управление выключателем',
                                                     has_channel=True,
                                                     commands_parts_list={'XA00': {'XL01': 'Port1', 'XL02': 'Port2'}},
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
                                                                                             'XF27': ('3', '8', '19')})
                                                               ])
        template2: VirtualTemplate = VirtualTemplate(name='Управление АВР',
                                                     has_channel=True,
                                                     commands_parts_list={'XA10': {'XL21': 'Port1', 'XL22': 'Port2'}},
                                                     variants=[TemplateVariant(name='DAVR',
                                                                               signal_parts={'XB21': ('3', '3', '15'),
                                                                                             'XB22': ('3', '4', None)})
                                                               ])
        template3: VirtualTemplate = VirtualTemplate(name='Управление РПН',
                                                     has_channel=True,
                                                     commands_parts_list={'XA20': {'XL11': 'Port1', 'XL12': 'Port2'}},
                                                     variants=[TemplateVariant(name='DLTC',
                                                                               signal_parts={'XB10': ('3', '3', '7')})
                                                               ])
        template4: VirtualTemplate = VirtualTemplate(name='Пуск ДГ',
                                                     has_channel=True,
                                                     commands_parts_list={'XA30': {'XL04': 'Port1'}},
                                                     variants=[TemplateVariant(name='DDGS',
                                                                               signal_parts={})
                                                               ])
        template5: VirtualTemplate = VirtualTemplate(name='Пуск АСП',
                                                     has_channel=True,
                                                     commands_parts_list={'XA40': {'XL08': 'Port1'}},
                                                     variants=[TemplateVariant(name='DACNPS',
                                                                               signal_parts={})
                                                               ])
        template6: VirtualTemplate = VirtualTemplate(name='Квитирование сигнализации',
                                                     has_channel=True,
                                                     commands_parts_list={'XA50': {'XL50': 'Port1'},
                                                                          'XA51': {'XL51': 'Port1'}},
                                                     variants=[TemplateVariant(name='DSIGN',
                                                                               signal_parts={})
                                                               ])
        template7: VirtualTemplate = VirtualTemplate(name='Вкл при ручной синхронизации',
                                                     has_channel=True,
                                                     commands_parts_list={'XA60': {'XL03': 'Port1'}},
                                                     variants=[TemplateVariant(name='DSYNC',
                                                                               signal_parts={})
                                                               ])
        wired_template_1: TemplateVariant = TemplateVariant(name='SW_1623_1',
                                                            signal_parts={'XF27': ('3', '11', None)})
        wired_template_2: TemplateVariant = TemplateVariant(name='SW_1623_2',
                                                            signal_parts={'XK52': ('3', '9', None)})
        wired_template_3: TemplateVariant = TemplateVariant(name='SW_1623_AVR',
                                                            signal_parts={})
        fill_ref_options: FillRefOptions = FillRefOptions(sim_table_name='[Сигналы и механизмы]',
                                                          ref_table_name='[REF]',
                                                          sign_table_name='[DIAG]',
                                                          vs_sign_table_name='[DIAG_VS]',
                                                          virtual_templates=[template1, template2, template3, template4,
                                                                             template5, template6,
                                                                             template7],
                                                          virtual_schemas_table_name='[VIRTUAL SCHEMAS]',
                                                          wired_template_variants=[wired_template_1, wired_template_2,
                                                                                   wired_template_3])
        # <-------------------------------fill_ref_options------------------------------------------------------------->

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->
        template_dsw1_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None)]
        template_dsw1_output_ports_1: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XL01'),
                                                          OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                     part='XL02')]
        template_dsw1_output_ports_2: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XA01'),
                                                          OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                     part='XA02')]
        template_dsw1: Template = Template(name='DSW1',
                                           input_ports={'XA00': template_dsw1_input_ports},
                                           output_ports={'XA00': template_dsw1_output_ports_1,
                                                         'XA70': template_dsw1_output_ports_2})

        template_dsw2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17)]
        template_dsw2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw2: Template = Template(name='DSW2',
                                           input_ports={'XA00': template_dsw2_input_ports},
                                           output_ports={'XA00': template_dsw2_output_ports})

        template_dsw3_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17),
                                                      InputPort(page=3, cell_num=7, kks=None, part='XB19',
                                                                unrel_ref_cell_num=18)]
        template_dsw3_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw3: Template = Template(name='DSW3',
                                           input_ports={'XA00': template_dsw3_input_ports},
                                           output_ports={'XA00': template_dsw3_output_ports})

        template_dsw4_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB01',
                                                                unrel_ref_cell_num=15),
                                                      InputPort(page=3, cell_num=4, kks=None, part='XB02',
                                                                unrel_ref_cell_num=None),
                                                      InputPort(page=3, cell_num=5, kks=None, part='XB07',
                                                                unrel_ref_cell_num=16),
                                                      InputPort(page=3, cell_num=6, kks=None, part='XB08',
                                                                unrel_ref_cell_num=17),
                                                      InputPort(page=3, cell_num=7, kks=None, part='XF27',
                                                                unrel_ref_cell_num=18)]
        template_dsw4_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL01'),
                                                        OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                   part='XL02')]
        template_dsw4: Template = Template(name='DSW4',
                                           input_ports={'XA00': template_dsw4_input_ports},
                                           output_ports={'XA00': template_dsw4_output_ports})

        template_davr2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB21',
                                                                 unrel_ref_cell_num=12),
                                                       InputPort(page=3, cell_num=4, kks=None, part='XB22',
                                                                 unrel_ref_cell_num=None)]
        template_davr2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL21'),
                                                         OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                    part='XL22')]
        template_davr2: Template = Template(name='DAVR2',
                                            input_ports={'XA10': template_davr2_input_ports},
                                            output_ports={'XA10': template_davr2_output_ports})

        template_dltc2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=3, kks='10BBT0#EK001', part='XB10',
                                                                 unrel_ref_cell_num=16),
                                                       InputPort(page=3, cell_num=4, kks='10BBT0#EK001', part='XN10',
                                                                 unrel_ref_cell_num=17),
                                                       InputPort(page=3, cell_num=5, kks='10BBT0#EK001', part='XF34',
                                                                 unrel_ref_cell_num=18),
                                                       InputPort(page=3, cell_num=6, kks='10BBT0#EK001', part='XB14',
                                                                 unrel_ref_cell_num=19),
                                                       InputPort(page=3, cell_num=7, kks='10BBT0#EK002', part='XM30',
                                                                 unrel_ref_cell_num=20),
                                                       InputPort(page=3, cell_num=8, kks='10BBT0#EK002', part='XM29',
                                                                 unrel_ref_cell_num=21),
                                                       InputPort(page=3, cell_num=9, kks='10BBT0#GH103', part='XF24',
                                                                 unrel_ref_cell_num=22),
                                                       InputPort(page=3, cell_num=10, kks='10BBT0#GH103', part='XF35',
                                                                 unrel_ref_cell_num=23),
                                                       InputPort(page=3, cell_num=11, kks='10BBT0#GH103', part='XF15',
                                                                 unrel_ref_cell_num=24)]
        template_dltc2_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL11'),
                                                         OutputPort(name='Port2', page=2, cell_num=8, kks=None,
                                                                    part='XL12'),
                                                         OutputPort(name='Port3', page=2, cell_num=11, kks=None,
                                                                    part='XF33')]
        template_dltc2: Template = Template(name='DLTC2',
                                            input_ports={'XA20': template_dltc2_input_ports},
                                            output_ports={'XA20': template_dltc2_output_ports})
        template_ddgs_input_ports: list[InputPort] = []
        template_ddgs_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                   part='XL04')]
        template_ddgs: Template = Template(name='DDGS',
                                           input_ports={'XA30': template_ddgs_input_ports},
                                           output_ports={'XA30': template_ddgs_output_ports})

        template_dacnps_input_ports: list[InputPort] = []
        template_dacnps_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                     part='XL08')]
        template_dacnps: Template = Template(name='DACNPS',
                                             input_ports={'XA40': template_dacnps_input_ports},
                                             output_ports={'XA40': template_dacnps_output_ports})

        template_dsign_input_ports: list[InputPort] = []
        template_dsign_output_ports_1: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                      part='XL50')]
        template_dsign_output_ports_2: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                      part='XL51')]
        template_sign: Template = Template(name='DSINC',
                                           input_ports={'XA50': template_dsign_input_ports},
                                           output_ports={'XA50': template_dsign_output_ports_1,
                                                         'XA51': template_dsign_output_ports_2})

        template_dsync_input_ports: list[InputPort] = []
        template_dsync_output_ports: list[OutputPort] = [OutputPort(name='Port1', page=2, cell_num=5, kks=None,
                                                                    part='XL03')]
        template_dsync: Template = Template(name='DACNPS',
                                            input_ports={'XA60': template_dsync_input_ports},
                                            output_ports={'XA60': template_dsync_output_ports})

        wired_template_dsw1_input_ports: list[InputPort] = [InputPort(page=3, cell_num=11, kks=None, part='XF27',
                                                                      unrel_ref_cell_num=None)]
        wired_template_dsw1_output_ports: list[OutputPort] = []
        wired_template_dsw1: Template = Template(name='SW_1623_1',
                                                 input_ports={'XA00': wired_template_dsw1_input_ports},
                                                 output_ports={'XA00': wired_template_dsw1_output_ports})

        wired_template_dsw2_input_ports: list[InputPort] = [InputPort(page=3, cell_num=9, kks=None, part='XK52',
                                                                      unrel_ref_cell_num=None)]
        wired_template_dsw2_output_ports: list[OutputPort] = []
        wired_template_dsw2: Template = Template(name='SW_1623_2',
                                                 input_ports={'XA00': wired_template_dsw2_input_ports},
                                                 output_ports={'XA00': wired_template_dsw2_output_ports})

        wired_template_avr_input_ports: list[InputPort] = [InputPort(page=3, cell_num=9, kks=None, part='XK52',
                                                                     unrel_ref_cell_num=None)]
        wired_template_avr_output_ports: list[OutputPort] = []
        wired_template_avr: Template = Template(name='SW_1623_AVR',
                                                input_ports={'XA00': wired_template_avr_input_ports},
                                                output_ports={'XA00': wired_template_avr_output_ports})
        fill_ref2_options: FillRef2Options = FillRef2Options(control_schemas_table='[VIRTUAL SCHEMAS]',
                                                             predifend_control_schemas_table='[PREDEFINED SCHEMAS]',
                                                             ref_table='[REF]',
                                                             sim_table='[Сигналы и механизмы]',
                                                             iec_table='[МЭК 61850]',
                                                             templates=[template_dsw1, template_dsw2, template_dsw3,
                                                                        template_dsw4, template_davr2, template_dltc2,
                                                                        template_ddgs, template_dacnps, template_sign,
                                                                        template_dsync, wired_template_dsw1,
                                                                        wired_template_dsw2, wired_template_avr],
                                                             wired_signal_input_page=2,
                                                             wired_signal_input_cell=5,
                                                             wired_signal_input_port='Port1')

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->

        # <-------------------------------find_schemas_options--------------------------------------------------------->

        schema1: Schema = Schema(name="Управление выключателем",
                                 command_parts=['XL01', 'XL02'],
                                 signal_parts=['XB01', 'XB02', 'XB07', 'XB08', 'XF26', 'XF03', 'XF02', 'XF19'])
        find_schemas_options = FindSchemasOptions(sim_table_name='[Сигналы и механизмы]',
                                                  schemas=[schema1])
        # <-------------------------------find_schemas_options--------------------------------------------------------->

        return Options(generate_table_options=generate_option, fill_ref_options=fill_ref_options,
                       fill_mms_address_options=fill_mms_options, find_schemas_options=find_schemas_options,
                       fill_ref2_options=fill_ref2_options)
