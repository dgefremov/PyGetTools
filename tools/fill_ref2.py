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
    templates: [Template]


class FillRef2:
    _options: FillRef2Options

    def __init__(self, options: FillRef2Options):
        self._options = options

    def check(self):
        data: list[dict[str, str]] = None