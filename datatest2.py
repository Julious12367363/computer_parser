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

def get_parametrs(data, key):
    if 'components' in data:
        for component in data['components']:
            if key in component:
                return component[key]

            if 'fullSpecsGrouped' in component:
                for group in component['fullSpecsGrouped']['groups']:
                    for item in group['items']:
                        if item['name'] == key:
                            return item['value']
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

def extract_pci_versions(input_string):
    versions = []
    for part in input_string.split(','):
        part = part.strip()
        if "PCI Express" in part:
            match = re.search(r'PCI Express (\d+)\.', part)
            if match:
                version = int(match.group(1))
                versions = [f"pci{i}" for i in range(version, 1, -1)]  
                break
    return versions

def process_string(input_string):
        modified_string = re.sub(r'express', 'e', input_string, flags=re.IGNORECASE)
        modified_string = re.sub(r'x\d+', '', modified_string)
        modified_string = modified_string.replace('-', '')
        modified_string = modified_string.replace(' ', '').lower()
        result = ','.join(part for part in modified_string.split(',') if part)
        result = result.replace('2.0','2').replace('3.0','3').replace('4.0','4')
        result = result.replace('e','')
        p = result.split(',')
        return p

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

    for m in range(len(motherboards)):
        for p in range(len(processors)):
            for v in range(len(videocards)):
                for r in range(len(rams)):
                    for b in range(len(bodys)):
                        for s in range(len(ssds)):
                            components = {
                                "motherboard": {
                                    "name": motherboards[m]["component_name"],
                                    "connect": "PCI-E 2.0 x1, PCI-E 3.0 x16",
                                    "form_factor": get_parametrs(motherboards[m], 'Форм-фактор'),
                                    "chipset" : get_parametrs(motherboards[m], 'Чипсет'),
                                    "socket_type": get_parametrs(motherboards[m], 'Сокет'),
                                    "ram_slots": get_parametrs(motherboards[m], 'Количество слотов оперативной памяти'),
                                    "compatible_ram": get_parametrs(motherboards[m], 'Тип памяти')
                                },
                                "processor": {
                                    "name": processors[p]["component_name"],
                                    "socket_type": get_parametrs(processors[p], 'Сокет'),
                                    "type" : get_parametrs(processors[p], 'Тип памяти')
                                },
                                "ram": {
                                    "name": rams[r]["component_name"],
                                    "type": get_parametrs(rams[r], 'Тип памяти'),
                                },
                                "video_card": {
                                    "name": videocards[v]["component_name"],
                                    "connect": "PCI Express 4.0",
                                    "width": get_parametrs(videocards[v], 'Толщина'),
                                    "length": get_parametrs(videocards[v], 'Длина'),
                                    "hight": get_parametrs(videocards[v], 'Высота'),

                                },
                                "ssd": {
                                    "name": ssds[s]["component_name"],
                                    "form_factor":get_parametrs(ssds[s], 'Форм-фактор'),
                                },
                                "body": {
                                    "name": bodys[b]["component_name"],
                                    "form_factor":get_parametrs(bodys[b], 'Форм-фактор материнской платы'),
                                    "width": get_parametrs(bodys[b], 'Ширина'),
                                    "length": get_parametrs(bodys[b], 'Глубина'),
                                    "hight": get_parametrs(bodys[b], 'Высота'),
                                    "max_video_card": get_parametrs(bodys[b], 'Максимальная длина видеокарты'),
                                }
                            }

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
                            mother_connect = process_string(components["motherboard"]["connect"])
                            print("mother_connect = ",mother_connect)

                            video_connects= extract_pci_versions(components["video_card"]["connect"])
                            print("video_connects = ",video_connects)

                            words_to_remove = ["DIMM", "SDRAM"]
                            print(components["motherboard"])
                            for m1 in range(len(motherboards)):
                                print("motherboards[m1] = ",motherboards[m1])
                                print()
                            try:
                                input_string = components["motherboard"]["compatible_ram"]
                                for word in words_to_remove:
                                    input_string = input_string.replace(word, "")
                                result_string = ', '.join(part.strip() for part in input_string.split(',') if part.strip())

                                for i in range(len(result_string)):
                                    if result_string[i] != '-' and result_string[i] != ' ':
                                        r += result_string[i]

                                for i in range(len(components["body"]["form_factor"])):
                                    if components["body"]["form_factor"][i] != '-' and components["body"]["form_factor"][i] != ' ':
                                        f += components["body"]["form_factor"][i]

                                form_factors = f.split(',')
                                for i in range(len(form_factors)):
                                    form_factors[i] = form_factors[i].lower()

                                RAMS = r.split(',')
                                for i in range(len(RAMS)):
                                    RAMS[i] = RAMS[i].lower()

                                proc = components["processor"]["type"].lower()
                                processor = proc.split(',')

                                m_socket = components["motherboard"]["socket_type"].lower()
                                m_socket = m_socket.replace('socket','')

                                p_socket = components["processor"]["socket_type"].lower()
                                p_socket = p_socket.replace('socket','')

                                print("form factor sizes and body sizes = ",sizes[components["motherboard"]["form_factor"].lower()]["length"], components["body"]["length"][:3], sizes[components["motherboard"]["form_factor"].lower()]["width"], components["body"]["width"][:3])
                                print("ssd sizes l w h = ", components["ssd"]["length"][:3], components["ssd"]["width"][:3], components["ssd"]["hight"][:3] )
                                print("ssd = ", components["ssd"]["form_factor"][:3])
                                print("m_socket = ", m_socket)
                                print("p_socket = ", p_socket)
                                print("processor = ",processor)
                                print("form_factors= ", form_factors)
                                print("f= ",f.lower())
                                print("mother= ", components["motherboard"]["form_factor"].lower())
                                print("RAMS= ", RAMS)
                                print("r= ",r.lower())
                                print("ram= ", components["ram"]["type"][:4].lower())
                            except:
                                pass
                            
                            compatible = True

                            if p_socket != m_socket: #motherboard and processor
                                print(f"{components['processor']['socket_type']} cant conect {components['motherboard']['socket_type']}.")
                                compatible = False

                            if components["ram"]["type"][:4].lower() not in RAMS: #motherboard and ram
                                print(f'{components["ram"]["type"]} cant conect {RAMS}')
                                compatible = False

                            if components["ram"]["type"][:4].lower() not in processor: #processor and ram
                                print(f'{components["ram"]["type"]} cant conect {components["processor"]["type"].split(",")}')
                                compatible = False

                            if len(mother_connect) == 2: # motherboard and videocard
                                if mother_connect[0] not in video_connects and mother_connect[1] not in video_connects:
                                    print('2, mother_connect not in video_connects')
                                    compatible = False
                                    
                            if len(mother_connect) == 1: # motherboard and videocard
                                if mother_connect[0] not in video_connects:
                                    print('1, mother_connect not in video_connects')
                                    compatible = False 

                            if int(components["body"]["max_video_card"][:3]) < int(components["video_card"]["length"][:3]): #videocard and body
                                print(f'{components["body"]["max_video_card"] < components["video_card"]["length"]}')
                                compatible = False

                            if components["motherboard"]["form_factor"].lower() not in form_factors: # motherboard and body
                                print("not in form_factors")
                                compatible = False

                            # try: # motherboard and body
                            #     if int(sizes[components["motherboard"]["form_factor"].lower()]["length"]) > int(components["body"]["length"][:3]) or int(sizes[components["motherboard"]["form_factor"].lower()]["width"]) > int(components["body"]["width"][:3]):
                            #         print("form_factor sizes > body")
                            #         compatible = False
                            # except KeyError as e:
                            #     print(f"Ошибка! Ключ {e} не найден.")
                            #     compatible = False

                            if components["ssd"]["form_factor"][:3] != "3.5": #ssd
                                print('ssd not 3,5')
                                compatible = False

                            if compatible:
                                print("all good")
                                for key in components:
                                    print(f"- {components[key]['name']}")
                                print()
                                for i in range(100):
                                    print("+")
                                print()
                                return [motherboards[m],processors[p],videocards[v],rams[r],bodys[b],ssds[s]]

if __name__ == "__main__":
    compatible()
    