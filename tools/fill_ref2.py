import logging
from dataclasses import dataclass

from tools.utils.sql_utils import Connection
from tools.utils.progress_utils import ProgressBar


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Cell:
    page: int
    cell_num: int
    kks: str | None
    part: str

    def clone(self) -> 'Cell':
        return Cell(self.page, self.cell_num, self.kks, self.part)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class Template:
    name: str
    inputs: [Cell]
    outputs: [Cell]

    def clone(self) -> 'Template':
        return Template(self.name, self.inputs, self.outputs)


@dataclass(init=True, repr=False, eq=False, order=False, frozen=True)
class FillRef2Options:
    control_schemas_table: str
    ref_table: str
    sim_table: str
    iec_table: str
    templates: [Template]


class FillRef2:
    _options: FillRef2Options
    _access: Connection

    def __init__(self, options: FillRef2Options, access: Connection):
        self._options = options
        self._access = access

    def _signal_list(self, kks: str, kksp: str, cabinet: str, kks_shemas: list[str]) -> dict[str, list[str]]:
        """
        Функция получения списка сигналов для расстановки ссылок. Поиск осуществляется сначала
        по ККС, потом по KKSp.
        :param kks: ККС, для которого осуществляется поиск Part
        :param kksp: KKSp для которого осуществляется поиск Part
        :param cabinet: Имя шкафа для сужения поиска
        :param kks_shemas: Список ККС для схем управления. Part с такими ККС игнорируются (для исключения пересечений
        при наличии в пределах KKSp двух схем управления
        :return: Список PART с их KKS
        """
        parts_dict: dict[str, list[str]] = {}
        pars_from_sim: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table,
                                                                           fields=['PART'],
                                                                           key_names=['KKS', 'CABINET'],
                                                                           key_values=[kks, cabinet])
        for value in pars_from_sim:
            if value['PART'] not in pars_from_sim:
                parts_dict[value['PART']] = [kks]

        parts_from_iec: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.iec_table,
                                                                           fields=['PART'],
                                                                           key_names=['KKS', 'CABINET'],
                                                                           key_values=[kks, cabinet])
        for value in parts_from_iec:
            if value['PART'] not in pars_from_sim:
                parts_dict[value['PART']] = [kks]

        values_from_kksp: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.sim_table_name,
                                                                            fields=['PART', 'KKS'],
                                                                            key_names=['KKSp', 'CABINET'],
                                                                            key_values=[kksp, cabinet])
        for value in values_from_kksp:
            # Если ККС относится к схеме, которая есть в списке схем - пропускаем
            if value['KKS'] in kks_shemas:
                continue

            if value['PART'] not in parts_dict:
                parts_dict[value['PART']] = [value['KKS']]
            else:
                parts_dict[value['PART']].append(value['KKS'])
        return parts_dict

    def find_ref_for_template(self, kks: str, part: str, cabinet: str, template_name: str,
                              ref_base: dict[(str, str), str]) -> None:
        local_ref_base: dict[(str, str), str] = []
        template: Template = next((templ for templ in self._options.templates
                                   if templ.name.upper() == template_name.upper()), None)
        if template is None:
            logging.error(f"Не найден шаблон с именем {template_name} для схемы управления {kks}_{part}")
            return

        for cell in template.inputs:


    def check(self, ref_base: dict[(str, str), str]):
        value_list: list[dict[str, str]] = self._access.retrieve_data(table_name=self._options.control_schemas_table,
                                                                      fields=['KKS', 'CABINET', 'SCHEMA', 'PART'])
        for value in value_list:
            template_name: str = value['SCHEMA']
            kks: str = value['KKS']
            part: str = value['PART']
            cabinet: str = value['CABINET']
