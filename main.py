# noinspection PyUnresolvedReferences
from tools.fill_mms_address import FillMMSAdress
# noinspection PyUnresolvedReferences
from tools.generate_tables import GenerateTables
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
from tools.utils.sql_utils import Connection


def run_scripts():
    configure_logger('log', 'log')
    options: Options = Options.load_kursk()
    # options: Options = Options.load_ruppur()
    connection: Connection = Connection.connect_to_postgres(database='kursk_un_1',
                                                            user='postgres',
                                                            password='postgres',
                                                            server='SR-RET-CAD',
                                                            port=5432)

    # Генерация таблиц из таблицы [Сигналы и механизмы АЭП]
    # Закомментировать если не используется
    GenerateTables.run(options=options.generate_table_options, connection=connection)

    # Расстановка MMS адресов для сигналов
    # Закомментировать если не используется
    FillMMSAdress.run(options=options.fill_mms_address_options, connection=connection)

    # Расстановка ссылок
    # Закомментировать если не используется
    FillRef2.run(options=options.fill_ref2_options, connection=connection)

    # Генерация CID файлов на основе шаблона
    # Закомментировать если не используется
    # CopyCid.run(connection=connection,
    #            source_cid_path='/home/dgefremov@rasu.local/Проекты/Руппур/ППО/All_in_one_25MV.cid',
    #            target_path='/home/dgefremov@rasu.local/Проекты/Руппур/ППО/CID_EMUL_un2/',
    #            mask='255.255.255.0')

    # RepairCid.run(cid_path='D:\\Work\\Руппур\\!CID\\',
    #               file_filter='^D10BB[A-F](.*)')


if __name__ == '__main__':
    run_scripts()