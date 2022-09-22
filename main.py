from tools.fill_mms_address import FillMMSAdress
from tools.fill_ref import FillRef
from tools.generate_tables import GenerateTables
from tools.find_schemas import FindSchemas
from tools.fill_ref2 import FillRef2
from tools.options import Options
from tools.utils.log_utils import configure_logger


def run_scripts():
    configure_logger('log', 'log')
    options: Options = Options.load_ruppur()
    base_path: str = 'C:\\Data\\Руппур база\\ПТК СКУ ЭЧ ЭБ_3.14.accdb'

    # Генерация таблиц из таблицы [Сигналы и механизмы АЭП]
    # Закомментировать если не используется
    GenerateTables.run(options=options.generate_table_options, base_path=base_path)

    # Расстановка MMS адресов для сигналов
    # Закомментировать если не используется
    # FillMMSAdress.run(options=options.fill_mms_address_options, base_path=base_path)

    # Расстановка ссылок
    # Закомментировать если не используется
    # FillRef.run(options=options.fill_ref_options, base_path=base_path)

    # Расстановка ссылок
    # Закомментировать если не используется
    # FillRef2.run(options=options.fill_ref2_options, base_path=base_path)

    # Поиск вариантов схем
    # Закомментировать если не используется
    # FindSchemas.run(options=options.find_schemas_options, base_path=base_path)

    # Генерация CID файлов на основе шаблона
    # Закомментировать если не используется
    # CopyCid.run(base_path='c:\\User data\\ПТК СКУ ЭЧ ЭБ_3.09.accdb',
    #             source_cid_path='c:\\User data\\All_in_one_25MV.cid',
    #             target_path='c:\\User data\\5\\',
    #             mask='255.255.255.0')


if __name__ == '__main__':
    run_scripts()
