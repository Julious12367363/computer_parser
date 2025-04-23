import os
import time
import json
from datetime import datetime
from flask import Flask
from flask import render_template, request, jsonify, flash, Response
from models import db, Links, Characteristics
from config import config_by_name
from job_get_links import parse_first_links
from parser_page import parse_card_component
from flask_migrate import Migrate
from sqlalchemy import and_, or_
from supabase_service import SupabaseService
from flask_supabase import Supabase
from compatibilyty_algoritm import compatible


def find_prices(data):
    prices = []
    
    if isinstance(data, dict):
        # Если data - словарь, проверяем наличие ключа 'price'
        if 'price' in data:
            prices.append(data['price'])
        
        # Рекурсивно проверяем все значения в словаре
        for value in data.values():
            prices.extend(find_prices(value))
    
    elif isinstance(data, list):
        # Если data - список, проверяем каждый элемент
        for item in data:
            prices.extend(find_prices(item))
    
    return prices

def sort_components_by_price(components):
    """
    Сортирует массив компонентов по цене в порядке убывания.
    """
    sorted_components = sorted(components, key=lambda x: x['price'], reverse=True)
    return sorted_components

def get_build_ranges(build_type):
    builds = {
        "игровой": {
            'videocard': [0, 0.45],
            'processor': [0, 0.2],
            'ram': [0, 0.07],
            'motherboard': [0, 0.1],
            'ssd': [0, 0.09],
            'body': [0, 0.03],
            'cooler': [0, 0.02],
            'charge': [0, 0.04]
        },
        "графический": {
            'videocard': [0, 0.48],
            'processor': [0, 0.16],
            'ram': [0, 0.12],
            'motherboard': [0, 0.1],
            'ssd': [0, 0.04],
            'body': [0, 0.04],
            'cooler': [0, 0.02],
            'charge': [0, 0.04]
        },
        "офисный": {
            'processor': [0, 0.26],
            'ram': [0, 0.1],
            'motherboard': [0, 0.19],
            'ssd': [0, 0.21],
            'body': [0, 0.09],
            'cooler': [0, 0.02],
            'charge': [0, 0.05],
            'videocard': [0, 0.08]
        },
        "для работы с мультимедиа": {
            'processor': [0, 0.18],
            'ram': [0, 0.1],
            'ssd': [0, 0.20],
            'videocard': [0, 0.25],
            'motherboard': [0, 0.12],
            'body': [0, 0.07],
            'cooler': [0, 0.02],
            'charge': [0, 0.06]
        },
        "для программирования": {
            'processor': [0, 0.30],
            'ram': [0, 0.19],
            'ssd': [0, 0.25],
            'motherboard': [0, 0.1],
            'body': [0, 0.06],
            'cooler': [0, 0.02],
            'charge': [0, 0.03],
            'videocard': [0, 0.08]
        },
        "для хост сервера": {
            'processor': [0, 0.28],
            'ram': [0, 0.22],
            'motherboard': [0, 0.15],
            'ssd': [0, 0.145],
            'body': [0, 0.05],
            'cooler': [0, 0.02],
            'charge': [0, 0.045],
            'videocard': [0, 0.06]
        },
        "бюджетная": {          #34000 (29563) - min, max - 250000 (179226)
            'processor': [0, 0.20],
            'ram': [0.03, 0.13],
            'motherboard': [0, 0.20],
            'ssd': [0, 0.18],
            'body': [0, 0.10],
            'cooler': [0, 0.025],
            'charge': [0, 0.08],
            'videocard': [0, 0.09]
        }
    }

    return builds.get(build_type.lower(), "Неизвестный тип сборки")

