import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from supabase_service import SupabaseService
from models import Links, Characteristics
from job_get_new_link_supabase import init_driver
from flask_supabase import create_client, Client
from config import Config
from models import Links, Characteristics
import pytz


def clean_price(text: str) -> str:
    """
    из строки вида <meta content="20020" itemprop="price"/> извлекаем цену
    """
    pattern = r'content="(\d+)"'

    match = re.search(pattern, text)
    if match:
        price = match.group(1)
        return price


def change_spec_symbol(text) -> str:
    """
    Заменяем символ 3.5\" на 3.5''
    """
    # new_text = text.replace('3.5\"', "3.5''")
    new_text = text.replace('"value":"3.5""}', '"value":"3.5"}')
    new_text = text.replace('"value":"2.5""}', '"value":"2.5"}')
    return new_text


def find_json(text) -> dict:
    articul_yandex = ""
    fullSpecsGrouped = {}
    categorySlug = ""
    try:
        changed_text = change_spec_symbol(text)
        new_dict = json.loads(changed_text)
        if 'collections' in new_dict and new_dict['collections']:
            if 'minimalSpecs' in new_dict['collections'] and \
                    new_dict['collections']['minimalSpecs']:
                collections = next(iter(new_dict[
                    'collections'
                    ][
                        'minimalSpecs'
                    ].values()), None)
                if 'fullSpecsGrouped' in new_dict['collections']:
                    fullSpecsGrouped = next(iter(new_dict[
                        'collections'
                        ][
                            'fullSpecsGrouped'
                        ].values()), None)
                if 'specItems' in collections and collections['specItems'][0] \
                        and 'name' in collections['specItems'][0]:
                    articul_yandex = collections['specItems'][0]['value']
                    if 'transition' in collections['specItems'][1] and \
                            'params' in \
                            collections['specItems'][1]['transition'] and \
                            'categorySlug' in \
                            collections['specItems'][1]['transition']['params']:
                        categorySlug = collections['specItems'][1]['transition']['params']['categorySlug']

            # print()
            # print("fullSpecsGrouped=", fullSpecsGrouped)
            # print()
            # print("articul_yandex=", articul_yandex)
            parsed_dict = {
                "component_type": categorySlug,
                "articul_yandex": articul_yandex,
                "fullSpecsGrouped": fullSpecsGrouped,
                }
            return parsed_dict
    except Exception as e:
        print(f"Ошибка преобразования текста в JSON: {e}, текст: \n{text}")


