from typing import Dict, List
from sql_utils import SQLUtils
from utils import print_log


class Telegram:
    channels: Dict[int, str]

    def __init__(self):
        self.channels = {}

    def add_channel(self, channel: int, kks: str, part: str):
        self.channels[channel] = '{0}_{1}'.format(kks, part)


class Controller:
    telegrams: Dict[str, Telegram]

    def __init__(self):
        self.telegrams = {}

    def add_telegram(self, telegram_name: str, channel: int, kks: str, part: str):
        telegram: Telegram
        if telegram_name in self.telegrams:
            telegram = self.telegrams[telegram_name]
        else:
            telegram = Telegram()
            self.telegrams[telegram_name] = telegram
        telegram.add_channel(channel, kks, part)


def get_project_schema(postgre_base: SQLUtils, project: str) -> str:
    project_schema: List[Dict[str, str]] = postgre_base.retrieve_data('get_sys.projects', ['schema_get'],
                                                                      ['project_name'],
                                                                      [project])
    if len(project_schema) != 1:
        print_log("Не найден проект")
        raise Exception("GetBaseError")

    return project_schema[0]['schema_get']


def get_complex_id(postgre_base: SQLUtils, project_schema_name: str, complex_name: str) -> str:
    complex_ids: List[Dict[str, str]] = postgre_base.retrieve_data('{0}.complexes'.format(project_schema_name),
                                                                   ['complex_id'], ['complex_name'], [complex_name])

    if len(complex_ids) != 1:
        print_log("Не найден ПТК")
        raise Exception("GetBaseError")

    return complex_ids[0]['complex_id']


def get_abonents(postgre_base: SQLUtils, project_name: str, complex_name) -> Dict[int, Controller]:
    project_schema_name: str = get_project_schema(postgre_base, project_name)
    complex_id: str = get_complex_id(postgre_base, project_schema_name, complex_name)

    telegrams_data: List[Dict[str, str]] = postgre_base.retrieve_data(
        table_name='{0}.project_pageright'.format(project_schema_name),
        fields=['abonent_id', 'kks_source', 'signalcode', 'telegram', 'kanal'],
        key_names=['telegram', 'area'],
        key_values=['null', 'null'],
        key_operator=['IS NOT', 'IS NOT']
    )
    controller_list: Dict[int, Controller] = {}

    for telegram_data in telegrams_data:
        abonent_id: int = int(telegram_data['abonent_id'])
        telegram_name: str = telegram_data['telegram']
        channel: int = int(telegram_data['kanal'])
        kks: str = telegram_data['kks_source']
        part: str = telegram_data['signalcode']

        controller: Controller
        if abonent_id in controller_list:
            controller = controller_list[abonent_id]
        else:
            controller = Controller()
            controller_list[abonent_id] = controller
        controller.add_telegram(telegram_name, channel, kks, part)
    return controller_list
