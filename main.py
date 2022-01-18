from tools.generate_tables import run, GenerateTableOptions


def fill_tables():
    run(GenerateTableOptions(path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3_test.accdb',
                             network_data_table_name='[Network Data]',
                             controller_data_table_name='TPTS',
                             aep_table_name='[Сигналы и механизмы АЭП]',
                             sim_table_name='[Сигналы и механизмы]',
                             iec_talbe_name='[МЭК 61850]'))


if __name__ == '__main__':
    fill_tables()
