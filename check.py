from compatibilyty_algoritm import compatible
from compatibilyty_algoritm import get_parameter_by_key

def is_valid(comp):
    """
        Проверка, что у компонента есть все характеристики, которые нужны для проверки совместимости
    """
    flag = True
    if "component_type" in comp:
        if comp["component_type"] == 'materinskaia-plata':
            q = comp["component_name"]
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Слоты PCI-E подробно')
            if q == None:
                if get_parameter_by_key(comp, 'Версия PCI Express') == None: flag = False
            q = get_parameter_by_key(comp, 'Форм-фактор')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Сокет')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Тип памяти')
            if q == None: flag = False
        elif comp["component_type"] == 'protsessory-cpu':
            q = comp["component_name"]
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Сокет')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Тип памяти')
            if q == None: flag = False
            q = get_parameter_by_key(comp,'Тепловыделение')
            if q == None: flag = False
        elif comp["component_type"] == 'operativnaia-pamiat':
            q = comp['component_name']
            if q == None: flag = False
            if get_parameter_by_key(comp, 'Тип памяти') == None:
                if get_parameter_by_key(comp, 'Тип') == None:
                    flag = False
        elif comp["component_type"] == 'videokarty':
            q = comp['component_name']
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Тип подключения')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Длина')
            if q == None: flag = False
        elif comp["component_type"] == 'korpusa':
            q = comp['component_name']
            if q == None: flag = False 
            q = get_parameter_by_key(comp, 'Форм-фактор материнской платы')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Ширина')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Глубина')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Высота')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Максимальная длина видеокарты')
            if q == None: flag = False
        elif comp["component_type"] == 'vnutrennie-tverdotelnye-nakopiteli-ssd':
            q = comp['component_name']
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Форм-фактор')
            if q == None: flag = False
        elif comp["component_type"] == 'kulery-i-sistemy-okhlazhdeniia':
            q = comp['component_name']
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Сокет')
            if q == None: 
                if get_parameter_by_key(comp, 'Сокет процессора') == None: flag = False
            q = get_parameter_by_key(comp,'Максимальная рассеиваемая мощность (TDP), Вт')
            if q == None: flag = False
        elif comp["component_type"] == 'bloki-pitaniia':
            q = comp['component_name']
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Форм-фактор')
            if q == None: flag = False
            q = get_parameter_by_key(comp, 'Мощность')
            if q == None: flag = False
        else:
            flag = False
    else:
        flag = False
    return flag

