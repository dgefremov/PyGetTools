from typing import Dict, List
from sql_utils import SQLUtils
from tpts_classes import Controller, IecModule, Ied


def get_abonents(access_base: SQLUtils) -> List[Controller]:
    abonents_data: List[Dict[str, str]] = access_base.retrieve_data(
        table_name='TPTS',
        fields=['CABINET', 'ABONENT_ID', 'RESERVED', 'TPTSTYPE'],
        key_values=None,
        key_names=None)

    controllers: List[Controller] = []

    for abonent_data in abonents_data:
        cabinet: str = abonent_data['CABINET']
        db_name: str = ''
        abonent_id: int = int(abonent_data['ABONENT_ID'])
        controller_type: str = abonent_data['TPTSTYPE']
        is_reserved: bool = abonent_data['RESERVED'] == 'Y'.casefold()

        controller: Controller = Controller.create(
            cabinet=cabinet,
            abonent_id=abonent_id,
            controller_type=controller_type,
            is_reserved=is_reserved,
            db_name=db_name,
            sign='база')
        controller.iec_modules = get_iecmodules(access_base, controller)
        controllers.append(controller)
    return controllers


def get_iecmodules(access_base: SQLUtils, controller: Controller) -> List[IecModule]:
    iec_modules_data: List[Dict[str, str]] = access_base.retrieve_data(
        table_name='[Модули связи с процессом]',
        fields=['SLOT_MP', 'REDND_INTF', 'IP'],
        key_names=['CABINET', 'MODULE'],
        key_values=[controller.cabinet, '1691'],
        sort_by=['SLOT_MP'])

    iec_modules: List[IecModule] = []
    index: int = 0
    while index < len(iec_modules_data):
        iec_module_data: Dict[str, str] = iec_modules_data[index]
        master_slot: int = round(float(iec_module_data['SLOT_MP']))
        is_reserved: bool = iec_module_data['REDND_INTF'].casefold() == 'Y'.casefold()
        mask: str = '255.255.255.0'
        master_ip: str = iec_module_data['IP']

        iec_module: IecModule
        if is_reserved:
            index += 1
            iec_res_module_data: Dict[str, str] = iec_modules_data[index]
            slave_ip: str = iec_res_module_data['IP']
            slave_slot: int = round(float(iec_res_module_data['SLOT_MP']))
            iec_module = IecModule.create_reserved(
                master_slot=master_slot,
                slave_slot=slave_slot,
                master_ip=master_ip,
                slave_ip=slave_ip,
                mask=mask,
                parent=controller)
        else:
            iec_module = IecModule.create(
                master_slot=master_slot,
                master_ip=master_ip,
                parent=controller,
                mask=mask)
        iec_module.ieds = get_ieds(access_base, iec_module)
        iec_modules.append(iec_module)
        index += 1
    return iec_modules


def get_ieds(access_base: SQLUtils, iec_module: IecModule) -> List[Ied]:
    ieds_data: List[Dict[str, str]] = access_base.retrieve_data(
        table_name='[МЭК 61850]',
        fields=['KKSp', 'IP', 'IED_NAME'],
        key_names=['CABINET', 'SLOT_MP'],
        key_values=[iec_module.get_controller().cabinet, iec_module.master_slot],
        uniq_values=True)
    ieds: List[Ied] = []
    for ied_data in ieds_data:
        ip: str = ied_data['IP']
        ied_name: str = ied_data['IED_NAME']
        kksp: str = ied_data['KKSp']
        ied: Ied = Ied.create(
            kksp=kksp,
            ied_name=ied_name,
            ip=ip)
        ieds.append(ied)
    return ieds
