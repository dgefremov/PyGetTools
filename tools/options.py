from tools.generate_tables import GenerateTableOptions, DoublePointSignal, SWTemplate, SignalModification, \
    SWTemplateVariant
from tools.fill_mms_address import FillMMSAddressOptions, DPCSignal, DatasetDescription, DatasetDescriptionList, \
    BSCSignal, SignalRange
from tools.fill_ref2 import FillRef2Options, InputPort, OutputPort, Template, TSODUPanel, TSODUData, TSODUDescription, \
    TSODUTemplate
from dataclasses import dataclass


@dataclass(init=True, repr=False, eq=True, order=False, frozen=True)
class Options:
    generate_table_options: GenerateTableOptions
    fill_mms_address_options: FillMMSAddressOptions
    fill_ref2_options: FillRef2Options

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
        sw_template1: SWTemplate = SWTemplate(
            connection='NTSW0113',
            signals={'XB01', 'XB02', 'XL01', 'XL02', 'XB07', 'XB08'},
            variants=[SWTemplateVariant(schema=['SCW_NKU_04_0_SIGN',
                                                'SCW_NKU_04_0_SIGN_WITHOUT_BPU'],
                                        parts=[],
                                        schema_part='XA00'),
                      SWTemplateVariant(schema=['SCW_NKU_04_3_SIGN',
                                                'SCW_NKU_04_3_SIGN_WITHOUT_BPU'],
                                        parts=['XK17', 'XF06'],
                                        schema_part='XA00'),
                      SWTemplateVariant(schema=['SCW_NKU_04_4_SIGN',
                                                'SCW_NKU_04_4_SIGN_WITHOUT_BPU'],
                                        parts=['XK52', 'XK00', 'XK39', 'XB07'],
                                        schema_part='XA00')])
        sw_template2: SWTemplate = SWTemplate(connection='NTSW0114',
                                              signals={'XB21', 'XB22', 'XL21', 'XL22'},
                                              variants=[SWTemplateVariant(schema=['ATSW_1623',
                                                                                  'ATSW_1623_WITHOUT_BPU'],
                                                                          parts=[],
                                                                          schema_part='XA10')])
        signal_modification1 = SignalModification(signal_kks=r'^[1-2]0BBG0[13]GS001$',  # 10BBG01GS001, 10BBG03GS001
                                                  signal_part='^XB17$',
                                                  new_template='BI_1623_INV',
                                                  new_name_rus='Нерабочее положение',
                                                  new_full_name_rus='Нерабочее положение тележки выкатного элемента',
                                                  new_name_eng='Truck non-work pos',
                                                  new_full_name_eng='Non-working position of roll-out element truck',
                                                  new_part='XB08')
        # signal_modification2 = SignalModification(signal_kks='10BFR07GH001',
        #                                          signal_part='XA10',
        #                                          new_kks='10BFR07EK001')
        signal_modification3 = SignalModification(signal_kks=r'^[12]0BB[A-C]27GU012$',
                                                  signal_part='^XF20$',
                                                  new_template='BI_1623_INV',
                                                  new_name_rus='БАВР-В исправно',
                                                  new_full_name_rus='БАВР-В исправно',
                                                  new_name_eng='BAVR-V works correct',
                                                  new_full_name_eng='BAVR-V works correct'
                                                  )
        signal_modification4 = SignalModification(signal_kks=r'^[12]0BB[A-C]27GU012$',
                                                  signal_part='^XF20$',
                                                  new_template='BI_1623_INV',
                                                  new_name_rus='БАВР-В исправно',
                                                  new_full_name_rus='БАВР-В исправно',
                                                  new_name_eng='BAVR-V works correct',
                                                  new_full_name_eng='BAVR-V works correct'
                                                  )

        generate_option: GenerateTableOptions = GenerateTableOptions(network_data_table_name='Network Data',
                                                                     controller_data_table_name='TPTS',
                                                                     aep_table_name='Сигналы и механизмы АЭП',
                                                                     sim_table_name='Сигналы и механизмы',
                                                                     iec_table_name='МЭК 61850',
                                                                     ied_table_name='IED',
                                                                     ref_table_name='REF',
                                                                     ps_table_name='PREDEFINED_SCHEMAS',
                                                                     fake_signals_table_name='FAKE_SIGNALS',
                                                                     sign_table_name='DIAG',
                                                                     skip_duplicate_signals=[('00BCE', 'XB20')],
                                                                     dps_signals=[signal1, signal2, signal3, signal4,
                                                                                  signal5, signal6, signal7],
                                                                     sw_templates=[sw_template1, sw_template2],
                                                                     signal_modifications=[signal_modification1,
                                                                                           # signal_modification2,
                                                                                           signal_modification3,
                                                                                           signal_modification4],
                                                                     copy_ds_to_sim_table=True)
        # <-------------------------------generate_table_options------------------------------------------------------->

        # <-------------------------------fill_mms_address_options----------------------------------------------------->
        dps_signal_cb = DPCSignal(signal_part=('XB01', 'XB02'),
                                  command_part=('XL01', 'XL02'))

        dps_signal_cb3 = DPCSignal(signal_part=('XB01', 'XB02'),
                                   command_part=None)

        dps_signal_alt = DPCSignal(signal_part=('XB21', 'XB22'),
                                   command_part=('XL21', 'XL22'))

        dps_signal_gb = DPCSignal(signal_part=('XB31', 'XB32'),
                                  command_part=None)

        dps_signal_cb2 = DPCSignal(signal_part=('XB01', 'XB02'),
                                   command_part=('XA01', 'XA02'))

        bsc_signal = BSCSignal(signal_part='XB10',
                               command_part=('XL11', 'XL12'))

        bsc_signal2 = BSCSignal(signal_part='XB10',
                                command_part=None)

        dataset_1: DatasetDescription = DatasetDescription(name='Dataset01',
                                                           sps_range=SignalRange(1, 50),
                                                           path='Device/LLN0.DataSet01',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS101',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS101')

        dataset_2: DatasetDescription = DatasetDescription(name='Dataset0',
                                                           sps_range=SignalRange(51, 75),
                                                           spc_range=SignalRange(1, 10),
                                                           dpc_range=SignalRange(1, 10),
                                                           bsc_range=SignalRange(1, 2),
                                                           path='Device/LLN0.DataSet02',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS201',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS201')

        dataset_3: DatasetDescription = DatasetDescription(name='Dataset03',
                                                           mv_range=SignalRange(1, 25),
                                                           path='Device/LLN0.DataSet03',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS301',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS301')

        dpc_signals: list[DPCSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb, dps_signal_cb3]

        fill_mms_options: FillMMSAddressOptions = FillMMSAddressOptions(iec_table_name='МЭК 61850',
                                                                        ied_table_name='IED',
                                                                        mms_table_name='MMS',
                                                                        dpc_signals=dpc_signals,
                                                                        bsc_signals=[bsc_signal, bsc_signal2],
                                                                        datasets=DatasetDescriptionList(
                                                                            [dataset_1, dataset_2, dataset_3]))
        # <-------------------------------fill_mms_address_options----------------------------------------------------->

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->
        sc_cb_24_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB02', unrel_ref_cell_num=18),
                                           InputPort(page=3, cell_num=4, kks=None, part='XB01',
                                                     unrel_ref_cell_num=None),
                                           InputPort(page=3, cell_num=5, kks=None, part='XM00', unrel_ref_cell_num=19)]
        cb_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XL01'),
                                       OutputPort(name='Port2', kks=None, part='XL02')]

        sc_cb_24: Template = Template(name='SC_CB_24',
                                      input_ports={'XA00': sc_cb_24_input},
                                      output_ports={'XA00': []},
                                      ts_odu_data=TSODUData(input_ports=[],
                                                            output_ports=[]),
                                      alarm_sound_signal_port='Port1',
                                      warn_sound_signal_port='Port2')

        sc_kru_10_3_sign_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB02',
                                                             unrel_ref_cell_num=18),
                                                   InputPort(page=3, cell_num=4, kks=None, part='XB01',
                                                             unrel_ref_cell_num=None),
                                                   InputPort(page=3, cell_num=5, kks=None, part='XM36',
                                                             unrel_ref_cell_num=19),
                                                   InputPort(page=3, cell_num=6, kks=None, part='XK51',
                                                             unrel_ref_cell_num=20),
                                                   InputPort(page=3, cell_num=7, kks='00BCE__EW905', part='XK15',
                                                             unrel_ref_cell_num=21)]
        cb_ts_input: list[InputPort] = [InputPort(page=3, cell_num=14, kks=None, part='XL01',
                                                  unrel_ref_cell_num=None),
                                        InputPort(page=3, cell_num=15, kks=None, part='XL02',
                                                  unrel_ref_cell_num=None)]

        cb_ts_output: list[OutputPort] = [OutputPort(name='Port5', kks=None, part='XB02',
                                                     blink_port_name='Port6', flicker_port_name='Port7'),
                                          OutputPort(name='Port8', kks=None, part='XB01',
                                                     blink_port_name='Port9', flicker_port_name='Port10'),
                                          OutputPort(name='Port11', kks=None, part='XF19',
                                                     blink_port_name='Port12')]
        cb_ts_data: TSODUData = TSODUData(confirm_command_page='3', confirm_command_cell=16,
                                          input_ports=cb_ts_input,
                                          output_ports=cb_ts_output)
        sc_kru_10_3_sign_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA01'),
                                                     OutputPort(name='Port2', kks=None, part='XA02')]

        sc_kru_10_3_sign: Template = Template(name='SC_KRU_10_3_SIGN',
                                              input_ports={'XA70': sc_kru_10_3_sign_input},
                                              output_ports={'XA70': sc_kru_10_3_sign_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_kru_10_3_sign_without_bpu: Template = Template(name='SC_KRU_10_3_SIGN_WITHOUT_BPU',
                                                          input_ports={'XA70': sc_kru_10_3_sign_input},
                                                          output_ports={'XA70': sc_kru_10_3_sign_output})

        sc_kru_10_6_sign_input: list[InputPort] = [
            InputPort(page=3, cell_num=3, kks=None, part='XB02',
                      unrel_ref_cell_num=18),
            InputPort(page=3, cell_num=4, kks=None, part='XB01',
                      unrel_ref_cell_num=None),
            InputPort(page=3, cell_num=5, kks=None, part='XF02',
                      unrel_ref_cell_num=19),
            InputPort(page=3, cell_num=6, kks=None, part='XF03',
                      unrel_ref_cell_num=20),
            InputPort(page=3, cell_num=7, kks=None, part='XF19',
                      unrel_ref_cell_num=21),
            InputPort(page=3, cell_num=8, kks=None, part='XF26',
                      unrel_ref_cell_num=22),
            InputPort(page=3, cell_num=9, kks='_0_____GU011', part='XK00',
                      unrel_ref_cell_num=23),
            InputPort(page=3, cell_num=10, kks=None, part='XB08',
                      unrel_ref_cell_num=24),
            InputPort(page=3, cell_num=12, kks=None, part='XB07',
                      unrel_ref_cell_num=25)]
        sc_kru_10_6_sign: Template = Template(name='SC_KRU_10_6_SIGN',
                                              input_ports={'XA00': sc_kru_10_6_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_kru_10_6_sign_without_bpu: Template = Template(name='SC_KRU_10_6_SIGN_WITHOUT_BPU',
                                                          input_ports={'XA00': sc_kru_10_6_sign_input},
                                                          output_ports={'XA00': cb_output})

        sc_kru_10_7_sign_input: list[InputPort] = sc_kru_10_6_sign_input + [
            InputPort(page=3, cell_num=11, kks='_0_____GU012', part='XK00',
                      unrel_ref_cell_num=26)]
        sc_kru_10_7_sign: Template = Template(name='SC_KRU_10_7_SIGN',
                                              input_ports={'XA00': sc_kru_10_7_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_kru_10_7_sign_without_bpu: Template = Template(name='SC_KRU_10_7_SIGN_WITHOUT_BPU',
                                                          input_ports={'XA00': sc_kru_10_7_sign_input},
                                                          output_ports={'XA00': cb_output})

        sc_kru_10_7_ext_sign: Template = Template(name='SC_KRU_10_7_EXT_SIGN',
                                                  input_ports={'XA00': sc_kru_10_6_sign_input},
                                                  output_ports={'XA00': cb_output},
                                                  ts_odu_data=cb_ts_data,
                                                  alarm_sound_signal_port='Port3',
                                                  warn_sound_signal_port='Port4')

        sc_nku_04_1_sign_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB02',
                                                             unrel_ref_cell_num=18),
                                                   InputPort(page=3, cell_num=4, kks=None, part='XB01',
                                                             unrel_ref_cell_num=None),
                                                   InputPort(page=3, cell_num=5, kks=None, part='XF27',
                                                             unrel_ref_cell_num=19),
                                                   InputPort(page=3, cell_num=12, kks=None, part='XB07',
                                                             unrel_ref_cell_num=20)]
        sc_nku_04_1_sign: Template = Template(name='SC_NKU_04_1_SIGN',
                                              input_ports={'XA00': sc_nku_04_1_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_nku_04_1_sign_without_bpu: Template = Template(name='SC_NKU_04_1_SIGN_WITHOUT_BPU',
                                                          input_ports={'XA00': sc_nku_04_1_sign_input},
                                                          output_ports={'XA00': cb_output})

        ltc_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB10',
                                                unrel_ref_cell_num=None)]

        ltc_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XL11'),
                                        OutputPort(name='Port2', kks=None, part='XL12')]

        ltc_ts_input: list[InputPort] = [InputPort(page=3, cell_num=10, kks=None, part='XL11',
                                                   unrel_ref_cell_num=None),
                                         InputPort(page=3, cell_num=11, kks=None, part='XL12',
                                                   unrel_ref_cell_num=None)]
        ltc_ts_data: TSODUData = TSODUData(confirm_command_page='3', confirm_command_cell=12,
                                           input_ports=ltc_ts_input,
                                           output_ports=[])

        ltc: Template = Template(name='LTC',
                                 input_ports={'XA20': ltc_input},
                                 output_ports={'XA20': ltc_output},
                                 ts_odu_data=ltc_ts_data,
                                 alarm_sound_signal_port=None)

        ltc_without_bpu: Template = Template(name='LTC_WITHOUT_BPU',
                                             input_ports={'XA20': ltc_input},
                                             output_ports={'XA20': ltc_output})

        ltc_failure_input: list[InputPort] = [InputPort(page=1, cell_num=7, kks='_0BBT__GH103', part='XF24',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=8, kks=None, part='XF34',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=9, kks='_0BBT__EK011', part='XK26',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=10, kks='_0BBT__EK021', part='XK26',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=11, kks='_0BBT__EK001', part='XM29',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=12, kks='_0BBT__EK002', part='XM29',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=13, kks='_0BBT__EK001', part='XM30',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=14, kks='_0BBT__EK002', part='XM30',
                                                        unrel_ref_cell_num=None),
                                              ]

        ltc_failure_ts_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XF33')]

        ltc_failure_ts_data: TSODUData = TSODUData(input_ports=[],
                                                   output_ports=ltc_failure_ts_output)

        ltc_failure: Template = Template(name='LTC_FAILURE',
                                         input_ports={'XA30': ltc_failure_input},
                                         output_ports={'XA30': []},
                                         ts_odu_data=ltc_failure_ts_data,
                                         alarm_sound_signal_port=None)

        ats_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB22', unrel_ref_cell_num=18),
                                      InputPort(page=3, cell_num=4, kks=None, part='XB21',
                                                unrel_ref_cell_num=None)]

        ats_ouput: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XL21'),
                                       OutputPort(name='Port2', kks=None, part='XL22'),
                                       OutputPort(name='Port3', kks=None, part='XA20', page=3, cell_num=5),
                                       OutputPort(name='Port4', kks=None, part='XA20', page=3, cell_num=6),
                                       OutputPort(name='Port6', kks=None, part='XA20', page=3, cell_num=7),
                                       OutputPort(name='Port7', kks=None, part='XA20', page=3, cell_num=8)]

        ats_ts_output: list[OutputPort] = [OutputPort(name='Port3', kks=None, part='XB22',
                                                      blink_port_name='Port4', flicker_port_name='Port5'),
                                           OutputPort(name='Port6', kks=None, part='XB21',
                                                      blink_port_name='Port7', flicker_port_name='Port8')]

        ats_ts_input: list[InputPort] = [InputPort(page=3, cell_num=14, kks=None, part='XL21',
                                                   unrel_ref_cell_num=None),
                                         InputPort(page=3, cell_num=15, kks=None, part='XL22',
                                                   unrel_ref_cell_num=None)]

        ats_ts_data: TSODUData = TSODUData(confirm_command_page='3',
                                           confirm_command_cell=16,
                                           input_ports=ats_ts_input,
                                           output_ports=ats_ts_output)
        ats: Template = Template(name='ATS',
                                 input_ports={'XA10': ats_input},
                                 output_ports={'XA10': ats_ouput},
                                 ts_odu_data=ats_ts_data)

        ats_without_bpu: Template = Template(name='ATS_WITHOUT_BPU',
                                             input_ports={'XA10': ats_input},
                                             output_ports={'XA10': ats_ouput})

        ats_vk_ouput: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA10', page=3, cell_num=23),
                                          OutputPort(name='Port2', kks=None, part='XA10', page=3, cell_num=21),
                                          OutputPort(name='Port3', kks=None, part='XA10', page=3, cell_num=22)]
        ats_vk_ouput_2: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA10', page=2, cell_num=23),
                                            OutputPort(name='Port2', kks=None, part='XA10', page=2, cell_num=21),
                                            OutputPort(name='Port3', kks=None, part='XA10', page=2, cell_num=22)]
        ats_vk: Template = Template(name='ATS_VK',
                                    input_ports={'XA20': [], 'XA30': []},
                                    output_ports={'XA20': ats_vk_ouput, 'XA30': ats_vk_ouput_2},
                                    ts_odu_data=None)

        scw_nku_04_3_sign_input: list[InputPort] = [InputPort(page=3, cell_num=5, kks=None, part='XK17',
                                                              unrel_ref_cell_num=None),
                                                    InputPort(page=3, cell_num=6, kks=None, part='XF06',
                                                              unrel_ref_cell_num=None),
                                                    InputPort(page=3, cell_num=7, kks=None, part='XF07',
                                                              unrel_ref_cell_num=None)]

        scw_nku_04_3_sign_input_without_bpu: list[InputPort] = [InputPort(page=2, cell_num=5, kks=None, part='XK17',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2, cell_num=6, kks=None, part='XF06',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2, cell_num=7, kks=None, part='XF07',
                                                                          unrel_ref_cell_num=None)]

        cbw_ts_output: list[OutputPort] = [OutputPort(name='Port3', kks=None, part='XB02',
                                                      blink_port_name='Port4', flicker_port_name='Port5'),
                                           OutputPort(name='Port6', kks=None, part='XB01',
                                                      blink_port_name='Port7', flicker_port_name='Port8'),
                                           OutputPort(name='Port9', kks=None, part='XF19',
                                                      blink_port_name='Port10')]
        cbw_ts_data: TSODUData = TSODUData(confirm_command_page='3', confirm_command_cell=16,
                                           input_ports=cb_ts_input,
                                           output_ports=cbw_ts_output)

        scw_nku_04_3_sign: Template = Template(name='SCW_NKU_04_3_SIGN',
                                               input_ports={'XA00': scw_nku_04_3_sign_input},
                                               output_ports={'XA00': []},
                                               ts_odu_data=cbw_ts_data,
                                               alarm_sound_signal_port='Port1',
                                               warn_sound_signal_port='Port2')

        scw_nku_04_3_sign_without_bpu: Template = Template(name='SCW_NKU_04_3_SIGN_WITHOUT_BPU',
                                                           input_ports={'XA00': scw_nku_04_3_sign_input_without_bpu},
                                                           output_ports={'XA00': []})

        scw_nku_04_0_sign: Template = Template(name='SCW_NKU_04_0_SIGN',
                                               input_ports={'XA00': []},
                                               output_ports={'XA00': []},
                                               ts_odu_data=cbw_ts_data,
                                               alarm_sound_signal_port='Port1',
                                               warn_sound_signal_port='Port2')

        scw_nku_04_0_sign_without_bpu: Template = Template(name='SCW_NKU_04_0_SIGN_WITHOUT_BPU',
                                                           input_ports={'XA00': []},
                                                           output_ports={'XA00': []})

        scw_nku_04_4_sign_input: list[InputPort] = [InputPort(page=3, cell_num=5, kks=None, part='XK52',
                                                              unrel_ref_cell_num=None),
                                                    InputPort(page=3, cell_num=6, kks='_0_____EW204', part='XK00',
                                                              unrel_ref_cell_num=None),
                                                    InputPort(page=3, cell_num=7, kks=None, part='XK39',
                                                              unrel_ref_cell_num=None),
                                                    InputPort(page=3, cell_num=8, kks=None, part='XB07',
                                                              unrel_ref_cell_num=None)]

        scw_nku_04_4_sign_input_without_bpu: list[InputPort] = [InputPort(page=2, cell_num=5, kks=None, part='XK52',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2, cell_num=6, kks='_0_____EW204',
                                                                          part='XK00',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2, cell_num=7, kks=None, part='XK39',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2, cell_num=8, kks=None, part='XB07',
                                                                          unrel_ref_cell_num=None)]

        scw_nku_04_4_sign: Template = Template(name='SCW_NKU_04_4_SIGN',
                                               input_ports={'XA00': scw_nku_04_4_sign_input},
                                               output_ports={'XA00': []},
                                               ts_odu_data=cbw_ts_data,
                                               alarm_sound_signal_port='Port1',
                                               warn_sound_signal_port='Port2')

        scw_nku_04_4_sign_without_bpu: Template = Template(name='SCW_NKU_04_4_SIGN_WITHOUT_BPU',
                                                           input_ports={'XA00': scw_nku_04_4_sign_input_without_bpu},
                                                           output_ports={'XA00': []})

        atsw_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA30', page=3, cell_num=5),
                                         OutputPort(name='Port2', kks=None, part='XA30', page=3, cell_num=6),
                                         OutputPort(name='Port4', kks=None, part='XA30', page=3, cell_num=7),
                                         OutputPort(name='Port5', kks=None, part='XA30', page=3, cell_num=8)]

        atsw_ts_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XB22',
                                                       blink_port_name='Port2', flicker_port_name='Port3'),
                                            OutputPort(name='Port4', kks=None, part='XB21',
                                                       blink_port_name='Port5', flicker_port_name='Port6')]
        atsw_ts_input: list[InputPort] = [InputPort(page=2, cell_num=14, kks=None, part='XL21',
                                                    unrel_ref_cell_num=None),
                                          InputPort(page=2, cell_num=15, kks=None, part='XL22',
                                                    unrel_ref_cell_num=None)]

        atsw_ts_data: TSODUData = TSODUData(confirm_command_page='2',
                                            confirm_command_cell=16,
                                            input_ports=atsw_ts_input,
                                            output_ports=atsw_ts_output)

        atsw: Template = Template(name='ATSW_1623',
                                  input_ports={'XA10': []},
                                  output_ports={'XA10': atsw_output},
                                  ts_odu_data=atsw_ts_data)

        atsw_without_bpu: Template = Template(name='ATSW_1623_WITHOUT_BPU',
                                              input_ports={'XA10': []},
                                              output_ports={'XA10': atsw_output})

        diag_standalone_output_ports: list[OutputPort] = [OutputPort(name='Port1', kks='_0BYA__EG801', part='XW01',
                                                                     blink_port_name='Port2')]

        diag_middle_output_ports: list[OutputPort] = \
            diag_standalone_output_ports + [OutputPort(name='Port1', kks='_0BYA__EG951', part='XW01'),
                                            OutputPort(name='Port2', kks='_0BYA__EG952', part='XW01')]
        diag_first_in_row_output_ports: list[OutputPort] = \
            diag_standalone_output_ports + [OutputPort(name='Port3', kks='_0BYA__EG802', part='XW01',
                                                       blink_port_name='Port4')]

        diag1_input_ports: list[InputPort] = [InputPort(page=1, cell_num=3, kks='_0BYA__EG301', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=4, kks='_0BYA__EG302', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=5, kks='_0BYA__EG503', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=6, kks='_0BYA__EG502', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=7, kks='_0BYA__EG701', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=8, kks='_0BYA__EG401', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=2, cell_num=4, kks='_0BYA__EG901', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=2, cell_num=5, kks='_0BYA__EG902', part='XG01',
                                                        unrel_ref_cell_num=None)]
        diag1: Template = Template(name='DIAG1',
                                   input_ports={'XG00': diag1_input_ports},
                                   output_ports={'XG00': diag_middle_output_ports},
                                   alarm_sound_signal_port=None)

        diag1_first_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=2, cell_num=16, kks='_0BYA__EG953', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=2, cell_num=17, kks='_0BYA__EG954', part='XG01',
                                           unrel_ref_cell_num=None)]
        diag1_first: Template = Template(name='DIAG1_FIRST',
                                         input_ports={'XG00': diag1_first_input_ports},
                                         output_ports={'XG00': diag_first_in_row_output_ports},
                                         alarm_sound_signal_port=None)

        diag2_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG601', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=1, cell_num=10, kks='_0BYA__EG602', part='XG01',
                                           unrel_ref_cell_num=None)]
        diag2: Template = Template(name='DIAG2',
                                   input_ports={'XG00': diag2_input_ports,
                                                'XG20': diag2_input_ports},
                                   output_ports={'XG00': diag_middle_output_ports,
                                                 'XG20': diag_standalone_output_ports},
                                   alarm_sound_signal_port=None)
        diag2_first_input_ports: list[InputPort] = \
            diag2_input_ports + [InputPort(page=2, cell_num=16, kks='_0BYA__EG953', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=2, cell_num=17, kks='_0BYA__EG954', part='XG01',
                                           unrel_ref_cell_num=None)]

        diag2_first: Template = Template(name='DIAG2_FIRST',
                                         input_ports={'XG00': diag2_first_input_ports},
                                         output_ports={'XG00': diag_first_in_row_output_ports},
                                         alarm_sound_signal_port=None)

        diag_bya03_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG311', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=1, cell_num=10, kks='_0BYA__EG312', part='XG01',
                                           unrel_ref_cell_num=None)]
        diag_bya03: Template = Template(name='DIAG_BYA03',
                                        input_ports={'XG00': diag_bya03_input_ports},
                                        output_ports={'XG00': diag_middle_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya04_input_ports: list[InputPort] = \
            diag1_first_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG311', part='XG01',
                                                 unrel_ref_cell_num=None),
                                       InputPort(page=1, cell_num=10, kks='_0BYA__EG312', part='XG01',
                                                 unrel_ref_cell_num=None)]

        diag_bya04: Template = Template(name='DIAG_BYA04',
                                        input_ports={'XG00': diag_bya04_input_ports},
                                        output_ports={'XG00': diag_first_in_row_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya10_input_ports: list[InputPort] = diag_bya03_input_ports

        diag_bya10: Template = Template(name='DIAG_BYA10',
                                        input_ports={'XG00': diag_bya10_input_ports},
                                        output_ports={'XG00': diag_middle_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya21_input_ports: list[InputPort] = \
            diag2_first_input_ports + [InputPort(page=1, cell_num=11, kks='_0BYA__EG601', part='XG01',
                                                 unrel_ref_cell_num=None),
                                       InputPort(page=1, cell_num=12, kks='_0BYA__EG602', part='XG01',
                                                 unrel_ref_cell_num=None)]

        diag_bya21: Template = Template(name='DIAG_BYA21',
                                        input_ports={'XG00': diag_bya21_input_ports},
                                        output_ports={'XG00': diag_first_in_row_output_ports},
                                        alarm_sound_signal_port=None)

        custom_template_f_meas = Template(name='AO_TS_ODU_F',
                                          input_ports={'XQ22': [InputPort(page=2,
                                                                          cell_num=10,
                                                                          kks='_0MKA01CE101',
                                                                          part='XQ16',
                                                                          unrel_ref_cell_num=None),
                                                                InputPort(page=2,
                                                                          cell_num=8,
                                                                          kks='_0MKA01CE001',
                                                                          part='XQ22',
                                                                          unrel_ref_cell_num=None)]},
                                          output_ports={'XQ22': []})
        custom_template_sum = Template(name='AO_TS_ODU_SUM',
                                       input_ports={'XQ23': [InputPort(page=2,
                                                                       cell_num=8,
                                                                       kks='_0MKA01CE101',
                                                                       part='XQ23',
                                                                       unrel_ref_cell_num=None),
                                                             InputPort(page=2,
                                                                       cell_num=10,
                                                                       kks='_0MKA01CE201',
                                                                       part='XQ23',
                                                                       unrel_ref_cell_num=None)],
                                                    'XQ24': [InputPort(page=2,
                                                                       cell_num=8,
                                                                       kks='_0MKA01CE101',
                                                                       part='XQ24',
                                                                       unrel_ref_cell_num=None),
                                                             InputPort(page=2,
                                                                       cell_num=10,
                                                                       kks='_0MKA01CE201',
                                                                       part='XQ24',
                                                                       unrel_ref_cell_num=None)],
                                                    },
                                       output_ports={'XQ23': [], 'XQ24': []})

        custom_template_or_x3 = Template(name='OR_X_3',
                                         input_ports={'XE00': [
                                             InputPort(page=2,
                                                       cell_num=3,
                                                       kks=r'{schema_kks:0:7}EK011{schema_kks:12:13}',
                                                       part='XB11',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=4,
                                                       kks=r'{schema_kks:0:7}EK021{schema_kks:12:13}',
                                                       part='XB11',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=5,
                                                       kks=r'{schema_kks:0:7}EK031{schema_kks:12:13}',
                                                       part='XB11',
                                                       unrel_ref_cell_num=None),

                                             InputPort(page=2,
                                                       cell_num=8,
                                                       kks=r'{schema_kks:0:7}EK011{schema_kks:12:13}',
                                                       part='XB12',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=9,
                                                       kks=r'{schema_kks:0:7}EK021{schema_kks:12:13}',
                                                       part='XB12',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=10,
                                                       kks=r'{schema_kks:0:7}EK031{schema_kks:12:13}',
                                                       part='XB12',
                                                       unrel_ref_cell_num=None),

                                             InputPort(page=2,
                                                       cell_num=13,
                                                       kks=r'{schema_kks:0:7}EK011{schema_kks:12:13}',
                                                       part='XB70',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=14,
                                                       kks=r'{schema_kks:0:7}EK021{schema_kks:12:13}',
                                                       part='XB70',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=2,
                                                       cell_num=15,
                                                       kks=r'{schema_kks:0:7}EK031{schema_kks:12:13}',
                                                       part='XB70',
                                                       unrel_ref_cell_num=None)
                                         ]},
                                         output_ports={'XE00': []})

        ts_odu_panel1: TSODUPanel = TSODUPanel(name='10CWG09',
                                               confirm_part='XG01',
                                               confirm_kks='10CWG09CH200K',
                                               abonent=321,
                                               acknowledgment_kks='10CWG09CH100K',
                                               acknowledgment_part='XG01',
                                               lamp_test_kks='10CWG09CH011K',
                                               lamp_test_part='XG01',
                                               lamp_test_port='Port1',
                                               display_test_kks='10CWG09CH010K',
                                               display_test_part='XG01',
                                               display_test_port='Port1')
        ts_odu_panel2: TSODUPanel = TSODUPanel(name='10CWG10',
                                               confirm_part='XG01',
                                               confirm_kks='10CWG10CH200K',
                                               abonent=321,
                                               acknowledgment_kks='10CWG10CH100K',
                                               acknowledgment_part='XG01',
                                               lamp_test_kks='10CWG10CH011K',
                                               lamp_test_part='XG01',
                                               lamp_test_port='Port1',
                                               display_test_kks='10CWG10CH010K',
                                               display_test_part='XG01',
                                               display_test_port='Port1')
        ts_odu_panel3: TSODUPanel = TSODUPanel(name='10CWB40',
                                               confirm_part=None,
                                               confirm_kks=None,
                                               abonent=321,
                                               acknowledgment_kks='10CWB40CH100K',
                                               acknowledgment_part='XG01',
                                               lamp_test_kks='10CWB40CH011K',
                                               lamp_test_part='XG01',
                                               lamp_test_port='Port1',
                                               display_test_kks='10CWB40CH010K',
                                               display_test_part='XG01',
                                               display_test_port='Port1')

        display: TSODUTemplate = TSODUTemplate(name='BO_TS_ODU_DISPL%',
                                               acknolegment_page='1',
                                               acknolegment_cell='4',
                                               display_test_page='1',
                                               display_test_cell='3',
                                               input_ports=[],
                                               output_ports=[])

        lamp: TSODUTemplate = TSODUTemplate(name='BO_TS_ODU_LAMP%',
                                            lamp_test_page='1',
                                            lamp_test_cell='4',
                                            input_ports=[],
                                            output_ports=[])

        ts_odu_description: TSODUDescription = TSODUDescription(panels=[ts_odu_panel1, ts_odu_panel2, ts_odu_panel3],

                                                                alarm_sound_kks='10CWG10GH001S',
                                                                alarm_sound_part='XN06',
                                                                alarm_sound_check_kks='10CWG10CH020K',
                                                                alarm_sound_check_part='XG01',
                                                                alarm_sound_check_port='Port1',
                                                                alarm_sound_check_page='1',
                                                                alarm_sound_check_cell='8',
                                                                warning_sound_kks='10CWG10GH001S',
                                                                warning_sound_part='XN05',
                                                                warn_sound_check_kks='10CWG10CH020K',
                                                                warn_sound_check_part='XG02',
                                                                warn_sound_check_port='Port1',
                                                                warn_sound_check_page='1',
                                                                warn_sound_check_cell='8',
                                                                cabinet='10BYA02',
                                                                )

        fill_ref2_options: FillRef2Options = FillRef2Options(control_schemas_table='VIRTUAL SCHEMAS',
                                                             predifend_control_schemas_table='PREDEFINED SCHEMAS',
                                                             ref_table='REF',
                                                             sim_table='Сигналы и механизмы',
                                                             iec_table='МЭК 61850',
                                                             fake_signals_table='FAKE_SIGNALS',
                                                             templates=[ats, ats_vk, ltc, ltc_failure,
                                                                        sc_cb_24, sc_kru_10_3_sign,
                                                                        sc_kru_10_6_sign, sc_kru_10_7_sign,
                                                                        sc_kru_10_7_ext_sign,
                                                                        sc_nku_04_1_sign, scw_nku_04_0_sign,
                                                                        scw_nku_04_3_sign, scw_nku_04_4_sign, atsw,
                                                                        diag1, diag1_first, diag2, diag2_first,
                                                                        diag_bya03, diag_bya04, diag_bya10, diag_bya21,
                                                                        custom_template_or_x3,

                                                                        sc_kru_10_3_sign_without_bpu,
                                                                        sc_kru_10_6_sign_without_bpu,
                                                                        sc_kru_10_7_sign_without_bpu,
                                                                        sc_nku_04_1_sign_without_bpu,
                                                                        ltc_without_bpu, ats_without_bpu,
                                                                        scw_nku_04_3_sign_without_bpu,
                                                                        scw_nku_04_0_sign_without_bpu,
                                                                        scw_nku_04_4_sign_without_bpu,
                                                                        atsw_without_bpu
                                                                        ],
                                                             wired_signal_output_default_page=1,
                                                             wired_signal_output_default_cell=7,
                                                             wired_signal_output_blink_default_page=1,
                                                             wired_signal_output_blink_default_cell=9,
                                                             wired_signal_output_flicker_default_page=1,
                                                             wired_signal_output_flicker_default_cell=11,
                                                             ts_odu_algorithm='Логика ТС ОДУ',
                                                             ts_odu_table='Сигналы и механизмы ТС ОДУ',
                                                             ts_odu_info=ts_odu_description,
                                                             abonent_table='TPTS',
                                                             wired_signal_default_input_port='Port1',
                                                             ts_odu_templates_displ=display,
                                                             ts_odu_templates_lamp=lamp,
                                                             custom_templates_ts_odu=[custom_template_f_meas,
                                                                                      custom_template_sum],
                                                             read_english_description=True)

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->

        return Options(generate_table_options=generate_option,
                       fill_mms_address_options=fill_mms_options,
                       fill_ref2_options=fill_ref2_options)

    @staticmethod
    def load_kursk() -> 'Options':
        # <-------------------------------generate_table_options------------------------------------------------------->
        signal1: DoublePointSignal = DoublePointSignal(single_part='XB00',
                                                       on_part='XB01',
                                                       off_part='XB02')
        signal2: DoublePointSignal = DoublePointSignal(single_part='XA00',
                                                       on_part='XA01',
                                                       off_part='XA02')
        signal3: DoublePointSignal = DoublePointSignal(single_part='XB20',
                                                       on_part='XB21',
                                                       off_part='XB22')
        signal4: DoublePointSignal = DoublePointSignal(single_part='XA20',
                                                       on_part='XA21',
                                                       off_part='XA22')
        signal5: DoublePointSignal = DoublePointSignal(single_part='XB30',
                                                       on_part='XB31',
                                                       off_part='XB32')
        signal6: DoublePointSignal = DoublePointSignal(single_part='XA10',
                                                       on_part='XA11',
                                                       off_part='XA12')
        sw_template1: SWTemplate = SWTemplate(connection='NTSW0113',
                                              signals={'XB01', 'XB02', 'XA01', 'XA02', 'XB07', 'XB08'},
                                              variants=[SWTemplateVariant(schema=['SCW_NKU_04_2_SIGN_WITHOUT_ME'],
                                                                          parts=['XF27', 'XK17'],
                                                                          schema_part='XA30'),
                                                        SWTemplateVariant(schema=['SCW_NKU_04_2_SIGN_WITHOUT_ME'],
                                                                          parts=['XF27', 'XK77'],
                                                                          schema_part='XA20'),
                                                        SWTemplateVariant(schema=['SCW_NKU_04_1_SIGN_WITHOUT_ME'],
                                                                          parts=['XB07'],
                                                                          schema_part='XA10')])
        sw_template2: SWTemplate = SWTemplate(connection='NTSW0114',
                                              signals={'XB21', 'XB22', 'XA21', 'XA22'},
                                              variants=[SWTemplateVariant(schema=['ATSW_1623_WITHOUT_BPU'],
                                                                          parts=[],
                                                                          schema_part='XA10')])

        generate_option: GenerateTableOptions = GenerateTableOptions(network_data_table_name='Network Data',
                                                                     controller_data_table_name='TPTS',
                                                                     aep_table_name='Сигналы и механизмы АЭП',
                                                                     sim_table_name='Сигналы и механизмы',
                                                                     iec_table_name='МЭК 61850',
                                                                     ied_table_name='IED',
                                                                     ps_table_name='PREDEFINED_SCHEMAS',
                                                                     fake_signals_table_name='FAKE_SIGNALS',
                                                                     ref_table_name='REF',
                                                                     sign_table_name='DIAG',
                                                                     skip_duplicate_signals=[],
                                                                     dps_signals=[signal1, signal2, signal3, signal4,
                                                                                  signal5, signal6],
                                                                     sw_templates=[sw_template1, sw_template2],
                                                                     copy_ds_to_sim_table=False)
        # <-------------------------------generate_table_options------------------------------------------------------->

        # <-------------------------------fill_mms_address_options----------------------------------------------------->
        dps_signal_cb = DPCSignal(signal_part=('XB01', 'XB02'),
                                  command_part=('XA01', 'XA02'))

        dps_signal_alt = DPCSignal(signal_part=('XB21', 'XB22'),
                                   command_part=('XA21', 'XA22'))

        dps_signal_gb = DPCSignal(signal_part=('XB31', 'XB32'),
                                  command_part=None)

        bsc_signal = BSCSignal(signal_part='XB10',
                               command_part=('XA11', 'XA12'))

        dataset_1: DatasetDescription = DatasetDescription(name='Dataset01',
                                                           sps_range=SignalRange(1, 50),
                                                           path='Device/LLN0.DataSet01',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS101',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS101')

        dataset_2: DatasetDescription = DatasetDescription(name='Dataset0',
                                                           sps_range=SignalRange(51, 75),
                                                           spc_range=SignalRange(1, 10),
                                                           dpc_range=SignalRange(1, 10),
                                                           bsc_range=SignalRange(1, 2),
                                                           path='Device/LLN0.DataSet02',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS201',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS201')

        dataset_3: DatasetDescription = DatasetDescription(name='Dataset03',
                                                           mv_range=SignalRange(1, 25),
                                                           path='Device/LLN0.DataSet03',
                                                           rcb_main='Device/LLN0.RP.Report_A_DS301',
                                                           rcb_res='Device/LLN0.RP.Report_B_DS301')

        dpc_signals: list[DPCSignal] = [dps_signal_cb, dps_signal_alt, dps_signal_gb]

        fill_mms_options: FillMMSAddressOptions = FillMMSAddressOptions(iec_table_name='МЭК 61850',
                                                                        ied_table_name='IED',
                                                                        dpc_signals=dpc_signals,
                                                                        bsc_signals=[bsc_signal],
                                                                        datasets=DatasetDescriptionList(
                                                                            [dataset_1, dataset_2, dataset_3]),
                                                                        mms_table_name='MMS')
        # <-------------------------------fill_mms_address_options----------------------------------------------------->

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->

        scw_nku_04_1_sign_without_me_input_ports_var_1: list[InputPort] = [
            InputPort(page=3, cell_num=5, kks='_0_____EK204',
                      part='XB07', unrel_ref_cell_num=None)]

        scw_nku_04_1_sign_without_me_output_ports: list[OutputPort] = []
        scw_nku_04_1_sign_without_me: Template = Template(name='SCW_NKU_04_1_SIGN_WITHOUT_ME',
                                                          input_ports={
                                                              'XA10': scw_nku_04_1_sign_without_me_input_ports_var_1},
                                                          output_ports={
                                                              'XA10': scw_nku_04_1_sign_without_me_output_ports},
                                                          alarm_sound_signal_port='Port1',
                                                          warn_sound_signal_port='Port2')

        scw_nku_04_1_sign_without_me_input_ports_var_1: list[InputPort] = [
            InputPort(page=3, cell_num=5, kks=None,
                      part='XF27', unrel_ref_cell_num=None),
            InputPort(page=3, cell_num=6, kks=None,
                      part='XK77', unrel_ref_cell_num=None),
        ]

        scw_nku_04_1_sign_without_me_input_ports_var_2: list[InputPort] = [
            InputPort(page=3, cell_num=5, kks=None,
                      part='XF27', unrel_ref_cell_num=None),
            InputPort(page=3, cell_num=6, kks=None,
                      part='XK17', unrel_ref_cell_num=None),
        ]

        scw_nku_04_2_sign_without_me: Template = Template(name='SCW_NKU_04_2_SIGN_WITHOUT_ME',
                                                          input_ports={
                                                              'XA20': scw_nku_04_1_sign_without_me_input_ports_var_1,
                                                              'XA30': scw_nku_04_1_sign_without_me_input_ports_var_2
                                                          },
                                                          output_ports={
                                                              'XA20': scw_nku_04_1_sign_without_me_output_ports,
                                                              'XA30': scw_nku_04_1_sign_without_me_output_ports},
                                                          alarm_sound_signal_port='Port1',
                                                          warn_sound_signal_port='Port2')

        sc_nku_04_1_sign_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB02',
                                                             unrel_ref_cell_num=18),
                                                   InputPort(page=3, cell_num=4, kks=None, part='XB01',
                                                             unrel_ref_cell_num=None),
                                                   InputPort(page=3, cell_num=5, kks=None, part='XF27',
                                                             unrel_ref_cell_num=19),
                                                   InputPort(page=3, cell_num=12, kks=None, part='XB07',
                                                             unrel_ref_cell_num=20)]

        cb_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA01'),
                                       OutputPort(name='Port2', kks=None, part='XA02')]

        cb_ts_data: TSODUData = TSODUData(input_ports=[],
                                          output_ports=[])

        sc_nku_04_1_sign: Template = Template(name='SC_NKU_04_1_SIGN_WITHOUT_ME',
                                              input_ports={'XA00': sc_nku_04_1_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_kru_10_6_sign_input: list[InputPort] = [
            InputPort(page=3, cell_num=3, kks=None, part='XB02',
                      unrel_ref_cell_num=18),
            InputPort(page=3, cell_num=4, kks=None, part='XB01',
                      unrel_ref_cell_num=None),
            InputPort(page=3, cell_num=5, kks=None, part='XF02',
                      unrel_ref_cell_num=19),
            InputPort(page=3, cell_num=6, kks=None, part='XF03',
                      unrel_ref_cell_num=20),
            InputPort(page=3, cell_num=7, kks=None, part='XF27',
                      unrel_ref_cell_num=21),
            InputPort(page=3, cell_num=8, kks=None, part='XF26',
                      unrel_ref_cell_num=22),
            InputPort(page=3, cell_num=9, kks=None, part='XF09',
                      unrel_ref_cell_num=23),
            InputPort(page=3, cell_num=10, kks=None, part='XB08',
                      unrel_ref_cell_num=24),
            InputPort(page=3, cell_num=12, kks=None, part='XB07',
                      unrel_ref_cell_num=25)]
        sc_kru_10_6_sign: Template = Template(name='SC_KRU_10_6_SIGN_WITHOUT_ME',
                                              input_ports={'XA00': sc_kru_10_6_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        sc_kru_10_6_sign_without_contr: Template = Template(name='SC_KRU_10_6_SIGN_WITHOUT_ME_C',
                                                            input_ports={'XA00': sc_kru_10_6_sign_input},
                                                            output_ports={'XA00': []},
                                                            ts_odu_data=cb_ts_data,
                                                            alarm_sound_signal_port='Port3',
                                                            warn_sound_signal_port='Port4')

        sc_kru_10_8_sign_input: list[InputPort] = [
            InputPort(page=3, cell_num=3, kks=None, part='XB02',
                      unrel_ref_cell_num=18),
            InputPort(page=3, cell_num=4, kks=None, part='XB01',
                      unrel_ref_cell_num=None),
            InputPort(page=3, cell_num=5, kks=None, part='XF02',
                      unrel_ref_cell_num=19),
            InputPort(page=3, cell_num=6, kks=None, part='XF03',
                      unrel_ref_cell_num=20),
            InputPort(page=3, cell_num=7, kks=None, part='XF27',
                      unrel_ref_cell_num=21),
            InputPort(page=3, cell_num=8, kks=None, part='XF26',
                      unrel_ref_cell_num=22),
            InputPort(page=3, cell_num=9, kks=None, part='XF09',
                      unrel_ref_cell_num=23),
            InputPort(page=3, cell_num=10, kks=None, part='XB08',
                      unrel_ref_cell_num=24),
            InputPort(page=3, cell_num=11, kks=None, part='XK02',
                      unrel_ref_cell_num=25),
            InputPort(page=3, cell_num=12, kks=None, part='XK20',
                      unrel_ref_cell_num=26),
            InputPort(page=3, cell_num=13, kks=None, part='XB07',
                      unrel_ref_cell_num=27)]
        sc_kru_10_8_sign: Template = Template(name='SC_KRU_10_8_SIGN_WITHOUT_ME',
                                              input_ports={'XA00': sc_kru_10_8_sign_input},
                                              output_ports={'XA00': cb_output},
                                              ts_odu_data=cb_ts_data,
                                              alarm_sound_signal_port='Port3',
                                              warn_sound_signal_port='Port4')

        ats_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks=None, part='XB22', unrel_ref_cell_num=18),
                                      InputPort(page=3, cell_num=4, kks=None, part='XB21',
                                                unrel_ref_cell_num=None)]
        ats_ouput: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA21'),
                                       OutputPort(name='Port2', kks=None, part='XA22'),
                                       OutputPort(name='Port3', kks=None, part='XA20', page=3, cell_num=5),
                                       OutputPort(name='Port4', kks=None, part='XA20', page=3, cell_num=6),
                                       OutputPort(name='Port6', kks=None, part='XA20', page=3, cell_num=7),
                                       OutputPort(name='Port7', kks=None, part='XA20', page=3, cell_num=8)]
        ats_without_bpu: Template = Template(name='ATS_WITHOUT_BPU',
                                             input_ports={'XA10': ats_input},
                                             output_ports={'XA10': ats_ouput})

        ats_vk_ouput: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA10', page=3, cell_num=23),
                                          OutputPort(name='Port2', kks=None, part='XA10', page=3, cell_num=21),
                                          OutputPort(name='Port3', kks=None, part='XA10', page=3, cell_num=22)]
        ats_vk_ouput_2: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA10', page=2, cell_num=23),
                                            OutputPort(name='Port2', kks=None, part='XA10', page=2, cell_num=21),
                                            OutputPort(name='Port3', kks=None, part='XA10', page=2, cell_num=22)]
        ats_vk: Template = Template(name='ATS_VK',
                                    input_ports={'XA20': [], 'XA30': []},
                                    output_ports={'XA20': ats_vk_ouput, 'XA30': ats_vk_ouput_2},
                                    ts_odu_data=None)

        ltc_input: list[InputPort] = [InputPort(page=3, cell_num=3, kks='_0BBT0_CE001', part='XQ28',
                                                unrel_ref_cell_num=None)]

        ltc_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA11'),
                                        OutputPort(name='Port2', kks=None, part='XA12')]

        ltc_ts_input: list[InputPort] = [InputPort(page=3, cell_num=10, kks=None, part='XA11',
                                                   unrel_ref_cell_num=None),
                                         InputPort(page=3, cell_num=11, kks=None, part='XA12',
                                                   unrel_ref_cell_num=None)]
        ltc_ts_data: TSODUData = TSODUData(input_ports=ltc_ts_input,
                                           output_ports=[])

        ltc: Template = Template(name='LTC_WITHOUT_CONF',
                                 input_ports={'XA20': ltc_input},
                                 output_ports={'XA20': ltc_output},
                                 ts_odu_data=ltc_ts_data,
                                 alarm_sound_signal_port=None)

        atsw_output: list[OutputPort] = [OutputPort(name='Port1', kks=None, part='XA30', page=3, cell_num=5),
                                         OutputPort(name='Port2', kks=None, part='XA30', page=3, cell_num=6),
                                         OutputPort(name='Port4', kks=None, part='XA30', page=3, cell_num=7),
                                         OutputPort(name='Port5', kks=None, part='XA30', page=3, cell_num=8)]

        atsw_without_bpu: Template = Template(name='ATSW_1623_WITHOUT_BPU',
                                              input_ports={'XA10': []},
                                              output_ports={'XA10': atsw_output})
        signal_set_xh52_input = [InputPort(page=1, cell_num=8, kks=None, part='XM84',
                                           unrel_ref_cell_num=None)]
        signal_set_xh52: Template = Template(name='ANALOG_SIGNAL_SET',
                                             input_ports={'XH52': signal_set_xh52_input},
                                             output_ports={'XH52': []})

        # --------------------------------------------------------------------------------------------------------------
        diag_standalone_output_ports: list[OutputPort] = [OutputPort(name='Port1', kks='_0BYA__EG801', part='XW01',
                                                                     blink_port_name='Port2')]

        xq_s_input_ports: list[InputPort] = [InputPort(page=1, cell_num=7, kks=None, part='XQ23',
                                                       unrel_ref_cell_num=None),
                                             InputPort(page=1, cell_num=11, kks=None, part='XQ24',
                                                       unrel_ref_cell_num=None)]
        xq_s_output_ports: list[OutputPort] = []
        template_xq_s: Template = Template(name='XQ_S',
                                           input_ports={'XQ25': xq_s_input_ports},
                                           output_ports={'XQ25': xq_s_output_ports})

        diag_middle_output_ports: list[OutputPort] = \
            diag_standalone_output_ports + [OutputPort(name='Port1', kks='_0BYA__EG951', part='XW01'),
                                            OutputPort(name='Port2', kks='_0BYA__EG952', part='XW01')]
        diag_first_output_ports: list[OutputPort] = \
            diag_standalone_output_ports + [OutputPort(name='Port3', kks='_0BYA__EG802', part='XW01',
                                                       blink_port_name='Port4')]

        diag1_input_ports: list[InputPort] = [InputPort(page=1, cell_num=3, kks='_0BYA__EG301', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=4, kks='_0BYA__EG302', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=5, kks='_0BYA__EG503', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=6, kks='_0BYA__EG502', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=7, kks='_0BYA__EG701', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=1, cell_num=8, kks='_0BYA__EG401', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=2, cell_num=4, kks='_0BYA__EG901', part='XG01',
                                                        unrel_ref_cell_num=None),
                                              InputPort(page=2, cell_num=5, kks='_0BYA__EG902', part='XG01',
                                                        unrel_ref_cell_num=None)]
        diag1: Template = Template(name='DIAG1',
                                   input_ports={'XG00': diag1_input_ports},
                                   output_ports={'XG00': diag_middle_output_ports},
                                   alarm_sound_signal_port=None)

        diag1_first_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=2, cell_num=16, kks='_0BYA__EG953', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=2, cell_num=17, kks='_0BYA__EG954', part='XG01',
                                           unrel_ref_cell_num=None)]
        diag1_first: Template = Template(name='DIAG1_FIRST',
                                         input_ports={'XG00': diag1_first_input_ports},
                                         output_ports={'XG00': diag_first_output_ports},
                                         alarm_sound_signal_port=None)

        diag2_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG601', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=1, cell_num=10, kks='_0BYA__EG602', part='XG01',
                                           unrel_ref_cell_num=None)]
        diag2: Template = Template(name='DIAG2',
                                   input_ports={'XG00': diag2_input_ports,
                                                'XG20': diag2_input_ports},
                                   output_ports={'XG00': diag_middle_output_ports,
                                                 'XG20': diag_standalone_output_ports},
                                   alarm_sound_signal_port=None)
        diag2_first_input_ports: list[InputPort] = \
            diag2_input_ports + [InputPort(page=2, cell_num=16, kks='_0BYA__EG953', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=2, cell_num=17, kks='_0BYA__EG954', part='XG01',
                                           unrel_ref_cell_num=None)]

        diag2_first: Template = Template(name='DIAG2_FIRST',
                                         input_ports={'XG00': diag2_first_input_ports},
                                         output_ports={'XG00': diag_first_output_ports},
                                         alarm_sound_signal_port=None)

        diag_bya03_input_ports: list[InputPort] = \
            diag1_first_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG311', part='XG01',
                                                 unrel_ref_cell_num=None),
                                       InputPort(page=1, cell_num=10, kks='_0BYA__EG312', part='XG01',
                                                 unrel_ref_cell_num=None)]
        diag_bya03: Template = Template(name='DIAG_BYA03_KURSK',
                                        input_ports={'XG00': diag_bya03_input_ports},
                                        output_ports={'XG00': diag_first_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya04_input_ports: list[InputPort] = \
            diag1_input_ports + [InputPort(page=1, cell_num=9, kks='_0BYA__EG311', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=1, cell_num=10, kks='_0BYA__EG312', part='XG01',
                                           unrel_ref_cell_num=None)]

        diag_bya04: Template = Template(name='DIAG_BYA04_KURSK',
                                        input_ports={'XG00': diag_bya04_input_ports},
                                        output_ports={'XG00': diag_middle_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya10_input_ports: list[InputPort] = diag_bya03_input_ports

        diag_bya10: Template = Template(name='DIAG_BYA10_KURSK',
                                        input_ports={'XG00': diag_bya10_input_ports},
                                        output_ports={'XG00': diag_first_output_ports},
                                        alarm_sound_signal_port=None)

        diag_bya21_input_ports: list[InputPort] = \
            diag2_input_ports + [InputPort(page=1, cell_num=11, kks='_0BYA__EG601', part='XG01',
                                           unrel_ref_cell_num=None),
                                 InputPort(page=1, cell_num=12, kks='_0BYA__EG602', part='XG01',
                                           unrel_ref_cell_num=None)]

        diag_bya21: Template = Template(name='DIAG_BYA21_KURSK',
                                        input_ports={'XG00': diag_bya21_input_ports},
                                        output_ports={'XG00': diag_middle_output_ports},
                                        alarm_sound_signal_port=None)

        # --------------------------------------------------------------------------------------------------------------
        custom_template_acknow = Template(name='BI_ACKNOW_WITH_EXT_SIGN_5P_1671',
                                          input_ports={'XG01': [InputPort(page=2,
                                                                          cell_num=7,
                                                                          kks='_0CWB60CH101K',
                                                                          part='XG02',
                                                                          unrel_ref_cell_num=None)],
                                                       'XG02': [InputPort(page=2,
                                                                          cell_num=7,
                                                                          kks='_0CWB60CH100K',
                                                                          part='XG02',
                                                                          unrel_ref_cell_num=None)],
                                                       },
                                          output_ports={'XG01': [], 'XG02': []})

        # --------------------------------------------------------------------------------------------------------------
        ts_odu_panel1: TSODUPanel = TSODUPanel(name='10CWG10',
                                               abonent=321,
                                               display_test_kks='10CWG10CH010K',
                                               display_test_part='XG01',
                                               display_test_port='Port1',
                                               confirm_kks=None,
                                               confirm_part=None,
                                               acknowledgment_kks='10CWG10CH101',
                                               acknowledgment_part='XG01',
                                               acknowledgment_flash_kks='10CWG10CH100',
                                               acknowledgment_flash_part='XG02')
        ts_odu_panel2: TSODUPanel = TSODUPanel(name='10CWB60',
                                               confirm_part=None,
                                               confirm_kks=None,
                                               abonent=321,
                                               acknowledgment_kks='10CWB60CH101K',
                                               acknowledgment_part='XG01',
                                               acknowledgment_flash_kks='10CWB60CH100K',
                                               acknowledgment_flash_part='XG01',
                                               lamp_test_kks='10CWB60CH011K',
                                               lamp_test_part='XG01',
                                               lamp_test_port='Port1',
                                               display_test_kks='10CWB60CH010K',
                                               display_test_part='XG01',
                                               display_test_port='Port1', )

        display: TSODUTemplate = TSODUTemplate(name='BO_TS_ODU_DISPL_WITH_FLASH_AKNOW%',
                                               acknolegment_page='1',
                                               acknolegment_cell='5',
                                               acknolegment_flash_page='1',
                                               acknolegment_flash_cell='4',
                                               display_test_page='1',
                                               display_test_cell='3',
                                               input_ports=[],
                                               output_ports=[])

        lamp: TSODUTemplate = TSODUTemplate(name='BO_TS_ODU_LAMP%',
                                            lamp_test_page='1',
                                            lamp_test_cell='4',
                                            input_ports=[],
                                            output_ports=[])

        ts_odu_description: TSODUDescription = TSODUDescription(panels=[ts_odu_panel1, ts_odu_panel2],
                                                                alarm_sound_kks='10CWG10GH001',
                                                                alarm_sound_part='XN04',
                                                                alarm_sound_check_kks='10CWG10CH020V',
                                                                alarm_sound_check_part='XG01',
                                                                alarm_sound_check_port='Port1',
                                                                alarm_sound_check_page='1',
                                                                alarm_sound_check_cell='8',
                                                                warning_sound_kks='10CWG10GH001',
                                                                warning_sound_part='XN05',
                                                                warn_sound_check_kks='10CWG10CH020W',
                                                                warn_sound_check_part='XG01',
                                                                warn_sound_check_port='Port1',
                                                                warn_sound_check_page='1',
                                                                warn_sound_check_cell='8',
                                                                cabinet='10BYA01'
                                                                )

        fill_ref2_options: FillRef2Options = FillRef2Options(control_schemas_table='VIRTUAL SCHEMAS',
                                                             predifend_control_schemas_table='PREDEFINED SCHEMAS',
                                                             ref_table='REF',
                                                             sim_table='Сигналы и механизмы',
                                                             iec_table='МЭК 61850',
                                                             fake_signals_table='FAKE_SIGNALS',
                                                             templates=[scw_nku_04_1_sign_without_me,
                                                                        signal_set_xh52,
                                                                        scw_nku_04_2_sign_without_me,
                                                                        sc_nku_04_1_sign, sc_kru_10_6_sign,
                                                                        sc_kru_10_8_sign, ats_without_bpu,
                                                                        sc_kru_10_6_sign_without_contr,
                                                                        ats_vk, ltc, atsw_without_bpu,
                                                                        diag1, diag1_first, diag2, diag2_first,
                                                                        diag_bya03, diag_bya04, diag_bya10, diag_bya21,
                                                                        template_xq_s],
                                                             wired_signal_output_default_page=1,
                                                             wired_signal_output_default_cell=7,
                                                             wired_signal_output_blink_default_page=1,
                                                             wired_signal_output_blink_default_cell=9,
                                                             wired_signal_output_flicker_default_page=1,
                                                             wired_signal_output_flicker_default_cell=11,
                                                             ts_odu_algorithm='Логика ТС ОДУ',
                                                             ts_odu_table='Сигналы и механизмы ТС ОДУ',
                                                             ts_odu_info=ts_odu_description,
                                                             abonent_table='TPTS',
                                                             wired_signal_default_input_port='Port1',
                                                             ts_odu_templates_displ=display,
                                                             ts_odu_templates_lamp=lamp,
                                                             custom_templates_ts_odu=[custom_template_acknow],
                                                             read_english_description=False)

        # <-------------------------------fill_ref2_address_options---------------------------------------------------->

        return Options(generate_table_options=generate_option, fill_mms_address_options=fill_mms_options,
                       fill_ref2_options=fill_ref2_options)
