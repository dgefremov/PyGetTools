import logging
import re
from dataclasses import dataclass
from enum import Enum
from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar

brackets_pattern = re.compile('({.+?})+')


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class InputPort:
    page: int
    cell_num: int
    kks: str | None
    part: str
    unrel_ref_cell_num: int | None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TSODUDescription:
    panels: list['TSODUPanel']
    alarm_sound_kks: str
    alarm_sound_part: str
    alarm_sound_check_kks: str
    alarm_sound_check_part: str
    alarm_sound_check_page: str
    alarm_sound_check_cell: str
    alarm_sound_check_port: str
    warning_sound_kks: str
    warning_sound_part: str
    warn_sound_check_kks: str
    warn_sound_check_part: str
    warn_sound_check_page: str
    warn_sound_check_cell: str
    warn_sound_check_port: str
    cabinet: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class OutputPort:
    name: str
    part: str
    kks: str | None
    page: int | None = None
    cell_num: int | None = None
    blink_port_name: str | None = None
    blink_page: int | None = None
    blink_cell_num: int | None = None
    flicker_port_name: str | None = None
    flicker_page: int | None = None
    flicker_cell_num: int | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Signal:
    kks: str
    part: str
    cabinet: str
    type: 'SignalType'
    descr_eng: str | None = None
    descr_rus: str | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class MozaicElement:
    place: str
    ts_odu_panel: str


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TSODUPanel:
    name: str
    confirm_part: str | None
    confirm_kks: str | None
    acknowledgment_kks: str | None
    acknowledgment_part: str | None
    abonent: int
    lamp_test_kks: str | None = None
    lamp_test_part: str | None = None
    lamp_test_port: str | None = 'Port1'
    display_test_kks: str | None = None
    display_test_part: str | None = None
    display_test_port: str | None = 'Port1'
    acknowledgment_flash_kks: str | None = None
    acknowledgment_flash_part: str | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class DynamicTemplate:
    target: MozaicElement
    type: str
    source: list[Signal]


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class VirtualSchema:
    kks: str
    part: str
    schema: str
    descr_rus: str
    descr_eng: str
    cabinet: str
    channel: int = 0


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TSODUData:
    input_ports: list[InputPort]
    output_ports: list[OutputPort]
    confirm_command_page: str | None = None
    confirm_command_cell: int | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Template:
    name: str
    input_ports: dict[str, list[InputPort]]
    output_ports: dict[str, list[OutputPort]]
    ts_odu_data: TSODUData | None = None
    alarm_sound_signal_port: str | None = None
    warn_sound_signal_port: str | None = None


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class TSODUTemplate:
    name: str
    input_ports: list[InputPort]
    output_ports: list[OutputPort]
    warning_port: str | None = None
    emergency_port: str | None = None
    lamp_test_page: str | None = None
    lamp_test_cell: str | None = None
    display_test_page: str | None = None
    display_test_cell: str | None = None
    acknolegment_page: str | None = None
    acknolegment_cell: str | None = None
    acknolegment_flash_page: str | None = None
    acknolegment_flash_cell: str | None = None


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
    ts_odu_info: TSODUDescription | None
    ref_table: str
    sim_table: str
    iec_table: str
    fake_signals_table: str
    abonent_table: str
    templates: list[Template]
    custom_templates_ts_odu: list[Template]
    ts_odu_templates_lamp: TSODUTemplate
    ts_odu_templates_displ: TSODUTemplate
    wired_signal_output_default_page: int
    wired_signal_output_default_cell: int
    wired_signal_output_blink_default_page: int
    wired_signal_output_blink_default_cell: int
    wired_signal_output_flicker_default_page: int
    wired_signal_output_flicker_default_cell: int
    wired_signal_default_input_port: str
    read_english_description: bool
    or_schema_name_prefix: str = 'OR_'
    or_schema_meas_name_prefix: str = 'OR_XQ_'
    or_schema_start_cell: int = 3
    or_schema_end_cell: int = 25
    control_schema_name_postfix: str = ''
    or_schema_code = 'XM'


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
    _connection: Connection
    _abonent_map: dict[str, int]
    _alarm_sound_container: dict[Signal, str]
    _warn_sound_container: dict[Signal, str]

    def __init__(self, options: FillRef2Options, connection: Connection):
        self._options = options
        self._connection = connection
        self._abonent_map = self._get_abonent_map()
        self._alarm_sound_container = {}
        self._warn_sound_container = {}

    # def _choose_signal_by_kksp(values: list[dict, str], kksp: list[str]) -> tuple[str | None, str | None, ErrorType]:
    def _choose_signal_by_kksp(self, values: list[dict[str, str]], kksp: list[str]) -> tuple[
                            str | None, str | None, ErrorType]:

        """
        Выбор среди результата запроса ККС, у которого KKSp совпадает с заданным
        :param values: Результат запроса к базе
        :param kksp: Сравниваемый KKSp
        :return: Код ошибки или KKS
        """
        signals: list[tuple[str, str]] = []
        for value in values:
            if value[self._connection.modify_column_name('KKSp')] in kksp:
                signals.append((value[self._connection.modify_column_name('KKS')],
                                value[self._connection.modify_column_name('CABINET')]))
        if len(signals) == 0:
            return None, None, ErrorType.NOVALUES
        if len(signals) > 1:
            return None, None, ErrorType.TOOMANYVALUES
        return signals[0][0], signals[0][1], ErrorType.NOERROR

    def _get_signal_from_sim_by_kks(self, cabinet: str | None, kks: str, kksp: list[str] | None,
                                    port: InputPort | OutputPort, schema_kks: str | None = None) -> tuple[
                                        str | None, str | None, ErrorType]:
        """
        Поиск сигнала по ККС в таблице СиМ
        :param cabinet: Имя стойки. Если None, поиск будет осуществляться и по другим стойкам
        :param kks: Шаблон для ККС искомого сигнала. Может быть None
        :param kksp: Код терминала. Не учитывается, если Cabinet=None
        :param port: Порт, для которого ищется терминал
        :return: Кортеж из ККС (если найден), имени стойки (если найдена) и кода ошибки
        """
        key_names: list[str] = ['KKS', 'MODULE', 'PART']
        key_values: list[str] = [self.transform_kks(kks, schema_kks), '1691', port.part]
        key_operator = ['LIKE', '<>', '=', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS', 'KKSp', 'CABINET'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        # Заодно загружается из таблицы СиМ ТС ОДУ
        values += self._connection.retrieve_data(
            table_name=self._options.ts_odu_table,
            fields=['KKS', 'KKSp', 'CABINET'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if kksp is not None:
                kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                                  kksp=kksp)
                return kks, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES

        if len(values) == 0:
            return None, None, ErrorType.NOVALUES
        if len(values) == 1:
            return (values[0][self._connection.modify_column_name('KKS')],
                    values[0][self._connection.modify_column_name('CABINET')], ErrorType.NOERROR)

    def _get_signal_from_iec_by_kks(self, kks: str, kksp: list[str] | None,
                                    port: InputPort | OutputPort, cabinet: str | None,
                                    schema_kks: str | None = None) -> tuple[str | None,
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
        key_values = [self.transform_kks(kks, schema_kks), port.part]
        key_operator = ['LIKE', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')

        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.iec_table,
                                                                      fields=['KKS', 'KKSp', 'CABINET'],
                                                                      key_names=key_names,
                                                                      key_values=key_values,
                                                                      key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if cabinet is not None and kksp is not None:
                kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                                  kksp=kksp)
                return kks, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return (values[0][self._connection.modify_column_name('KKS')],
                    values[0][self._connection.modify_column_name('CABINET')], ErrorType.NOERROR)
        return None, None, ErrorType.NOVALUES

    def _get_signal_from_sim_by_cabinet(self, kksp: list[str], port: InputPort | OutputPort, cabinet: str,
                                        schema_kks: str | None = None) -> \
            tuple[str | None, ErrorType]:
        """
        Поиск сигнала в таблице СиМ по KKSp
        :param kksp: Код терминала
        :param port: Порт, для которого ищется сигнал
        :param cabinet: Имя стойки
        :return: Кортеж из ККС (если найден) и кода ошибки
        """
        key_names = ['MODULE', 'PART', 'CABINET']
        key_values = ['1691', port.part, cabinet]
        key_operator = ['<>', '=', '=']
        if port.kks is not None:
            key_names.append('KKS')
            key_values.append(self.transform_kks(port.kks, schema_kks))
            key_operator.append('LIKE')

        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.sim_table,
            fields=['KKS', 'CABINET', 'KKSp'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                              kksp=kksp)
            return kks, error
        if len(values) == 1:
            return values[0][self._connection.modify_column_name('KKS')], ErrorType.NOERROR
        return None, ErrorType.NOVALUES

    def _get_signal_from_iec_by_cabinet(self, kksp: list[str], port: InputPort | OutputPort, cabinet: str,
                                        schema_kks: str | None = None) -> \
            tuple[str | None, ErrorType]:
        """
        Поиск сигнала в таблице МЭК по KKSp
        :param kksp: Код терминали
        :param port: Порт, для которого ищется сигнал
        :param cabinet: Имя стойки
        :return: Кортеж из ККС (если найден) и кода ошибки
        """
        key_names = ['PART', 'CABINET']
        key_values = [port.part, cabinet]
        key_operator = ['=', '=']
        if port.kks is not None:
            key_names.append('KKS')
            key_values.append(self.transform_kks(port.kks, schema_kks))
            key_operator.append('LIKE')

        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.iec_table,
            fields=['KKS', 'KKSp', 'CABINET'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                              kksp=kksp)
            return kks, error
        if len(values) == 1:
            return values[0][self._connection.modify_column_name('KKS')], ErrorType.NOERROR
        return None, ErrorType.NOVALUES

    def _get_signal_for_port(self, schema_kks: str, cabinet: str, kksp: list[str] | None, port: InputPort | OutputPort,
                             template_name) -> Signal | None:
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
                                                               port=port,
                                                               schema_kks=schema_kks)
        if error == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if error == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.WIRED)

        # Поиск сигнала в таблице МЭК по KKS, PART
        found_kks, _, result = self._get_signal_from_iec_by_kks(kks=kks,
                                                                port=port,
                                                                cabinet=cabinet,
                                                                kksp=kksp,
                                                                schema_kks=schema_kks)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.DIGITAL)
        # Поиск сигнала в таблице СИМ по PART и KKSp
        found_kks, result = self._get_signal_from_sim_by_cabinet(kksp=kksp,
                                                                 port=port,
                                                                 cabinet=cabinet,
                                                                 schema_kks=schema_kks)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.WIRED)
        # Поиск сигнала в таблице фейковых сигналов по KKS, PART
        found_kks, _, error = self._get_signal_from_fake_signals(cabinet=cabinet,
                                                                 kks=kks,
                                                                 kksp=kksp,
                                                                 port=port)
        if error == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if error == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.WIRED)

        # Поиск сигнала в таблице МЭК по PART и Cabinet
        found_kks, result = self._get_signal_from_iec_by_cabinet(kksp=kksp,
                                                                 port=port,
                                                                 cabinet=cabinet,
                                                                 schema_kks=schema_kks)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.DIGITAL)
        # Поиск сигнала в таблице СУ по PART и Cabinet
        found_kks, cabinet, result = self._get_signal_from_predefined_schemas(kks=kks,
                                                                              port=port,
                                                                              cabinet=cabinet,
                                                                              kksp=kksp)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.WIRED)
        # Поиск сигнала в таблице фэйковых сигналов по PART и Cabinet
        found_kks, cabinet, result = self._get_signal_from_fake_signals(kks=kks,
                                                                        port=port,
                                                                        cabinet=cabinet,
                                                                        kksp=kksp)
        if result == ErrorType.TOOMANYVALUES:
            logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                          f'с PART {port.part}')
            return None
        if result == ErrorType.NOERROR:
            return Signal(kks=found_kks,
                          part=port.part,
                          cabinet=cabinet,
                          type=SignalType.WIRED)

        # Поиск межстоечных сигналов (только если указан KKS)
        if port.kks is not None:
            # Поиск сигнала в другой стойке в таблице СИМ по ККС
            found_kks, cabinet, result = self._get_signal_from_sim_by_kks(kks=kks,
                                                                          kksp=None,
                                                                          port=port,
                                                                          cabinet=None,
                                                                          schema_kks=schema_kks)
            if result == ErrorType.TOOMANYVALUES:
                found_kks, cabinet, result = self._get_signal_from_sim_by_kks(kks=kks,
                                                                              kksp=kksp,
                                                                              port=port,
                                                                              cabinet=None,
                                                                              schema_kks=schema_kks)
                if result == ErrorType.NOERROR:
                    return Signal(kks=found_kks,
                                  part=port.part,
                                  cabinet=cabinet,
                                  type=SignalType.WIRED)

                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None
            if result == ErrorType.NOERROR:
                return Signal(kks=found_kks,
                              part=port.part,
                              cabinet=cabinet,
                              type=SignalType.WIRED)
            # Поиск сигнала в другой стойке в таблице МЭК по KKS, PART
            found_kks, cabinet, result = self._get_signal_from_iec_by_kks(kks=kks,
                                                                          kksp=None,
                                                                          port=port,
                                                                          cabinet=None,
                                                                          schema_kks=schema_kks)
            if result == ErrorType.TOOMANYVALUES:
                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None
            if result == ErrorType.NOERROR:
                return Signal(kks=found_kks,
                              part=port.part,
                              cabinet=cabinet,
                              type=SignalType.DIGITAL)
            # Поиск сигнала в таблице СУ
            found_kks, cabinet, result = self._get_signal_from_predefined_schemas(kks=kks,
                                                                                  port=port,
                                                                                  cabinet=None,
                                                                                  kksp=None)
            if result == ErrorType.NOERROR:
                return Signal(kks=found_kks,
                              part=port.part,
                              cabinet=cabinet,
                              type=SignalType.WIRED)

            if result == ErrorType.TOOMANYVALUES:
                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None

            # Поиск сигнала в таблице фейковых сигналов
            found_kks, cabinet, result = self._get_signal_from_fake_signals(kks=kks,
                                                                            port=port,
                                                                            cabinet=None,
                                                                            kksp=None)
            if result == ErrorType.NOERROR:
                return Signal(kks=found_kks,
                              part=port.part,
                              cabinet=cabinet,
                              type=SignalType.WIRED)

            if result == ErrorType.TOOMANYVALUES:
                logging.error(f'Найдено больше одного сигнала для шаблона {template_name} с KKS {schema_kks} для порта '
                              f'с PART {port.part}')
                return None

        logging.error(f'Не найден сигнал для шаблона {template_name} с KKS {schema_kks} для порта '
                      f'с PART {port.part}')
        return None

    def _get_signal_from_predefined_schemas(self, kks: str, port: InputPort | OutputPort, cabinet: str | None,
                                            kksp: list[str] | None):
        key_names = ['KKS', 'PART']
        key_values = [kks, port.part]
        key_operator = ['LIKE', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')

        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'CABINET'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if cabinet is not None and kksp is not None:
                kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                                  kksp=kksp)
                return kks + self._options.control_schema_name_postfix, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return (values[0][self._connection.modify_column_name('KKS')] +
                    self._options.control_schema_name_postfix,
                    values[0][self._connection.modify_column_name('CABINET')], ErrorType.NOERROR)
        return None, None, ErrorType.NOVALUES

    @staticmethod
    def transform_kks(kks: str, schema_kks: str | None) -> str:
        if schema_kks is not None and kks.count('{') >= 1:
            for str_template in re.findall(brackets_pattern, kks):
                if re.match(r'^{schema_kks:\d+:\d+}$', str_template):
                    parts: list[str] = str_template[1:-1].split(':')
                    kks = kks.replace(str_template, schema_kks[int(parts[1]): int(parts[2])])
                else:
                    raise Exception(f'Ошибка шаблона: {kks}')
            return kks
        else:
            return kks

    def _get_signal_from_fake_signals(self, kks: str, port: InputPort | OutputPort, cabinet: str | None,
                                      kksp: list[str] | None):
        key_names = ['KKS', 'PART']
        key_values = [kks, port.part]
        key_operator = ['LIKE', '=']
        if cabinet is not None:
            key_names.append('CABINET')
            key_values.append(cabinet)
            key_operator.append('=')

        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.fake_signals_table,
            fields=['KKS', 'CABINET', 'KKSp'],
            key_names=key_names,
            key_values=key_values,
            key_operator=key_operator)
        if len(values) > 1:
            # Если не задана стойка и KKSp, то для нескольких сигналов будет попытка выбрать один, относящийся
            # к данному терминалу
            if cabinet is not None and kksp is not None:
                kks, cabinet, error = self._choose_signal_by_kksp(values=values,
                                                                  kksp=kksp)
                return kks, cabinet, error
            else:
                return None, None, ErrorType.TOOMANYVALUES
        if len(values) == 1:
            return (values[0][self._connection.modify_column_name('KKS')],
                    values[0][self._connection.modify_column_name('CABINET')], ErrorType.NOERROR)
        return None, None, ErrorType.NOVALUES

    def _creare_ref_for_input_port(self, schema_kks: str, schema_part: str, cabinet: str,
                                   input_port: InputPort, kksp: list[str] | None, template_name: str,
                                   add_kks_postfix: bool) -> SignalRef | None:
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
        signal: Signal | None = self._get_signal_for_port(schema_kks=schema_kks,
                                                          cabinet=cabinet,
                                                          port=input_port,
                                                          kksp=kksp,
                                                          template_name=template_name)
        if signal is None:
            return None
        cabinet_prefix: str = '' if signal.cabinet == cabinet else f'{self._abonent_map[cabinet]}\\'
        kks_postfix: str = self._options.control_schema_name_postfix if add_kks_postfix else ''
        ref: str
        unrel_ref: str | None
        if signal.type == SignalType.DIGITAL:
            ref: str = f'{cabinet_prefix}{schema_kks}{kks_postfix}_' \
                       f'{schema_part}\\{input_port.page}\\{input_port.cell_num}'
            if input_port.unrel_ref_cell_num is not None:
                unrel_ref = f'{cabinet_prefix}{schema_kks}{kks_postfix}_' \
                            f'{schema_part}\\{input_port.page}\\{input_port.unrel_ref_cell_num}'
            else:
                unrel_ref = None
        else:
            ref: str = f'{self._options.wired_signal_default_input_port}:{cabinet_prefix}{schema_kks}' \
                       f'{kks_postfix}_{schema_part}\\{input_port.page}\\' \
                       f'{input_port.cell_num}'
            unrel_ref = None
        signal_ref: SignalRef = SignalRef(kks=signal.kks,
                                          part=signal.part,
                                          ref=ref,
                                          unrel_ref=unrel_ref)
        return signal_ref

    def _creare_ref_for_output_port(self, schema_kks: str, schema_part: str, cabinet: str, output_port: OutputPort,
                                    kksp: list[str] | None, template_name: str, add_kks_postfix: bool,
                                    signal: Signal | None = None) -> list[SignalRef] | None:
        """
        Создание ссылки для выходного сигналы схемы управления
        :param schema_kks: KKS схемы управления
        :param cabinet: Имя стойки
        :param output_port: Выходной порт
        :param kksp: KKS терминала
        :param template_name: Имя шаблона (для диагностических сообщений)
        :return: SignalRefs или None
        """
        if signal is None:
            signal: Signal | None = self._get_signal_for_port(schema_kks=schema_kks,
                                                              cabinet=cabinet,
                                                              port=output_port,
                                                              kksp=kksp,
                                                              template_name=template_name)
        if signal is None:
            return None
        signal_refs: list[SignalRef] = []
        ref: str
        ref = '' if output_port.name is None else f'{output_port.name}:'
        ref += '' if signal.cabinet == cabinet else f'{self._abonent_map[signal.cabinet]}\\'
        ref += f'{signal.kks}_{signal.part}'
        if signal.type == SignalType.WIRED or signal.type == SignalType.TS_ODU:
            if output_port.page is None or output_port.cell_num is None:
                ref += f'\\{self._options.wired_signal_output_default_page}\\' \
                       f'{self._options.wired_signal_output_default_cell}'
            else:
                ref += f'\\{output_port.page}\\{output_port.cell_num}'

            signal_ref: SignalRef = SignalRef(
                kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                part=schema_part,
                ref=ref,
                unrel_ref=None)
            signal_refs.append(signal_ref)
            if output_port.blink_port_name is not None:
                ref_blink: str = f'{output_port.blink_port_name}:'
                ref_blink += '' if signal.cabinet == cabinet else f'{self._abonent_map[signal.cabinet]}\\'
                ref_blink += f'{signal.kks}_{signal.part}'
                if output_port.blink_page is None or output_port.blink_cell_num is None:
                    ref_blink += f'\\{self._options.wired_signal_output_blink_default_page}\\' \
                                 f'{self._options.wired_signal_output_blink_default_cell}'
                else:
                    ref_blink += f'\\{output_port.blink_page}\\{output_port.blink_cell_num}'
                signal_blink_ref: SignalRef = SignalRef(
                    kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                    part=schema_part,
                    ref=ref_blink,
                    unrel_ref=None)
                signal_refs.append(signal_blink_ref)
            if output_port.flicker_port_name is not None:
                ref_flicker: str = f'{output_port.flicker_port_name}:'
                ref_flicker += '' if signal.cabinet == cabinet else f'{self._abonent_map[signal.cabinet]}\\'
                ref_flicker += f'{signal.kks}_{signal.part}'
                if output_port.flicker_page is None or output_port.flicker_cell_num is None:
                    ref_flicker += f'\\{self._options.wired_signal_output_flicker_default_page}\\' \
                                   f'{self._options.wired_signal_output_flicker_default_cell}'
                else:
                    ref_flicker += f'\\{output_port.flicker_page}\\{output_port.flicker_cell_num}'
                signal_ref_flicker: SignalRef = SignalRef(
                    kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                    part=schema_part,
                    ref=ref_flicker,
                    unrel_ref=None)
                signal_refs.append(signal_ref_flicker)
        else:
            signal_ref: SignalRef = SignalRef(
                kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                part=schema_part,
                ref=ref,
                unrel_ref=None)
            signal_refs.append(signal_ref)
        return signal_refs

    def _process_defined_schemas(self) -> list[SignalRef] | None:
        """
        Генерация ссылок для предопределенных схем управления
        :return: Список ошибок либо None при ошибках
        """
        error_flag: bool = False
        ref_list: list[SignalRef] = []
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'SCHEMA', 'PART', 'CABINET', 'TS_ODU_PANEL', 'INST_PLACE', 'KKSp', 'ONLY_FOR_REF'])
        logging.info('Запуск обработки таблицы со схемами управления...')
        if len(values) > 0:
            ProgressBar.config(max_value=len(values), step=1, prefix='Обработка схем управления', suffix='Завершено',
                               length=50)
            for value in values:
                ProgressBar.update_progress()
                schema_kks: str = value[self._connection.modify_column_name('KKS')]
                schema_part: str = value[self._connection.modify_column_name('PART')]
                cabinet: str = value[self._connection.modify_column_name('CABINET')]
                template_name: str = value[self._connection.modify_column_name('SCHEMA')]
                if ';' in value[self._connection.modify_column_name('KKSp')]:
                    kksp = value[self._connection.modify_column_name('KKSp')].split(';')
                else:
                    kksp = [value[self._connection.modify_column_name('KKSp')]]
                mozaic_element: MozaicElement | None = None
                if (value[self._connection.modify_column_name('TS_ODU_PANEL')] is not None and
                        value[self._connection.modify_column_name('TS_ODU_PANEL')] != '' and
                        value[self._connection.modify_column_name('INST_PLACE')] is not None and
                        value[self._connection.modify_column_name('INST_PLACE')] != ''):
                    mozaic_element = MozaicElement(
                        ts_odu_panel=value[self._connection.modify_column_name('TS_ODU_PANEL')],
                        place=value[self._connection.modify_column_name('INST_PLACE')])
                add_kks_postfix: bool = value[self._connection.modify_column_name('ONLY_FOR_REF')] == 'False'
                ref_list_for_schema: list[SignalRef] | None = \
                    self._get_ref_for_schema(schema_kks=schema_kks,
                                             schema_part=schema_part,
                                             schema_cabinet=cabinet,
                                             template_name=template_name,
                                             mozaic_element=mozaic_element,
                                             kksp=kksp,
                                             add_kks_postfix=add_kks_postfix,
                                             template_list=self._options.templates)
                if ref_list_for_schema is None:
                    error_flag = True
                else:
                    ref_list = ref_list + ref_list_for_schema
            if error_flag:
                logging.info('Завершено с ошибками.')
                return None
        logging.info('Завершено')
        return ref_list

    def _process_sound_signals(self) -> tuple[list[SignalRef], list[tuple[str, str, str]]]:

        refs: list[SignalRef] = []
        update_schemas: list[tuple[str, str, str]] = []
        refs_on_page: int = self._options.or_schema_end_cell - self._options.or_schema_start_cell + 1
        logging.info('Запуск обработки звуковых сигналов')
        if len(self._alarm_sound_container) > 0:
            ProgressBar.config(max_value=len(self._alarm_sound_container) + len(self._warn_sound_container),
                               step=1, prefix='Обработка звуковых сигналов', suffix='Завершено', length=50)
            index: int = 0
            for signal in self._alarm_sound_container:
                ProgressBar.update_progress()
                cell_num: int = index % (refs_on_page - 1) + self._options.or_schema_start_cell
                page_num: int = index // (refs_on_page - 1) + 2
                refs.append(self._get_ref_for_signal(source_signal=signal,
                                                     target_kks=self._options.ts_odu_info.alarm_sound_kks,
                                                     target_abonent=self._abonent_map[
                                                         self._options.ts_odu_info.cabinet],
                                                     target_part=self._options.ts_odu_info.alarm_sound_part,
                                                     target_page=page_num,
                                                     target_cell=cell_num,
                                                     source_port=self._alarm_sound_container[signal]))
                index += 1
            index = 0
            for signal in self._warn_sound_container:
                ProgressBar.update_progress()
                cell_num: int = index % (refs_on_page - 1) + self._options.or_schema_start_cell
                page_num: int = index // (refs_on_page - 1) + 2
                refs.append(self._get_ref_for_signal(source_signal=signal,
                                                     target_kks=self._options.ts_odu_info.alarm_sound_kks,
                                                     target_abonent=self._abonent_map[
                                                         self._options.ts_odu_info.cabinet],
                                                     target_part=self._options.ts_odu_info.warning_sound_part,
                                                     target_page=page_num,
                                                     target_cell=cell_num,
                                                     source_port=self._warn_sound_container[signal]))
                index += 1
            refs.append(SignalRef(kks=self._options.ts_odu_info.alarm_sound_check_kks,
                                  part=self._options.ts_odu_info.alarm_sound_check_part,
                                  ref=f'{self._options.ts_odu_info.alarm_sound_kks}_'
                                      f'{self._options.ts_odu_info.alarm_sound_part}\\'
                                      f'{self._options.ts_odu_info.alarm_sound_check_page}\\'
                                      f'{self._options.ts_odu_info.alarm_sound_check_cell}',
                                  unrel_ref=None))
            refs.append(SignalRef(kks=self._options.ts_odu_info.warn_sound_check_kks,
                                  part=self._options.ts_odu_info.warn_sound_check_part,
                                  ref=f'{self._options.ts_odu_info.warning_sound_kks}_'
                                      f'{self._options.ts_odu_info.warning_sound_part}\\'
                                      f'{self._options.ts_odu_info.warn_sound_check_page}\\'
                                      f'{self._options.ts_odu_info.warn_sound_check_cell}',
                                  unrel_ref=None))

            update_schemas = [(self._options.ts_odu_info.alarm_sound_kks,
                               self._options.ts_odu_info.alarm_sound_part,
                               f'SOUND_ALARM_{len(self._alarm_sound_container)}'),
                              (self._options.ts_odu_info.warning_sound_kks,
                               self._options.ts_odu_info.warning_sound_part,
                               f'SOUND_WARN_{len(self._warn_sound_container)}')]
        logging.info('Завершено.')
        return refs, update_schemas

    def _get_abonent_map(self) -> dict[str, int]:
        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.abonent_table,
                                                                      fields=['CABINET', 'ABONENT_ID'])
        return {value[
                    self._connection.modify_column_name('CABINET')]:
                        int(value[self._connection.modify_column_name('ABONENT_ID')]) for value in values}

    def _get_signal_for_ts_odu_logic(self, kks: str, part: str) -> \
            tuple[Signal | None, ErrorType]:
        values_from_sim: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.sim_table,
                                                                               fields=['CABINET'],
                                                                               key_names=['KKS', 'PART', 'MODULE'],
                                                                               key_values=[kks, part, '1691'],
                                                                               key_operator=['=', '=', '<>'])
        if len(values_from_sim) == 1:
            cabinet: str = values_from_sim[0][self._connection.modify_column_name('CABINET')]
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.WIRED), ErrorType.NOERROR
        values_from_iec: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.iec_table,
                                                                               fields=['CABINET'],
                                                                               key_names=['KKS', 'PART'],
                                                                               key_values=[kks, part])
        if len(values_from_iec) == 1:
            cabinet: str = values_from_iec[0][self._connection.modify_column_name('CABINET')]
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.DIGITAL), ErrorType.NOERROR

        values_from_fake: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.fake_signals_table,
            fields=['CABINET'],
            key_names=['KKS', 'PART'],
            key_values=[kks, part])

        if len(values_from_fake) == 1:
            cabinet: str = values_from_fake[0][self._connection.modify_column_name('CABINET')]
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.WIRED), ErrorType.NOERROR

        values_from_ts_odu: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.ts_odu_table,
                                                                                  fields=['CABINET'],
                                                                                  key_names=['KKS', 'PART'],
                                                                                  key_values=[kks, part])
        if len(values_from_ts_odu) == 1:
            cabinet: str = values_from_ts_odu[0][self._connection.modify_column_name('CABINET')]
            return Signal(kks=kks,
                          part=part,
                          cabinet=cabinet,
                          type=SignalType.TS_ODU), ErrorType.NOERROR
        logging.error(f'Сигнал {kks}_{part} не найден ни в одной таблице')
        return None, ErrorType.NOVALUES

    def _process_or_schemas(self) -> tuple[list[VirtualSchema], list[SignalRef], list[tuple[str, str, str]]] | None:
        ok_flag: bool = True
        used_names: list[str] = []
        dynamic_templates: list[DynamicTemplate] = []
        updated_schemas: list[tuple[str, str, str]] = []
        virtual_schemas: list[VirtualSchema] = []
        signal_refs: list[SignalRef] = []
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.ts_odu_algorithm,
            fields=['KKS', 'PART', 'CABINET', 'INST_PLACE', 'TS_ODU_PANEL', 'TYPE'])
        logging.info('Запуск обработки логики ТС ОДУ...')
        if len(values) > 0:
            ProgressBar.config(max_value=len(values), step=1, prefix='Обработка логики ТС ОДУ', suffix='Завершено',
                               length=50)
            for value in values:
                ProgressBar.update_progress()
                source_signal, source_error = self._get_signal_for_ts_odu_logic(
                    kks=value[self._connection.modify_column_name('KKS')],
                    part=value[self._connection.modify_column_name('PART')])
                if source_error != ErrorType.NOERROR:
                    ok_flag = False
                    continue
                mozaic_element: MozaicElement = MozaicElement(
                    place=value[self._connection.modify_column_name('INST_PLACE')],
                    ts_odu_panel=value[self._connection.modify_column_name('TS_ODU_PANEL')])

                dynamic_template: DynamicTemplate | None = \
                    next((template for template in dynamic_templates
                          if template.target.ts_odu_panel == mozaic_element.ts_odu_panel
                          and template.target.place == mozaic_element.place and
                          template.type == value[self._connection.modify_column_name('TYPE')]), None)
                if dynamic_template is None:
                    dynamic_template = DynamicTemplate(target=mozaic_element,
                                                       source=[source_signal],
                                                       type=value[self._connection.modify_column_name('TYPE')])
                    dynamic_templates.append(dynamic_template)
                else:
                    dynamic_template.source.append(source_signal)
            for dynamic_template in dynamic_templates:
                result = self._get_refs_for_dynamic_template(dynamic_template=dynamic_template,
                                                             used_names=used_names)
                if result is None:
                    ok_flag = False
                    continue
                virtual_schemas += result[0]
                signal_refs += result[1]
                if result[2] is not None:
                    updated_schemas.append(result[2])
            if not ok_flag:
                logging.info('Завершено с ошибками.')
                return None
        logging.info('Завершено.')
        return virtual_schemas, signal_refs, updated_schemas

    def _process_ts_odu_signals(self, updated_schemas: list[tuple[str, str, str]]) -> list[SignalRef] | None:
        ok_flag: bool = True
        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.ts_odu_table,
                                                                      fields=['KKS', 'PART', 'KKSp', 'SCHEMA'])
        logging.info('Запуск обработки сигналов ТС ОДУ...')
        refs: list[SignalRef] = []
        if len(values) > 0:
            ProgressBar.config(max_value=len(values), step=1, prefix='Обработка сигналов ТС ОДУ', suffix='Завершено',
                               length=50)
            for value in values:
                ProgressBar.update_progress()
                kks: str = value[self._connection.modify_column_name('KKS')]
                part: str = value[self._connection.modify_column_name('PART')]
                template_name: str = updated_schemas[2] if updated_schemas[0] == kks and updated_schemas[1] == part \
                    else value[self._connection.modify_column_name('SCHEMA')]
                ts_odu_panel_name: str = value[self._connection.modify_column_name('KKSp')]
                template: TSODUTemplate | None = None
                if template_name is None:
                    continue
                for templ in [self._options.ts_odu_templates_lamp, self._options.ts_odu_templates_displ]:
                    if (templ.name.endswith('%') and template_name.startswith(templ.name[:-1])) \
                            or template_name == templ.name:
                        template = templ
                        break
                if template is None:
                    continue
                ts_odu_panel: TSODUPanel = next((panel for panel in self._options.ts_odu_info.panels if panel.name ==
                                                 ts_odu_panel_name), None)
                acknowledgment_signal: Signal = Signal(kks=ts_odu_panel.acknowledgment_kks,
                                                       part=ts_odu_panel.acknowledgment_part,
                                                       cabinet=self._options.ts_odu_info.cabinet,
                                                       type=SignalType.TS_ODU)
                if template.acknolegment_cell is not None and template.acknolegment_page is not None:
                    ref: SignalRef = self._get_ref_for_signal(source_signal=acknowledgment_signal,
                                                              target_abonent=self._abonent_map[
                                                                  acknowledgment_signal.cabinet],
                                                              target_kks=kks,
                                                              target_part=part,
                                                              target_page=template.acknolegment_page,
                                                              target_cell=template.acknolegment_cell)
                    refs.append(ref)

                acknowledgment_flash_signal: Signal = Signal(kks=ts_odu_panel.acknowledgment_flash_kks,
                                                             part=ts_odu_panel.acknowledgment_flash_part,
                                                             cabinet=self._options.ts_odu_info.cabinet,
                                                             type=SignalType.TS_ODU)
                if template.acknolegment_flash_cell is not None and template.acknolegment_flash_page is not None:
                    ref: SignalRef = self._get_ref_for_signal(source_signal=acknowledgment_flash_signal,
                                                              target_abonent=self._abonent_map[
                                                                  acknowledgment_flash_signal.cabinet],
                                                              target_kks=kks,
                                                              target_part=part,
                                                              target_page=template.acknolegment_flash_page,
                                                              target_cell=template.acknolegment_flash_cell)
                    refs.append(ref)

                if template.warning_port is not None:
                    self._warn_sound_container[Signal(kks=kks,
                                                      part=part,
                                                      cabinet=acknowledgment_signal.cabinet,
                                                      type=SignalType.TS_ODU)] = template.warning_port

                if template.display_test_cell is not None and template.display_test_page is not None \
                        and ts_odu_panel.display_test_kks is not None and \
                        ts_odu_panel.display_test_part is not None \
                        and ts_odu_panel.display_test_port is not None:
                    display_test_ref: str = f'{ts_odu_panel.display_test_port}:{kks}_{part}\\' \
                                            f'{template.display_test_page}\\{template.display_test_cell}'
                    refs.append(SignalRef(kks=ts_odu_panel.display_test_kks,
                                          part=ts_odu_panel.display_test_part,
                                          ref=display_test_ref,
                                          unrel_ref=None))
                if template.lamp_test_cell is not None and template.lamp_test_page is not None \
                        and ts_odu_panel.lamp_test_kks is not None and \
                        ts_odu_panel.lamp_test_part is not None \
                        and ts_odu_panel.lamp_test_port is not None:
                    lamp_test_ref: str = f'{ts_odu_panel.lamp_test_port}:{kks}_{part}\\' \
                                         f'{template.lamp_test_page}\\{template.lamp_test_cell}'
                    refs.append(SignalRef(kks=ts_odu_panel.lamp_test_kks,
                                          part=ts_odu_panel.lamp_test_part,
                                          ref=lamp_test_ref,
                                          unrel_ref=None))
                input_port_list: list[InputPort] = template.input_ports
                if input_port_list is not None:
                    for input_port in input_port_list:
                        source_signal, error = self._get_signal_for_ts_odu_logic(kks=input_port.kks,
                                                                                 part=input_port.part)
                        if error == ErrorType.TOOMANYVALUES:
                            logging.error(
                                f'Найдено больше одного сигнала для порта {input_port.kks}_{input_port.part} для '
                                f'шкафа {ts_odu_panel_name}')
                            ok_flag = False
                            continue
                        if error == ErrorType.NOVALUES:
                            logging.error(
                                f'Не найдено ни одного сигнала для порта {input_port.kks}_{input_port.part} для '
                                f'шкафа {ts_odu_panel_name}')
                            ok_flag = False
                            continue
                        ref: str = f'{kks}_{part}\\{input_port.page}\\{input_port.cell_num}'
                        refs.append(SignalRef(kks=source_signal.kks,
                                              part=source_signal.part,
                                              ref=ref,
                                              unrel_ref=None))
                output_port_list: list[OutputPort] = template.output_ports
                if output_port_list is not None:
                    for output_port in output_port_list:
                        target_signal, error = self._get_signal_for_ts_odu_logic(kks=output_port.kks,
                                                                                 part=output_port.part)
                        if error == ErrorType.TOOMANYVALUES:
                            logging.error(
                                f'Найдено больше одного сигнала для порта {output_port.kks}_{output_port.part} '
                                f'для шкафа {ts_odu_panel_name}')
                            ok_flag = False
                            continue
                        if error == ErrorType.NOVALUES:
                            logging.error(
                                f'Не найдено ни одного сигнала для порта {output_port.kks}_{output_port.part} для'
                                f' шкафа {ts_odu_panel_name}')
                            ok_flag = False
                            continue
                        ref: str = (f'{target_signal.kks}_{target_signal.part}\\{output_port.page}\\'
                                    f'{output_port.cell_num}')
                        refs.append(SignalRef(kks=kks,
                                              part=part,
                                              ref=ref,
                                              unrel_ref=None))
            if not ok_flag:
                logging.info('Завершено с ошибками.')
                return None
        logging.info('Завершено.')
        return refs

    def _get_refs_for_ts_odu_in_define_schema(self, schema_kks: str, schema_part: str, schema_abonent: int,
                                              schema_cabinet: str, ts_odu_data: TSODUData,
                                              mozaic_element: MozaicElement,
                                              add_kks_postfix: bool) \
            -> list[SignalRef] | None:
        refs: list[SignalRef] = []
        if mozaic_element is None:
            return []
        ts_odu_panel: TSODUPanel | None = next((panel for panel in self._options.ts_odu_info.panels if panel.name ==
                                                mozaic_element.ts_odu_panel), None)
        if ts_odu_panel is None:
            logging.error(f'Не найдена панель ТС ОДУ {mozaic_element.ts_odu_panel}')
            return None
        if ts_odu_data.confirm_command_page is not None and ts_odu_data.confirm_command_cell is not None:
            if ts_odu_panel.confirm_part is None or ts_odu_panel.confirm_kks is None:
                logging.error('Для панели не предусмотрена подтверждение')
            kks: str = schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks
            confirm_ref: str = f'Port1:{schema_abonent}\\{kks}_{schema_part}\\' \
                               f'{ts_odu_data.confirm_command_page}\\{ts_odu_data.confirm_command_cell}'
            refs.append(SignalRef(kks=ts_odu_panel.confirm_kks,
                                  part=ts_odu_panel.confirm_part,
                                  ref=confirm_ref,
                                  unrel_ref=None))
        signals_in_mozaic_element: list[Signal] = []
        values: list[dict[str, str]] = self._connection.retrieve_data(table_name=self._options.ts_odu_table,
                                                                      fields=['KKS', 'PART'],
                                                                      key_names=['INST_PLACE', 'KKSp'],
                                                                      key_values=[mozaic_element.place,
                                                                                  mozaic_element.ts_odu_panel])
        if len(values) == 0:
            logging.error(f'Не найден сигналы для мозаичного элемента {mozaic_element.place} панели '
                          f'{mozaic_element.ts_odu_panel}')
            return None
        if len(values) != (len(ts_odu_data.output_ports) + len(ts_odu_data.input_ports)):
            logging.error(f'Число сигналов для мозаичного элемента {mozaic_element.place} панели '
                          f'{mozaic_element.ts_odu_panel} не совпадает с числом сигналов в шаблоне')
            return None
        if sum(value[self._connection.modify_column_name('PART')].startswith('XL') or
               value[self._connection.modify_column_name('PART')].startswith('XA') for value in values) \
                != len(ts_odu_data.input_ports):
            logging.error(f'Число команд для мозаичного элемента {mozaic_element.place} панели '
                          f'{mozaic_element.ts_odu_panel} не совпадает с числом сигналов в шаблоне')
            return None
        for value in values:
            signals_in_mozaic_element.append(Signal(kks=value[self._connection.modify_column_name('KKS')],
                                                    part=value[self._connection.modify_column_name('PART')],
                                                    cabinet=self._options.ts_odu_info.cabinet,
                                                    type=SignalType.TS_ODU))
        for ouput_port in ts_odu_data.output_ports:
            output_signal: Signal | None = next((signal for signal in signals_in_mozaic_element
                                                 if signal.part == ouput_port.part), None)
            if output_signal is None:
                logging.error(f'Не найден сигнал {ouput_port.part}')
                return None
            refs_for_output_port = self._creare_ref_for_output_port(schema_kks=schema_kks,
                                                                    schema_part=schema_part,
                                                                    cabinet=schema_cabinet,
                                                                    output_port=ouput_port,
                                                                    kksp=[ts_odu_panel.name],
                                                                    template_name='ТС ОДУ',
                                                                    signal=output_signal,
                                                                    add_kks_postfix=add_kks_postfix)
            refs += refs_for_output_port
        for input_port in ts_odu_data.input_ports:
            input_signal: Signal | None = next((signal for signal in signals_in_mozaic_element
                                                if signal.part == input_port.part), None)
            if input_signal is None:
                logging.error(f'Не найден сигнал {input_port.part}')
                return None
            kks: str = schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks
            ref = self._get_ref_for_signal(source_signal=input_signal,
                                           target_kks=kks,
                                           target_part=schema_part,
                                           target_abonent=schema_abonent,
                                           target_page=input_port.page,
                                           target_cell=input_port.cell_num)
            refs.append(ref)

        return refs

    def _get_target_signal_for_ts_odu(self, dynamic_template: DynamicTemplate) -> Signal | None:
        values: list[dict[str, str]]
        if self._options.read_english_description:
            values = self._connection.retrieve_data(table_name=self._options.ts_odu_table,
                                                    fields=['PART', 'NAME_RUS', 'NAME_ENG', 'KKS'],
                                                    key_names=['INST_PLACE', 'KKSp', 'TYPE'],
                                                    key_values=[dynamic_template.target.place,
                                                                dynamic_template.target.ts_odu_panel,
                                                                dynamic_template.type])
        else:
            values = self._connection.retrieve_data(table_name=self._options.ts_odu_table,
                                                    fields=['PART', 'NAME_RUS', 'KKS'],
                                                    key_names=['INST_PLACE', 'KKSp', 'TYPE'],
                                                    key_values=[dynamic_template.target.place,
                                                                dynamic_template.target.ts_odu_panel,
                                                                dynamic_template.type])

        if len(values) == 0:
            logging.error(f'Не найден МЭ в панели {dynamic_template.target.ts_odu_panel} по координатам '
                          f'{dynamic_template.target.place}')
            return None
        if len(values) > 1:
            logging.error(f'Повторы в таблице СиМ ТС ОДУ для панели {dynamic_template.target.ts_odu_panel} '
                          f'координаты {dynamic_template.target.place} элемента {dynamic_template.type}')
            return None
        descr_eng: str
        if self._options.read_english_description:
            descr_eng = values[0][self._connection.modify_column_name('NAME_ENG')]
        else:
            descr_eng = ""
        signal: Signal = Signal(kks=values[0][self._connection.modify_column_name('KKS')],
                                part=values[0][self._connection.modify_column_name('PART')],
                                cabinet=self._options.ts_odu_info.cabinet,
                                type=SignalType.TS_ODU,
                                descr_rus=values[0][self._connection.modify_column_name('NAME_RUS')],
                                descr_eng=descr_eng)
        return signal

    def _create_virtual_schema(self, target_kks: str, target_part: str, descr_rus: str, descr_eng: str,
                               target_abonent: int, source_signals: list[Signal]) -> \
            tuple[VirtualSchema, list[SignalRef]]:
        kks: str
        # if index is not None:
        #    kks = f'{target_signal.kks[0:7]}{self._options.or_schema_code}{index}'
        # else:
        #    kks = f'{target_signal.kks}'
        schema: str
        if all(signal.part.startswith('XQ') for signal in source_signals):
            schema: str = f'{self._options.or_schema_meas_name_prefix}{len(source_signals)}'
        else:
            schema: str = f'{self._options.or_schema_name_prefix}{len(source_signals)}'
        virtual_schema: VirtualSchema = VirtualSchema(kks=target_kks,
                                                      part=target_part,
                                                      descr_rus=descr_rus,
                                                      descr_eng=descr_eng,
                                                      schema=schema,
                                                      cabinet=source_signals[0].cabinet)
        refs: list[SignalRef] = []
        refs_on_page: int = self._options.or_schema_end_cell - self._options.or_schema_start_cell + 1

        index: int = 0
        for signal in source_signals:
            cell_num: int = index % (refs_on_page - 1) + self._options.or_schema_start_cell
            page_num: int = index // (refs_on_page - 1) + 2
            refs.append(self._get_ref_for_signal(source_signal=signal,
                                                 target_kks=target_kks,
                                                 target_abonent=target_abonent,
                                                 target_part=target_part,
                                                 target_page=page_num,
                                                 target_cell=cell_num))
            index += 1
        return virtual_schema, refs

    @staticmethod
    def _get_free_name(kks_prefix: str, index: int, part: str, used_names: list[str]) -> str:
        while index < 999:
            kks = f'{kks_prefix}{str.zfill(str(index), 3)}'
            if f'{kks}_{part}' not in used_names:
                used_names.append(f'{kks}_{part}')
                return kks
            used_names.append(f'{kks}_{part}')
            index += 1
        raise Exception('Не удалось подобрать индекс')

    def _create_schemas_for_or_logic(self, template: DynamicTemplate,
                                     target_signal: Signal,
                                     target_ts_odu_panel: TSODUPanel,
                                     used_names: list[str]) -> (
            tuple)[list[VirtualSchema], list[SignalRef], tuple[str, str, str] | None]:

        # Сначала формируется словарь, где ключ - это имя стойки, значение - список сигналов от этой стойки,
        # т.е. группировка сигналов по имени стойки
        source_signals_by_cabinet: dict[str, list[Signal]] = {}
        for source_signal in template.source:
            signals_in_cabinet: list[Signal]
            if source_signal.cabinet not in source_signals_by_cabinet:
                signals_in_cabinet = [source_signal]
                source_signals_by_cabinet[source_signal.cabinet] = signals_in_cabinet
            else:
                signals_in_cabinet = source_signals_by_cabinet[source_signal.cabinet]
                signals_in_cabinet.append(source_signal)
        # Если стойка одна, то только для нее формируем схему OR
        if len(source_signals_by_cabinet.keys()) == 1:
            kks = self._get_free_name(kks_prefix=target_signal.kks[0:7] + self._options.or_schema_code,
                                      index=0,
                                      part=target_signal.part,
                                      used_names=used_names)
            virtual_schema, refs = self._create_virtual_schema(target_kks=kks,
                                                               target_part=target_signal.part,
                                                               descr_rus=target_signal.descr_rus,
                                                               descr_eng=target_signal.descr_eng,
                                                               source_signals=list(list(source_signals_by_cabinet.
                                                                                        values())[0]),
                                                               target_abonent=self._abonent_map[
                                                                   list(source_signals_by_cabinet.keys())[0]])
            signal: Signal = Signal(kks=virtual_schema.kks,
                                    part=virtual_schema.part,
                                    cabinet=virtual_schema.cabinet,
                                    type=SignalType.TS_ODU,
                                    descr_rus=virtual_schema.descr_rus,
                                    descr_eng=virtual_schema.descr_eng)
            refs.append(self._get_ref_for_signal(source_signal=signal,
                                                 target_kks=target_signal.kks,
                                                 target_abonent=target_ts_odu_panel.abonent,
                                                 target_part=target_signal.part,
                                                 target_page=self._options.wired_signal_output_default_page,
                                                 target_cell=self._options.wired_signal_output_default_cell))
            return [virtual_schema], refs, None
        # Если стоек несколько - для каждой формируем схему OR и общую схему OR в панели ТС ОДУ
        index: int = 0
        cabinet_index: int = 0
        virtual_schemas: list[VirtualSchema] = []
        source_cabinet_or_signals: list[Signal] = []
        refs: list[SignalRef] = []
        for cabinet in source_signals_by_cabinet.keys():
            cabinet_index += 1
            if len(source_signals_by_cabinet[cabinet]) == 1:
                # Если сигнал в стойке один, обходимся без формирования схемы OR,
                # источником будет сам сигнал
                source_signal: Signal = source_signals_by_cabinet[cabinet][0]
                source_cabinet_or_signals.append(source_signal)
            else:
                # Если сигналов несколько, предварительно создаем OR схему в шкафу
                kks = self._get_free_name(kks_prefix=target_signal.kks[0:7] + self._options.or_schema_code,
                                          index=cabinet_index,
                                          part=target_signal.part,
                                          used_names=used_names)
                cabinet_schema, cabinet_refs = self._create_virtual_schema(
                    target_kks=kks,
                    target_part=target_signal.part,
                    descr_rus=target_signal.descr_rus,
                    descr_eng=target_signal.descr_eng,
                    source_signals=source_signals_by_cabinet[cabinet],
                    target_abonent=self._abonent_map[cabinet])
                source_cabinet_or_signal: Signal = Signal(kks=cabinet_schema.kks,
                                                          part=cabinet_schema.part,
                                                          cabinet=cabinet,
                                                          type=SignalType.TS_ODU)
                virtual_schemas.append(cabinet_schema)
                refs += cabinet_refs
                source_cabinet_or_signals.append(source_cabinet_or_signal)
            index += 1
        # В шкафу ТС ОДУ OR схема не создается, т.к. будет использоваться непосредственно схемы для
        # вывода дискретного сигнала. Ее префикс TS_ODU_
        index: int = 0
        for signal in source_cabinet_or_signals:
            index += 1
            refs_on_page: int = self._options.or_schema_end_cell - self._options.or_schema_start_cell + 1
            cell_num: int = index % refs_on_page + self._options.or_schema_start_cell - 1
            page_num: int = index // refs_on_page + 2
            refs.append(self._get_ref_for_signal(source_signal=signal,
                                                 target_kks=target_signal.kks,
                                                 target_abonent=target_ts_odu_panel.abonent,
                                                 target_part=target_signal.part,
                                                 target_page=page_num,
                                                 target_cell=cell_num))

        updated_schema_name: str
        if template.type.startswith('LAMP'):

            updated_schema_name = f'{self._options.ts_odu_templates_lamp.name[:-1]}_{len(source_signals_by_cabinet)}'
        elif template.type.startswith('DISPLAY'):
            updated_schema_name = f'{self._options.ts_odu_templates_displ.name[:-1]}_{len(source_signals_by_cabinet)}'
        else:
            logging.error(f'Не удалось определить тип: {template.type}')
            raise Exception('Ошибка')

        return virtual_schemas, refs, (target_signal.kks, target_signal.part, updated_schema_name)

    def _get_refs_for_dynamic_template(self, dynamic_template: DynamicTemplate,
                                       used_names: list[str]) -> \
            tuple[list[VirtualSchema], list[SignalRef], tuple[str, str, str] | None] | None:
        target_ts_odu_panel: TSODUPanel | None = next((panel for panel in self._options.ts_odu_info.panels
                                                       if panel.name == dynamic_template.target.ts_odu_panel), None)
        if target_ts_odu_panel is None:
            logging.error(f"Не найдена панель ТС ОДУ с именем {dynamic_template.target.ts_odu_panel}")
            return None
        target_signal: Signal | None = self._get_target_signal_for_ts_odu(dynamic_template=dynamic_template)
        if target_signal is None:
            return None
        # Если в шаблоне 1 сигнал-источник и 1 сигнал приемник, то сразу формируется ссылка
        if len(dynamic_template.source) == 1:
            return [], [self._get_ref_for_signal(source_signal=dynamic_template.source[0],
                                                 target_kks=target_signal.kks,
                                                 target_part=target_signal.part,
                                                 target_abonent=target_ts_odu_panel.abonent,
                                                 target_page=self._options.wired_signal_output_default_page,
                                                 target_cell=self._options.wired_signal_output_default_cell)], None
        # Случай, когда несколько сигналов источников на один сигнал приемник
        # В этом случае формируются схемы управления OR
        return self._create_schemas_for_or_logic(template=dynamic_template,
                                                 target_signal=target_signal,
                                                 target_ts_odu_panel=target_ts_odu_panel,
                                                 used_names=used_names)

    def _get_ref_for_signal(self, source_signal: Signal, target_kks: str, target_part: str, target_abonent: int,
                            target_page: str | int, target_cell: str | int, source_port: str | None = None) -> \
            SignalRef:
        ref: str
        abonent: str = f'{target_abonent}\\' if target_abonent != self._abonent_map[source_signal.cabinet] else ''
        if source_signal.type == SignalType.DIGITAL:
            ref: str = f'{abonent}{target_kks}_{target_part}\\{target_page}\\{target_cell}'
        else:
            port_prefix = self._options.wired_signal_default_input_port if source_port is None else source_port
            ref: str = f'{port_prefix}:{abonent}{target_kks}_{target_part}\\{target_page}\\{target_cell}'
        signal_ref: SignalRef = SignalRef(kks=source_signal.kks,
                                          part=source_signal.part,
                                          ref=ref,
                                          unrel_ref=None)
        return signal_ref

    def _get_ref_for_schema(self, schema_kks: str, schema_part: str, schema_cabinet: str,
                            add_kks_postfix: bool,
                            template_list: list[Template],
                            template_name: str, kksp: list[str] | None = None,
                            mozaic_element: MozaicElement | None = None,
                            skip_schemas: bool = False) -> list[SignalRef] | None:
        """
        Генерация ссылок для схемы управления
        :param schema_kks: KKS схемы управления
        :param schema_part: PART схемы управления
        :param schema_cabinet: Имя стойки
        :param template_name: Имя шаблона (для диагностических сообщений)
        :param kksp: Код терминала (если известен)
        :param mozaic_element: Мозаичный элемент (если есть)
        :return: Список ссылок либо None при ошибке
        """
        ref_list: list[SignalRef] = []
        template: Template | None = next((templ for templ in template_list
                                          if templ.name == template_name), None)
        schema_abonent: int | None = self._get_abonent_map()[schema_cabinet]
        if schema_abonent is None:
            logging.error(f'Не найден абонент для стойки {schema_cabinet}')
            return None
        if template is None:
            if skip_schemas:
                return []
            else:
                logging.error(f'Не найден шаблон с именем {template_name}')
                return None
        if schema_part not in template.input_ports or schema_part not in template.output_ports:
            logging.error(f'Не найдены сигналы для шаблона {template_name} для PART {schema_part}')
            return None
        if template.alarm_sound_signal_port is not None:
            self._alarm_sound_container[Signal(
                kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                part=schema_part,
                cabinet=schema_cabinet,
                type=SignalType.WIRED,
                descr_rus='АварЗвук',
                descr_eng='AlarmSound')] = template.alarm_sound_signal_port
        if template.warn_sound_signal_port is not None:
            self._warn_sound_container[Signal(
                kks=schema_kks + self._options.control_schema_name_postfix if add_kks_postfix else schema_kks,
                part=schema_part,
                cabinet=schema_cabinet,
                type=SignalType.WIRED,
                descr_rus='ПредЗвук',
                descr_eng='WarnSound')] = template.warn_sound_signal_port
        input_port_list: list[InputPort] | None = template.input_ports[schema_part]
        if input_port_list is not None:
            for port in input_port_list:
                signal_ref: SignalRef | None = self._creare_ref_for_input_port(schema_kks=schema_kks,
                                                                               schema_part=schema_part,
                                                                               cabinet=schema_cabinet,
                                                                               input_port=port,
                                                                               kksp=kksp,
                                                                               template_name=template_name,
                                                                               add_kks_postfix=add_kks_postfix)
                if signal_ref is None:
                    return None
                ref_list.append(signal_ref)

        output_port_list: list[OutputPort] | None = template.output_ports[schema_part]
        if output_port_list is not None:
            for port in output_port_list:
                signal_ref: list[SignalRef] | None = self._creare_ref_for_output_port(schema_kks=schema_kks,
                                                                                      schema_part=schema_part,
                                                                                      cabinet=schema_cabinet,
                                                                                      output_port=port,
                                                                                      kksp=kksp,
                                                                                      template_name=template_name,
                                                                                      add_kks_postfix=add_kks_postfix)
                if signal_ref is None:
                    return None
                ref_list += signal_ref
        if template.ts_odu_data is not None:
            refs: list[SignalRef] | None = self._get_refs_for_ts_odu_in_define_schema(schema_kks=schema_kks,
                                                                                      schema_part=schema_part,
                                                                                      schema_abonent=schema_abonent,
                                                                                      schema_cabinet=schema_cabinet,
                                                                                      mozaic_element=mozaic_element,
                                                                                      ts_odu_data=template.ts_odu_data,
                                                                                      add_kks_postfix=add_kks_postfix)
            if refs is None:
                return None
            ref_list += refs
        return ref_list

    def _write_ref(self, ref_list: list[SignalRef]) -> None:
        """
        Функция записи ссылок в базу
        :param ref_list: Список со ссылками
        :return: None
        """
        for ref in ref_list:
            self._connection.insert_row(table_name=self._options.ref_table,
                                        column_names=['KKS', 'PART', 'REF', 'UNREL_REF'],
                                        values=[ref.kks, ref.part, ref.ref, ref.unrel_ref])
        self._connection.commit()

    def _write_control_schemas(self, dynamic_schemas: list[VirtualSchema]):
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.predifend_control_schemas_table,
            fields=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR_RUS', 'DESCR_ENG'],
            key_names=['ONLY_FOR_REF'],
            key_values=[False])
        for value in values:
            self._connection.insert_row(table_name=self._options.control_schemas_table,
                                        column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR_RUS',
                                                      'DESCR_ENG'],
                                        values=[value[self._connection.modify_column_name('KKS')] +
                                                self._options.control_schema_name_postfix,
                                                value[self._connection.modify_column_name('CABINET')],
                                                value[self._connection.modify_column_name('SCHEMA')],
                                                value[self._connection.modify_column_name('CHANNEL')],
                                                value[self._connection.modify_column_name('PART')],
                                                value[self._connection.modify_column_name('DESCR_RUS')],
                                                value[self._connection.modify_column_name('DESCR_ENG')]])
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.fake_signals_table,
            fields=['KKS', 'CABINET', 'SCHEMA', 'PART', 'DESCR_RUS', 'DESCR_ENG'])
        for value in values:
            self._connection.insert_row(table_name=self._options.control_schemas_table,
                                        column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR_RUS',
                                                      'DESCR_ENG'],
                                        values=[value[self._connection.modify_column_name('KKS')],
                                                value[self._connection.modify_column_name('CABINET')],
                                                value[self._connection.modify_column_name('SCHEMA')],
                                                '0',
                                                value[self._connection.modify_column_name('PART')],
                                                value[self._connection.modify_column_name('DESCR_RUS')],
                                                value[self._connection.modify_column_name('DESCR_ENG')]])
        for dynamic_schema in dynamic_schemas:
            self._connection.insert_row(table_name=self._options.control_schemas_table,
                                        column_names=['KKS', 'CABINET', 'SCHEMA', 'CHANNEL', 'PART', 'DESCR_RUS',
                                                      'DESCR_ENG'],
                                        values=[dynamic_schema.kks, dynamic_schema.cabinet, dynamic_schema.schema,
                                                dynamic_schema.channel, dynamic_schema.part, dynamic_schema.descr_rus,
                                                dynamic_schema.descr_eng])
        self._connection.commit()

    def _update_schemas(self, updated_schemas: list[tuple[str, str, str]]):
        for schema in updated_schemas:
            kks: str = schema[0]
            part: str = schema[1]
            name: str = schema[2]
            self._connection.update_field(table_name=self._options.ts_odu_table,
                                          fields=['SCHEMA'],
                                          values=[name],
                                          key_names=['KKS', 'PART'],
                                          key_values=[kks, part])
        self._connection.commit()

    def _process_custom_schemas_in_ts_odu(self) -> list[SignalRef] | None:
        ref_list: list[SignalRef] = []
        error_flag: bool = False
        values: list[dict[str, str]] = self._connection.retrieve_data(
            table_name=self._options.ts_odu_table,
            fields=['KKS', 'PART', 'SCHEMA', 'KKSp'])
        logging.info('Запуск обработка нетиповых сигналов ТС ОДУ...')
        if len(values) > 0:
            ProgressBar.config(max_value=len(values), step=1, prefix='Обработка нетиповых сигналов ТС ОДУ',
                               suffix='Завершено', length=50)
            cabinet: str = self._options.ts_odu_info.cabinet
            for value in values:
                ProgressBar.update_progress()
                schema_kks: str = value[self._connection.modify_column_name('KKS')]
                schema_part: str = value[self._connection.modify_column_name('PART')]
                template_name: str = value[self._connection.modify_column_name('SCHEMA')]
                mozaic_element: MozaicElement | None = None
                add_kks_postfix: bool = False
                ref_list_for_schema: list[SignalRef] | None = \
                    self._get_ref_for_schema(schema_kks=schema_kks, schema_part=schema_part, schema_cabinet=cabinet,
                                             template_name=template_name,
                                             mozaic_element=mozaic_element,

                                             add_kks_postfix=add_kks_postfix,
                                             template_list=self._options.custom_templates_ts_odu,
                                             skip_schemas=True)
                if ref_list_for_schema is None:
                    error_flag = True
                else:
                    ref_list = ref_list + ref_list_for_schema
            if error_flag:
                logging.info('Завершено с ошибками.')
                return None
        logging.info('Завершено.')
        return ref_list

    def _process(self):
        ref_for_predefined_schemas: list[SignalRef] | None = self._process_defined_schemas()
        if ref_for_predefined_schemas is None:
            return
        ts_odu_ref_list: list[SignalRef] = []
        refs_for_ts_odu_signals: list[SignalRef] | None = []
        virtual_schemas: list[VirtualSchema] | None = []
        updated_sound_schemas: list[tuple[str, str, str]] = []
        updated_schemas: list[tuple[str, str, str]] = []
        sound_refs: list[SignalRef] = []
        custom_refs: list[SignalRef] | None = []
        if self._options.ts_odu_info is not None:
            process_or_schemas_result = self._process_or_schemas()
            if process_or_schemas_result is None:
                return
            virtual_schemas, ts_odu_ref_list, updated_schemas = process_or_schemas_result
            refs_for_ts_odu_signals = self._process_ts_odu_signals(updated_schemas=updated_schemas)
            if refs_for_ts_odu_signals is None:
                return
            sound_refs, updated_sound_schemas = self._process_sound_signals()
            custom_refs: list[SignalRef] | None = self._process_custom_schemas_in_ts_odu()
            if custom_refs is None:
                return
        refs: list[SignalRef] = \
            ref_for_predefined_schemas + ts_odu_ref_list + refs_for_ts_odu_signals + sound_refs + custom_refs
        logging.info('Запись результатов...')
        self._connection.clear_table(table_name=self._options.ref_table)
        self._connection.clear_table(table_name=self._options.control_schemas_table)
        self._write_ref(ref_list=refs)
        self._write_control_schemas(dynamic_schemas=virtual_schemas)
        self._update_schemas(updated_schemas=updated_schemas + updated_sound_schemas)
        logging.info('Завершено.')

    @staticmethod
    def run(options: FillRef2Options, connection: Connection) -> None:
        logging.info('Запуск скрипта "Расстановка ссылок"...')
        with connection:
            fill_ref_class: FillRef2 = FillRef2(options=options,
                                                connection=connection)
            fill_ref_class._process()
        logging.info('Выпонение скрипта "Расстановка ссылок" завершено.')
        logging.info('')