def parse_card_component(driver, url) -> dict:
    """
    для данного url возвращает словарь с названием, характеристиками вида
    {
                    'component_name': 'Видеокарта KFA2 GeForce GTX 1060 EX, 6GB GDDR5, PCI-E, 6144MB, 192 Bit',
                    'component_type': "materinskie-platy",
                    'url': "",
                    'image_url': ["", ""],
                    'price': 1500.00,
                    'articul_yandex': {'value': '5537064366', 'name': 'Артикул Маркета', 'withCopyValueButton': True},
                    'fullSpecsGrouped': {
                        'groups': [
                            {
                                'name': 'Графический процессор',
                                'items': [
                                    {'name': 'Бренд', 'value': 'KFA2'},
                                    {'name': 'Комплектация', 'value': 'Retail'},
                                    {'name': 'Название видеокарты', 'value': 'GeForce GTX 1060'},
                            }
                        ]
                    }
    """
    json_text = ""
    title = ""
    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()),
    #     options=options
    #     )

    # driver = webdriver.Chrome(executable_path='path/to/chromedriver', options=options)
    try:
        # driver = webdriver.Chrome()
        driver.get(url)
        html = driver.page_source
        time.sleep(4)
        soup = BeautifulSoup(html, 'html.parser')
        if not (soup.find_all(
            string=re.compile("Нет в продаже")
            ) or
            soup.find_all
                (string=re.compile("Нет у продавца")
                 )
        ):
            items = soup.find_all('noframes', {'data-apiary': 'patch'})
            # action = ActionChains(driver)
            # action.move_by_offset(60, 500).click().perform()
            time.sleep(4)
            for item in items:
                if '{"widgets":{"@card/SpecsListNewGrid"' in str(item):
                    json_text = item.string
                    break
            try:
                component_dict = find_json(json_text)
                price_text = soup.find('meta', itemprop='price')
                price = clean_price(str(price_text))

                title = soup.find('h1', {
                    'data-additional-zone': 'title',
                    'data-auto': 'productCardTitle',
                    'class': 'ds-text ds-text_weight_med ds-text_withHyphens ds-text_typography_lead-text _3liU0 ds-text_lead-text_normal ds-text_lead-text_med'
                })
                if not title:
                    title = soup.find('h1', {
                        'data-additional-zone': 'title',
                        'data-auto': 'productCardTitle',
                        'class': 'ds-text ds-text_weight_med ds-text_withHyphens ds-text_typography_headline-5 _3liU0 ds-text_headline-5_normal ds-text_headline-5_med'
                    })
                if title:
                    component_dict["component_name"] = title.text
                else:
                    print("Заголовок компонента не найден.")
                    component_dict["component_name"] = ""

                article_element = soup.find('article', class_='_3zVgf _3Urwh _2xIXL')
                if article_element:
                    # Находим элемент <img> внутри article
                    img_element = article_element.find('img')

                    if img_element:
                        # Извлекаем путь к изображению из атрибута src
                        img_src = img_element.get('src')
                        component_dict["image_url"] = [img_src]
                    else:
                        print("Элемент <img> не найден внутри <article>.")
                        component_dict["image_url"] = [""]
                else:
                    print("Элемент <article> не найден.")
                    component_dict["image_url"] = [""]
                component_dict["price"] = price
                component_dict["url"] = url
                if component_dict["component_type"] == "":
                    if "materinskaia-plata" in url:
                        component_dict["component_type"] = "materinskaia-plata"
                    elif "videokarty" in url:
                        component_dict["component_type"] = "videokarty"
                    elif "protsessory-cpu" in url:
                        component_dict["component_type"] = "protsessory-cpu"
                    elif "vnutrennie-tverdotelnye-nakopiteli-ssd" in url:
                        component_dict["component_type"] = "vnutrennie-tverdotelnye-nakopiteli-ssd"
                    elif "moduli-pamiati" in url:
                        component_dict["component_type"] = "moduli-pamiati"
                    elif "vnutrennie-zhestkie-diski" in url:
                        component_dict["component_type"] = "vnutrennie-zhestkie-diski"
                    elif "kompiuternye-korpusa" in url:
                        component_dict["component_type"] = "kompiuternye-korpusa"
                    elif "bloki-pitaniia-dlia-kompiuterov" in url:
                        component_dict["component_type"] = "bloki-pitaniia-dlia-kompiuterov"
                    elif "kulery-i-sistemy-okhlazhdeniia-dlia-kompiuterov" in url:
                        component_dict["component_type"] = "kulery-i-sistemy-okhlazhdeniia-dlia-kompiuterov"
                    elif "zvukovye-karty" in url:
                        component_dict["component_type"] = "zvukovye-karty"

                if component_dict["component_type"] == "materinskie-platy":
                    component_dict["component_type"] = "materinskaia-plata"

                # print("component_dict=", component_dict)
                # driver.quit()
            # if price != "" and title != "" and component_dict['fullSpecsGrouped']:
                return component_dict
            # else:
            except Exception as e:
                print(f"Ошибка ", e)
                print("Не все данные удалось спарсить на странице url=", url)
                return {'error': f"Не все данные удалось спарсить на странице url=url"}
                return None
        else:
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nНет в продаже\nurl={url}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    except Exception as e:
        print(f"Ошибка при парсинге страницы\n{url}\n", e)
        # driver.quit()


