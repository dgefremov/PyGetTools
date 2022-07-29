import logging
from dataclasses import dataclass
from enum import Enum
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
class Signal:
    kks: str
    part: str
    cabinet: str
    type: 'SignalType'


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TSODUPanel:
    name: str
    confirm_part: str
    abonent: int


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DynamicTemplate:
    target: Signal
    source: list[Signal]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Template:
    name: str
    input_ports: dict[str, list[InputPort]]
    output_ports: dict[str, list[OutputPort]]

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
    ts_odu_algorithm: str
    ts_odu_table: str
    ts_odu_panels: list[TSODUPanel]
    ref_table: str
    sim_table: str
    iec_table: str
    abonent_table: str
    templates: [Template]
    wired_signal_input_page: int
    wired_signal_input_cell: int
    wired_signal_input_port: str


class ErrorType(Enum):
    NOERROR = 0
    NOVALUES = 1
    TOOMANYVALUES = 2


class SignalType(Enum):
    WIRED = 0
    DIGITAL = 1
    TS_ODU = 2


class FillRef2:
    _options: FillRef2Options
    _access: Connection

    def __init__(self, options: FillRef2Options, access: Connection):
        self._options = options
        self._access = access

    @staticmethod
    def choose_signal_by_kksp(values: list[dict, str], kksp: str) -> tuple[str | None, ErrorType]:
        """
        Выбор среди результата запроса ККС, у которого KKSp совпадает с заданным
        :param values: Результат запроса к базе
        :param kksp: Сравниваемый KKSp
        :return: Код ошибки или KKS
        """
        signals: list[str] = []
        for value in values:
            if value['KKSp'] == kksp:
                signals.append(value['KKS'])
        if len(signals) == 0:
            return None, ErrorType.NOVALUES
        if len(signals) > 1:
            return None, ErrorType.TOOMANYVALUES
        return signals[0], ErrorType.NOERROR

    def _get_signal_from_sim_by_kks(self, cabinet: str | None, kks: str, kksp: str | None,
                                    port: InputPort | OutputPort) -> tuple[str | None, str | None, ErrorType]:
        """
        Поиск сигнала по ККС в таблице  СиМ
        :param cabinet: Имя стойки. Если None, поиск будет осуществляться и по другим стойкам
        :param kks: Шаблон для ККС искомого сигнала. Может быть None
        :param kksp: Код терминала. Не учитывается, если Cabinet=None
        :param port: Порт, для которого ищется терминал
        :return: Кортеж из ККС (если найден), имени стойки (если найдена) и кода ошибки
        """
        key_names: list[str] = ['KKS', 'MODULE', 'PART']
        key_values: list[str] = [kks, '1691', port.part]
        key_operator = ['LIKE', '<>', '=', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS', 'KKSp', 'CABINET'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if cabinet is not None and kksp is not None:
                kks, error = self.choose_signal_by_kksp(values=values,
                                                        kksp=kksp)
                return kks, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES

        if len(values) == 0:
            return None, None, ErrorType.NOVALUES
        if len(values) == 1:
            return values[0]['KKS'], values[1]['CABINET'], ErrorType.NOERROR

    def _get_signal_from_iec_by_kks(self, kks: str, kksp: str | None,
                                    port: InputPort | OutputPort, cabinet: str | None) -> tuple[str | None,
                                                                                                str | None, ErrorType]:
        """
        Поиск сигнала по ККС в таблице МЭК
        :param cabinet: Имя стойки. Если None, поиск будет осуществляться и по другим стойкам
        :param kks: Шаблон для ККС искомого сигнала. Может быть None
        :param kksp: Код терминала. Не учитывается, если Cabinet=None
        :param port: Порт, для которого ищется терминал
        :return: Кортеж из ККС (если найден), имени стойки (если найдена) и кода ошибки
        """
        key_names = ['KKS', 'PART']
        key_values = [kks, port.part]
        key_operator = ['LIKE', '=', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')

        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.iec_table,
                                                                  fields=['KKS', 'KKSp', 'CABINET'],
                                                                  key_names=key_names,
                                                                  key_values=key_values,
                                                                  key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if cabinet is not None and kksp is not None:
                kks, error = self.choose_signal_by_kksp(values=values,
                                                        kksp=kksp)
                return kks, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return values[0]['KKS'], values[0]['CABINET'], ErrorType.NOERROR
        return None, None, ErrorType.NOVALUES

    def _get_signal_from_sim_by_kksp(self, kksp: str, port: InputPort | OutputPort, cabinet: str) -> \
            tuple[str | None, ErrorType]:
        """
        Поиск сигнала в таблице СиМ по KKSp
        :param kksp: Код терминала
        :param port: Порт, для которого ищется сигнал
        :param cabinet: Имя стойки
        :return: Кортеж из ККС (если найден) и кода ошибки
        """
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS'],
            key_names=['MODULE', 'KKSp', 'PART', 'CABINET'],
            key_values=['1691', kksp, port.part, cabinet],
            key_operator=['<>', '=', '=', '='])
        if len(values) > 1:
            return None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return values[0]['KKS'], ErrorType.NOERROR
        return None, ErrorType.NOVALUES

    def _get_signal_from_iec_by_kksp(self, kksp: str, port: InputPort | OutputPort, cabinet: str) -> \
            tuple[str | None, ErrorType]:
        """
        Поиск сигнала в таблице МЭК по KKSp
        :param kksp: Код терминали
        :param port: Порт, для которого ищется сигнал
        :param cabinet: Имя стойки
        :return: Кортеж из ККС (если найден) и кода ошибки
        """
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.iec_table,
            fields=['KKS'],
            key_names=['KKSp', 'PART', 'CABINET'],
            key_values=[kksp, port.part, cabinet])
        if len(values) > 1:
            return None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return values[0]['KKS'], ErrorType.NOERROR

    def _get_signal_for_port(self, schema_kks: str, cabinet: str, kksp: str, port: InputPort | OutputPort,
                             template_name) -> tuple[str, str, str, bool] | None:
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
        # Поиск сигнала в таблице СИМ по KKS, PART
        found_kks, _, error = self._get_signal_from_sim_by_kks(cabinet=cabinet,
                                                               kks=kks,
                                                               kksp=kksp,
                                                               port=port)
        if error == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if error == ErrorType.NOERROR:
            return found_kks, port.part, cabinet, False

        # Поиск сигнала в таблице МЭК по KKS, PART
        kks, _, result = self._get_signal_from_iec_by_kks(kks=kks,
                                                          port=port,
                                                          cabinet=cabinet,
                                                          kksp=kksp)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return kks, port.part, cabinet, True
        # Если сигнал задан шаблоном, то на этом этапе он уже должен быть найден
        if port.kks is not None:
            logging.error(f'Не найден сигнао для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
        # Поиск сигнала в таблице СИМ по PART и KKSp
        kks, result = self._get_signal_from_sim_by_kksp(kksp=kksp,
                                                        port=port,
                                                        cabinet=cabinet)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return kks, port.part, cabinet, False
        # Поиск сигнала в таблице МЭК по PART и KKSp
        kks, result = self._get_signal_from_iec_by_kksp(kksp=kksp,
                                                        port=port,
                                                        cabinet=cabinet)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return kks, port.part, cabinet, True
        # Поиск межстоечных сигналов (только если указан KKS)
        if port.kks is not None:
            # Поиск сигнала в другой стойке в таблице СИМ по ККС
            kks, cabinet, result = self._get_signal_from_iec_by_kks(kks=kks,
                                                                    kksp=None,
                                                                    port=port,
                                                                    cabinet=None)
            if result == ErrorType.TOOMANYVALUES:
                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None
            if result == ErrorType.NOERROR:
                return kks, port.part, cabinet, False
            # Поиск сигнала в другой стойке в таблице МЭК по KKS, PART
            kks, cabinet, result = self._get_signal_from_iec_by_kks(kks=kks,
                                                                    kksp=None,
                                                                    port=port,
                                                                    cabinet=None)
            if result == ErrorType.TOOMANYVALUES:
                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None
            if result == ErrorType.NOERROR:
                return kks, port.part, cabinet, True

        logging.error(f'Не найден сигнал для шаблона {template_name} с KKS {schema_kks} для порта '
                      f'с PART {port.part}')
        return None

    def _get_kksp_for_template(self, template: Template, schema_part: str, schema_kks: str, cabinet: str) -> str | None:
        """
        Функция определения KKSp для заданного шаблона и ККС
        :param template: шаблон схемы управления
        :param: kks: ККС схемы управления
        :return: KKSp для данного KKS
        """
        kksp_list: list[str] = []
        for output_port in template.output_ports[schema_part]:
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
        cabinet_prefix: str = '' if signal[3] == cabinet else f'{cabinet}\\'
        ref: str
        unrel_ref: str | None
        if is_digital:
            ref: str = f'{cabinet_prefix}{schema_kks}_{schema_part}\\{input_port.page}\\{input_port.cell_num}'
            if input_port.unrel_ref_cell_num is not None:
                unrel_ref = f'{cabinet_prefix}{schema_kks}_{schema_part}\\{input_port.page}\\' \
                            f'{input_port.unrel_ref_cell_num}'
            else:
                unrel_ref = None
        else:
            ref: str = f'{cabinet_prefix}{self._options.wired_signal_input_port}:{schema_kks}_{schema_part}\\' \
                       f'{cabinet_prefix}{input_port.page}\\{input_port.cell_num}'
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
        cabinet_prefix: str = '' if signal[3] == cabinet else f'{signal[3]}\\'
        ref: str
        if is_digital:
            ref = f'{cabinet_prefix}{output_port.name}:{signal_kks}_{signal_part}'
        else:
            ref = f'{cabinet_prefix}{output_port.name}:{signal_kks}_{signal_part}\\' \
                  f'{self._options.wired_signal_input_page}\\{self._options.wired_signal_input_cell}'
        signal_ref: SignalRef = SignalRef(kks=signal_kks,
                                          part=signal_part,
                                          ref=ref,
                                          unrel_ref=None)
        return signal_ref

    def _get_ref_for_defined_schemas(self) -> list[SignalRef] | None:
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

    def _get_abonent_map(self) -> dict[str, int]:
        values: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.abonent_table,
                                                                  fields=['CABINET', 'ABONENT'])
        return {value['CABINET']: int(value['ABONENT']) for value in values}

    def _get_signal_from_dynamic_algorithm(self, kks: str, part: str) -> \
            tuple[Signal | None, ErrorType]:
        values_from_sim: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table,
                                                                           fields=['CABINET'],
                                                                           key_names=['KKS', 'PART'],
                                                                           key_values=[kks, part])
        if len(values_from_sim) == 1:
            cabinet: str = values_from_sim[0]['CABINET']
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.WIRED), ErrorType.NOERROR
        values_from_iec: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.iec_table,
                                                                           fields=['CABINET'],
                                                                           key_names=['KKS', 'PART'],
                                                                           key_values=[kks, part])
        if len(values_from_iec) == 1:
            cabinet: str = values_from_iec[0]['CABINET']
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.DIGITAL), ErrorType.NOERROR
        values_from_ts_odu: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.ts_odu_table,
                                                                              fields=['CABINET'],
                                                                              key_names=['KKS', 'PART'],
                                                                              key_values=[kks, part])
        if len(values_from_ts_odu) == 1:
            cabinet: str = values_from_ts_odu[0]['CABINET']
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.TS_ODU), ErrorType.NOERROR
        logging.error(f'Сигнал {kks}_{part} не найден ни в одной таблице')
        return None, ErrorType.NOVALUES

    def _get_ref_for_ts_odu(self) -> list[SignalRef] | None:
        abonent_map: dict[str, int] = self._get_abonent_map()
        ok_flag: bool = True
        dynamic_templates: list[DynamicTemplate] = []
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.ts_odu_algorithm,
            fields=['KKS_SOURCE', 'PART_SOURCE', 'KKS_TARGET', 'PART_TARGET'])
        for value in values:
            source_signal, source_error = self._get_signal_from_dynamic_algorithm(kks=value['KKS_SOURCE'],
                                                                                  part=value['PART_SOURCE'])
            target_signal, target_error = self._get_signal_from_dynamic_algorithm(kks=value['KKS_TARGET'],
                                                                                  part=value['PART_TARGET'])
            if source_error != ErrorType.NOERROR or target_error != ErrorType.NOERROR:
                ok_flag = False
                continue

            dynamic_template: DynamicTemplate | None = next((template for template in dynamic_templates
                                                             if template.target.kks == target_signal.kks and
                                                             template.target.part == target_signal.part), None)
            if dynamic_template is None:
                dynamic_template = DynamicTemplate(target=target_signal,
                                                   source=[source_signal])
                dynamic_templates.append(dynamic_template)
            else:
                dynamic_template.source.append(source_signal)
        if not ok_flag:
            return None

    def _get_refs_for_dynamic_template(self, dynamic_templates: list[DynamicTemplate]):
        ok_flag: bool = True
        abonent_map: dict[str, int] = self._get_abonent_map()
        for dynamic_template in dynamic_templates:
            source_signals_dict: dict[str, list[Signal]] = {}
            # Сначала формируется словарь, где ключ - это имя стойки, значение - список сигналов от этой стойки,
            # т.е. группировка сигналов по имени стойки
            for source_signal in dynamic_template.source:
                signals_in_cabinet: list[Signal] | None = source_signals_dict[source_signal.cabinet]
                if signals_in_cabinet is None:
                    signals_in_cabinet = [source_signal]
                    source_signals_dict[source_signal.cabinet] = signals_in_cabinet
                else:
                    signals_in_cabinet.append(source_signal)
            # Дальше обрабатываем списки сигналов от каждой стойки
            for cabinet in source_signals_dict:
                abonent: int
                ts_odu_panel: TSODUPanel | None = None
                ts_odu_panel = next((panel for panel in self._options.ts_odu_panels
                                                        if panel.name == cabinet), None)
                if ts_odu_panel is None:
                    logging.error(f"Не найден абонент для стойки {cabinet}")
                    ok_flag = False






    def _get_ref_for_wired_schemas(self) -> list[SignalRef] | None:
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
        if schema_part not in template.input_ports or schema_part not in template.output_ports:
            logging.error(f'Не найдены сигналы для шаблона {template_name} для PART {schema_part}')
            return None
        kksp: str | None = self._get_kksp_for_template(template=template,
                                                       schema_kks=schema_kks,
                                                       schema_part=schema_part,
                                                       cabinet=cabinet)
        if kksp is None:
            return None

        input_port_list: list[InputPort] | None = template.input_ports[schema_part]
        if input_port_list is not None:
            for port in input_port_list:
                signal_ref: SignalRef | None = self._creare_ref_for_input_port(schema_kks=schema_kks,
                                                                               schema_part=schema_part,
                                                                               cabinet=cabinet,
                                                                               input_port=port,
                                                                               kksp=kksp,
                                                                               template_name=template_name)
                if signal_ref is None:
                    return None
                ref_list.append(signal_ref)

        output_port_list: list[OutputPort] | None = template.output_ports[schema_part]
        if output_port_list is not None:
            for port in output_port_list:
                signal_ref: SignalRef | None = self._creare_ref_for_output_port(schema_kks=schema_kks,
                                                                                cabinet=cabinet,
                                                                                output_port=port,
                                                                                kksp=kksp,
                                                                                template_name=template_name)
                if signal_ref is None:
                    return None
                ref_list.append(signal_ref)
            return ref_list

    def _write_ref(self, ref_list: list[SignalRef]) -> None:
        """
        Функция записи ссылок в базу
        :param ref_list: Список со ссылками
        :return: None
        """
        for ref in ref_list:
            self._access.insert_row(table_name=self._options.ref_table,
                                    column_names=['KKS', 'PART', 'REF', 'UNREL_REF'],
                                    values=[ref.kks, ref.part, ref.ref, ref.unrel_ref])
        self._access.commit()

    def _write_control_schemas(self):
        values: list[dict[str, str]] = self._access.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR'])
        for value in values:
            self._access.insert_row(table_name=self._options.control_schemas_table,
                                    column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR'],
                                    values=[value['KKS'], value['CABINET'], value['SCHEMA'], value['CHANNEL'],
                                            value['PART'], value['DESCR']])
        self._access.commit()

    def _fill_ref(self):
        ref_for_predefined_schemas: list[SignalRef] | None = self._get_ref_for_defined_schemas()
        ref_for_wired_schemas: list[SignalRef] | None = self._get_ref_for_wired_schemas()
        if ref_for_wired_schemas is not None and ref_for_predefined_schemas is not None:
            ref_list: list[SignalRef] = ref_for_predefined_schemas + ref_for_wired_schemas
            self._access.clear_table(table_name=self._options.ref_table)
            self._access.clear_table(table_name=self._options.control_schemas_table)
            self._write_ref(ref_list=ref_list)
            self._write_control_schemas()

    @staticmethod
    def run(options: FillRef2Options, base_path: str) -> None:
        logging.info('Запуск скрипта "Расстановка ссылок"...')
        with Connection.connect_to_mdb(base_path=base_path) as access:
            fill_ref_class: FillRef2 = FillRef2(options=options,
                                                access=access)
            fill_ref_class._fill_ref()
        logging.info('Выпонение скрипта "Расстановка ссылок" завершено.')
        logging.info('')
