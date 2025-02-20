from flask import Flask, render_template, request, redirect, url_for, session, flash
import time
import json
import copy
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
from selenium.webdriver.common.proxy import Proxy, ProxyType

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
    new_string = new_string.replace('-',' ')
    # Используем регулярное выражение для поиска версии PCI
    match = re.search(r'PCI Express (\d+)\.(\d+)', new_string, re.IGNORECASE)
    if match:
        # Извлекаем основную версию и формируем нужный формат
        major_version = match.group(1)
        return [f'pci{major_version}']
    return []

def generate_pci_versions(input_array):
    # Если массив пустой, возвращаем пустой массив
    if not input_array:
        return []

    # Извлекаем номер версии из первого элемента
    version_string = input_array[0]
    match = re.match(r'pci(\d+)', version_string, re.IGNORECASE)
    
    if match:
        # Получаем максимальную версию
        max_version = int(match.group(1))
        # Генерируем список версий от 1 до max_version
        return [f'pci{num}' for num in range(max_version, 0, -1)]
    return []

def extract_pci_versions(pci_string):
    #pci_string = "PCI-E 4.0 x16"
    #pci_string = "5 x PCI-E 3.0 x16, PCI-E 4.0 x16"
    #pci_string = "PCI-E 3.0 x1, PCI-E 3.0 x16"
    #pci_string = "2 x PCI 3.0 x16, PCI-E 3.0 x1"
    pci_string = pci_string.replace('x','')
    if pci_string[0].isalpha() == False:
        pci_string = pci_string[1:len(pci_string)]
    #print(pci_string)
    pci_versions = [item.strip() for item in pci_string.split(',')]
    extracted_versions = []
    for version in pci_versions:
        if "PCI-E" in version or "PCI-e" in version:
            version_number = version.split(' ')[1].split('.')[0]
            extracted_versions.append(int(version_number))
    
    return extracted_versions

def get_all_pci_versions(existing_versions):
    if not existing_versions:
        return []
    max_version = max(existing_versions)
    all_versions = []

    for version in range(1, max_version + 1):
        if version in existing_versions:
            all_versions.append(f'pci{version}')
        elif version - 1 in existing_versions:
            all_versions.append(f'pci{version}')

    for version in range(max_version, 0, -1):
        if f'pci{version}' not in all_versions:
            all_versions.append(f'pci{version}')
    
    return all_versions

