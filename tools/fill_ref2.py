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
    unrel_ref_cell_num: int | None


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
    unrel_ref: str | None


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
    wired_signal_input_port: str


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

    def _creare_ref_for_input_port(self, schema_kks: str, schema_part: str, cabinet: str, input_port: InputPort,
                                   kksp: str,
                                   template_name: str) -> SignalRef | None:
        """
        Создание ссылки для входного сигналы схемы управления
        :param schema_kks: KKS схемы управления
        :param schema_part: PART схемы управления
        :param cabinet: Имя стойки
        :param input_port: Входной порт
        :param kksp: KKS терминала
        :param template_name: Имя шаблона (для диагностических сообщений)
        :return: SignalRef или None
        """
        signal: tuple[str, str, bool] | None = self._get_signal_for_port(schema_kks=schema_kks,
                                                                         cabinet=cabinet,
                                                                         port=input_port,
                                                                         kksp=kksp,
                                                                         template_name=template_name)
        if signal is None:
            return None
        signal_kks: str = signal[0]
        signal_part: str = signal[1]
        is_digital: bool = signal[2]
        ref: str
        unrel_ref: str | None
        if is_digital:
            ref: str = f'{schema_kks}_{schema_part}\\{input_port.page}\\{input_port.cell_num}'
            unrel_ref = f'{schema_kks}_{schema_part}\\{input_port.page}\\{input_port.unrel_ref_cell_num}'
        else:
            ref: str = f'{self._options.wired_signal_input_port}:{schema_kks}_{schema_part}\\' \
                       f'{input_port.page}\\{input_port.cell_num}'
            unrel_ref = None
        signal_ref: SignalRef = SignalRef(kks=signal_kks,
                                          part=signal_part,
                                          ref=ref,
                                          unrel_ref=unrel_ref)
        return signal_ref

    def _creare_ref_for_output_port(self, schema_kks: str, cabinet: str, output_port: OutputPort, kksp: str,
                                    template_name: str) -> SignalRef | None:
        """
        Создание ссылки для выходного сигналы схемы управления
        :param schema_kks: KKS схемы управления
        :param cabinet: Имя стойки
        :param output_port: Выходной порт
        :param kksp: KKS терминала
        :param template_name: Имя шаблона (для диагностических сообщений)
        :return: SignalRef или None
        """
        signal: tuple[str, str, bool] | None = self._get_signal_for_port(schema_kks=schema_kks,
                                                                         cabinet=cabinet,
                                                                         port=output_port,
                                                                         kksp=kksp,
                                                                         template_name=template_name)
        if signal is None:
            return None
        signal_kks: str = signal[0]
        signal_part: str = signal[1]
        is_digital: bool = signal[2]
        ref: str
        if is_digital:
            ref = f'{output_port.name}:{signal_kks}_{signal_part}'
        else:
            ref = f'{output_port.name}:{signal_kks}_{signal_part}\\{self._options.wired_signal_input_page}' \
                  f'\\{self._options.wired_signal_input_cell}'
        signal_ref: SignalRef = SignalRef(kks=signal_kks,
                                          part=signal_part,
                                          ref=ref,
                                          unrel_ref=None)
        return signal_ref

    def get_ref_for_defined_schemas(self) -> list[SignalRef] | None:
        """
        Генерация ссылок для предопределенных схем управления
        :return: Список ошибок либо None при ошибках
        """
        error_flag: bool = False
        ref_list: list[SignalRef] = []
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'SCHEMA', 'PART', 'CABINET'])
        for value in values:
            schema_kks = value['KKS']
            schema_part = value['PART']
            cabinet = value['CABINET']
            template_name = value['SCHEMA']
            ref_list_for_schema: list[SignalRef] | None = self._get_ref_for_schema(schema_kks=schema_kks,
                                                                                   schema_part=schema_part,
                                                                                   cabinet=cabinet,
                                                                                   template_name=template_name)
            if ref_list_for_schema is None:
                error_flag = True
            else:
                ref_list = ref_list + ref_list_for_schema
        if error_flag:
            return None
        return ref_list

    def get_ref_for_wired_schemas(self) -> list[SignalRef] | None:
        """
        Генерация ссылок для проводных схем управления
        :return: Список ошибок либо None при ошибках
        """
        error_flag: bool = False
        ref_list: list[SignalRef] = []
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS', 'SCHEMA', 'PART', 'CABINET'],
            key_names=['OBJECT_TYP'],
            key_values=['SW'])
        for value in values:
            schema_kks = value['KKS']
            schema_part = value['PART']
            cabinet = value['CABINET']
            template_name = value['SCHEMA']
            ref_list_for_schema: list[SignalRef] | None = self._get_ref_for_schema(schema_kks=schema_kks,
                                                                                   schema_part=schema_part,
                                                                                   cabinet=cabinet,
                                                                                   template_name=template_name)
            if ref_list_for_schema is None:
                error_flag = True
            else:
                ref_list = ref_list + ref_list_for_schema
        if error_flag:
            return None
        return ref_list

    def _get_ref_for_schema(self, schema_kks: str, schema_part: str, cabinet: str, template_name: str) \
            -> list[SignalRef] | None:
        """
        Генерация ссылок для схемы управления
        :param schema_kks: KKS схемы управления
        :param schema_part: PART схемы управления
        :param cabinet: Имя стойки
        :param template_name: Имя шаблона (для диагностических сообщений)
        :return: Список ссылок либо None при ошибке
        """
        ref_list: list[SignalRef] = []
        template: Template | None = next((templ for templ in self._options.templates
                                          if templ.name == template_name), None)
        if template is None:
            logging.error(f'Не найден шаблон с именем {template_name}')
            return None
        kksp: str | None = self._get_kksp_for_template(template=template,
                                                       schema_kks=schema_kks,
                                                       cabinet=cabinet)
        if kksp is None:
            return None

        for port in template.input_ports:
            signal_ref: SignalRef | None = self._creare_ref_for_input_port(schema_kks=schema_kks,
                                                                           schema_part=schema_part,
                                                                           cabinet=cabinet,
                                                                           input_port=port,
                                                                           kksp=kksp,
                                                                           template_name=template_name)
            if signal_ref is None:
                return None
            ref_list.append(signal_ref)

        for port in template.output_ports:
            signal_ref: SignalRef | None = self._creare_ref_for_output_port(schema_kks=schema_kks,
                                                                            cabinet=cabinet,
                                                                            output_port=port,
                                                                            kksp=kksp,
                                                                            template_name=template_name)
            if signal_ref is None:
                return None
            ref_list.append(signal_ref)
        return ref_list

    @staticmethod
    def run(options: FillRef2Options, base_path: str) -> None:
        logging.info('Запуск скрипта "Расстановка ссылок"...')
        with Connection.connect_to_mdb(base_path=base_path) as access:
            fill_ref_class: FillRef2 = FillRef2(options=options,
                                                access=access)
            fill_ref_class._fill_ref()
        logging.info('Выпонение скрипта "Расстановка ссылок" завершено.')
        logging.info('')
