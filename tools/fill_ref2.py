import logging
from dataclasses import dataclass

from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class InputPort:
    page: int
    cell_num: int
    kks: str | None
    part: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class OutputPort:
    name: str
    page: int
    cell_num: int
    kks: str | None
    part: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Template:
    name: str
    input_ports: [InputPort]
    output_ports: [OutputPort]

    def clone(self) -> 'Template':
        return Template(self.name, self.input_ports, self.output_ports)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class SignalRef:
    kks: str
    part: str
    ref: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FillRef2Options:
    control_schemas_table: str
    predifend_control_schemas_table: str
    ref_table: str
    sim_table: str
    iec_table: str
    templates: [Template]
    wired_signal_input_page: int
    wired_signal_input_cell: int
    wired_signal_output_page: int
    wired_signal_output_cell: int


class FillRef2:
    _options: FillRef2Options
    _access: Connection

    def __init__(self, options: FillRef2Options, access: Connection):
        self._options = options
        self._access = access

    def _get_signal_for_port(self, schema_kks: str, cabinet: str, kksp: str, port: InputPort | OutputPort,
                             template_name) -> tuple[str, str, bool] | None:
        """
        Функция поиска сигнала для порта шаблона
        :param schema_kks: KKS схемы управления
        :param cabinet: Имя стойки
        :param kksp: KKS терминала
        :param port: Порт шаблона
        :param template_name: Имя шаблона
        :return: Сигнал как кортеж KKS, PART, ФлагЦифровогоСигнала
        """
        kks: str = port.kks if port.kks is not None else schema_kks
        # Поиск сигнала в таблице СИМ по KKS, PART и KKSp
        values_from_sim: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS'],
            key_names=['KKS', 'MODULE', 'KKSp', 'PART', 'CABINET'],
            key_values=[kks, '1691', kksp, port.part, cabinet],
            key_operator=['LIKE', '<>', '=', '=', '='])
        if len(values_from_sim) > 1:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if len(values_from_sim) == 1:
            return values_from_sim[0]['KKS'], port.part, False
        # Поиск сигнала в таблице МЭК по KKS, PART и KKSp
        values_from_iec: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.iec_table,
                                                                           fields=['KKS'],
                                                                           key_names=['KKS', 'KKSp', 'PART', 'CABINET'],
                                                                           key_values=[kks, kksp, port.part, cabinet],
                                                                           key_operator=['LIKE', '=', '=', '='])
        if len(values_from_iec) > 1:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if len(values_from_iec) == 1:
            return values_from_iec[0]['KKS'], port.part, True
        # Если сигнал задан шаблоном, то на этом этапе он уже должен быть найден
        if port.kks is not None:
            logging.error(f'Не найден сигнао для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
        # Поиск сигнала в таблице СИМ по PART и KKSp
        values_from_sim_with_kksp: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS'],
            key_names=['MODULE', 'KKSp', 'PART', 'CABINET'],
            key_values=['1691', kksp, port.part, cabinet],
            key_operator=['<>', '=', '=', '='])
        if len(values_from_sim_with_kksp) > 1:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if len(values_from_sim_with_kksp) == 1:
            return values_from_sim[0]['KKS'], port.part, False
        # Поиск сигнала в таблице МЭК по PART и KKSp
        values_from_iec_with_kksp: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.iec_table,
            fields=['KKS'],
            key_names=['KKSp', 'PART', 'CABINET'],
            key_values=[kksp, port.part, cabinet])
        if len(values_from_iec_with_kksp) > 1:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if len(values_from_iec_with_kksp) == 1:
            return values_from_iec[0]['KKS'], port.part, True
        logging.error(f'Не найден сигнао для шаблона {template_name} с KKS {schema_kks} для порта '
                      f'с PART {port.part}')
        return None

    def _get_kksp_for_template(self, template: Template, schema_kks: str, cabinet: str) -> str | None:
        """
        Функция определения KKSp для заданного шаблона и ККС
        :param template: шаблон схемы управления
        :param: kks: ККС схемы управления
        :return: KKSp для данного KKS
        """
        kksp_list: list[str] = []
        for output_port in template.output_ports:
            values_from_sim: list[dict[str, str]]
            kks: str = output_port.kks if output_port.kks is not None else schema_kks
            values_from_sim = self._access.retrieve_data(table_name=self._options.sim_table,
                                                         fields=['KKSp'],
                                                         key_names=['KKS', 'PART', 'MODULE', 'CABINET'],
                                                         key_values=[kks, output_port.part, '1691', cabinet],
                                                         key_operator=['LIKE', '=', '<>', '='])
            if len(values_from_sim) > 1:
                logging.error(f'Найдено больше одной команды {output_port.part} для шаблона {template.name} '
                              f'c KKS={schema_kks}')
                return None

            values_from_iec: list[dict[str, str]]
            values_from_iec = self._access.retrieve_data(table_name=self._options.iec_table,
                                                         fields=['KKSp'],
                                                         key_names=['KKS', 'PART', 'CABINET'],
                                                         key_values=[kks, output_port.part, cabinet],
                                                         key_operator=['LIKE', '=', '='])
            if len(values_from_iec) > 1 or (len(values_from_iec) == 1 and len(values_from_sim) == 1):
                logging.error(f'Найдено больше одной команды {output_port.part} для шаблона {template.name}'
                              f' c KKS={schema_kks}')
                return None
            if len(values_from_iec) == 0 and len(values_from_sim) == 0:
                logging.error(f'Не найдена команда {output_port.part} для шаблона {template.name} c KKS={schema_kks}')
                return None
            kksp: str = values_from_sim[0]['KKSp'] if len(values_from_sim) == 1 else values_from_iec[0]['KKSp']
            kksp_list.append(kksp)
        several_kksp = next((True for item in kksp_list[1:] if kksp_list[0] != item), False)
        if several_kksp:
            logging.error(f'Для команд шаблона {template.name} с KKS={schema_kks} найдены различные KKSp')
            return None
        return kksp_list[0]

    def get_ref_for_defined_schemas(self):
        error_flag: bool = False
        ref_list: list[SignalRef] = []
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'SCHEMA', 'PART', 'CABINET'])
        for value in values:
            kks = value['KKS']
            part = value['PART']
            cabinet = value['CABINET']
            template_name = value['SCHEMA']
            template: Template | None = next((templ for templ in self._options.templates
                                              if templ.name == template_name), None)
            if template is None:
                logging.error(f'Не найден шаблон с именем {template_name}')
                error_flag = True
                continue
            kksp: str | None = self._get_kksp_for_template(template=template,
                                                           schema_kks=kks,
                                                           cabinet=cabinet)
            if kksp is None:
                error_flag = True
                continue

            for input_port in template.input_ports:
                signal: tuple[str, str, bool] | None = self._get_signal_for_port(schema_kks=kks,
                                                                                 cabinet=cabinet,
                                                                                 port=input_port,
                                                                                 kksp=kksp,
                                                                                 template_name=template_name)
                if signal is None:
                    error_flag = True
                    continue
                ref: str
                if signal[2]:
                    ref = f'{signal[0]}_{signal[1]}'
                else:
                    ref = f'{signal[0]}_{signal[1]}\\{self._options.wired_signal_input_page}' \
                          f'\\{self._options.wired_signal_input_cell}'
                signal_ref: SignalRef = SignalRef(kks=signal[0],
                                                  part=signal[1],
                                                  ref=ref)
                ref_list.append(signal_ref)

            for output_port in template.output_ports:
                signal: tuple[str, str, bool] | None = self._get_signal_for_port(schema_kks=kks,
                                                                                 cabinet=cabinet,
                                                                                 port=output_port,
                                                                                 kksp=kksp,
                                                                                 template_name=template_name)
                if signal is None:
                    error_flag = True
                    continue
                ref: str
                if signal[2]:
                    ref = f'{signal[0]}_{signal[1]}'
                else:
                    ref = f'{signal[0]}_{signal[1]}\\{self._options.wired_signal_input_page}' \
                          f'\\{self._options.wired_signal_input_cell}'
                signal_ref: SignalRef = SignalRef(kks=signal[0],
                                                  part=signal[1],
                                                  ref=ref)
                ref_list.append(signal_ref)

    @staticmethod
    def run(options: FillRef2Options, base_path: str) -> None:
        logging.info('Запуск скрипта "Расстановка ссылок"...')
        with Connection.connect_to_mdb(base_path=base_path) as access:
            fill_ref_class: FillRef2 = FillRef2(options=options,
                                                access=access)
            fill_ref_class._fill_ref()
        logging.info('Выпонение скрипта "Расстановка ссылок" завершено.')
        logging.info('')
