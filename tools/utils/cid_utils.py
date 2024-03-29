from dataclasses import dataclass
from enum import Enum
from lxml import etree as et

import logging


@dataclass(init=True, unsafe_hash=False, repr=False, eq=False, order=False, frozen=True)
class NodeDescription:
    xpath: str
    attribute: str | None
    allow_multiply: bool = False


@dataclass(init=True, unsafe_hash=False, repr=False, eq=True, order=False, frozen=True)
class ParameterData:
    data: list[NodeDescription]


class Nodes(ParameterData, Enum):
    IP = ParameterData([NodeDescription('/SCL/Communication/SubNetwork/ConnectedAP/Address/P[@type="IP"]', None)])
    MASK = ParameterData([NodeDescription('/SCL/Communication/SubNetwork/ConnectedAP/Address/P[@type="IP-SUBNET"]',
                                          None)])
    IEDNAME = ParameterData([NodeDescription('/SCL/Header', 'id'),
                             NodeDescription('/SCL/Communication/SubNetwork/ConnectedAP', 'iedName'),
                             NodeDescription('/SCL/IED', 'name')])
    DESCR = ParameterData([NodeDescription('/SCL/IED', 'desc')]) \

    WRONGINTPERIODINREPORT = ParameterData([NodeDescription(
        '/SCL/IED/AccessPoint/Server/LDevice/LN0/ReportControl[@intgPd="0"]/TrgOps[@period="true"]',
        'period', True)])


def save_xml(xml_content: bytes, target_file_name: str):
    with open(target_file_name, 'wb') as xml_file:
        # BOM (byte-order-mark) символы
        xml_file.write(b'\xef\xbb\xbf')

        # Замена одинарных кавычек в xml_declaration на двойные
        end_of_first_line: int = xml_content.index(b'\n')
        first_line: bytes = xml_content[:end_of_first_line].replace(b"'", b'"')
        xml_content = first_line + xml_content[end_of_first_line:]

        # Преобразование LF -> CRLF
        xml_content = xml_content.replace(b'\n', b'\r\n')

        xml_file.write(xml_content)


def get_updated_content(source_file_name: str, parameters: list[tuple[ParameterData, str]]) -> bytes:
    namespaces = {'scl': 'http://www.iec.ch/61850/2003/SCL'}

    is_correct: bool = True
    tree: et.ElementTree = et.parse(source_file_name)
    for parameter, value in parameters:
        for node in parameter.data:
            path: str = node.xpath
            xpath: str = path.replace('/', '/scl:')
            elements = tree.xpath(xpath, namespaces=namespaces)
            if len(elements) == 0:
                is_correct = False
                logging.error("Для файла {0} не найден параметр {1}".format(source_file_name, path))
                continue
            elif len(elements) > 1 and not node.allow_multiply:
                is_correct = False
                logging.error("Для файла {0} найдено несколько параметров параметр {1}".format(source_file_name, path))
                continue
            for element in elements:
                if node.attribute is None:
                    element.text = value if value is not None else ''
                else:
                    if node.attribute not in element.keys():
                        is_correct = False
                        logging.error(
                            "Для файла {0} и параметра {1} не найден атрибут {2}".format(source_file_name, path,
                                                                                         node.attribute))
                        break
                    element.attrib[node.attribute] = value if value is not None else ''

    if is_correct:
        root: et.Element = tree.getroot()
        return et.tostring(root, xml_declaration=True, encoding='utf-8')
    else:
        raise Exception('WrongXMLData')