def main():
    motherboards=[
        {'id': 4576, 'component_name': 'Материнская плата Afox AFOX motherboard intel H510, INTEL Socket 1200, Mini-ITX (17 x17cm)', 
        'component_type': 'materinskaia-plata', 'url': 'https://market.yandex.ru//product--mo1uHfBYB95u0G&uniqueId=12054742', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/1522540/2a00000192078e1d9a551e42d194d50a59e6/orig'], 
        'price': 5773, 'articul_yandex': '5489793254', 
        'fullSpecsGrouped': {'groups': [   
            {'name': 'Процессор', 
                'items': [
                    {'name': 'Бренд', 'value': 'AFOX'}, 
                    {'name': 'Сокет', 'value': 'LGA1200'}, 
                    {'name': 'Количество разъемов M.2', 'value': '1'},
                    {'name': 'Чипсет', 'value': 'Intel H510'}, 
                    {'name': 'Тип памяти', 'value': 'DDR4'},  
                    {'name': 'Форм-фактор', 'value': 'ATX'},
                    {'name': 'Слоты PCI-E подробно', 'value': 'PCI-Express 4.0'},
                    ]
                }, 
            ]
            }
        }
    ]

    processors = [
        {'id': 818, 'component_name': 'Центральный процессор AMD Ryzen 5 8400F, 6 ядер, 12 потоков, 4200МГц, AM5, OEM', 
        'component_type': 'protsessory-cpu', 'url': 'https://market.yandex.ru//n=12054742', 'image_url': ['https:///orig'], 'price': 12389, 'articul_yandex': '5570189255', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Общие характеристики', 
                'items': [
                        {'name': 'Сокет', 'value': 'LGA1200'}, 
                        {'name': 'Тип памяти', 'value': 'DDR4'}, 
                        {'name': 'Тепловыделение', 'value': '65 Вт'}, 
                    ]
                }, 
            ]
            }
        }
    ]
    videocards = [
        {'id': 778, 'component_name': 'Видеокарта Ninja RTX2060 SUPER NF206SG86F, GDDR6, 8ГБ, поддержка DLSS', 
        'component_type': 'videokarty', 
        'url': 'https://market.yandex.ru//product--vidQwMzQ4Nj&uniqueId=12054742', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/11549745/2a0000018d29ebc7d9b12f370f5803a54ee4/orig'], 
        'price': 33360, 'articul_yandex': '4927541040', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Графический процессор', 
                'items': [
                        {'name': 'Тип подключения', 'value': 'PCI-Express 4.0'},
                        {'name': 'Длина', 'value': '225 мм'}, 
                        {'name': 'Высота', 'value': '122 мм'}, 
                        {'name': 'Толщина', 'value': '40 мм'},
                        ]
                }, 
            ]
            }
        }
    ]

    rams = [
        {'id': 427, 'component_name': 'Оперативная память Kingston FURY Beast 16 ГБ (8 ГБ x 2 шт.) DDR4 2666 МГц DIMM CL16 KF426C16BBK2/16', 
        'component_type': 'operativnaia-pamiat', 
        'url': 'https://market.yandex.ru//product--operativnaia-pamiat-kingston-fuYp-VqMpcSjkrCoPcCQKZfaMhSWH7wXdVWVi54', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/1729672/2a00000191e68be229213ebd267e3361c9ab/orig'], 
        'price': 3975, 'articul_yandex': '5769277961', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Характеристики', 
                'items': [
                    {'name': 'Тип', 'value': 'DDR4'}, 
                    {'name': 'Дополнительная информация', 'value': 'tRCmin - 45.75ns; tRFCmin - 260ns; операционная температура от 0 до +85 градусов'}]}, 
                    {'name': 'Дополнительно', 'items': [{'name': 'Гарантийный срок', 'value': '1 г.'}
                                                        ]}]}}]
    bodys = [
            {'id': 806, 'component_name': 'Корпус Ginzzu A400, Midi Tower, без БП, 2xUSB 2.0, AU, черный', 
            'component_type': 'korpusa', 
            'url': 'https://market.yandex.ru//product--korpuLzEvMRAHgH3m7QY%2C&uniqueId=897497', 
            'image_url': ['https://avatars.mds.yandex.net/get-mpic/5272727/2a00000191b2cb265410a1ed6b796d1cf64f/orig'], 
            'price': 1898, 'articul_yandex': '5298570320', 
            'fullSpecsGrouped': {
                'groups': [
                    {'name': 'Форм-фактор и размеры', 
                    'items': [
                        {'name': 'Ширина', 'value': '170 мм'}, 
                        {'name': 'Высота', 'value': '405 мм'}, 
                        {'name': 'Глубина', 'value': '308 мм'},
                        {'name': 'Форм-фактор материнской платы', 'value': 'ATX, Micro-ATX, Mini-ITX'}, 
                        {'name': 'Максимальная длина видеокарты', 'value': '260 мм'}, 
                        {'name': 'Блок питания', 'value': 'отсутствует'},
                        ]
                    }, 
                ]
            }
        }
    ]
    ssds = [
        {'id': 1274, 'component_name': 'SSD KingSpec 1 ТБ 3,5 дюйма SATA3 Ноутбук Настольный жесткий диск со скоростью чтения до 560 МБ / с', 
        'component_type': 'vnutrennie-tverdotelnye-nakopiteli-ssd', 
        'url': 'https://market.yandex.ru//product--ssd-kingspec-1-tb-2-5-diuima-404040CVAx1KKvYzgyYTcxYjA1NmE2NWUzMmUwNjAwLzEvMRDnAYB95u0G&uniqueId=179734549', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/5243677/2a00000193a50d9628b2a09ab7788d7fd682/orig'], 
        'price': 5999, 'articul_yandex': '5899927626', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Основные характеристики', 
                'items': [
                    {'name': 'Форм-фактор', 'value': '3.5"'},
                    {'name': 'Назначение', 'value': 'для ноутбука и настольного компьютера, игровой'}, 
                    ]}, {'name': 'Подключение', 'items': [{'name': 'Интерфейсы', 'value': 'SATA 6Gb/s'}, {'name': 'Стандарт SSD', 'value': 'SATA'}, {'name': 'Макс. скорость интерфейса', 'value': '600 МБ/с'}]}, {'name': 'Параметры накопителя', 'items': [{'name': 'Скорость чтения', 'value': '560 МБ/с'}, {'name': 'Скорость записи', 'value': '520 МБ/с'}]}, {'name': 'Ударостойкость и ресурс работы', 'items': [{'name': 'Время наработки на отказ', 'value': '1000000 ч'}, {'name': 'Суммарное число записываемых байтов (TBW)', 'value': '480 ТБ'}]}, {'name': 'Функции', 'items': [{'name': 'Поддержка технологий', 'value': 'TRIM'}]}, {'name': 'Дополнительно', 'items': [{'name': 'Макс. рабочая температура', 'value': '70 °C'}, {'name': 'Потребляемая мощность', 'value': '1.6 Вт'}, {'name': 'Высота', 'value': '7 мм'}, {'name': 'Длина', 'value': '100 мм'}, {'name': 'Ширина', 'value': '70 мм'}, {'name': 'Вес', 'value': '30 г'}, {'name': 'Дополнительная информация', 'value': '1*ssd'}, {'name': 'Гарантийный срок', 'value': '1 г., актуальный срок гарантии указан в гарантийном талоне производителя, приложенному к товару, и может отличаться в большую или меньшую сторону на момент покупки.'}, {'name': 'Размеры, мм', 'value': ' 100*70*7'}, {'name': 'Тип', 'value': ' Внутренний SSD-диск'}, 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    {'name': 'Тип накопителя', 'value': ' SSD'}]}]}}]
    charges = [
        {'id': 5945, 'component_name': 'Блок питания Deepcool PF350 80+ 350W', 
        'component_type': 'bloki-pitaniia', 
        'url': 'https://market.yandex.ru//product--blok-pitaniia-deepcool-atx-350w-pf350-8013&show-uid=17401319566493352417816058&nid=26912850&from=search&cpa=1&do-waremd5=aLCeTEwkqiFRKo-tdEBVbw&cpc=UR6JCnO9pZfxriRB4BwUZ0zWJPkt_wtvKDz07JE2Xgl1cU_I9eFp5GNY_q8SvyiKC55mQ0UrZUbVPQbyJ4DQQr24BQDX5fTy5CpERW6z1rVh9XdYU763HKDLQmWYBechtDlyRWL4wkTGnvx_1pydllMXpWQAnML6kPrCsnKNXRbd_XjinfjklSJLeT--bPoaVUQXiP1XqWD6eeUjDJeqEfqyd8R2cLpZ_ihfVAbulIV6IKQIrA9Brtnmfy_94cF3gabt1iCvkqa6ubVhHMj81lCl9nddiJxLKBX3tVjYxB2cFETHhDBoaaT7BpYv5MZTDM78VcdJPX6kWDMfE1xpnAr166NKcbcIXCCPAB6Bf8RdMQRq3P7OYZddDXe92UB8MZrQ6f50d0U_f7ixVgNj01gsN9HHL8EreJwJQxe4nlRHdU0ZBFVmQ7DDaWkOh0Iu&cc=CjIxNzQwMTMxOTU2NDI0Lzc0YTVkY2M5MmRkZGY4NzZiYmZkMWYwYmE0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=119485579', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/12424084/2a000001940c9fe231265a534ea0f4b59a0c/orig'], 
        'price': 2999, 'articul_yandex': '5997751671', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Основные характеристики', 
                'items': [
                    {'name': 'Форм-фактор', 'value': 'ATX'},
                    {'name': 'Мощность', 'value': '600Вт'},   
                     ]
                    }, 
                ]
            }
        }
    ]

    coolers = [ {'id': 5945, 'component_name': 'Кулер', 
        'component_type': 'kulery-i-sistemy-okhlazhdeniia', 
        'url': 'https://market.yandex.ru//&uniqueId=119485579', 
        'image_url': ['https://avatars.mds.yandex.net/get-mpic/12424084/2a000001940c9fe231265a534ea0f4b59a0c/orig'], 
        'price': 2999, 'articul_yandex': '5997751671', 
        'fullSpecsGrouped': {
            'groups': [
                {'name': 'Основные характеристики', 
                'items': [
                    {'name': 'Сокет процессора', 'value': 'LGA1200'}, 
                    {'name': 'Максимальная рассеиваемая мощность (TDP), Вт', 'value': '350 Вт'}
                     ]
                    }, 
                ]
            }
        }
    ]


    comp_result = compatible(
                    motherboards=motherboards,
                    processors=processors,
                    videocards=videocards,
                    rams=rams,
                    bodys=bodys,
                    ssds=ssds,
                    coolers=coolers,
                    charges=charges
                    )
    # print(comp_result)
    # print('mother = ', is_valid(motherboards))
    # print('proc = ', is_valid(processors))
    # print('ram = ', is_valid(rams))
    # print('videocard =', is_valid(videocards,))

    # print('body = ', is_valid(bodys))
    # print('ssd = ', is_valid(ssds))
    # print('cooler = ', is_valid(coolers))
    # print('charge = ', is_valid(charges))
    
if __name__ == "__main__":
    main()