# noinspection PyUnresolvedReferences
from tools.fill_mms_address import FillMMSAdress
# noinspection PyUnresolvedReferences
from tools.generate_tables import GenerateTables
# noinspection PyUnresolvedReferences
from tools.find_schemas import FindSchemas
# noinspection PyUnresolvedReferences
from tools.fill_ref2 import FillRef2
# noinspection PyUnresolvedReferences
from tools.repair_cid import RepairCid
# noinspection PyUnresolvedReferences
from tools.options import Options
# noinspection PyUnresolvedReferences
from tools.utils.log_utils import configure_logger
# noinspection PyUnresolvedReferences
from tools.copy_cid import CopyCid


def run_scripts():
    configure_logger('log', 'log')
    options: Options = Options.load_kursk()
    base_path: str = 'D:\\Work\\Курск база\\0.006_БД РАСУ.accdb'
    # options: Options = Options.load_ruppur()
    # base_path: str = 'D:\\Work\\Руппур база\\2.004_БД РАСУ.accdb'

    # Генерация таблиц из таблицы [Сигналы и механизмы АЭП]
    # Закомментировать если не используется
    GenerateTables.run(options=options.generate_table_options, base_path=base_path)

    # Расстановка MMS адресов для сигналов
    # Закомментировать если не используется
    FillMMSAdress.run(options=options.fill_mms_address_options, base_path=base_path)

    # Расстановка ссылок
    # Закомментировать если не используется
    FillRef2.run(options=options.fill_ref2_options, base_path=base_path)

    # Поиск вариантов схем
    # Закомментировать если не используется
    # FindSchemas.run(options=options.find_schemas_options, base_path=base_path)

    # Генерация CID файлов на основе шаблона
    # Закомментировать если не используется
    #CopyCid.run(base_path=base_path,
    #            source_cid_path='D:\\Work\\Курск база\\!CID\\!All_in_one_25MV.cid',
    #            target_path='D:\\Work\\Курск база\\!CID\\',
    #            mask='255.255.255.0')

    # RepairCid.run(cid_path='D:\\Work\\Руппур\\!CID\\',
    #               file_filter='^D10BB[A-F](.*)')


if __name__ == '__main__':
    run_scripts()
