import logging
import os.path

from tools.utils.progress_utils import ProgressBar
from tools.utils.cid_utils import ParameterData, Nodes, save_xml, get_updated_content
from tools.utils.sql_utils import Connection


# @dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
# class CopyCidOptions:
#     """
#     Класс настроек
#     """
#     base_path: str
#     source_cid: str
#     target_path: str
#     mask: str


class CopyCid:
    """
    Основной класс копирования CID файлов
    """
    _connection: Connection
    _source_cid_path: str
    _target_path: str
    _mask: str

    def __init__(self, connection: Connection, source_cid_path: str, target_path: str, mask: str):
        self._connection = connection
        self._source_cid_path = source_cid_path
        self._target_path = target_path
        self._mask = mask

    def _get_data_from_base(self) -> dict[str, list[tuple[ParameterData, str]]]:
        """
        Загрузка данных для генерации из базы
        :return: Словарь со значениями из базы
        """
        with self._connection as base:
            data: list[dict[str, str]] = base.retrieve_data_from_joined_table(
                table_name1='iec_61850',
                table_name2='ied',
                joined_fields=['ied_name'],
                fields=['icd_path', 'ip', 'sensr_type', 'ied.ied_name'],
                key_names=None,
                key_values=None,
                uniq_values=True)
            data_for_xml: dict[str, list[tuple[ParameterData, str]]] = {}
            _, file_extension = os.path.splitext(self._source_cid_path)
            for value in data:
                file_name: str = self._target_path + value['icd_path']
                if file_name[-4:].upper() not in ('.CID', '.ICD', 'SCD'):
                    file_name = file_name + file_extension
                    ip: str = value['ip']
                    ied_name: str = value['ied.ied_name']
                    sensr_type: str = value['sensr_type']
                parameters: list[tuple[any, str]] = [(Nodes.IP.value, ip),
                                                     (Nodes.MASK.value, self._mask),
                                                     (Nodes.IEDNAME.value, ied_name),
                                                     (Nodes.DESCR.value, sensr_type)]

                data_for_xml[file_name] = parameters
            return data_for_xml

    def create_files(self, data_for_xml: dict[str, list[tuple[ParameterData, str]]]) -> None:
        """
        Копирование файлов
        :param data_for_xml: Данные из базы со значениями свойств
        :return: None
        """
        ProgressBar.config(max_value=len(data_for_xml), step=1, prefix='Копирование файлов', suffix='Завершено')
        for file in data_for_xml:
            data: bytes = get_updated_content(source_file_name=self._source_cid_path,
                                              parameters=data_for_xml[file])
            save_xml(xml_content=data, target_file_name=file)
            ProgressBar.update_progress()

    @staticmethod
    def run(connection: Connection, source_cid_path: str, target_path: str, mask: str) -> None:
        logging.info('Запуск скрипта...')
        copy_class: CopyCid = CopyCid(connection=connection,
                                      source_cid_path=source_cid_path,
                                      target_path=target_path,
                                      mask=mask)

        logging.info('Загрузка данных из базы...')
        data_for_xml: dict[str, list[tuple[ParameterData, str]]] = copy_class._get_data_from_base()
        logging.info('Загрузка завершена.')

        logging.info('Запуск копирования файлов...')
        copy_class.create_files(data_for_xml=data_for_xml)
        logging.info('Выполнение завершено.')
