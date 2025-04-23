
import re

def get_parameter_by_key(data, search_key):
    if search_key in data:
        return data[search_key]

    if 'fullSpecsGrouped' in data:
        for group in data['fullSpecsGrouped']['groups']:
            if 'items' in group:
                for item in group['items']:
                    if item['name'] == search_key:
                        return item['value']
    return None

def get_value_by_key(d, target_key):
    """
    Рекурсивная функция для поиска значения по ключу в вложенном словаре.

    :param d: Словарь, в котором выполнить поиск.
    :param target_key: Ключ, значение которого нужно найти.
    :return: Значение по ключу, если найдено; иначе None.
    """
    # Проверяем, если ключ текущего словаря совпадает с искомым
    if target_key in d:
        return d[target_key]
    
    # Итерируемся по всем элементам словаря
    for value in d.values():
        # Если значение - это словарь, рекурсивно ищем в нем
        if isinstance(value, dict):
            found_value = get_value_by_key(value, target_key)
            if found_value is not None:
                return found_value
        # Если значение - это список, проверяем каждый элемент списка
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    found_value = get_value_by_key(item, target_key)
                    if found_value is not None:
                        return found_value
                elif isinstance(item, str) and item == target_key: # Если элемент - строка
                    return item
    return None

result = {
        'components': [
            {
                'component_name': 'video_card KFA2 GeForce GTX 1060 EX, 6GB GDDR5, PCI-E, 6144MB, 192 Bit',
                'price': 15000.00,
                'fullSpecsGrouped': {
                    'groups': [
                        {
                            'name': 'Графический процессор',
                            'items': [
                                {'name': 'Бренд', 'value': 'KFA2', 'transition': {'type': 'catalog', 'params': {'glfilters': ['7893318:7693369']}}}, {'name': 'Комплектация', 'value': 'Retail'}, {'name': 'Название видеокарты', 'value': 'GeForce GTX 1060'}, {'name': 'Кодовое название видеопроцессора', 'value': 'GP106-400'}, {'name': 'Разработчик видеокарты', 'value': 'NVIDIA', 'transition': {'type': 'catalog', 'params': {'glfilters': ['50048792:50220415']}}}, {'name': 'Линейка', 'value': 'GeForce', 'transition': {'type': 'catalog', 'params': {'glfilters': ['4878791:12108566']}}}, {'name': 'Техпроцесс', 'value': '16 нм'}, {'name': 'Тип подключения', 'value': 'PCI Express 3.0', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128795:50197661']}}}, {'name': 'Количество видеопроцессоров', 'value': '1'}, {'name': 'Количество поддерживаемых мониторов', 'value': '3'}]}, {'name': 'Технические характеристики', 'items': [{'name': 'Максимальное разрешение', 'value': '7680x4320'}, {'name': 'Частота видеопроцессора', 'value': '1733 МГц'}, {'name': 'Частота памяти', 'value': '8008 МГц'}, {'name': 'Объем видеопамяти (точно)', 'value': '6144 МБ'}, {'name': 'Объем видеопамяти', 'value': '6 ГБ', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45123612:50195424']}}}, {'name': 'Тип памяти', 'value': 'GDDR5', 'transition': {'type': 'catalog', 'params': {'glfilters': ['37338070:38439390']}}}, {'name': 'Разрядность шины памяти', 'value': '192 бит', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45131906:50218305']}}}, {'name': 'Область применения', 'value': 'игровая'}]}, {'name': 'Дополнительные характеристики', 'items': [{'name': 'Разъем дополнительного питания', 'value': '6 pin'}, {'name': 'Рекомендуемая мощность блока питания', 'value': '400 Вт'}, {'name': 'TDP', 'value': '120 Вт'}, {'name': 'Дизайн системы охлаждения', 'value': 'кастомный'}, {'name': 'Количество вентиляторов', 'value': '2'}, {'name': 'Длина', 'value': '228 мм'}, {'name': 'Высота', 'value': '132 мм'}, {'name': 'Толщина', 'value': '42 мм'}, {'name': 'Количество занимаемых слотов', 'value': '2'}]}, {'name': 'Разъемы и интерфейсы', 'items': [{'name': 'Разъемы и интерфейсы', 'value': 'выход DisplayPort, выход HDMI, DVI-D', 'transition': {'type': 'catalog', 'params': {'glfilters': ['35324530:52026180,35358590']}}}, {'name': 'Версия DisplayPort', 'value': '1.4'}, {'name': 'Тип HDMI', 'value': '2.0b', 'transition': {'type': 'catalog', 'params': {'glfilters': ['27142431:28729069']}}}]}, {'name': 'Математический блок', 'items': [{'name': 'Версия CUDA', 'value': '6.1'}, {'name': 'Число универсальных процессоров', 'value': '1280'}, {'name': 'Число текстурных блоков', 'value': '80'}, {'name': 'Число блоков растеризации', 'value': '48'}, {'name': 'Версия DirectX', 'value': '12'}, {'name': 'Версия OpenGL', 'value': '4.5'}, {'name': 'Версия OpenCL', 'value': '1.2'}, {'name': 'Версия шейдеров', 'value': '5.0'}, {'name': 'Частота шейдерных блоков', 'value': '1518 МГц'}, {'name': 'Максимальная степень анизотропной фильтрации', 'value': '16x'}]}, {'name': 'Дополнительно', 'items': [{'name': 'Гарантийный срок', 'value': '30 дн., 30 дней от даты получения товара'}]}], 'transitionId': 'tr_17236491404324351385'
                },
            },
        ]
    }

#print(get_parametrs(result, 'user'))
#print(get_parametrs(result, 'price'))
#print(get_parametrs(result, 'Бренд'))
#print(get_parametrs(result, 'Комплектация'))
#print(get_parametrs(result, 'Разработчик видеокарты'))
#print(get_parametrs(result, 'Гарантийный срок'))
#print(get_parametrs(result, 'Дополнительные характеристики'))
#print(get_parametrs(result, 'Разъем дополнительного питания'))

 # components = {
#     "motherboard": {
#         "name": "ASUS ROG Strix B550-F",
#         "connect": "PCI-E 2.0 x1, PCI-E 3.0 x16",
#         "form_factor": "XLATX",
#         "chipset" : "AMD A620",
#         "socket_type": "AM4",
#         "ram_slots": 4,
#         "compatible_ram": "DDR IV, DDR-4, DDR4, DDR4 SDRAM, DDR4-SDRAM"
#     },
#     "processor": {
#         "name": "AMD Ryzen 5 5600X",
#         "socket_type": "AM4",
#         "type" :"DDR4",
#     },
#     "ram": {
#         "name": "Corsair Vengeance LPX 16GB",
#         "type": "DDR4",
#     },
#     "video_card": {
#         "name": "NVIDIA GeForce RTX 3060",
#         "connect": "PCI Express 4.0",
#         "width": "100 мм",
#         "length": "100 мм",
#         "hight": "100 мм",

#     },
#     "ssd": {
#         "name": "Винчестер SATA 500Gb WD Caviar Blue WD5000AAKX-001CA0",
#         "form_factor":"3.5",
#     },
#     "body": {
#         "name": "Корпус 1STPLAYER FD3 White (FD3-WH-4F1-W)",
#         "form_factor":"ATX, Micro-ATX, Mini-ITX",
#         "width": "300 мм",
#         "length": "400 мм",
#         "hight": "200 мм",
#         "max_video_card": "150 мм",
#     }
# }

def extract_pci_version(new_string):
    new_string = new_string.lower().replace('-',' ')
    match = re.search(r'pci express\s+(\d+)\.\d+', new_string, re.IGNORECASE)
    if match:
        try:
            number = int(match.group(1))
            return [number]
        except:
            if 'pci express' in new_string:
                return [1]
            return []
    else:
        if 'pci express' in new_string:
                return [1]
        return []

def extract_pci_versions(pci_string):
    #pci_string = "PCI-E 4.0 x16"
    #pci_string = "5 x PCI-E 3.0 x16, PCI-E 4.0 x16"
    #pci_string = "PCI-E 3.0 x1, PCI-E 3.0 x16"
    #pci_string = "2 x PCI 3.0 x16, PCI-E 3.0 x1"
    #pci_string = "mini PCI-E x1"
    #pci_string = "2 x mini PCI-E x1"
    #pci_string = "2 x PCI-E 3.0 x16, 3 x PCI-E 2.0 x16, PCI-E 4.0 x16"
    #pci_string = "PCI-E 3.0 x1, PCI-E 3.0 x16, количество PCI-E x1 - 1, количество PCI-E x16 - 1"
    pci_string.strip()
    pci_string = pci_string.replace('x','')
    if pci_string[0].isdigit() and pci_string[1] == '.' and pci_string[2].isdigit():
        return [int(pci_string[0])]
    if pci_string[0].isalpha() == False:
        pci_string = pci_string[1:len(pci_string)]
    pci_string = pci_string.lower()
    pci_versions = [item.strip() for item in pci_string.split(',')]
    extracted_versions = []
    for version in pci_versions:
        if "pci-e" in version:
            if 'mini' in version:
                return ['1']
            if 'поддержка' in version:
                v = version.replace('поддержка ','')
                version_number = v.split(' ')[1].split('.')[0]
            else:
                version_number = version.split(' ')[1].split('.')[0]
            if version_number.isdigit():
                try:
                    if extracted_versions[0] < int(version_number):
                        extracted_versions.append(int(version_number))
                except:
                    extracted_versions.append(int(version_number))
    extracted_versions.sort()
    return extracted_versions[::-1]

def get_all_pci_versions(existing_versions):
    if not existing_versions:
        return [0]
    all_versions = []
    max = existing_versions[0]
    for i in range(1,max+1):
        all_versions.append(i)
    
    return all_versions[::-1]

def compatible(
               motherboards=[],
               processors=[],
               videocards=[],
               rams=[],
               bodys=[],
               ssds=[],
               coolers=[],
               charges=[]
                   ):
    f = ''
    r = ''
    # motherboards = get_components_by_type_and_price("materinskie-platy",500,30000)
    # processors = get_components_by_type_and_price("protsessory-cpu",500,30000)
    # videocards = get_components_by_type_and_price("videokarty",500,30000)
    # rams = get_components_by_type_and_price("moduli-pamiati",500,30000)
    # bodys = get_components_by_type_and_price("kompiuternye-korpusa",500,30000)
    # ssds = get_components_by_type_and_price("vnutrennie-tverdotelnye-nakopiteli-ssd",500,30000)
    # print("motherboards = ",motherboards)
    # print("processors = ",processors)
    # print("videocards = ",videocards)
    # print("rams = ",rams)
    # print("bodys = ",bodys)
    # print("ssds = ",ssds)

    sizes = {
        "itx": {
            "length": "170",
            "width": "170"
        },
        "matx": {
            "length": "244",
            "width": "244",
        },
        "flexatx": {
            "length": "229",
            "width": "191"
        },
        "atx": {
            "length": "305",
            "width": "244"
        },
        "microatx": {
            "length": "284",
            "width": "208"
        },
        "xlatx": {
            "length": "343",
            "width": "262"
        },
        "eatx": {
            "length": "305",
            "width": "330"
        },
        "eeatx": {
            "length": "347",
            "width": "330"
        },
        "hptx": {
            "length": "345",
            "width": "381"
        },
        "wtx": {
            "length": "356",
            "width": "425"
        }
        }

    m = 0
    p = 0
    r = 0
    v = 0
    b = 0
    s = 0
    co = 0
    ch = 0
    mb = 0
    pb = 0
    rb = 0
    vb = 0
    bb = 0
    sb = 0
    cob = 0
    chb = 0
    map = 0
    mar = 0
    for m in range(len(motherboards)):
        print("m = ", m,p,r,v,b,s,co,ch)
        mb = 0
        pb = 0
        rb = 0
        vb = 0
        bb = 0
        sb = 0
        cob = 0
        chb = 0
        map = 0
        mar = 0
        for p in range(len(processors)):
            #print("p = ", m,p,r,v,b,s,co,ch)
            pb = 0
            rb = 0
            vb = 0
            bb = 0
            sb = 0
            cob = 0
            chb = 0
            map = 0
            mar = 0
            if  mb == 1:
                break
            for r in range(len(rams)):
                #print("r = ", m,p,r,v,b,s,co,ch)
                rb = 0
                vb = 0
                bb = 0
                sb = 0
                cob = 0
                chb = 0
                map = 0
                mar = 0
                if  mb or pb == 1:
                    break
                for v in range(len(videocards)):
                    #print("v = ", m,p,r,v,b,s,co,ch)
                    vb = 0
                    bb = 0
                    sb = 0
                    cob = 0
                    chb = 0
                    map = 0
                    mar = 0
                    if  mb or pb or rb == 1:
                        break
                    for b in range(len(bodys)):
                        bb = 0
                        sb = 0
                        cob = 0
                        chb = 0
                        map = 0
                        mar = 0
                        if  mb or pb or rb or vb == 1:
                            break
                        for s in range(len(ssds)):
                            sb = 0
                            cob = 0
                            chb = 0
                            map = 0
                            mar = 0
                            if mb or pb or rb or vb or bb == 1:
                                break
                            for co in range(len(coolers)): 
                                cob = 0
                                chb = 0
                                map = 0
                                mar = 0
                                if mb or pb or rb or vb or bb or sb == 1:
                                    break
                                for ch in range(len(charges)):
                                    if mb or pb or rb or vb or bb or sb or cob == 1:
                                        break
                                    cooler_socket = ''
                                    count = 0
                                    mb = 0
                                    pb = 0
                                    rb = 0
                                    vb = 0
                                    bb = 0
                                    sb = 0
                                    cob = 0
                                    chb = 0
                                    map = 0
                                    mar = 0
                                    w = ''
                                    f = ''
                                    ra = ''
                                    c = ''
                                    try:
                                        q = motherboards[m]["component_name"]
                                        if q == None: mb = 1
                                        q = get_parameter_by_key(motherboards[m], 'Слоты PCI-E подробно')
                                        if q == None: mb = 1
                                        q = get_parameter_by_key(motherboards[m], 'Форм-фактор')
                                        if q == None: mb = 1
                                        q = get_parameter_by_key(motherboards[m], 'Сокет')
                                        if q == None: mb = 1
                                        q = get_parameter_by_key(motherboards[m], 'Тип памяти')
                                        if q == None: mb = 1
                                    except:
                                        mb = 1
                                    try:
                                        q = processors[p]["component_name"]
                                        if q == None: pb = 1
                                        q = get_parameter_by_key(processors[p], 'Сокет')
                                        if q == None: pb = 1
                                        q = get_parameter_by_key(processors[p], 'Тип памяти')
                                        if q == None: pb = 1
                                        q = get_parameter_by_key(processors[p],'Тепловыделение')
                                        if q == None: pb = 1
                                    except:
                                        pb = 1
                                    try:
                                        q = rams[r]["component_name"]
                                        if q == None: rb = 1
                                        if get_parameter_by_key(rams[r], 'Тип памяти') == None:
                                            if get_parameter_by_key(rams[r], 'Тип') == None:
                                                rb = 1
                                            else:
                                                w = get_parameter_by_key(rams[r], 'Тип')
                                        else:
                                            w = get_parameter_by_key(rams[r], 'Тип памяти')
                                    except:
                                        rb = 1
                                    try:
                                        q = videocards[v]["component_name"]
                                        if q == None: vb = 1
                                        q = get_parameter_by_key(videocards[v], 'Тип подключения')
                                        if q == None: vb = 1
                                        q = get_parameter_by_key(videocards[v], 'Длина')
                                        if q == None: vb = 1
                                    except:
                                        vb = 1
                                    try:
                                        q = bodys[b]["component_name"]
                                        if q == None: bb = 1
                                        q = get_parameter_by_key(bodys[b], 'Форм-фактор материнской платы')
                                        if q == None: bb = 1
                                        q = get_parameter_by_key(bodys[b], 'Ширина')
                                        if q == None: bb = 1
                                        q = get_parameter_by_key(bodys[b], 'Глубина')
                                        if q == None: bb = 1
                                        q = get_parameter_by_key(bodys[b], 'Высота')
                                        if q == None: bb = 1
                                        q = get_parameter_by_key(bodys[b], 'Максимальная длина видеокарты')
                                        if q == None: bb = 1
                                    except:
                                        bb = 1
                                    try:
                                        q = ssds[s]["component_name"]
                                        if q == None: sb = 1
                                        q = get_parameter_by_key(ssds[s], 'Форм-фактор')
                                        if q == None: sb = 1
                                    except:
                                        sb = 1
                                    try:
                                        q = coolers[co]["component_name"]
                                        if q == None: cob = 1
                                        q = get_parameter_by_key(coolers[co], 'Сокет')
                                        if q == None: 
                                            if get_parameter_by_key(coolers[co], 'Сокет процессора') == None: cob = 1
                                            else:
                                                cooler_socket = get_parameter_by_key(coolers[co], 'Сокет процессора')
                                        else:
                                            cooler_socket = get_parameter_by_key(coolers[co], 'Сокет')
                                        #print("cooler_socket = ",cooler_socket)
                                        q = get_parameter_by_key(coolers[co],'Максимальная рассеиваемая мощность (TDP), Вт')
                                        if q == None: cob = 1
                                    except:
                                        cob = 1
                                    try:
                                        q = charges[ch]["component_name"]
                                        if q == None: chb = 1
                                        q = get_parameter_by_key(charges[ch], 'Форм-фактор')
                                        if q == None: chb = 1
                                        q = get_parameter_by_key(charges[ch], 'Мощность')
                                        if q == None: chb = 1
                                    except:
                                        chb = 1
                                    if mb or pb or rb or vb or bb or sb or cob == 1:
                                        break
                                    try:
                                        pci = get_parameter_by_key(motherboards[m], 'Слоты PCI-E подробно')
                                        if pci == None:
                                            pci = get_parameter_by_key(motherboards[m], 'Версия PCI Express')
                                            if pci == None:
                                                mb = 1
                                    except:
                                        mb = 1 
                                    if chb == 0:
                                        components = {
                                            "motherboard": {
                                                "name": motherboards[m]["component_name"],
                                                "connect": pci,
                                                "form_factor": get_parameter_by_key(motherboards[m], 'Форм-фактор'),
                                                "socket_type": get_parameter_by_key(motherboards[m], 'Сокет'),
                                                "compatible_ram": get_parameter_by_key(motherboards[m], 'Тип памяти')
                                            },
                                            "processor": {
                                                "name": processors[p]["component_name"],
                                                "socket_type": get_parameter_by_key(processors[p], 'Сокет'),
                                                "type" : get_parameter_by_key(processors[p], 'Тип памяти'),
                                                "power" : get_parameter_by_key(processors[p],'Тепловыделение'),
                                            },
                                            "ram": {
                                                "name": rams[r]["component_name"],
                                                "type": w,
                                            },
                                            "video_card": {
                                                "name": videocards[v]["component_name"],
                                                "connect": get_parameter_by_key(videocards[v], 'Тип подключения'),
                                                "width": get_parameter_by_key(videocards[v], 'Толщина'),
                                                "length": get_parameter_by_key(videocards[v], 'Длина'),
                                                "hight": get_parameter_by_key(videocards[v], 'Высота'),

                                            },
                                            "body": {
                                                "name": bodys[b]["component_name"],
                                                "form_factor":get_parameter_by_key(bodys[b], 'Форм-фактор материнской платы'),
                                                "width": get_parameter_by_key(bodys[b], 'Глубина'),
                                                "length": get_parameter_by_key(bodys[b], 'Ширина'),
                                                "hight": get_parameter_by_key(bodys[b], 'Высота'),
                                                "max_video_card": get_parameter_by_key(bodys[b], 'Максимальная длина видеокарты'),
                                            },
                                            "ssd": {
                                                "name": ssds[s]["component_name"],
                                                "form_factor":get_parameter_by_key(ssds[s], 'Форм-фактор'),
                                            },
                                            "coolers":{
                                                "name": coolers[co]["component_name"],
                                                "socket_type": cooler_socket,
                                                "power" : get_parameter_by_key(coolers[co],'Максимальная рассеиваемая мощность (TDP), Вт'),
                                            },
                                            "charges":{
                                                "name": charges[ch]["component_name"],
                                                "form_factor": get_parameter_by_key(charges[ch], 'Форм-фактор'),
                                                "power": get_parameter_by_key(charges[ch], 'Мощность'),
                                            }
                                        }
                                        cooler_power = ''
                                        processor_power = ''
                                        p_power = components["processor"]['power']
                                        c_power = components["coolers"]['power']
                                        for i in range(len(p_power)):
                                            if p_power[i].isdigit():
                                                processor_power += p_power[i]
                                        for i in range(len(c_power)):
                                            if c_power[i].isdigit():
                                                cooler_power += c_power[i]

                                        body_factor = components["body"]["form_factor"]
                                        power_factor = components["charges"]["form_factor"]
                                        pci_string = components["motherboard"]["connect"]
                                        mother_connect = get_all_pci_versions(extract_pci_versions(pci_string))
                                        #print(mother_connect)
                                        video_connects = get_all_pci_versions(extract_pci_version(components["video_card"]["connect"]))
                                        #print(video_connects)
                                        input_string = components["motherboard"]["compatible_ram"]
                                        for word in ["DIMM", "SDRAM"]:
                                            input_string = input_string.replace(word, "")
                                        result_string = ', '.join(part.strip() for part in input_string.split(',') if part.strip())

                                        for i in range(len(result_string)):
                                            if result_string[i] != '-' and result_string[i] != ' ':
                                                ra += result_string[i]

                                        for i in range(len(body_factor)):
                                            if body_factor[i] != '-' and body_factor[i] != ' ':
                                                f += body_factor[i].lower()
                                        
                                        for i in range(len(power_factor)):
                                            if power_factor[i] != '-' and power_factor[i] != ' ' and power_factor[i].isalpha():
                                                c += power_factor[i].lower()
                                            #print(c,power_factor[i])

                                        charge_factor = c.split(',')
                                        for i in range(len(charge_factor)):
                                            charge_factor[i] = charge_factor[i].lower()

                                        form_factors = f.split(',')
                                        for i in range(len(form_factors)):
                                            form_factors[i] = form_factors[i].lower()

                                        RAMS = ra.split(',')
                                        for i in range(len(RAMS)):
                                            RAMS[i] = RAMS[i].lower()

                                        proc = components["processor"]["type"].lower()
                                        processor = proc.split(',')

                                        m_socket = components["motherboard"]["socket_type"].lower()
                                        m_socket = m_socket.replace('socket','')
                                        m_socket = m_socket.replace('(','')
                                        m_socket = m_socket.replace('e)','')
                                        m_socket = m_socket.replace(' ','')

                                        p_socket = components["processor"]["socket_type"].lower()
                                        p_socket = p_socket.replace('socket','')
                                        p_socket = p_socket.replace('()','')
                                        p_socket = p_socket.replace('e)','')
                                        p_socket = p_socket.replace(' ','')

                                        sock = ''
                                        sok = cooler_socket
                                        sok = sok.strip().lower()
                                        if 'socket' in sok:
                                            sok = sok.replace('socket ','')
                                        for i in range(len(sok)):
                                            if sok[i] != '-' and sok[i] != ' ':
                                                sock += sok[i]
                                        c_socket = sock.split(',')
                                        charge_power = ''
                                        ch_power = get_parameter_by_key(charges[ch], 'Мощность').lower()
                                        for i in range(len(ch_power)):
                                            if ch_power[i].isdigit():
                                                charge_power += ch_power[i]
                                        compatible = True
                                        if p_socket != m_socket: #motherboard and processor
                                            #print(f"{components['processor']['socket_type']} cant conect {components['motherboard']['socket_type']}.")
                                            compatible = False
                                            pb = 1
                                            map = 1

                                        if components["ram"]["type"][:4].lower() not in RAMS: #motherboard and ram
                                            #print(f'MAR {components["ram"]["type"][:4].lower()} cant conect {RAMS}')
                                            compatible = False
                                            rb = 1
                                            mar = 1

                                        if components["ram"]["type"][:4].lower() not in processor: #processor and ram
                                            #print(f'PAR {components["ram"]["type"][:4].lower()} cant conect {processor}')
                                            compatible = False
                                            if map == 0 and mar == 0:
                                                rb = 1

                                        if video_connects[0] == 0: # motherboard and videocard
                                            #print(f'{video_connects} didn`t exsist')
                                            compatible = False
                                            vb = 1

                                        if mother_connect[0] == 0:  # motherboard and videocard
                                            #print(f'{mother_connect} didn`t exsist')
                                            compatible = False
                                            mb = 1

                                        if float(components["body"]["max_video_card"][:3]) < float(components["video_card"]["length"][:3]): #videocard and body
                                            #print(f'{components["body"]["max_video_card"]} < {components["video_card"]["length"]}')
                                            compatible = False
                                            bb = 1

                                        if components["motherboard"]["form_factor"].lower() not in form_factors: # motherboard and body
                                            #print(f'{components["motherboard"]["form_factor"].lower()} not in {form_factors} ')
                                            compatible = False
                                            bb = 1
                                    
                                        if components["ssd"]["form_factor"][:3] != "3.5": #ssd
                                            if (components["ssd"]["form_factor"][:3] != "M.2"):
                                                #print(f'ssd not 3,5 and not M.2 {components["ssd"]["form_factor"][:3]}')
                                                compatible = False
                                                sb = 1
                                            else:
                                                try:
                                                    ssd_connect = get_parameter_by_key(motherboards[m], 'Количество разъемов M.2')
                                                    try:
                                                        if int(ssd_connect) > 0:
                                                            pass
                                                        else:
                                                            #print(f'not found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                                            compatible = False
                                                    except:
                                                        #print(f'Not found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                                        compatible = False
                                                except:
                                                    #print(f'NNot found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                                    compatible = False
                                        
                                        if int(processor_power) > int(cooler_power): #processor and cooler
                                            #print(f' proc_p > cool_p {processor_power} > {cooler_power}, {m},{p},{r},{v},{b},{s},{co},{ch}')
                                            compatible = False
                                            cob = 1
                                            break
                                        
                                        if p_socket not in c_socket:
                                            #print(f'p_socket not in c_socket {p_socket} <> {c_socket}')
                                            compatible = False
                                            cob = 1

                                        for i in range(len(charge_factor)):
                                            for j in range(len(form_factors)):
                                                if charge_factor[i] in form_factors[j]:
                                                    count = 1
                                                    break
                                        if count == 0:
                                            #print(f'charge_factor not in form_factors {charge_factor} {form_factors}') 
                                            compatible = False
                                            chb = 1

                                        try:
                                            if int(charge_power) < 500:
                                                #print(f'power {get_parameter_by_key(charges[ch], "Мощность")} < 500')
                                                compatible = False
                                                chb = 1
                                        except:
                                            #print(f'power {get_parameter_by_key(charges[ch], "Мощность")} < 500')
                                            compatible = False
                                            chb = 1

                                        if compatible:
                                            for key in components:
                                                print(f"- {components[key]['name']}")
                                            print()
                                            print(f'{m},{p},{r},{v},{b},{s},{co},{ch}')
                                            return [motherboards[m],processors[p],rams[r],videocards[v],bodys[b],ssds[s],coolers[co],charges[ch]]
if __name__ == "__main__":
    compatible()
    