import logging
import os.path
from typing import List, Dict, Tuple
from dataclasses import dataclass

from tools.utils.progress_utils import ProgressBar
from tools.utils.cid_utils import ParameterData, Nodes, save_xml, get_updated_content
from tools.utils.sql_utils import Connection


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class CopyCidOptions:
    """
    Класс настроек
    """
    base_path: str
    source_cid: str
    target_path: str
    mask: str


class CopyCid:
    """
    Основной класс копирования CID файлов
    """
    _options: CopyCidOptions

    def __init__(self, options: CopyCidOptions):
        self._options = options

    def _get_data_from_base(self) -> Dict[str, List[Tuple[ParameterData, str]]]:
        """
        Загрузка данных для генерации из базы
        :return: Словарь со значениями из базы
        """
        with Connection.connect_to_mdb(self._options.base_path) as access_base:
            data: List[Dict[str, str]] = access_base.retrieve_data_from_joined_table(
                table_name1='[МЭК 61850]',
                table_name2='[IED]',
                joined_fields=['IED_NAME'],
                fields=['ICD_PATH', 'IP', '[IED].SENSR_TYPE', '[IED].IED_NAME'],
                key_names=None,
                key_values=None,
                uniq_values=True)
            data_for_xml: Dict[str, List[Tuple[ParameterData, str]]] = {}
            _, file_extension = os.path.splitext(self._options.source_cid)
            for value in data:
                file_name: str = self._options.target_path + value['ICD_PATH']
                if file_name[-4:].upper() not in ('.CID', '.ICD', 'SCD'):
                    file_name = file_name + file_extension
                parameters: List[Tuple[ParameterData, str]] = [(Nodes.IP.value, value['IP']),
                                                               (Nodes.MASK.value, self._options.mask),
                                                               (Nodes.IEDNAME.value, value['[IED].IED_NAME']),
                                                               (Nodes.DESCR.value, value['[IED].SENSR_TYPE'])]

                data_for_xml[file_name] = parameters
            return data_for_xml

    def create_files(self, data_for_xml: Dict[str, List[Tuple[ParameterData, str]]]) -> None:
        """
        Копирование файлов
        :param data_for_xml: Данные из базы со значениями свойств
        :return: None
        """
        ProgressBar.config(max_value=len(data_for_xml), step=1, prefix='Копирование файлов', suffix='Завершено')
        for file in data_for_xml:
            data: bytes = get_updated_content(source_file_name=self._options.source_cid,
                                              parameters=data_for_xml[file])
            save_xml(xml_content=data, target_file_name=file)
            ProgressBar.update_progress()

    @staticmethod
    def run(options: CopyCidOptions) -> None:
        """
        Запуск скрипта
        :param options: Настройки скрипта
        :return: None
        """
        logging.info('Запуск скрипта...')
        copy_class: CopyCid = CopyCid(options)

        logging.info('Загрузка данных из базы...')
        data_for_xml: Dict[str, List[Tuple[ParameterData, str]]] = copy_class._get_data_from_base()
        logging.info('Загрузка завершена.')

        logging.info('Запуск копирования файлов...')
        copy_class.create_files(data_for_xml=data_for_xml)
        logging.info('Выполнение завершено.')
