from typing import Set
from dataclasses import dataclass

from utils.get_base_utils import Controller, Telegram, get_abonents
from utils.sql_utils import SQLUtils
from utils.common_utils import print_log


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Options:
    user: str
    password: str
    server: str
    port: int
    base: str
    project_1: str
    project_2: str
    complex_1: str
    complex_2: str


def run(options: Options):
    with SQLUtils.Connection.connect_to_postgre(options.base, options.user, options.password, options.server,
                                                options.port) as _postgre_base:
        _controllers_from_get1 = get_abonents(_postgre_base, options.project_1, options.complex_1)
        _controllers_from_get2 = get_abonents(_postgre_base, options.project_2, options.complex_2)
    abonents1: Set[int] = set(_controllers_from_get1.keys())
    abonents2: Set[int] = set(_controllers_from_get2.keys())
    abonents_diff_1: Set[int] = abonents1.difference(abonents2)
    abonents_diff_2: Set[int] = abonents2.difference(abonents1)
    abonents_inters: Set[int] = abonents1.intersection(abonents2)

    if len(abonents_diff_1) > 0:
        [print('Абонент {} присутствует только в проекте {}'.format(item, options.project_1)) for item in
         abonents_diff_1]
    if len(abonents_diff_2) > 0:
        [print('Абонент {} присутствует только в проекте {}'.format(item, options.project_2)) for item in
         abonents_diff_2]
    for abonent_id in abonents_inters:
        controller1: Controller = _controllers_from_get1[abonent_id]
        controller2: Controller = _controllers_from_get2[abonent_id]

        telegram_names1: Set[str] = set(controller1.telegrams.keys())
        telegram_names2: Set[str] = set(controller2.telegrams.keys())
        telegram_names_diff_1: Set[str] = telegram_names1.difference(telegram_names2)
        telegram_names_diff_2: Set[str] = telegram_names2.difference(telegram_names1)
        telegram_names_inters: Set[str] = telegram_names1.intersection(telegram_names2)

        if len(telegram_names_diff_1) > 0:
            [print('Телеграмма {} присутствует только в проекте {}'.format(item, options.project_1)) for item in
             telegram_names_diff_1]
        if len(telegram_names_diff_2) > 0:
            [print('Телеграмма {} присутствует только в проекте {}'.format(item, options.project_2)) for item in
             telegram_names_diff_2]

        for telegram_name in telegram_names_inters:
            telegram1: Telegram = controller1.telegrams[telegram_name]
            telegram2: Telegram = controller2.telegrams[telegram_name]

            telegram_channels1: Set[int] = set(telegram1.channels.keys())
            telegram_channels2: Set[int] = set(telegram2.channels.keys())
            telegram_channels_diff_1: Set[int] = telegram_channels1.difference(telegram_channels2)
            telegram_channels_diff_2: Set[int] = telegram_channels2.difference(telegram_channels1)

            if len(telegram_channels_diff_1) > 0:
                [print('Канал {} телеграммы {} для контроллера {} присутствует только в проекте {}'
                       .format(item, telegram_name, abonent_id, options.project_1))
                 for item in telegram_channels_diff_1]
            if len(telegram_channels_diff_2) > 0:
                [print('Канал {} телеграммы {} для контроллера {} присутствует только в проекте {}'
                       .format(item, telegram_name, abonent_id, options.project_2))
                 for item in telegram_channels_diff_2]

            for channel in telegram1.channels:
                signal1: str = telegram1.channels[channel]
                signal2: str = telegram2.channels[channel]
                if signal1.casefold() != signal2.casefold():
                    print_log('Отличия в канале {0} телеграммы {1} в контроллере {2}'.format(
                        telegram_name, abonent_id, channel))

    print_log('Загрузка данных из get завершена.')
