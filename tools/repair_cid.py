import logging
import re
from os import walk

from tools.utils.cid_utils import ParameterData, save_xml, get_updated_content
from tools.utils.progress_utils import ProgressBar


class RepairCid:
    cid_path: str
    parameters: list[tuple[ParameterData, str]]
    file_filter: str | None

    def __init__(self, cid_path: str, parameters: list[tuple[ParameterData, str]], file_filter: str | None):
        self.cid_path = cid_path
        self.file_filter = file_filter
        self.parameters = parameters

    def _create_files(self, data_for_xml: dict[str, list[tuple[ParameterData, str]]]) -> None:
        ProgressBar.config(max_value=len(data_for_xml), step=1, prefix='Копирование файлов', suffix='Завершено')
        for file in data_for_xml:
            data: bytes = get_updated_content(source_file_name=self.cid_path + file,
                                              parameters=data_for_xml[file])
            save_xml(xml_content=data, target_file_name=self.cid_path + file)
            ProgressBar.update_progress()

    def repair(self):
        filenames: list[str] = next(walk(self.cid_path), (None, None, []))[2]
        filtered_filenames: list[str] = []
        if self.file_filter is not None:
            pattern = re.compile(self.file_filter)
            filtered_filenames.extend([filename for filename in filenames if pattern.match(filename)])
        else:
            filtered_filenames = filenames
        data_for_xml: dict[str, list[tuple[ParameterData, str]]] = \
            dict([(filename, self.parameters) for filename in filtered_filenames])
        self._create_files(data_for_xml=data_for_xml)

    @staticmethod
    def run(cid_path: str, file_filter: str | None, parameters: list[tuple[ParameterData, str]]):
        logging.info('Запуск скрипта...')
        repair_class: RepairCid = RepairCid(cid_path=cid_path,
                                            file_filter=file_filter,
                                            parameters=parameters)
        logging.info('Запуск исправления файлов...')
        repair_class.repair()
        logging.info('Выполнение завершено.')
