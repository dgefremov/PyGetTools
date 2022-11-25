from tools.fill_mms_address import FillMMSAdress
from tools.fill_ref import FillRef
from tools.generate_tables import GenerateTables
from tools.find_schemas import FindSchemas
from tools.fill_ref2 import FillRef2
from tools.options import Options
from tools.utils.log_utils import configure_logger
from tools.copy_cid import CopyCid


def run_scripts():
    configure_logger('log', 'log')
    options: Options = Options.load_kursk()
    base_path: str = 'C:\\Data\\Курск база\\ПТК СКУ ЭЧ ЭБ КуАЭС_0.006.accdb'
    # options: Options = Options.load_kursk()
    # base_path: str = 'Y:\\Отдел ПА\\10_Текущие работы\\АЭС Курская-2\\СКУ ЭЧ ЭБ\\10_Разработка\\04_ЗЗИ\\ТПТС\\0.006 от 2022.05 (неофициально)\\Редактируемые версии\\ПТК СКУ ЭЧ ЭБ КуАЭС_0.006.accdb'

    # Генерация таблиц из таблицы [Сигналы и механизмы АЭП]
    # Закомментировать если не используется
    # GenerateTables.run(options=options.generate_table_options, base_path=base_path)

    # Расстановка MMS адресов для сигналов
    # Закомментировать если не используется
    # FillMMSAdress.run(options=options.fill_mms_address_options, base_path=base_path)

    # Расстановка ссылок
    # Закомментировать если не используется
    # FillRef.run(options=options.fill_ref_options, base_path=base_path)

    # Расстановка ссылок
    # Закомментировать если не используется
    FillRef2.run(options=options.fill_ref2_options, base_path=base_path)

    # Поиск вариантов схем
    # Закомментировать если не используется
    # FindSchemas.run(options=options.find_schemas_options, base_path=base_path)

    # Генерация CID файлов на основе шаблона
    # Закомментировать если не используется
    # CopyCid.run(base_path=base_path,
    #            source_cid_path='C:\\Data\\Курск база\\All_in_one_25MV.cid',
    #            target_path='C:\\Data\\Курск база\\!CID\\',
    #            mask='255.255.255.0')


if __name__ == '__main__':
    run_scripts()