def create_app(config_name='dev'):
    app = Flask(__name__)
    # migrate = Migrate(app, db)

    # Загрузка конфигурации
    app.config.from_object(config_by_name[config_name])

    supabase = SupabaseService()

    # # Инициализация базы данных
    # db.init_app(app)

    def extract_prices(comp_result):
        prices = 0
        if comp_result:
            for component in comp_result:
                price = component.get('price')
                if price is not None:  # Проверка на наличие цены
                    prices += price
            return prices

    @app.route('/links/<int:link_id>/update_links', methods=['GET'])
    def update_link(link_id):
        """
        Route для парсинга ссылки по id
        """
        try:
            count = 0
            # Находим ссылку по id
            unparsed_links = Links.query.filter(
                Links.id == int(link_id)
            ).all()
            parsed_results = []

            # Перебираем ссылки
            for link_obj in unparsed_links:
                try:
                    # Парсим карточку компонента
                    parsed_data = parse_card_component(link_obj.link)

                    if parsed_data and 'component_name' in parsed_data and parsed_data['component_name']:
                        # Обновляем объект ссылки
                        link_obj.is_parsed = True
                        link_obj.title = parsed_data['component_name']
                        link_obj.component = parsed_data['component_type']
                        link_obj.image_url = parsed_data['image_url'][0] if parsed_data['image_url'] else None
                        link_obj.price = int(parsed_data['price'])
                        link_obj.articul_yandex = parsed_data['articul_yandex']
                        link_obj.is_actual = True
                        link_obj.date_parse = datetime.utcnow()  # datetime.now(datetime.timezone.utc)

                        # Сохраняем характеристики с проверкой на уникальность
                        for group in parsed_data['fullSpecsGrouped']['groups']:
                            for item in group['items']:
                                # Проверяем, существует ли уже такая характеристика
                                existing_characteristic = Characteristics.query.filter_by(
                                    link_id=link_obj.id,
                                    group=group['name'],
                                    name=item['name']
                                ).first()

                                if not existing_characteristic:  # Если характеристики нет, сохраняем новую
                                    characteristic = Characteristics(
                                        link_id=link_obj.id,
                                        group=group['name'],
                                        name=item['name'],
                                        value=item['value']
                                    )
                                    db.session.add(characteristic)

                        # parsed_results.append(link_obj)

                        # Добавляем результат
                        parsed_results.append({
                            'link': link_obj.link,
                            'status': 'Parsed successfully'
                        })
                        count += 1
                        print('Parsed successfully one page', count)
                    else:
                        if 'error' in parsed_data:
                            link_obj.is_actual = False
                        parsed_results.append({
                            'link': link_obj.link,
                            'status': 'Parsing failed'
                        })
                        count += 1
                        print('Parsing one page failed', count)

                except Exception as link_parse_error:
                    print(f"Ошибка при парсинге ссылки {link_obj.link}: {link_parse_error}")
                    parsed_results.append({
                        'link': link_obj.link,
                        'status': 'Error during parsing',
                        'error': str(link_parse_error)
                    })

                # Коммитим изменения
                db.session.commit()
        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            db.session.rollback()
            return jsonify({
                'error': str(e),
                'status': 'Parsing failed'
            }), 500
        # print("len(parsed_results=", len(parsed_results))
        # print("parsed_results=", parsed_results)
        # print("link_id=", link_id)
        return jsonify({
            'total_parsed': len(parsed_results),
            'results': parsed_results,
            'id': link_id
        }), 200

    # @app.route('/parse_unparsed_links', methods=['GET'])
    # def parse_unparsed_links():
    #     """
    #     Route для парсинга неспарсенных ссылок по 10 шт
    #     """
    #     try:
    #         count = 0
    #         # Находим все неспарсенные ссылки
    #         unparsed_links = Links.query.filter(
    #             # Links.title.like("%Корпус%"),
    #             Links.is_parsed == False,
    #             Links.is_actual == True
    #         ).limit(100).all()

    #         # Список для результатов
    #         parsed_results = []

    #         # Перебираем неспарсенные ссылки
    #         for link_obj in unparsed_links:
    #             try:
    #                 # Парсим карточку компонента
    #                 parsed_data = parse_card_component(link_obj.link)
    #                 if parsed_data and parsed_data['component_name'] and parsed_data['component_name'] != "" and parsed_data['price']:
    #                     # Обновляем объект ссылки
    #                     link_obj.is_parsed = True
    #                     link_obj.title = parsed_data['component_name']
    #                     link_obj.component = parsed_data['component_type']
    #                     link_obj.image_url = parsed_data['image_url'][0] if parsed_data['image_url'] else None
    #                     link_obj.price = int(parsed_data['price'])
    #                     link_obj.articul_yandex = parsed_data['articul_yandex']
    #                     link_obj.is_actual = True
    #                     link_obj.date_parse = datetime.utcnow()

    #                     # Сохраняем характеристики с проверкой на уникальность
    #                     for group in parsed_data['fullSpecsGrouped']['groups']:
    #                         for item in group['items']:
    #                             # Проверяем, существует ли уже такая характеристика
    #                             existing_characteristic = Characteristics.query.filter_by(
    #                                 link_id=link_obj.id,
    #                                 group=group['name'],
    #                                 name=item['name']
    #                             ).first()

    #                             if not existing_characteristic:  # Если характеристики нет, сохраняем новую
    #                                 characteristic = Characteristics(
    #                                     link_id=link_obj.id,
    #                                     group=group['name'],
    #                                     name=item['name'],
    #                                     value=item['value']
    #                                 )
    #                                 db.session.add(characteristic)

    #                     # Добавляем результат
    #                     parsed_results.append({
    #                         'link': link_obj.link,
    #                         'status': 'Parsed successfully'
    #                     })
    #                     count += 1
    #                     print('Parsed successfully one page', count)
    #                 else:
    #                     if 'error' in parsed_data:
    #                         link_obj.is_actual = False
    #                     parsed_results.append({
    #                         'link': link_obj.link,
    #                         'status': 'Parsing failed'
    #                     })
    #                     count += 1
    #                     print('Parsing one page failed', count)

    #             except Exception as link_parse_error:
    #                 print(f"Ошибка при парсинге ссылки {link_obj.link}: {link_parse_error}")
    #                 parsed_results.append({
    #                     'link': link_obj.link,
    #                     'status': 'Error during parsing',
    #                     'error': str(link_parse_error)
    #                 })

    #             # Коммитим изменения
    #             db.session.commit()
    #     except Exception as e:
    #         # Откатываем транзакцию в случае ошибки
    #         db.session.rollback()
    #         return jsonify({
    #             'error': str(e),
    #             'status': 'Parsing failed'
    #         }), 500
    #     return jsonify({
    #         'total_parsed': len(parsed_results),
    #         'results': parsed_results
    #     }), 200

    @app.route('/characteristics', methods=['GET'])
    def render_characteristics():
        try:
            # Параметры запроса
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            component_type = request.args.get('component_type')
            group = request.args.get('group')
            query = request.args.get('query')

            # Базовый запрос
            link_query = Links.query

            # Применяем фильтры
            if component_type:
                link_query = link_query.filter_by(component=component_type)

            # Пагинация ссылок
            paginated_links = link_query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            # Подготовка характеристик
            characteristics = []
            for link in paginated_links.items:
                # Получаем характеристики для каждой ссылки
                link_characteristics = Characteristics.query.filter_by(link_id=link.id)

                # Фильтрация по группе
                if group:
                    link_characteristics = link_characteristics.filter_by(group=group)

                # Фильтрация по запросу
                if query:
                    link_characteristics = link_characteristics.filter(
                        or_(
                            Characteristics.name.ilike(f'%{query}%'),
                            Characteristics.value.ilike(f'%{query}%')
                        )
                    )

                # Группировка характеристик
                grouped_characteristics = {}
                for char in link_characteristics:
                    if char.group not in grouped_characteristics:
                        grouped_characteristics[char.group] = []
                    grouped_characteristics[char.group].append({
                        'name': char.name,
                        'value': char.value
                    })

                characteristics.append({
                    'name': link.title,
                    'component_type': link.component,
                    'url': link.link,
                    'grouped_characteristics': grouped_characteristics
                })

            # Получаем уникальные типы компонентов и группы характеристик
            component_types = db.session.query(Links.component).distinct().all()
            component_types = [type[0] for type in component_types]

            characteristic_groups = db.session.query(Characteristics.group).distinct().all()
            characteristic_groups = [group[0] for group in characteristic_groups]

            return render_template(
                'characteristics.html',
                characteristics=characteristics,
                component_types=component_types,
                characteristic_groups=characteristic_groups,
                current_page=page,
                total_pages=paginated_links.pages
            )
        except Exception as e:
            flash(f'Ошибка загрузки характеристик: {str(e)}', 'error')
            return render_template('error.html'), 500

    # Дополнительный route для получения статистики
    @app.route('/parsing_stats', methods=['GET'])
    def parsing_stats():
        """
        Route для получения статистики парсинга
        """
        statistic = supabase.get_statistic()
        return jsonify(statistic), 200

    # @app.route('/parse_links')
    # def parse_links():
    #     """
    #     Парсит все ссылки со страницы с каталогом компонентов
    #     """
    #     try:
    #         parts = parse_first_links()
    #         # parts = {'materinskaia-plata': [{'title': 'Материнская плата Gigabyte X870E AORUS ELITE WIFI7, AM5, AMD X870E, ATX, RTL (X870E AORUS ELITE WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/896261145?hid=90401&sku=103674681358&show-uid=17397231487408394058616001&from-show-uid=17397231487408394058616001&cpa=1&do-waremd5=pPVcukcbSnqTz20f3ba1Rw&cpc=CXSMTylTSEjkPmiAn75abHzJjx5bsWB1_zwb_AnBzPekS9W8h3H2NDDSkDydcyD5QgYAJXSDJgzJqjAKYIJSIoCktXjA5VPnByrAY9pWPXtBTfFktWxEvavYscagpZ60YLg6ZgONMAAYMa4IzRkEgUv7Tkjvf6FTRbw7oy4bYnJuI5ApSEAk60OKkcjTAvlMqVVFDprSiLXo1Po3-n7d-BEV_aLlIqbukim_ycInpKA%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte X870E AORUS PRO, AM5, AMD X870E, ATX, RTL (X870E AORUS PRO)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-pro-rtl/865839269?hid=90401&sku=103642422487&show-uid=17397231487408394058616002&from-show-uid=17397231487408394058616002&cpa=1&do-waremd5=ZfceagZG-XUxgsFDiUwZPg&cpc=CXSMTylTSEiFuPxIOnwlYDZ1HTJEBJmJ3aE7LYYvsjFKUdbR68OAPzb4RlVNJtq4Ag51rUaTrTAm99DZSswhVarWJuGsGfikbsyUFx0p67nDf21JcwahNH5_YRhgigIrvjsuC2QIC1LACfZqSiuQZV9sCYIBDjWX4BHylCMKBTHuVdbXeFI-9YLAUd41cVMruQb0obiM00ePlf4agXqZsXBCbXPBBQUVwaWNLmOgsIs%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE WIFI7, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-wifi7-rtl/860729485?hid=90401&sku=103638107353&show-uid=17397231487408394058616003&from-show-uid=17397231487408394058616003&cpa=1&do-waremd5=1waB_dchmRaJvVgagFUOlw&cpc=CXSMTylTSEiTJdFT11lkQyrY47jLk2TYUwPHmM0Zq-frNGRH1syqX0Wyk8k5cxK2vxemjwZHjML9jLKbfbT3nfHEVUJyEM6NbyQH_T7sUAjAVSXY6cBB2mSkCG8u97eT7a_W0H1__zG-aCEXNnXX6nVd1odaEFEYdERtI_UXR1ZzR0djIYAeG5_SCzgc9ygMVcoKr_5mYOjmPCyCkzT8gbyUc0to9rQ5of-MocOKnZI%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE WIFI7 ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE WIFI7 ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-wf7-ice-rtl/860725692?hid=90401&sku=103638103565&show-uid=17397231487408394058616004&from-show-uid=17397231487408394058616004&cpa=1&do-waremd5=UX7xf_wtvA8V6Vz5nJib8A&cpc=CXSMTylTSEihVz2AncGsru2aJgdQ26hhRtKz0jGb-8G52RRjCE0i8CpQuCS1LLal8UXXvKBKc75YYO8FUquUIEQJ7xPRTC0Rpdg4oONWs-S3ttvQ7aSvgK1rH_CVOVJHaUGQC33q6VveFtRpqp-kLrO1kA62XeQ-9hv99c-vnNK8eu1iuwykOZ34VTNlHkJ2WweOu82GhBrSTR3piF4w4LzLn3ixHMSBLuMJWNDoHDk%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE X ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE X ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-x-ice-rtl/860739555?hid=90401&sku=103638117406&show-uid=17397231487408394058616005&from-show-uid=17397231487408394058616005&cpa=1&do-waremd5=DDiRMJPnbiuCv7Pn0oGhsw&cpc=CXSMTylTSEhUGnCL4Emv4gP1Bd8LnQPE5v-V4Rz1AoUZh_I3wNU76BFqzk9TyShS4eqw8sHrp3b1WPuzx8LQ3dmtCvJSSKyv01Syeze5LLTl96bZMdwhYe-3fphScnYAlXhyOM7VghHKP_1A6LiMyvSfJmM1f5si5jD7iT3Mi2pwpFo5iz7lM9HSENimV8bCdpBfpWDws_rL65Vp-ZA_K5ZOGwkPq_jk0VsU1JgKTqc%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890I AORUS ULTRA, LGA1851, Intel Z890, Mini-ITX, RTL (Z890I AORUS ULTRA)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890i-aorus-ultra-rtl/841947043?hid=90401&sku=103618765338&show-uid=17397231487408394058616006&from-show-uid=17397231487408394058616006&cpa=1&do-waremd5=kS5YN4VZFGVDNiLjwJhPig&cpc=CXSMTylTSEgNcQNkkuTkA3z6tMv5RL-6U1Fqf95pe9orXbmVX9sVfHV2wwh-XcrCEjJIl4bBvuUdg4q3Y0DXKzurZm6ZqlCoYJo_5di1yY_iTS35q3eUQS9gYSc6BztyMTDhfbiOMIDIwlG6AwWBhWSCVj4puGcLbJAxLZKyHwSqrrTdP6TF1NjQs8mnWBmA8QtehvIdyEoltMyT7srzdfkF5G1_AyekRYT1_scpYM0%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 AORUS PRO ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS PRO ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-pro-ice-rtl/841060181?hid=90401&sku=103617752018&show-uid=17397231487408394058616007&from-show-uid=17397231487408394058616007&cpa=1&do-waremd5=2QDAK5a0K_l4awzS1sIPcA&cpc=CXSMTylTSEicqSVYFaloLTsLrbe1_VlPu5iCguUf6yH9FaiSRQA4KB5vF6wJHYeVm2IZzlApkqleRies22rOJqkyOiPHqN0reqnJe61sNFgr32RMkN9l4DlB17gJSOnam2g9DfC8T1krhxarDzJSR_jnBIz6rfFXIBuNBAaokXI88e0X65Ssmvlo5JzQ9fCZA_qRVHvbEwUiL4KCLaFXBc40YUSu3aMJMlj6dnkdnlE%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 UD WIFI6E, LGA1851, Intel Z890, ATX, RTL (Z890 UD WIFI6E)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-ud-wifi6e-rtl/831162034?hid=90401&sku=103605455831&show-uid=17397231487408394058616008&from-show-uid=17397231487408394058616008&cpa=1&do-waremd5=o8onj8YRR1vtXDBikWTGGQ&cpc=CXSMTylTSEiZNdu8KBXsf2wIq2d_GpbkJE4earjmHOJiNPKda05n1uGlxmN7t5vhkBdGUgVE5ndJaf4QwI3DRBmuyXFAavwQtchDyVPa912TekY4n4vi9DKVAwZGy-pjNRcFi4Zsa7LHPpu0MPhve5XnDKm_sUHs0RNL70E5E45FiIcHHSRoltpBV4swZC7ENt6UY7RqaMwl9dOoWPNnoWNsp9yA9BA3E_0PW9uHlRU%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 GAMING X WIFI7, LGA1851, Intel Z890, ATX, RTL (Z890 GAMING X WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-gaming-x-wifi7/860742497?hid=90401&sku=103638119347&show-uid=17397231487408394058616009&from-show-uid=17397231487408394058616009&cpa=1&do-waremd5=qbc7x-R_RGTMccDgOiGacw&cpc=CXSMTylTSEjPTEzD39QNFkr24_hBhcfhQ12lB8x_OKm6KjosLa7LmCTJpd6dGpJHJ9xfmd10Sxn9LwgDBIFCevwEtQEZpFdhHcKjE9GeVsu8pZSOA9lF-VsOMHa4iXQEPno7QOs9VnuEoYainjX6WlggUHLh75iZmHPt1A2MJsbyN6kVRi4liuJLL2Rmc9t_ynqxDYDDBbXGkeFqe6zDfZn-We1Hp-FBVBzb4wcWsHU%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890M GAMING X, LGA1851, Intel Z890, Micro-ATX, RTL (Z890M GAMING X)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890m-gaming-x-rtl/829959465?hid=90401&sku=103604154371&show-uid=17397231487408394058616010&from-show-uid=17397231487408394058616010&cpa=1&do-waremd5=Vs6oMkGw7OP4sm2fcZzxkg&cpc=CXSMTylTSEidSnohFzC6enQc8FOYKZvPbb9BGcKVo87DlRwDGxZphcoiZMrgp4obHVjTljiDnkieqMa2z4iP7n8cz7Pi6syBf8AZ-LjBm91FDqRi277bOPRMlEooQqlUkIybEvE1AaAW2e0_fx8I1CsBKLhftUL_ErnLNyoM-cpGDKzYG7cBBxJCHFpiYCb8kldl8cMIdzfB8Vn6oUiHTUvrs2ml9VxsRXTiGEvfoqI%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890M AORUS ELITE WIFI7 ICE, LGA1851, Intel Z890, Micro-ATX, RTL (Z890M AORUS ELITE WIFI7 ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890m-aorus-elite-wf7-ice-rtl/836196877?hid=90401&sku=103611771458&show-uid=17397231487408394058616011&from-show-uid=17397231487408394058616011&cpa=1&do-waremd5=pMwIAUE2r7Q9K9wb0PSbwg&cpc=CXSMTylTSEiBPbRvp5-ijdPj_11bA-cCvCRRTYllNXU1Zg4J7xzoTt5L1UNlsxvLBDpEV434xgyAluFbzbn9eruH5y08ybnbFkPESJSit6voPTvuqQlFNTiZsn1AuFH0f9ANdfLLvPWh561LV_96c3QjoviIsalIZPufwjEZsioSzeeav5dBSHeDHebstQjkogLVgJtbyKrjfRUdq6h7gks4jrPVbEe6yHFJveN-j_Q%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte H610M H V2 DDR4, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-h610m-h-v2-ddr4-rtl/826066619?hid=90401&sku=103599862406&show-uid=17397231487800507513016001&nid=26912770&from=search&cpa=1&do-waremd5=m2BigUyKAu9HbRTzPgMPJg&sponsored=1&cpc=CXSMTylTSEh7UNODMUfoK3_2MXa9alixnveLXuYbdxHUFf5Xqz83EaTtiXT0g0PIn5gnMMBvY6lqQ38HeevCgQYafTLL60hqfaUFJ_kn2tycd-KLNTWAFAydwy1ALX-QpGkEws0dRTInWET0w7-vMhV88wBk_TUcRIk1zPP4kZ6YlXSmOrkX2i5l8ZCCKDXP4TMhdOIDt4bhU_FYSmqC2uBh7RlP5UuWXNWbgNYH96i8J5kCp9IosJJXjLhdPFhMhzBYKnKdquy9ZN61aOTHrLjlnK5sj-sUCeK_0o6z7HAYnlU_lf0opHqWLg2Ue0T8_aiK0T8b4jw4TtFaZKXZgNk788KWkENleZZRjDWJOr1ArDug9I5nsDz9oQlaspKOLZZBuQ2-U-0ZOdNmDL9LaV5NPW_2CJpT2VEa8kGF7J9WXrxOEHLEFYvR1dgDiSrCRCfprjbxoxMQ7lvGADJWRwNT7yb-edmJbz2BEfambmjbGxwEkHB8qtPsWpJyX36C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата Gigabyte A520M K V2', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-a520m-k-v2/1820745178?hid=90401&sku=101951780938&show-uid=17397231487800507513016002&nid=26912770&from=search&cpa=1&do-waremd5=8zYiTD_nFlvXtiKiT8YFaw&cpc=CXSMTylTSEh8NX8scEz7ZDG8JIDe4hyMe6byg_zyYQNbcV-_WH-rDHMaELKmgroHYU9VQJGG5rnBIRrldG16HlqET-rZQD_fDR1A29mqHfol5GVP-k0In7MiVqfY6pJvIdorzqBx4760rAOBtcf12wmrOQs_IKO8dUKc6TJ9C_Y5-XvdYnfRFqxGZo80H8fRVj8iOCB1yKRxfZZlGHhFQvM1NBs8ZoAVDovHfwzVYZTAdcBpr3IS1K3h7YMI95Idbj1NL4YfUj0iXZmHlb5QKnbaidTxk6p8dahqa4jljw0-VVKgViJUERTT4u8sqMS_TtAARD_UwzZ0HMTXs1WdTxo5KqPBFITF3rsrhSrQ2iGkvg5DX5sniGgngPu_FTMhTYjwYipMGrb44qbrGOVLUXzSN6r_tk30gaC8RCUnkFkbnOI196GXmGIfYfr9wI6Jz7EO23tb0onOxA-YkYpIvw%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Msi MPG B550 GAMING PLUS (AM4, ATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mpg-b550-gaming-plus-am4-atx/1779555126?hid=90401&sku=733855138&show-uid=17397231487800507513016003&nid=26912770&from=search&cpa=1&do-waremd5=9wndwHYlm4r1Hd3WMOfaAw&sponsored=1&cpc=CXSMTylTSEgP34BjhXAetRxVqJkw5Mf9_VC3dFOAmQZWQKmI3ZaaUKWumuRS-4xQCQCFyexokuZQKb-ZvNNVVRqLrmEVvFvsnUaCwWD-RRzOnjhSSnyVNgPf6VjhpbZu-jz21GHJcSB3lr3krJKkTry2nQTGXXCKI0KzxHK99u0DTvmfW26AZ50NnssshUBZpwybvAQ9Opwli4A3dqn1yr3fa1GY7HLqAGv2r2hheKYQ7fgdVANqxX0TcHeeUiZ7WWBl3qUSeYFIvksFrH7R2F-fJS8uA_3ia75LHlDE5gGZcJ3Jsi_qWQ8ZbkU_FktgQsWapTBZ80qOvv5Ulu53PMNWRpBWe1YEpi_rddvGgdSESauniCeIINPl7BOr8RB27Fe_Cyq9WVCNwOBoxczUt4WsYayRjfezSdJIiBcOR6uOtfQZMfvSZcp0hLPWsmvECOUHerNZMdFVDUuGcgR2feUfmxCMKpaqKbNeldcpRG8pIBL2Yyn2V3eDisFzcWfEZ90BUVCjhAwdUwPyq2Nb4KX-_J4nscifn3JSIF3sD89PwM4TNfugEpDYhB7xQBvIP29_w8qpg7rZZxB1uhPtXA1mGOjUBFPUNOl_9dRKBXJfLerIXZtQRRdA2gjsNw2R&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата Supermicro MBD-X13SEM-F-B', 'link': 'https://market.yandex.ru//product--supermicro-materinskaia-plata-supermicro-mbd-x13sem-f-b-mbd-x13sem-f/683317602?hid=90401&sku=103534581332&show-uid=17397231488049511310316001&from-show-uid=17397231488049511310316001&cpa=1&do-waremd5=ZXwWsAvrE5t2r7C5dV6UoQ&cpc=CXSMTylTSEgTsGWgiwKBKFy5m3eMbkgA0LIwsyf4Tx96GzZFXA-uVCLgIur8CRHBA02VfqIZuWRdpub5nw3uDrTKgtmrZ1DcUXMktelrupiDxwDLdsX9Vq-ng6s6dErpjSxAbdukAXPY0M5rOey1jKp3GImhbIGQDQUFuewPlOYMM-IgzfQDPeezHEblTngI5lDQAANc6LvXmYg2chlMqXnjo12iY5kVDxZkySYoc-Y%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS ROG MAXIMUS Z790 DARK HERO, LGA1700, Z790, Intel, DDR5, WiFi, ATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-dark-hero-lga1700-z790-intel-ddr5-wifi-atx/70439847?hid=90401&sku=102785993706&show-uid=17397231488049511310316002&from-show-uid=17397231488049511310316002&cpa=1&do-waremd5=kHRpAA4w1sqgJbg46uS9fA&cpc=CXSMTylTSEgBzZMLpWlXJVPaKRPF318rt6uhktFql_QcbdmpWufKNRwUM4N1schs1_CbSMMCB1mBUPFbDKgLIsD1eRej4TXR-lCpO6ziWkgK87_jtL8e0bq9BartKAJyyJ4C4oE5fQSIErAf0hYttZ-qqhc4jrK4I1fP9lSsx7Rx5YP_m9x5i03Hgw1rNnRCGknQbyB17q-Y8NHBWlJgagjI0I3aepgzdrzAuOUgOrY%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS 90MB1H50-M0EAY0, LGA1700, Intel Z790, ATX, RTL (90MB1H50-M0EAY0)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-hero-btf-90mb1h50-m0eay0/618448638?hid=90401&sku=103513089880&show-uid=17397231488049511310316003&from-show-uid=17397231488049511310316003&cpa=1&do-waremd5=f3cn8AOStZLaloT_H7Fu6g&cpc=CXSMTylTSEgj25cnX1HpSTHH-Lg-1MlwmpPPIZblR6DqynD1zGH0GM7D2GOupMNaJgGQzu39QkjhqAvvAsUOLvpoKCQrxjUnGr9k4QX9YWOVRP9JGFEUvVUZYuOyUE3udZFGA9rsHDY6TRkTk85yZshhSX4iDNyprm60vP2dINQr6v3lGkpyYzxVWyS4lHmiSTDqtNeIzq24PhqyE8fchUFe7bKNiw8hj0FWJ8QUlD0%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS ROG MAXIMUS Z790 APEX ENCORE', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-apex-encore-90mb1fx0-m0eay0/217614976?hid=90401&sku=103186893090&show-uid=17397231488049511310316004&from-show-uid=17397231488049511310316004&cpa=1&do-waremd5=mTfZzEobZUWx64PSqjZZTg&cpc=CXSMTylTSEjzUZAys4mhB7IoHGfbA5su0RDii-qVQGaGW75KThQVvLrRYowoKzUS9Hmcp-uAMGOJJuiRu0tYLrAf3-qoZ40sOyKuh_G0HpAmsnJXqD9MK36PZ9QRGLDvwnJXEJw7wO3UWZmC71k0mLYqsEVTQNoU1-vfKCrKM3H3Sn-uIMmYAcl0daaVmJB7PEUnuiAWsg7VWoVNqtMSHGhpFdxOFMdrro64lN0kvUw%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MSI MS-S1251', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-ms-s1251/44265055?hid=90401&sku=102617213909&show-uid=17397231488049511310316005&from-show-uid=17397231488049511310316005&cpa=1&do-waremd5=l_aDEoz1UDVFB9JQmstL6Q&cpc=CXSMTylTSEh6-8q8MOA9aDQjdQ2cq6IFoJgfE8aanfgAGsMUw9oAbZEAy8lie0FUKDXIx50tkPmuO7u-_D3B5nS3QChkzDF-JOoB-6uo5nKXmXDF9_2eL8z8ffxmKZ64_6BZy4p_WevxDVsTbNBFcH8rdstLbrH88WU8g42EWB7c-KAOFFkBUL3tt4-qH1OfpBCXLP6dYbW8wwdLq9BNL90nBSXQ2Of_DJLtyj0jsPo%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MBD-X12SPA-TF-B LGA4189, C621A, 16*DDR4(3200), 4*M.2, 7*PCIE, 10Glan, Glan, IPMI lan, USB Type-C, 4*USB 3.2, VGA, 2*COM', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-x12spa-tf-b/1785038542?hid=90401&sku=101872319278&show-uid=17397231488049511310316006&from-show-uid=17397231488049511310316006&cpa=1&do-waremd5=3XlUhDf8FlCadN0ZGqnlIg&cpc=CXSMTylTSEjttJGD3QrQuqLbtwhWPB-X9g-6EjXJy4CRBEI9gmmPBkOZqcOmApC7wn9AtX7czXA5XEB3DMB_fR_ZCDVfDFRKnVy5yaY2xWGTul47AVPnbfcKMhziA5F6s1goedFMr5uFZpB9NI57ucaGkvsws8Q5VExMcZ_r-VE7F54gYYZ0Bgal_46ZVeZoID6k1lfnrCM%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Supermicro MBD-X13SWA-TF-B', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-mbd-x13swa-tf-b/119770821?hid=90401&sku=103038595827&show-uid=17397231488049511310316007&from-show-uid=17397231488049511310316007&cpa=1&do-waremd5=7aTUMr0uhTryDMTU7CKGGg&cpc=CXSMTylTSEilrr2qvQMagcxkG3VEO1iuKOJ0ynVJYXdtZI7eJveVYFrmBma6HC28dlrQhkUoPKqAkEaFeSxNBUJBoj9qgFGQnADd4OFcfHdyTvfjlwxCLJ9UpDOSIU7JdLCNeaPBYP9iH-RtQvyPL8AdLjMvzFSDx_X37JKxwgFE_LFH5rC4ds5uKwEUgFF5yiBkAOdBJZe67t4UJh8_IluJaAQ2gsOcgvE1ETAlVSo%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Supermicro MBD-X13DAI-T-B, E-ATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-mbd-x13dai-t-b-e-atx/83714367?hid=90401&sku=102871114543&show-uid=17397231488049511310316008&from-show-uid=17397231488049511310316008&cpa=1&do-waremd5=jqS_qE17HxUoWyqWZukH9g&cpc=CXSMTylTSEhH6Ag5kvJ38JiFZTm04aR2lHuA6ztlW0SquidqX5WqtEh9-CHWJaxDraC8dUsVBNKZOgA9Oncv1_M8TtKtdko1wuOHaLREB55jBOlH8P09KuApyk-W8vD0Wx9R9J5zuUyMnVHWDItET3YFo0GoF9UkbhoqXYED1fqB0PIo_S6sa4jLCMB3f_xQiklH99OS4EpSOQH3JYqT_ijWRTxm06Rjtqr28KCC-nw%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата SuperMicro MBD-X12DPI-NT6-B 3rd Gen Intel Xeon Scalable processors Dual Socket LGA-4189 (Socket P+) supported, CPU TDP supports Up to 270W TDP, 3 UPI up to 11.2 GT/s, Intel C621A, Up to 4TB RDIMM, DDR4-3200MHz Up to 4TB', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-x12dpi-nt6-b/1785038500?hid=90401&sku=101872319224&show-uid=17397231488049511310316009&from-show-uid=17397231488049511310316009&cpa=1&do-waremd5=5fSKcUYV54m5nx-QuATtqw&cpc=CXSMTylTSEiHiAEVyWz5IobBd2joMRrOUMVnetdJoACh-4SBMv9mtp0T4oin0GSsU3v82uJH_6QR9Q23hLv3lNDYhcgF6dsZqgw3RewBPx6ii_DVPloUKWrAo7iqFq3itlsbO2ZNeSNl4aTiEUh-BHxfRtFAwYcOKz33fqD_XH1L7A8bFjEdR2OLoc6Z_pXuhXBzpX3k6FLo9KfWrSabX9Yl95RzCvvwshDbMZtUvjc%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MSI MPG Z890 CARBON WIFI, LGA1851, Intel Z890, ATX, RTL (MPG Z890 CARBON WIFI)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mpg-z890-carbon-wifi-lga1851-intel-z890-atx-rtl-mpg-z890-carbon-wifi/958831922?hid=90401&sku=103737171222&show-uid=17397231488049511310316010&from-show-uid=17397231488049511310316010&cpa=1&do-waremd5=12_rWD0f8DyO9fav-m1TNA&cpc=CXSMTylTSEjDvIu5Yl4oNlFNQ18kvMHWIfBfsKyWZRd5oKi8ld1tO-apG6_tBk1rLaTlZob0hiStLeItcpzEbVbzCQdANa1K92nSdesUS9-nBQLoYyc-E_twj_R2jcif4aPEmCWgYAv9_7HNWQrhMEQpCvn8UiK82SWcUxOuG0fCY7u9fKz8BejNRTyhqE2Lz_2HUfQDUqE%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B550 GAMING X V2', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550-gaming-x-v2/1779555176?hid=90401&sku=766629016&show-uid=17397231487800507513016004&nid=26912770&from=search&cpa=1&do-waremd5=-XNDB753rINXrYj90xB1tA&cpc=CXSMTylTSEj9qUHLxciI_iWLS8iGnfy6XhmxABOxeclB77XDU0zejh32TCpHWFtPGQ-rdBRjnprbrbYFCqFc7W39p_GSz_y1P6rNr8CrqALp6hTT-VajW38nIUu7QqnL3uiWt0ylm6UUL9_AoW-r_VroCSP81CtqII1nb7dW8Ga5H_HkKzUFmIhOvS_dPqfwS8TEd5aQsRnQzWRNdpATtBtXbw_6uBUe7enbkHMpm8YdovJ-S8qRTISEhpamlCfsHFjjp88FMlZmi_tfObh8BUFfz4x53-KqK4EHU_PqchLHirNFNRDgtbr7dcltizDprQpEjYmyrtxQRGoY8rctOUHuiHwZh8wcjVtqTFNbh5xHCsa9UKC6kiBjA3FjB2ubnC_cyTgIHGHIjuVnojtGdMNvFy-S6Mcvtt4BtpMxE1qkKcj8mbZ8-us_c-Y5kVWPhtAFL4eFkXyMf9n-V9FFyg%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Asus PRIME B650M-K (AM5, mATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-prime-b650m-k-am5-matx/1932256909?hid=90401&sku=102296025496&show-uid=17397231487800507513016005&nid=26912770&from=search&cpa=1&do-waremd5=v6lA2lGNpOuMIYEs-bMqzw&sponsored=1&cpc=CXSMTylTSEj9K7E0S2HdF1k5E7khZGm_dNO04FH_lP9a3MNQSJVbfFia5GeHrTduFciq9Uh5Fe7nPKY9T-xewmjJ7CWDP-fTbAro2LpwCy9dY2s60N5HAdM6lg4UNP2PsCOZxaqDHRdDECijDK2dUQz5hYxVetfYedPVbtFm2aEnTm3zXVD3pq_Cov_R1RKVGrbMKMuD_IF3kKgJzt9_SbBiCKHEavifZhuVduQLU5RgrkfJ7FSUnyCzxuIKLcPVVtk5zB2FfZ6Q8esSNt77YwZS2t-XYixpJIB0dqLzSQqwpxzfVxn4v3SlX501k8wLT_-OuzTNNhClZhaa3B018L_7LLY5rZ_GGVhgxNTRGUMNT5UevNX0oYQcj6xihOjRozEkUjsszl01ZTMLehiiUhl6A3t4z_-16zH0mmLaTkwpBmdGE1mBoG3vzrNalayorDnKo3VxX6WSB5J9e3JUqns-SLnIPv9HswSwS-22WN4rWxAXB31hOAmvP6YgLmBn&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата ASRock B760M PRO RS/D4 Socket 1700, Intel®B760, 4xDDR4-3200, HDMI+DP, 2xPCI-Ex16, 1xPCI-Ex1, 4xSATA3(RAID0/1/5/10), 2xM.2, 8 Ch Audio, 1x2.5GLan, (2+4)xUSB2.0, (3+2)xUSB3.2, (1+1)xUSB3.2 Type-C™, ATX, 1xPS/2, RTL {} уц-5-3', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asrock-b760m-pro-rs-d4-rtl/1820740848?hid=90401&sku=101951773019&show-uid=17397231487800507513016006&nid=26912770&from=search&cpa=1&do-waremd5=utl-Uxl-wdvvx53dQFPtqA&sponsored=1&cpc=CXSMTylTSEjqUVKhM1Nq0rPaXbM9c7NoxFHth4IAluAshzTxTm9mODFaLSRiHaltxFJGgemzGvP6jmMRSJ8TpCkKVKxEfTLNGZMRgVyRmmOKynsNlZDX29FCbwxywn-omR2nQ93uF5dELDJMD3V8KnRQqMtku4HozhdriZSE6Gyjf64Q12zm3brtZtZHFWJ_3ouIrKk_QS6ggLMSbVFvzHZ1f2DlirwxkgTrVYRp5JiMm12htvuQezd8ym-bLctjXDDab4NR_8BzMSMXILDeflYb6lflXLZFsYtc0he1tU_rxoU0ImTaIkh5Ofb_A9o62MDRrMbORE_WH6hjZ06BTfXnMIMzdZLHtdHBVOH8aRsm0AuuOilAHRqnrZIHH8lo4SoCJ8JHFpMfi9TqXZ9vCyTSyVdJu6x9U9CNyBk3kYqkqc2O4tkRxtBHaKMyoDm69nBSl8i4NeODbo54tAskCVC1QQEpFBREyDOY2Tpld0XzZSn9jBveEadL8UGQL2le&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B550M DS3H', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550m-ds3h/1779555044?hid=90401&sku=675350012&show-uid=17397231487800507513016007&nid=26912770&from=search&cpa=1&do-waremd5=GvJJIJwJJhlEvYEktbGshg&cpc=CXSMTylTSEj8WhvXn2W-OyKUkv48qDjfFOFlKTYDyW1qu04E0hEJKOjTarDr3ZYgh6ajOdLRU0GtVEzFpF2qs2Z3jVsj0x_Bn_P3YpUCF-3ywDMQ_SOHmv5jCNZWltN8CHoSlBh3XoLiAxsAYHtRpC_hPK9MR0_BGy51_hqwIm_ARhuuvZP4NCq97CyLvv1f3z-6W_ekitNQPn8MtPRWPFz1sVH5iCzT3sn4xk6_PUnZh86fgfHbnoFfcM6JXr51vyz38nqOXdYKWhjKxGNUCfJajwK8rh2OGtzBUkv6VhMZt0zio99aNdTGEnALUYQcBrgHjpjMXpgY15Iuf0P7MuQMujmX5Rn1pN41D_fcROBmQL-dJQk6YkplJPpxZbEQ6DfjVEN-enJMoDnSNdpr2DZS-Y5QOkscabdk4VCYVydlSEvy_LiyoU5AbJC4Pb6gaIEVfVIEnEKVt-xcsqmQXw%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B450M K', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b450m-k/1782318038?hid=90401&sku=101864649749&show-uid=17397231487800507513016008&nid=26912770&from=search&cpa=1&do-waremd5=JPPzEbS4jbfxVK4LWCpz8g&cpc=CXSMTylTSEgSLF-JzKuFZOunx2-qJqhyGm0x2DnlcoktzYQsdrDuY9ZahQOQFeHUxY7UVZf7eH4SyQpxBJL5Cv5TNp0ncoHFbaT-Qf7fKIYWhWet7Gi35o3B4EebpaKPCrxc1lXdyw1g5JQgPsnP9yvMaqGhrOQDq0IXWC-2OJraL3pi-xtV-HeFCd4Yg05dlqP1KoYDghIl5ijEJEBzAcz_RIYxl8Iu-jRF3HiyAz0JV6ffIAVShafQ65npgGexzyFIZg6pGqdBKTuIx1PN3faIxvYGYFuhEVCZdRn5FYqjNS9LSfjFDq8vmCHW4KaTSuwQCzVmWeIhUMc_QphddAEOhkI7tDMUwBvZJ4dHNm-VROMYbGRHSoY67Cg-mGY-UGi5PZhjx649I6P_Iu2krexari52iBc0VCfEV5Ra92PuYlTmZpp4bSKM_tQX4ocKl-UPL9xbrjuiA9oudlDozQ%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B550M AORUS ELITE (AM4, mATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550m-aorus-elite-am4-matx/1779555055?hid=90401&sku=676266211&show-uid=17397231487800507513016009&nid=26912770&from=search&cpa=1&do-waremd5=RQivNFmxyPTcpJcCNiQRaw&sponsored=1&cpc=CXSMTylTSEg7qvP32Eimq8uDgT0OHcQrEEgvZfwX0iUK_--C52Wt4Yrva2dI-sRn6jCTU7ukFswAGEW9lCCXU-S4itjZ_fuhI-mQwJSJaibRGGcs_DrOi6FTol4cQJApz9A9iEqkc6n3wWH73VXcbJeluPP4RrvVfaAylLF-NN1DqciCs5krPYIaH5Oukw7Q-nXphYXxujY115PmqMG4zJocleWIMPX9Zdy9CpdFlXy5WZ-jVwqqP0j2GQb7tPQBrNjH-2epiTpmiLMfICEShYXISm2xZAMCNWcobzYAMhjxBYEczSi-hvBbBW21xI2pZqXRWv11Lv6G9Ump0YvYWL3mySYXMj1QJlZGAN8YUHGbgdIKzE0wxVqvla-HS165h9f8RtFgjhhjtCUYaqJIxODPKrE3y1b2g6Ayu-i_mq6Eakp9satxGxDNnzzN0viPZMt3hxVSxzY7eRBPCcfiZN77Y5_6nxTAxJgDELrpzHyiY_gzFYA8GIChJ2mC857fZRuSslgAxe7ug8JeBHXWmP2HiezPLYckLfTUqKfnOOyns5DgIe33Jlsps1OPyMvf827ix54iEF4_3GyS0Kv9M771wuR-E0okRFV3PsioowldJAleY_Rd7PlECNnu3xQ4&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата Gigabyte X870E AORUS ELITE WIFI7, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/762813300?hid=90401&sku=103565245584&show-uid=17397231487800507513016010&nid=26912770&from=search&cpa=1&do-waremd5=ZXXFBGZLSwihSchXNc3zhA&sponsored=1&cpc=CXSMTylTSEhj5AzliwWXhoIwd3W1r22BXtTwrCvwpVz-mDx7Bz1zEyij83F81kf7f3SU2Hz1cZh7epeHVs58vO-CyO-2YGx8JD3tzxdeJMQMknXdXzxO04TTfm86fhhR0Dt3jAr5q4_7YseBLJUNrI7ZEnOAfTsxeTOIZs-m37ebGLURNqUCU1zSvXoEu0KfVQRjwc8PAredWMopqEg1SHlLmDvFYB5hETkP0uFAnvZi8hnBa9SSHF3KZo9ZR4QQJF52iRMXQxt4uu5_bTEzq9SKzz3JwqAQehI1Wz-3bY0ogF9blAk2bJ0Jlp0TwKMrnE87ZGCx6jsnvDkPiNj-hVTymMayX1JERW2uXMnzl0YPvMuCmvRzcrqjYNMmrMfYZRR2NgW1QP4NPSUjo5cDlFZ-LwfodmGjs9tN7O2jirqt9UNt5aPnLkfcDhztrPoGEJBCct1dEyYJ5hXIcohqM-ogfEp-wWeZ960PWGAUApz7623YjI3gRlCRQH3MIRGT&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата MSI MAG B550M MORTAR MAX WIFI mATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mag-b550m-mortar-max-wifi-matx/1779556403?hid=90401&sku=1761111537&show-uid=17397231487800507513016011&nid=26912770&from=search&cpa=1&do-waremd5=zMYId93PxSbdhf_t-JIp-g&sponsored=1&cpc=CXSMTylTSEjwnjEnylkCcHGR0tEnjb3_ITWtXLyi-ZPJ_ha_xsDopi69btnH7l5AfkVmk6T2wxyu5SVms2TNIOXK8kw8gKAxoJjEmF-GJj4ldSxFrpSCwsFuW-PonS3Ypgt9D4H276rHPcpb_lbhuY6vP1POQWvxleZ_B8lAtaPeenIhnXfbZyOJKbXdfk5XQX5eGMe6ctM_beiONWjJc1hHdbGaU5eEalliNY6X5T5Yyvm-__U1k8-wVvTkBWsWFd3BXw3A2y2XCDY6oyd5AiAKndw54mVb_9qPEjh4r9I5qeZjBhR3NQ5Nzw_l60fW7WfxG9EOsq3IDT0apHh1Awe1kPDoGODzsJKIN27ptfIuYCE7zpDid_Mh5aPztigiFvJUfNU4qQH_FQC_zWZBM4NXN5r6Y4s3046pe_4z7ujYrM3YAG9Dn-wjviqnnDB6223vJkkad8LXv5-7Q6k_fVm1cebWnJF-zvgvUPEo3BkTl0Wf6S1A1cCzKIzg0f1e&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=12054742'}, {'title': 'Материнская плата Asrock B450M-HDV R4.0', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asrock-b450m-hdv-r4-0/1779554660?hid=90401&sku=334418263&show-uid=17397231487800507513016012&nid=26912770&from=search&cpa=1&do-waremd5=MD_eCfiz5kNP063EUMYILQ&cpc=CXSMTylTSEga3IHuoEwX-qt1lBPzD2_p3UXMZ_OWWA9y2AXgA4b_AWBPLs_kxUXmUtAJDqLxHj4JB9KHPvBPPTYxNc88fPt1ZoIg5DoyWy8tINvaQJn6MFRxjbJ3H9vWxCl8h-moOXhJT7OcA_WgZJHYB2Zeo8yV1EnktT7gdROKxPg1Rx98FCFiu3pc3JyTxCHt92B4W0-UuQxOEu72yvrrZk-JXsVyNR9nvd2H2BYCLq2P_hQTJ2eTb-m6yNeQZYu1bPRV3O6vQsqC7b0nYkDEcz8_-9I998GOcZqDSEBzTWc9IoX2Q8WVakoPHVwWjqQlPB7kKeyl9lJpXWPgH-WJfTFCjDvIRt0kHZoYQt2DY9XX5GpMnZksy45PGBogy5WGtKkPY1j8yBB0uEAk-GuhUAg_JPqKmBU1_4M3UrirpQP0RIT1lDeAs45IBr2OobIGRAdEDsOBHJKhhJ4Uxg%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B760M AORUS ELITE AX, RTL Socket 1700, WiFi, mATX, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b760m-aorus-elite-ax-rtl-socket-1700-wifi-matx-rtl/42794160?hid=90401&sku=102602962858&show-uid=17397231487800507513016013&nid=26912770&from=search&cpa=1&do-waremd5=h4PQ82F0XSBsKFm4uRf05w&sponsored=1&cpc=CXSMTylTSEiEX0SmkEdEnxN9QeIj3dWf8KqGF3qJJuAT8PvaEMKtCm1a4IUX3WRPu4Y_czHLf7YSU6S_Be_VRDub_Yxy4FhJtctvOWp-t87LGdHM02WcNm8hhjPo8dRRMzxW1kij_QH_k70uNTz6gJV2jEwieL_me4Eb3NNkfnm-4IdSPSPGkUkyQs7z24Kb38Y3cc_HJf8jiFISrBfRAI720AZPy-EJfIK1z9xf19rrG2QpkTZTTbkYXp91f75j411jGX1P2Kf1kgzvX_dYSXmNXtMUgTVxjSthj604SiqxCXp95wkDzz-kWLRy-ouXWjp5EhM4IBwwNToLtFunXHIfh3-KvyrWZd8QVO5J_Yu_0IxOMt-BvngvkNn15OOKE9kEs9EaBkrJaU7d9ajbi-rglvZBXMhwgKzour38TdKiN6FXhxLYfOSMKZt57W54QP04WPOC2Q4us7e_r-uCtYonw9HoSoaT8iWhTpC6h5P2-9CMFDgHNNgXwZUGqRJo&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата MSI Z790 GAMING PLUS WIFI LGA1700 Retail Z790 DDR5 ATX HDMI', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-z790-gaming-plus-wifi-lga1700-retail-z790-ddr5-atx-hdmi/39574459?hid=90401&sku=102581861759&show-uid=17397231487800507513016014&nid=26912770&from=search&cpa=1&do-waremd5=vVDoTLUCrFd4ajaHGCCJww&cpc=CXSMTylTSEgowN5TVDJyrmOPn_EuslWnt0cXhN5QQ3RzmBIfUJli4WI7Z_RtRkV9Q1v1aZwcm_9WiCIOhf20KaES4TxxB_ApAonB6GCxj7JnFum5U2s2ymmyxz8QsWRPVHNHAE_ZFApuSx8F7LpYNS12OjtPh_rIXD2gqsclwWzxvCK1ForqKZolewhAOyEy9xF6igGiph81MPJJpBp44d_Y--vk4ZAHWQV6RMOKe1pYYvPh5yir9oAvlFj4ybFlgq__9N3I1IL8F_SdEUhEgXpHD-q7SYyeHXKtFskz23d9tfnamLRNkLjQPahifTUJSBC0KGpCtM9otP5-LnfX15Y6m1an0i5ge7wroT3Me-I01b5n__-qdikw4wYSQR5k3RKknrqRXPnEqN56H1on718LiyNwGwn1IVEremn6h1Mbd43DT3kntz_NeJpiDjYrjeFl70EVGIrV5FPvGkvQqN5Oi-I5DVyDcP4flDjVDp6z3FfxDuaj3nlU5Y6436S54Yz7IM9P_JiZh12uyOIJ8X67pAgJqy40hvl2xNTmPnRPzOY31lvZKvzdRQXkyYKAebLwf1ByP3hlPhyit7eoLm1ukXIKPzTftIFdxSnuTgM%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=924877'}, {'title': 'Материнская плата Colorful CVN B760M FROZEN WIFI D5 V20, LGA1700, Intel B760, Micro-ATX, RTL (CVN B760M FROZEN WIFI D5 V20)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-colorful-cvn-b760m-frozen-wifi-d5-v20-lga1700-intel-b760-micro-atx-rtl-cvn-b760m-frozen-wifi-d5-v20/867552581?hid=90401&sku=103644418508&show-uid=17397231487800507513016015&nid=26912770&from=search&cpa=1&do-waremd5=9AXa9mRhAv55LU8Fc-6pig&sponsored=1&cpc=CXSMTylTSEi9DTZOXyZzxykiM_TVGCf7tSE8h7h0BGwAUMQRHCcRFdwPdcDOy6bk6tdrBVodtwBNmwf71usJUXfYCtuRfxEU8DRFnFPtRgJuFqiOBPYPo40NL5QLmUg7ka3dbXMYHTmi-v0hrEJDru12MZsNFhtFP_Z658vp0KSzP1DtX9sBVeuS00gvIPRmWjHDR7gMOqrNcDdl976jJ0HZ7I8RjsbvKucfTUV3JezTzAlQOgdFbXVonaxUKxwW72GEwMB6UR2TrH8h9FE9oQBTmGyig3dh4A6udC76UxgEDM6zo41lh5bxsSGndQKFYvuJYmCdnQ5JZ0tugzrDJdp3UZiAtU3vQr7u4tw7AQUPbVDY8dxr5Y90AV7JUCoijy-XkGChIJ82h9DIUM8ahHtN49wLgv3o2B_yUPlj3LqBvaF0fYYQqfxd4C8nYT_F_f27PGqmCGTfC6NWub13F0M_UYaab0RH_a-RoJfQOsZbrTXM9VNsa2-zPrHp4Hoy&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B760 DS3H DDR4, Socket 1700, Intel B760, 4xDDR4-3200, ATX, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b760-ds3h-ddr4-socket-1700-intel-b760-4xddr4-3200-atx-rtl/1812468853?hid=90401&sku=101926164825&show-uid=17397231487800507513016016&nid=26912770&from=search&cpa=1&do-waremd5=aZAssmitkw6-KY4qM5jjDg&sponsored=1&cpc=CXSMTylTSEgo2LOtt9NwU-z9USUnO59gwrXfMHhpwmJfnSZreIkD_Ih1bMLNHSY7cenp030jic8SzKSDBWHw2BO-5RtUJJ_skxvLpRI4-jjo2-WElX1AEaPoTd_1of4dDJiZGsA5vDtVCoWF-o3oqvID5wLG24kHkkZ8t0-jhPVYOONKFW1AEkm_H-85ulRTR8Xk5roiU_zj42ojjSd1L-SQK_-CErvbagNHkGBFYNp6QbAUYj1xizL87M_Kih4RvvC5lOkrFBKJsBUcVxVgMJpEOWHQv7XkkQdpIzwKapAEqvXfzeUZuP4Ucmc23zU5i1NVDhdIck0zvlVSpDp5hbNe2tlsK56kb-bS5ExQjPscOb2tAlcWwMmaYUs78zLsSBpnoIKMlgpNsRGjpyCFVFaIZKIW-DUKxzYvd1MXI4m4Noq1wuEu0sCM_JcMXucu5DEBsPLVwPZEt3AaIWMKG6j9J_5grdiBOgEaVZywtTs5pZmwJuPGHSTbelszC-Rz&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}]}

    #         with app.app_context():
    #             new_links_count = 0
    #             duplicate_links_count = 0

    #             for component, links in parts.items():
    #                 for link_data in links:
    #                     # Проверка на дубликаты с учетом компонента и ссылки
    #                     existing_link = Links.query.filter(
    #                         (Links.link == link_data['link']) #&
    #                         # (Links.component == component)
    #                     ).first()

    #                     link = link_data['link']
    #                     title = link_data['title']

    #                     if not existing_link:
    #                         new_link = Links(
    #                             link=link,
    #                             # component=component,
    #                             title=title,
    #                             is_parsed=False,
    #                             date_parse=datetime.utcnow()
    #                         )
    #                         db.session.add(new_link)
    #                         new_links_count += 1
    #                     else:
    #                         duplicate_links_count += 1

    #             db.session.commit()
    #             logger.info(f"Saved {new_links_count} new links, "
    #                         f"skipped {duplicate_links_count} duplicates")
    #             print(f"Saved {new_links_count} new links, "
    #                   f"skipped {duplicate_links_count} duplicates")
    #         return (f"Saved {new_links_count} new links, "
    #                     f"skipped {duplicate_links_count} duplicates")
    #     except Exception as e:
    #         print(f"Error parsing links: {e}")
    #         logger.error(f"Error parsing links: {e}")
    #         db.session.rollback()

    # @app.route('/update_is_actual_batched', methods=['POST'])
    # def update_is_actual_batched():
    #     try:
    #         # Размер пакета для обновления
    #         batch_size = 1000
    #         total_updated = 0

    #         # Получаем общее количество записей
    #         total_count = Links.query.count()

    #         # Постраничное обновление
    #         for offset in range(0, total_count, batch_size):
    #             # Получаем пакет записей
    #             batch = Links.query.offset(offset).limit(batch_size).all()

    #             # Обновляем каждую запись
    #             for link in batch:
    #                 link.is_actual = True

    #             # Фиксируем изменения для пакета
    #             db.session.commit()

    #             total_updated += len(batch)

    #         return jsonify({
    #             'status': 'success',
    #             'message': f'Обновлено записей: {total_updated}',
    #             'total_count': total_count
    #         }), 200

    #     except Exception as e:
    #         db.session.rollback()
    #         return jsonify({
    #             'status': 'error',
    #             'message': f'Ошибка пакетного обновления: {str(e)}'
    #         }), 500

    @app.route('/links/<int:link_id>/set_inactive', methods=['PATCH'])
    def set_link_inactive(link_id):
        """
        Роут для установки is_actual = False для конкретной ссылки по ID
        """
        try:
            # Находим ссылку по ID
            link = Links.query.get(link_id)

            # Проверяем, существует ли ссылка
            if not link:
                return jsonify({
                    'status': 'error',
                    'message': f'Ссылка с ID {link_id} не найдена'
                }), 404

            # Устанавливаем статус неактивности
            link.is_actual = False

            # Сохраняем изменения
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': f'Ссылка с ID {link_id} помечена как неактуальная',
                'link_details': {
                    'id': link.id,
                    'title': link.title,
                    'component': link.component,
                    'is_actual': link.is_actual
                }
            }), 200

        except Exception as e:
            # Откатываем транзакцию в случае ошибки
            db.session.rollback()

            return jsonify({
                'status': 'error',
                'message': f'Ошибка при обновлении статуса: {str(e)}'
            }), 500


    # # Создание базы данных
    # with app.app_context():
    #     db.create_all()

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        c = None
        got_price = None
        if request.method == 'POST':
            got_price = request.form['got_price']
            try:
                c = int(got_price)
                if c <=  25000:
                    return render_template('home.html', got_price=got_price)
                if got_price == None:
                    got_price = "70000"
                all_price = got_price
                print("all_price = ",all_price)
                selected_option = request.form.get('pc_option')
                print('selected_option =',selected_option)
            except:
                return render_template('home.html', got_price=got_price)
            price_ranges = get_build_ranges(selected_option)
            print("price_ranges=",price_ranges)

            coolers = get_components_by_type_and_price("kulery-i-sistemy-okhlazhdeniia", float(all_price) * price_ranges['cooler'][0], float(all_price) * price_ranges['cooler'][1])

            motherboards = get_components_by_type_and_price("materinskaia-plata", float(all_price) * price_ranges['motherboard'][0], float(all_price) * price_ranges['motherboard'][1])

            processors = get_components_by_type_and_price("protsessory-cpu", float(all_price) * price_ranges['processor'][0], float(all_price) * price_ranges['processor'][1])

            rams = get_components_by_type_and_price("operativnaia-pamiat", float(all_price) * price_ranges['ram'][0], float(all_price) * price_ranges['ram'][1])

            videocards = get_components_by_type_and_price("videokarty", float(all_price) * price_ranges['videocard'][0], float(all_price) * price_ranges['videocard'][1])

            bodys = get_components_by_type_and_price("korpusa", float(all_price) * price_ranges['body'][0], float(all_price) * price_ranges['body'][1])

            ssds = get_components_by_type_and_price("vnutrennie-tverdotelnye-nakopiteli-ssd", float(all_price) * price_ranges['ssd'][0], float(all_price) * price_ranges['ssd'][1])

            charges = get_components_by_type_and_price("bloki-pitaniia", float(all_price) * price_ranges['charge'][0], float(all_price) * price_ranges['charge'][1])

            motherboards = sort_components_by_price(motherboards)

            processors = sort_components_by_price(processors)

            rams = sort_components_by_price(rams)

            videocards = sort_components_by_price(videocards)

            bodys = sort_components_by_price(bodys)

            ssds = sort_components_by_price(ssds)

            coolers = sort_components_by_price(coolers)

            charges = sort_components_by_price(charges)

            print("motherboards = ", len(motherboards))
            print("processors = ", len(processors))
            print("rams = ", len(rams))
            print("videocards = ", len(videocards))
            print("bodys = ", len(bodys))
            print("ssds = ", len(ssds))
            print("coolers = ", len(coolers))
            print("charges = ", len(charges))

            print("motherboards = ", extract_prices(motherboards),float(all_price) * price_ranges['motherboard'][0], float(all_price) * price_ranges['motherboard'][1])
            print("processors = ", extract_prices(processors),float(all_price) * price_ranges['processor'][0], float(all_price) * price_ranges['processor'][1])
            print("rams = ", extract_prices(rams),float(all_price) * price_ranges['ram'][0], float(all_price) * price_ranges['ram'][1])
            print("videocards = ", extract_prices(videocards),float(all_price) * price_ranges['videocard'][0], float(all_price) * price_ranges['videocard'][1])
            print("bodys = ",extract_prices(bodys),float(all_price) * price_ranges['body'][0], float(all_price) * price_ranges['body'][1])
            print("ssds = ", extract_prices(ssds),float(all_price) * price_ranges['ssd'][0], float(all_price) * price_ranges['ssd'][1])
            print("coolers = ", extract_prices(coolers),float(all_price) * price_ranges['cooler'][0], float(all_price) * price_ranges['cooler'][1])
            print("charges = ", extract_prices(charges),float(all_price) * price_ranges['charge'][0], float(all_price) * price_ranges['charge'][1])            

            if len(motherboards) * len(processors) * len(rams) * len(videocards) * len(bodys) * len(ssds) * len(coolers) * len(charges) != 0:
                comp_result = compatible(
                                motherboards,
                                processors,
                                videocards,
                                rams,
                                bodys,
                                ssds,
                                coolers,
                                charges)
                pricess = find_prices(comp_result)
                print(pricess)
                print("comp_result = ", comp_result)
                result = {
                    'components': comp_result,
                    'total_price': extract_prices
                }
                total_price = extract_prices(comp_result)
                print(total_price)
            else:
                comp_result = None
            if comp_result:
                return render_template(
                    'result.html',
                    result=result,
                    all_price=all_price,
                    total_price=total_price
                    )
            else:
                return render_template('home.html', got_price=got_price)
        return render_template('home.html', name="name")

    @app.route('/about')
    def about():
        return render_template('about.html', name="name")

    @app.route('/contact')
    def contact():
        return render_template('contact.html',)

    @app.route('/result')
    def result():
        result = {
            'user': 'name',
            'total_cost': 75000.00,
            'components': [
                {
                    'component_name': 'Видеокарта KFA2 GeForce GTX 1060 EX, 6GB GDDR5, PCI-E, 6144MB, 192 Bit',
                    'component_type': "videokarty",
                    'url': "www.market.yandex/fgfdhgfd/fhhfhfd",
                    'image_url': ["https://avatars.mds.yandex.net/get-mpic/4409630/2a00000193e57d8c83efd97c8d7b1a0125a9/501x668", ""],
                    'price': 1500.00,
                    'articul_yandex': '5537064366',
                    'fullSpecsGrouped': {
                        'groups': [
                            {
                                'name': 'Графический процессор',
                                'items': [
                                    {'name': 'Бренд', 'value': 'KFA2', 'transition': {'type': 'catalog', 'params': {'glfilters': ['7893318:7693369']}}}, {'name': 'Комплектация', 'value': 'Retail'}, {'name': 'Название видеокарты', 'value': 'GeForce GTX 1060'}, {'name': 'Кодовое название видеопроцессора', 'value': 'GP106-400'}, {'name': 'Разработчик видеокарты', 'value': 'NVIDIA', 'transition': {'type': 'catalog', 'params': {'glfilters': ['50048792:50220415']}}}, {'name': 'Линейка', 'value': 'GeForce', 'transition': {'type': 'catalog', 'params': {'glfilters': ['4878791:12108566']}}}, {'name': 'Техпроцесс', 'value': '16 нм'}, {'name': 'Тип подключения', 'value': 'PCI Express 3.0', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128795:50197661']}}}, {'name': 'Количество видеопроцессоров', 'value': '1'}, {'name': 'Количество поддерживаемых мониторов', 'value': '3'}]}, {'name': 'Технические характеристики', 'items': [{'name': 'Максимальное разрешение', 'value': '7680x4320'}, {'name': 'Частота видеопроцессора', 'value': '1733 МГц'}, {'name': 'Частота памяти', 'value': '8008 МГц'}, {'name': 'Объем видеопамяти (точно)', 'value': '6144 МБ'}, {'name': 'Объем видеопамяти', 'value': '6 ГБ', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45123612:50195424']}}}, {'name': 'Тип памяти', 'value': 'GDDR5', 'transition': {'type': 'catalog', 'params': {'glfilters': ['37338070:38439390']}}}, {'name': 'Разрядность шины памяти', 'value': '192 бит', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45131906:50218305']}}}, {'name': 'Область применения', 'value': 'игровая'}]}, {'name': 'Дополнительные характеристики', 'items': [{'name': 'Разъем дополнительного питания', 'value': '6 pin'}, {'name': 'Рекомендуемая мощность блока питания', 'value': '400 Вт'}, {'name': 'TDP', 'value': '120 Вт'}, {'name': 'Дизайн системы охлаждения', 'value': 'кастомный'}, {'name': 'Количество вентиляторов', 'value': '2'}, {'name': 'Длина', 'value': '228 мм'}, {'name': 'Высота', 'value': '132 мм'}, {'name': 'Толщина', 'value': '42 мм'}, {'name': 'Количество занимаемых слотов', 'value': '2'}]}, {'name': 'Разъемы и интерфейсы', 'items': [{'name': 'Разъемы и интерфейсы', 'value': 'выход DisplayPort, выход HDMI, DVI-D', 'transition': {'type': 'catalog', 'params': {'glfilters': ['35324530:52026180,35358590']}}}, {'name': 'Версия DisplayPort', 'value': '1.4'}, {'name': 'Тип HDMI', 'value': '2.0b', 'transition': {'type': 'catalog', 'params': {'glfilters': ['27142431:28729069']}}}]}, {'name': 'Математический блок', 'items': [{'name': 'Версия CUDA', 'value': '6.1'}, {'name': 'Число универсальных процессоров', 'value': '1280'}, {'name': 'Число текстурных блоков', 'value': '80'}, {'name': 'Число блоков растеризации', 'value': '48'}, {'name': 'Версия DirectX', 'value': '12'}, {'name': 'Версия OpenGL', 'value': '4.5'}, {'name': 'Версия OpenCL', 'value': '1.2'}, {'name': 'Версия шейдеров', 'value': '5.0'}, {'name': 'Частота шейдерных блоков', 'value': '1518 МГц'}, {'name': 'Максимальная степень анизотропной фильтрации', 'value': '16x'}]}, {'name': 'Дополнительно', 'items': [{'name': 'Гарантийный срок', 'value': '30 дн., 30 дней от даты получения товара'}]}], 'transitionId': 'tr_17236491404324351385'
                    },
                },
                {
                    'component_name': 'Корпус Ginzzu D390, Mini Tower, без БП, боковая прозрачная панель из акрилового стекла, RGB подсветка на лицевой панели 16 режимов с возможностью отключения, 2xUSB 2.0, AU, белый',
                    'price': 3093.00,
                    'fullSpecsGrouped': {
                        'groups': [
                            {
                                'name': 'Форм-фактор и размеры', 'items': [{'name': 'Бренд', 'value': 'Ginzzu', 'transition': {'type': 'catalog', 'params': {'glfilters': ['7893318:7970377']}}}, {'name': 'Блок питания', 'value': 'отсутствует', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45129717:50205367']}}}, {'name': 'Форм-фактор материнской платы', 'value': 'Micro-ATX, Mini-ITX', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128671:51264124,51264122']}}}, {'name': 'Типоразмер корпуса', 'value': 'Midi-Tower', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128931:50197681']}}}, {'name': 'Максимальная высота процессорного кулера', 'value': '148 мм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['43992612:148~148']}}}, {'name': 'Максимальная длина видеокарты', 'value': '320 мм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['43992613:320~320']}}}, {'name': 'Ширина', 'value': '205 мм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['23679910:205~205']}}}, {'name': 'Высота', 'value': '390 мм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['14805336:390~390']}}}, {'name': 'Глубина', 'value': '405 мм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['14805523:405~405']}}}]}, {'name': 'Внешние характеристики', 'items': [{'name': 'Цвет подсветки', 'value': 'RGB'}, {'name': 'Материал корпуса', 'value': 'сталь'}]}, {'name': 'Конструкция', 'items': [{'name': 'Расположение блока питания', 'value': 'Сверху'}, {'name': 'Форм-фактор блока питания', 'value': 'ATX', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128701:50197286']}}}, {'name': 'Толщина стенок', 'value': '0.6 мм'}, {'name': 'Количество слотов расширения', 'value': '4'}, {'name': 'Число внутренних отсеков 2,5', 'value': '2', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45130631:50208977']}}}, {'name': 'Число внутренних отсеков 3,5', 'value': '2'}, {'name': 'Материал окна', 'value': 'акрил'}, {'name': 'Дополнительные опции', 'value': 'окно на боковой стенке'}]}, {'name': 'Охлаждение', 'items': [{'name': 'Число дополнительно устанавливаемых вентиляторов 80x80 мм', 'value': '1'}]}, {'name': 'Входы и выходы', 'items': [{'name': 'Интерфейсы лицевой панели', 'value': '3.5 мм jack (аудио), 3.5 мм jack (микрофон), USB 2.0 Type-A, USB 2.0 Type-A х2'}, {'name': 'Количество интерфейсов USB на лицевой панели', 'value': '2'}, {'name': 'Подробная комплектация', 'value': 'Набор крепежа, гарантийный талон, корпус'}]}, {'name': 'Дополнительно', 'items': [{'name': 'Дополнительная информация', 'value': 'возможность установки дополнительного вентилятора 80 мм на задней панели'}, {'name': 'Гарантийный срок', 'value': '1 г.'}, {'name': 'Вентиляторы в комплекте', 'value': ' Отсутствуют'}, {'name': 'Дополнительные отсеки', 'value': ' SSD-2'}, {'name': 'Лицевая панель', 'value': ' Сплошная'}, {'name': 'Название серии', 'value': ' D'}, {'name': 'Окно на боковой панели', 'value': ' Акрил'}, {'name': 'Поддержка тыловых вентиляторов', 'value': ' 1 x 80 мм'}, {'name': 'Поддержка фронтальных вентиляторов', 'value': ' 1 x 120 мм'}, {'name': 'Подсветка', 'value': ' RGB'}, {'name': 'Размеры, мм', 'value': ' 170х355х360'}, {'name': 'Тип', 'value': ' Компьютерный корпус'}, {'name': 'Фиксация боковых панелей', 'value': ' Винты'}]}], 'transitionId': 'tr_15438543092119394994'},
                },
                {
                    'component_name': 'Материнская плата Gigabyte B760M AORUS ELITE AX, RTL Socket 1700, WiFi, mATX, RTL',
                    'price': 14625.00,
                    'fullSpecsGrouped': {'groups': [{'name': 'Процессор', 'items': [{'name': 'Бренд', 'value': 'GIGABYTE', 'transition': {'type': 'catalog', 'params': {'glfilters': ['7893318:431404']}}}, {'name': 'Производитель процессора', 'value': 'Intel', 'transition': {'type': 'catalog', 'params': {'glfilters': ['35212250:35709051']}}}, {'name': 'Сокет', 'value': 'LGA1700', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45129251:50198743']}}}]}, {'name': 'Чипсет', 'items': [{'name': 'Чипсет', 'value': 'Intel B760', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45129871:50205984']}}}, {'name': 'Поддержка SLI/CrossFire', 'value': 'CrossFire'}]}, {'name': 'Память', 'items': [{'name': 'Количество слотов оперативной памяти', 'value': '4', 'transition': {'type': 'catalog', 'params': {'glfilters': ['44076031:4~4']}}}, {'name': 'Тип памяти', 'value': 'DDR5'}, {'name': 'Максимальная частота памяти', 'value': '7600 МГц', 'transition': {'type': 'catalog', 'params': {'glfilters': ['14806233:7600~7600']}}}]}, {'name': 'Слоты расширения', 'items': [{'name': 'Количество разъемов M.2', 'value': '2', 'transition': {'type': 'catalog', 'params': {'glfilters': ['44075953:2~2']}}}]}, {'name': 'Задняя панель', 'items': [{'name': 'Разъемы на задней панели', 'value': 'DisplayPort, HDMI', 'transition': {'type': 'catalog', 'params': {'glfilters': ['52353990:52354089,52354087']}}}]}, {'name': 'Внутренние разъемы', 'items': [{'name': 'Внутренние слоты и разъемы', 'value': '8 pin + 4 pin'}]}, {'name': 'Сеть', 'items': [{'name': 'Контроллер Ethernet', 'value': '2.5 Гбит/с'}, {'name': 'Чипсет Ethernet', 'value': 'Realtek RTL8125'}, {'name': 'Беспроводные интерфейсы', 'value': 'Wi-Fi 802.11ax', 'transition': {'type': 'catalog', 'params': {'glfilters': ['35363570:53327409']}}}]}, {'name': 'Аудио/видео', 'items': [{'name': 'Звук', 'value': '8-канальный кодек Realtek'}]}, {'name': 'Дополнительные параметры', 'items': [{'name': 'Поддержка RAID', 'value': 'RAID 0, RAID 1, RAID 10, RAID 5'}, {'name': 'Особенности', 'value': 'Двухканальный режим памяти'}, {'name': 'Форм-фактор', 'value': 'microATX', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128671:51264122']}}}]}, {'name': 'Дополнительно', 'items': [{'name': 'Гарантийный срок', 'value': '1 г., Гарантия 1 год'}, {'name': 'M.2 ключ E', 'value': ' Да'}, {'name': 'Аудиокодек', 'value': ' Realtek ALC897'}, {'name': 'Версия PCI Express', 'value': ' 4.0'}, {'name': 'Кол-во внутренних разъемов SATA 6 Гбит/с', 'value': ' 4'}, {'name': 'Количество PCI-E x16', 'value': ' 2'}, {'name': 'Количество разъемов питания для вентилятора', 'value': ' 8'}, {'name': 'Макс. объем RAM', 'value': ' 128 ГБ'}, {'name': 'Наличие беспроводного подключения сети', 'value': ' Да'}, {'name': 'Размеры, мм', 'value': ' 244х244'}, {'name': 'Разъем питания материнской платы', 'value': ' ATX 24 pin'}]}], 'transitionId': 'tr_1112777198653454571'},
                },
                {
                    'component_name': 'Процессор Intel Core i3-12100F OEM, LGA 1700, 4 x 3.3 ГГц, L2 - 5 МБ, L3 - 12 МБ, 2 х DDR4, DDR5-4800 МГц, TDP 89 Вт',
                    'price': 6305.00,
                    'fullSpecsGrouped': {'groups': [{'name': 'Общие характеристики', 'items': [{'name': 'Артикул Маркета', 'value': '51116155620'}, {'name': 'Бренд', 'value': 'Intel', 'transition': {'type': 'catalog', 'params': {'glfilters': ['7893318:453797']}}}, {'name': 'Вид поставки', 'value': 'OEM', 'transition': {'type': 'catalog', 'params': {'glfilters': ['37693330:38326419']}}}, {'name': 'Линейка процессоров', 'value': 'Intel Core i3', 'transition': {'type': 'catalog', 'params': {'glfilters': ['37331890:50198812']}}}, {'name': 'Сокет', 'value': 'LGA1700', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45129251:50198743']}}}, {'name': 'Назначение процессора', 'value': 'игровой, настольный ПК', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45128791:50197499,50197498']}}}, {'name': 'Дата выхода', 'value': 'Q1 2022'}]}, {'name': 'Ядро', 'items': [{'name': 'Микроархитектура', 'value': 'Alder Lake'}, {'name': 'Ядро процессора', 'value': 'Alder Lake-S', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45129732:50458615']}}}, {'name': 'Количество ядер', 'value': '4 шт.', 'transition': {'type': 'catalog', 'params': {'glfilters': ['24112630:4~4']}}}, {'name': 'Количество потоков', 'value': '8'}, {'name': 'Техпроцесс', 'value': '10 нм', 'transition': {'type': 'catalog', 'params': {'glfilters': ['45131851:50218162']}}}, {'name': 'Максимальный объем памяти', 'value': '128'}, {'name': 'Максимальное количество каналов памяти', 'value': '2 шт.'}, {'name': 'Тип памяти', 'value': 'DDR4, DDR5', 'transition': {'type': 'catalog', 'params': {'glfilters': ['37338070:38439421']}}}, {'name': 'Частота памяти', 'value': '3200/4800'}]}, {'name': 'Частота', 'items': [{'name': 'Частота процессора', 'value': '3300 МГц', 'transition': {'type': 'catalog', 'params': {'glfilters': ['34440533:3300~3300']}}}, {'name': 'Максимальная частота с Turbo Boost', 'value': '4300 МГц'}]}, {'name': 'Кэш', 'items': [{'name': 'Объем кэша L1', 'value': '320 КБ'}, {'name': 'Объем кэша L2', 'value': '0.5 МБ'}, {'name': 'Объем кэша L3', 'value': '12 МБ', 'transition': {'type': 'catalog', 'params': {'glfilters': ['43991892:12~12']}}}]}, {'name': 'Дополнительно', 'items': [{'name': 'Тепловыделение', 'value': '60 Вт', 'transition': {'type': 'catalog', 'params': {'glfilters': ['42683230:60~60']}}}, {'name': 'Максимальная рабочая температура', 'value': '100 °C'}, {'name': 'Встроенная графика', 'value': ' Intel UHD Graphics 770'}, {'name': 'Комплектация', 'value': ' оем - только процессор без кулера'}, {'name': 'Комплектация процессора', 'value': ' OEM (без кулера)'}, {'name': 'Макс. частота оперативной памяти, МГц', 'value': ' 4800'}, {'name': 'Наличие встроенной графики', 'value': ' Да'}, {'name': 'Особенности', 'value': ' Технология Turbo Boost'}]}], 'transitionId': 'tr_11703082813557362458'}
                },
                {
                    'component_type': 'operativnaia-pamiat',
                    'articul_yandex': '5292551061',
                    'fullSpecsGrouped':
                        {'groups': [{'name': 'Характеристики', 'items': [{'value': 'HyperX', 'transition': {'params': {'glfilters': ['7893318:14247010']}, 'type': 'catalog'}, 'name': 'Бренд'}, {'name': 'Линейка', 'value': 'Fury'}, {'value': 'DDR3', 'transition': {'params': {'glfilters': ['21194330:36778021']}, 'type': 'catalog'}, 'name': 'Тип'}, {'value': 'DIMM', 'transition': {'params': {'glfilters': ['45128594:50196750']}, 'type': 'catalog'}, 'name': 'Форм-фактор'}, {'value': '2 шт.', 'transition': {'params': {'glfilters': ['45129950:50206610']}, 'type': 'catalog'}, 'name': 'Количество модулей в комплекте'}, {'value': '8 ГБ', 'transition': {'params': {'glfilters': ['24892510:24892650']}, 'type': 'catalog'}, 'name': 'Объем одного модуля'}, {'value': '1866 МГц', 'transition': {'params': {'glfilters': ['27142471:28730172']}, 'type': 'catalog'}, 'name': 'Тактовая частота'}, {'name': 'Пропускная способность', 'value': 'PC14900'}, {'value': '10', 'transition': {'params': {'glfilters': ['45129494:50200124']}, 'type': 'catalog'}, 'name': 'CL'}, {'name': 'tRCD', 'value': '10'}, {'name': 'tRP', 'value': '10'}, {'name': 'tRAS', 'value': '2'}, {'name': 'Количество контактов', 'value': '240'}, {'name': 'Упаковка чипов', 'value': 'двусторонняя'}, {'value': 'XMP, игровая, радиатор', 'transition': {'params': {'glfilters': ['27140831:53316126,53316101,41924050']}, 'type': 'catalog'}, 'name': 'Особенности'}]}, {'name': 'Дополнительно', 'items': [{'name': 'Гарантийный срок', 'value': '6 мес.'}]}], 'transitionId': 'tr_746339349758020511'},
                    'component_name': 'Оперативная память для пк HyperX Fury DDR3 2 по 8 ГБ 1866 МГц 1.5V CL10 DIMM',
                    'image_url': ['https://avatars.mds.yandex.net/get-mpic/12354050/2a00000190e75245d1f541fe6a0901cb4e4b/orig'],
                    'price': '2574',
                    'url': 'https://market.yandex.ru/product--operativnaia-pamiat-dlia-pk-hyperx-fury-ddr3-2-po-8-gb-1866-mgts-1-5v-cl10-dimm/273917631?hid=90401&sku=103251969466&show-uid=17396338556334185986716004&from=search&cpa=1&do-waremd5=jdoz9XeIp4bCRurxSNQIKA&sponsored=1&cpc=Ineu5np4zhdrzIS8KJHTym5jlQ-hgzQ10R01330_QWrzsn94yqeopDRkNFtRZyLrV7MKtkaTml0M-LEI-WhOCYuZxBR5uDyba6grWVF6OU4GRX6ZKWnnnggpkh5nwp693Dmoyr2yGLewthAkhoNJgUIgHHchKR8zKYTdI70H5FxFhcx1iv1CGmHxtccCYoL7Ar8MBFIB5etx7IoiuW2b2cQ84v19le1zq9YkXp7qV40Q1_Imx2AhVRassVUyChInjD5MwieKrPLDJPSJJj_AVXhAd544jkuoN58q2e0YurnMfPEFkQLI2XuH6IHMEjt4S0lI0YbAF11wnxcBh_DnvFOBlhlaM-fys0lSPRVqEeAxJ25DPMuuFKedd9VGDnIfhgb4y2GjGqkimZ4X8Rn8GIVeFOg9WJKnEk79IAuiO2X5LQ1cBLOIiU4MhIK4vMOUDGAdejqwKT5R4UJ-351NU43hoOhXSyyjwy5C9sgKluRPkyQ_MhlMUg%2C%2C&cc=CjIxNzM5NjMzODU0ODcxL2U5NDBiZTU0MDViZDcwMThiMjc3ZjUxMTMwMmUwNjAwLzEvMRDnAYB95u0G&uniqueId=681499'
                },
                ]
        }

        return render_template('result.html', result=result)

    # @app.route('/links')
    # def get_links():
    #     # Параметры запроса
    #     page = request.args.get('page', 1, type=int)
    #     per_page = request.args.get('per_page', 20, type=int)
    #     component = request.args.get('component')
    #     is_parsed = request.args.get('is_parsed')
    #     image_url = request.args.get('image_url')
    #     price = request.args.get('price')
    #     articul_yandex = request.args.get('articul_yandex')

    #     # Базовый запрос
    #     query = Links.query

    #     # Фильтрация по компоненту
    #     if component:
    #         query = query.filter(Links.component == component)

    #     # Фильтрация по статусу парсинга
    #     if is_parsed is not None:
    #         query = query.filter(Links.is_parsed == (is_parsed.lower() == 'true'))

    #     # Пагинация
    #     pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    #     links = pagination.items

    #     # Получаем уникальные компоненты для фильтра
    #     components = db.session.query(Links.component.distinct()).all()
    #     components = [c[0] for c in components]

    #     return render_template(
    #         'links.html',
    #         links=links,
    #         pagination=pagination,
    #         components=components,
    #         image_url=image_url,
    #         price=price,
    #         articul_yandex=articul_yandex
    #         )

    # @app.route('/get_item')
    # def get_item():

    #     result = get_components_by_type_and_price("materinskaia-plata", 141, 500000)

    #     json_result = json.dumps(result, ensure_ascii=False).encode('utf-8')
    #     return Response(json_result, content_type='application/json; charset=utf-8')

    def get_components_by_type_and_price(
            component_type,
            min_price=0,
            max_price=None, 
            limit =250
            ) -> dict:
        """
        Получение компонентов определенного типа с фильтрацией и сортировкой по цене с убыванием
            {
            'component_name': 'Видеокарта KFA2 GeForce GTX 1060 EX, 6GB GDDR5, PCI-E, 6144MB, 192 Bit',
                    'component_type': "videokarty",
                    'url': "www.market.yandex/fgfdhgfd/fhhfhfd",
                    'image_url': ["https://avatars.mds.yandex.net/get-mpic/4409630/2a00000193e57d8c83efd97c8d7b1a0125a9/501x668", ""],
                    'price': 1500.00,
                    'articul_yandex': '5537064366',
                    'fullSpecsGrouped': {
                        'groups': [
                            {
                                'name': 'Графический процессор',
                                'items': [
                                    {'name': 'Бренд', 'value': 'KFA2'}
                                ]
                            }
                        ]
                    }
            }

        """
        try:

            start_time = time.time()
            # supabase = SupabaseService()
            min_price = int(min_price)
            max_price = int(max_price)
            if max_price:
                links = supabase.get_components_by_type_and_price_once(
                    component_type,
                    min_price=min_price,
                    max_price=max_price,
                    limit=limit
                    )
            else:
                links = supabase.get_components_by_type_and_price_once(
                    component_type,
                    min_price=min_price,
                    # max_price=max_price,
                    limit=limit
                    )
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Время выполнения запроса: {elapsed_time:.4f} секунд")
            # print("component_type=", component_type, " links=", links)
            return links

        except Exception as e:
            print("Ошибка при получении запроса с отбором по цене:", e)

    # @app.route('/links/<int:link_id>', methods=['DELETE'])
    # def delete_link(link_id):
    #     """
    #     Роут для удаления Links по ID
    #     """
    #     try:
    #         # Находим ссылку по ID
    #         link = Links.query.get(link_id)

    #         # Проверяем, существует ли ссылка
    #         if not link:
    #             return jsonify({
    #                 'status': 'error',
    #                 'message': f'Ссылка с ID {link_id} не найдена'
    #             }), 404

    #         # Удаляем связанные характеристики (cascade delete)

    #         # Удаляем ссылку
    #         db.session.delete(link)
    #         db.session.commit()

    #         return jsonify({
    #             'status': 'success',
    #             'message': f'Ссылка с ID {link_id} успешно удалена',
    #             'deleted_link': {
    #                 'id': link.id,
    #                 'title': link.title,
    #                 'component': link.component
    #             }
    #         }), 200

    #     except Exception as e:
    #         # Откатываем транзакцию в случае ошибки
    #         db.session.rollback()

    #         return jsonify({
    #             'status': 'error',
    #             'message': f'Ошибка при удалении ссылки: {str(e)}'
    #         }), 500

    return app


# Выбор конфигурации через переменную окружения
config_name = os.getenv('FLASK_CONFIG', 'dev')
app = create_app(config_name)


if __name__ == '__main__':
    app.run(debug=False)