def compatible(total_price,
               options=1,
               motherboards=[],
               processors=[],
               videocards=[],
               rams=[],
               bodys=[],
               ssds=[],
                   ):
    f = ''
    r = ''
    if options == 1:
        m = 0,25 * total_price
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
    for m in range(len(motherboards)):
        #print("m = ", m,p,r,v,b,s)
        for p in range(len(processors)):
           # print("p = ", m,p,r,v,b,s)
            for r in range(len(rams)):
             #   print("r = ", m,p,r,v,b,s)
                for v in range(len(videocards)):
                 #   print("v = ", m,p,r,v,b,s)
                    for b in range(len(bodys)):
                      #  print("b = ", m,p,r,v,b,s)
                        for s in range(len(ssds)):
                           # print("s = ", m,p,r,v,b,s)
                            mb = 0
                            pb = 0
                            rb = 0
                            vb = 0
                            bb = 0
                            sb = 0
                            map = 0
                            mar = 0
                            f = ''
                            ra = ''
                            try:
                                q = motherboards[m]["component_name"]
                                if q == None: mb = 1
                                q = get_parameter_by_key(motherboards[m], 'Слоты PCI-E подробно')
                                if q == None: mb = 1
                                q = get_parameter_by_key(motherboards[m], 'Форм-фактор')
                                if q == None: mb = 1
                                q = get_parameter_by_key(motherboards[m], 'Чипсет')
                                if q == None: mb = 1
                                q = get_parameter_by_key(motherboards[m], 'Сокет')
                                if q == None: mb = 1
                                q = get_parameter_by_key(motherboards[m], 'Количество слотов оперативной памяти')
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
                                q = get_parameter_by_key(videocards[v], 'Толщина')
                                if q == None: vb = 1
                                q = get_parameter_by_key(videocards[v], 'Длина')
                                if q == None: vb = 1
                                q = get_parameter_by_key(videocards[v], 'Высота')
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
                            except:
                                sb = 1
                            if mb or pb or rb or vb or bb == 1:
                                break
                            if sb == 0:
                                components = {
                                    "motherboard": {
                                        "name": motherboards[m]["component_name"],
                                        "connect": get_parameter_by_key(motherboards[m], 'Слоты PCI-E подробно'),
                                        "form_factor": get_parameter_by_key(motherboards[m], 'Форм-фактор'),
                                        "chipset" : get_parameter_by_key(motherboards[m], 'Чипсет'),
                                        "socket_type": get_parameter_by_key(motherboards[m], 'Сокет'),
                                        "ram_slots": get_parameter_by_key(motherboards[m], 'Количество слотов оперативной памяти'),
                                        "compatible_ram": get_parameter_by_key(motherboards[m], 'Тип памяти')
                                    },
                                    "processor": {
                                        "name": processors[p]["component_name"],
                                        "socket_type": get_parameter_by_key(processors[p], 'Сокет'),
                                        "type" : get_parameter_by_key(processors[p], 'Тип памяти')
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
                                    }
                                }
                                #print("components['motherboard']['connect'] = ",components["motherboard"]["connect"])
                                #print("components['video_card']['connect'] = ",components["video_card"]["connect"])
                                pci_string = components["motherboard"]["connect"]
                                extracted_versions = extract_pci_versions(pci_string)
                                mother_connect = get_all_pci_versions(extracted_versions)
                                video_connects = generate_pci_versions(extract_pci_version(components["video_card"]["connect"]))
                                # print("mother_connect", mother_connect) 
                                # print("video_connects = ",video_connects)
                                print()
                                print("motherboards[m] = ",motherboards[m]["url"])
                                print()
                                print("processors[p] = ",processors[p]["url"])
                                print()
                                print("rams[r] = ",rams[r]['url'])
                                print()
                                print("videocards[v] = ",videocards[v]['url'])
                                print()
                                print("bodys[b] = ",bodys[b]['url'])
                                print()
                                print("ssds[s] = ",ssds[s]['url'])
                                print()
                                # for i in range(len(ssds)):
                                #     print()
                                #     print("i = ",i)
                                #     print("ssds[s] = ",ssds[i]["url"])
                                #     print()

                                input_string = components["motherboard"]["compatible_ram"]
                                for word in ["DIMM", "SDRAM"]:
                                    input_string = input_string.replace(word, "")
                                result_string = ', '.join(part.strip() for part in input_string.split(',') if part.strip())

                                for i in range(len(result_string)):
                                    if result_string[i] != '-' and result_string[i] != ' ':
                                        ra += result_string[i]

                                for i in range(len(components["body"]["form_factor"])):
                                    if components["body"]["form_factor"][i] != '-' and components["body"]["form_factor"][i] != ' ':
                                        f += components["body"]["form_factor"][i]

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

                                # print("form factor sizes and body sizes = ",sizes[components["motherboard"]["form_factor"].lower()]["length"], components["body"]["length"][:3], sizes[components["motherboard"]["form_factor"].lower()]["width"], components["body"]["width"][:3])
                                # print("ssd = ", components["ssd"]["name"])
                                # print("ssd = ", components["ssd"]["form_factor"][:3])
                                # print("ssd = ", components["ssd"]["form_factor"])
                                # print("m_socket = ", m_socket)
                                # print("p_socket = ", p_socket)
                                # print("processor = ",processor)
                                # print("form_factors= ", form_factors)
                                # print("f= ",f.lower())
                                # print("mother= ", components["motherboard"]["form_factor"].lower())
                                # print("RAMS= ", RAMS)
                                # print("ra= ",ra.lower())
                                # print('Тип памяти/Тип = ',w)
                                # print("ram= ", components["ram"]["type"][:4].lower())
                                
                                compatible = True

                                if p_socket != m_socket: #motherboard and processor
                                    print(f"{components['processor']['socket_type']} cant conect {components['motherboard']['socket_type']}.")
                                    compatible = False
                                    pb = 1
                                    map = 1

                                if components["ram"]["type"][:4].lower() not in RAMS: #motherboard and ram
                                    print(f'MAR {components["ram"]["type"][:4].lower()} cant conect {RAMS}')
                                    compatible = False
                                    rb = 1
                                    mar = 1

                                if components["ram"]["type"][:4].lower() not in processor: #processor and ram
                                    print(f'PAR {components["ram"]["type"][:4].lower()} cant conect {processor}')
                                    compatible = False
                                    if map == 0 and mar == 0:
                                        rb = 1

                                if len(mother_connect) == 2: # motherboard and videocard
                                    if mother_connect[0] not in video_connects and mother_connect[1] not in video_connects:
                                        print(f'2, {mother_connect} not in {video_connects}')
                                        compatible = False
                                        vb = 1
                                        
                                if len(mother_connect) == 1: # motherboard and videocard
                                    if mother_connect[0] not in video_connects:
                                        print(f'1, {mother_connect} not in {video_connects}')
                                        compatible = False
                                        vb = 1 

                                if float(components["body"]["max_video_card"][:3]) < float(components["video_card"]["length"][:3]): #videocard and body
                                    print(f'{components["body"]["max_video_card"] < components["video_card"]["length"]}')
                                    compatible = False
                                    bb = 1

                                if components["motherboard"]["form_factor"].lower() not in form_factors: # motherboard and body
                                    print(f'{components["motherboard"]["form_factor"].lower()} not in {form_factors} ')
                                    compatible = False
                                    bb = 1
                            
                                if components["ssd"]["form_factor"][:3] != "3.5": #ssd
                                    if (components["ssd"]["form_factor"][:3] != "M.2"):
                                        print(f'ssd not 3,5 and not M.2 {components["ssd"]["form_factor"][:3]}')
                                        compatible = False
                                    else:
                                        try:
                                            ssd_connect = get_parameter_by_key(motherboards[m], 'Количество разъемов M.2')
                                            try:
                                                if int(ssd_connect) > 0:
                                                    pass
                                                else:
                                                    print(f'not found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                                    compatible = False
                                            except:
                                                print(f'Not found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                                compatible = False
                                        except:
                                            print(f'NNot found get_parameter_by_key(motherboards[m], "Количество разъемов M.2")')
                                            compatible = False

                                if compatible:
                                    print("all good")
                                    for key in components:
                                        print(f"- {components[key]['name']}")
                                    print()
                                    return [motherboards[m],processors[p],rams[r],videocards[v],bodys[b],ssds[s]]
                        if  mb or pb or rb or vb == 1:
                            break
                    if  mb or pb or rb == 1:
                        break
                if  mb or pb == 1:
                    break
            if  mb == 1:
                break
if __name__ == "__main__":
    compatible()
    