def get_unparsed_links_param(driver, limit: int = 100):
    """
    Получение неразобранных актуальных ссылок

    :param limit: максимальное количество ссылок для выборки
    :return: список неразобранных ссылок
    """
    try:
        supabase_service = SupabaseService()
        count_successfully = 0
        count_unsuccessfully = 0
        # Находим все неспарсенные ссылки
        unparsed_links = supabase_service.get_unparsed_links_sorted(limit=limit)
        # Links.query.filter(
        #     # Links.title.like("%Корпус%"),
        #     Links.is_parsed == False,
        #     Links.is_actual == True
        # ).limit(100).all()

        # Список для результатов
        parsed_results = []

        # Перебираем неспарсенные ссылки
        for link_obj in unparsed_links:
            try:
                # Парсим карточку компонента
                parsed_data = parse_card_component(driver, link_obj['link'])
                try:
                    if parsed_data and 'component_name' in parsed_data and parsed_data['component_name'] != "" and parsed_data['price']:
                        # Обновляем ссылку
                        link_data = Links(
                            link=parsed_data['url'],
                            title=parsed_data['component_name'],
                            component=parsed_data['component_type'],
                            image_url=parsed_data['image_url'][0] if parsed_data['image_url'] else None,
                            price=int(parsed_data['price']),
                            articul_yandex=parsed_data['articul_yandex'],
                            is_parsed=True,
                            is_actual=True,
                        )
                        # link_obj.date_parse = datetime.utcnow()
                        insert_link = supabase_service.insert_or_update_link(link_data)

                        # Сохраняем характеристики с проверкой на уникальность
                        for group in parsed_data['fullSpecsGrouped']['groups']:
                            for item in group['items']:
                                # # Проверяем, существует ли уже такая характеристика
                                # existing_characteristic = Characteristics.query.filter_by(
                                #     link_id=link_obj.id,
                                #     group=group['name'],
                                #     name=item['name']
                                # ).first()
                                supabase_service.insert_or_update_characteristics(
                                    Characteristics(
                                        link_id=insert_link['id'],
                                        group=group['name'],
                                        name=item['name'],
                                        value=item['value']
                                    )
                                )

                        # Добавляем результат
                        parsed_results.append({
                            'link': link_obj['link'],
                            'status': 'Parsed successfully'
                        })
                        count_successfully += 1
                        print('Parsed successfully:', count_successfully, " Parsed unsuccessfully:", count_unsuccessfully)
                    else:
                        # if 'error' in parsed_data:
                        # link_obj.is_actual = False
                        # Обновляем ссылку is_actual=False
                        link_data = Links(
                            link=link_obj['link'],
                            title=link_obj['title'],
                            is_parsed=False,
                            is_actual=False,
                        )
                        # link_obj.date_parse = datetime.utcnow()
                        insert_link = supabase_service.insert_or_update_link(link_data)
                        parsed_results.append({
                            'link': link_obj['link'],
                            'status': 'Parsing failed'
                        })
                        count_unsuccessfully += 1
                        print('Parsed successfully:', count_successfully, " Parsed unsuccessfully:", count_unsuccessfully)
                        # else:
                        #     parsed_results.append({
                        #         'link': link_obj['link'],
                        #         'status': 'Parsing failed'
                        #     })
                        #     count += 1
                        #     print('Parsing one page failed', count)
                except Exception as e:
                    print("Ошибка при парсинге карточки", e)
            except Exception as link_parse_error:
                print(f"Ошибка при парсинге ссылки {link_obj.link}: {link_parse_error}")
                parsed_results.append({
                    'link': link_obj['link'],
                    'status': 'Error during parsing',
                    'error': str(link_parse_error)
                })

    except Exception as e:
        print('Parsing failed', e)
        return {
            'error': str(e),
            'status': 'Parsing failed'
        }
    return {
        'total_parsed': len(parsed_results),
        'results': parsed_results
    }


