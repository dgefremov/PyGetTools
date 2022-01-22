from typing import List

from tools.generate_tables import GenerateTables


def fill_tables():
    dps_signal_cb = GenerateTables.DPSSignal('XB00', ['XB01', 'XB02'], 'XL00', ['XL01', 'XL02'])
    dps_signal_alt = GenerateTables.DPSSignal('XB20', ['XB21', 'XB22'], 'XL20', ['XL21', 'XL22'])
    dps_signal_gb = GenerateTables.DPSSignal('XB30', ['XB31', 'XB32'], None, [])
    dps_signal_cb2 = GenerateTables.DPSSignal(None, [], None, ['XA01', 'XA02'])
    bsc_signal = GenerateTables.BSCSignal('XB10', 'XL10', ['XL11', 'XL12'])
    dps_signals: List[GenerateTables.DPSSignal] = [dps_signal_cb, dps_signal_cb2, dps_signal_alt, dps_signal_gb]
    GenerateTables.run(GenerateTables.GenerateTableOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3_test.accdb',
                                                           network_data_table_name='[Network Data]',
                                                           controller_data_table_name='TPTS',
                                                           aep_table_name='[Сигналы и механизмы АЭП]',
                                                           sim_table_name='[Сигналы и механизмы]',
                                                           iec_table_name='[МЭК 61850]',
                                                           skip_duplicate_prefix=['00BCE'],
                                                           dps_signals=dps_signals,
                                                           bsc_signals=[bsc_signal]))



if __name__ == '__main__':
    fill_tables()