if __name__ == "__main__":
    url = 'https://market.yandex.ru/product--arturia-minifuse-1-black-zvukovaia-karta/892852822?sku=103671161771&uniqueId=82703763&do-waremd5=C6YUSoCLj81Jre4GRHaKoQ&sponsored=1&cpc=325ZcYO_vjRiiXwJ5MTu0Jzl7I0r0CPH2Jze3cnEBEAnfx2ni5Fp2eOQV1Cow0v8VHKz9KZHq3HsP0P93lkAo5W1zPmlFh1PAozcTPToyHlkZo3OeW71AEU2u_iudX9m4NwNCZhBaHX9dfudYqZOYktNezUoPnxCfzeU8jvO2Zymtsylg_wMUqysc8fTQ0ZM2cBvWvtxWRTNxHI5LQr_IWK4v40yyqRJfCjJHWa8839ku9e9VcKJEC1KPpbZI5JnOna9K3hB6rEMpvfng7m1oRGM3_K0Wld-t1Bdl9zGMlbFJki7f_GYAsFdHhqXa9Og4Yx2OWPUSdGk7a7g_FtUIkzUjxV73ND736Tv__H9i8oLW_fm12n-IIu8PwTXirfPxxud7WjPK_Z9_YlN7n4uoeuUi8Z7JMoJ9I5obAFNHJfMLOLGhFLia3B0kHgQ0P2fZjIks5ZomQIklp9P50KePyY1v1nEkkugvmiHu37kG9dv3Xv6_H_CiIoFjaWnA1lc&nid=26912870'
    url2 = 'https://market.yandex.ru/product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/762813300?sku=103565245584&uniqueId=833949&do-waremd5=ZXXFBGZLSwihSchXNc3zhA&sponsored=1&cpc=jUD-3oBzPEL8hobEMupkL9VjxJQAtnocAI1KTB1JX_g-SKcKxIN3Z5Q_2Xl16gyahEBlwTxL-vpeIz8vp8lrfmIWY-dmvL5qqTCMs6hPvZbdAajJF6vh2d9-RLJo9_26Tuc5ZmJmC8nfclO2HmMioXeMcHPXTzgEu4kvjQGkIFIw-ayaJrGYjIN6yhA0XfgqsuTHBGdKbMg_1zG8XEGGah7YJwSzr4s8hnM8yI8k3DSNJthVtgk4xi92W8UmqVmEUugvaC-6xs30aRvztz1e3vR8ISOJwrYjkdvl_drpfAebkjxnE1yz372o_aJHWoPxVxEOseBuUXqBE4KAPw9BXAy8g2WCTtTyBTaGjcpLOj_YdSL2NK-djJXL93Wa-pVHogepkBZUJEp7tQugtpIWI5qftm0tUzdL42xM9HRRKCkKPDz06C-1bkscRznCBj6I8yo0sKXPRcNfUF9CB0iYv5JBzZEEjJ7-Kq7JOv670M7a9wjxwdxfzQaVfaHcCZrN&nid=26912770'
    url3 = 'https://market.yandex.ru/product--operativnaia-pamiat-dlia-pk-hyperx-fury-ddr3-2-po-8-gb-1866-mgts-1-5v-cl10-dimm/273917631?hid=90401&sku=103251969466&show-uid=17396338556334185986716004&from=search&cpa=1&do-waremd5=jdoz9XeIp4bCRurxSNQIKA&sponsored=1&cpc=Ineu5np4zhdrzIS8KJHTym5jlQ-hgzQ10R01330_QWrzsn94yqeopDRkNFtRZyLrV7MKtkaTml0M-LEI-WhOCYuZxBR5uDyba6grWVF6OU4GRX6ZKWnnnggpkh5nwp693Dmoyr2yGLewthAkhoNJgUIgHHchKR8zKYTdI70H5FxFhcx1iv1CGmHxtccCYoL7Ar8MBFIB5etx7IoiuW2b2cQ84v19le1zq9YkXp7qV40Q1_Imx2AhVRassVUyChInjD5MwieKrPLDJPSJJj_AVXhAd544jkuoN58q2e0YurnMfPEFkQLI2XuH6IHMEjt4S0lI0YbAF11wnxcBh_DnvFOBlhlaM-fys0lSPRVqEeAxJ25DPMuuFKedd9VGDnIfhgb4y2GjGqkimZ4X8Rn8GIVeFOg9WJKnEk79IAuiO2X5LQ1cBLOIiU4MhIK4vMOUDGAdejqwKT5R4UJ-351NU43hoOhXSyyjwy5C9sgKluRPkyQ_MhlMUg%2C%2C&cc=CjIxNzM5NjMzODU0ODcxL2U5NDBiZTU0MDViZDcwMThiMjc3ZjUxMTMwMmUwNjAwLzEvMRDnAYB95u0G&uniqueId=681499'
    url = 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/896261145?hid=90401&sku=103674681358&show-uid=17397231487408394058616001&from-show-uid=17397231487408394058616001&cpa=1&do-waremd5=pPVcukcbSnqTz20f3ba1Rw&cpc=CXSMTylTSEjkPmiAn75abHzJjx5bsWB1_zwb_AnBzPekS9W8h3H2NDDSkDydcyD5QgYAJXSDJgzJqjAKYIJSIoCktXjA5VPnByrAY9pWPXtBTfFktWxEvavYscagpZ60YLg6ZgONMAAYMa4IzRkEgUv7Tkjvf6FTRbw7oy4bYnJuI5ApSEAk60OKkcjTAvlMqVVFDprSiLXo1Po3-n7d-BEV_aLlIqbukim_ycInpKA%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'
    url5 = 'https://market.yandex.ru/product--videokarta-asrock-amd-radeon-rx-6600-rx6600-clw-8g-8gb-challenger-gddr6-ret/868847027?hid=90401&sku=103645773421&show-uid=17403379099447944617516055&nid=26912670&from=search&cpa=1&do-waremd5=oyQmj2woj2c9qqF4aRygWw&cpc=-evkrX81I5b7TVk0PMiuTsMVt6mqLjJtJqQFpyAlBHSMM6TUQQiupOe2_dRDklreMCeYMBc71Gqk_MpuKl1p_bXyKzJKcetDgkuMUiFP99SDf0MjZhuT-kCbTqkBfpUoVQbFdyXlG28MbngCn44znMIYNWzPIAXBr29af1FXwC2UomWn7PUVeHNAUhTMnVAtHeMUZIIHuo5xaipeayEyxVNjTU6qBII7JywmyAlQdgtiDS3UaIUM6euQFy1k-vYA9o0HCW9TfO1srK44ts0ZC4EmLQUUBmvxHjlSnd6PZ-ZeBp7e4X9sk2PhLH5SNsvXhExk7T4Hhqe9CtG7hyYcPK98obwtGAQhhPTXRqqYrrGhT-NHXMO_wLOD--6Kip2g8JKSzzdXATfmQZfocH5JLhYE_cs-VeMLystVjDQUo2qm7_VS6Gt9bJsp4z0ZGqrV2pO68nBfFEU70mgkBZo06w%2C%2C&cc=CgAQB4B95u0G&uniqueId=858299'
    driver = init_driver()

    # parse_card_component(url)
    get_unparsed_links_param(driver, 500)
    driver.quit()
