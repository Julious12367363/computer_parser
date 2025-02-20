import json
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


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
    new_text = text.replace('3.5\"', "3.5''")
    return new_text


def find_json(text) -> dict:
    articul_yandex = ""
    fullSpecsGrouped = {}
    categorySlug = ""
    try:
        new_dict = json.loads(change_spec_symbol(text))
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


def parse_card_component(url) -> dict:
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
        driver = webdriver.Chrome()
        driver.get(url)
        html = driver.page_source
        time.sleep(5)
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
            time.sleep(5)
            for item in items:
                if '{"widgets":{"@card/SpecsListNewGrid"' in str(item):
                    json_text = item.string
                    break

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
                    print(f"Путь к изображению: {img_src}")
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

            print("component_dict=", component_dict)
            driver.quit()
        # if price != "" and title != "" and component_dict['fullSpecsGrouped']:
            return component_dict
        # else:
        else:
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nНет в продаже\nurl={url}\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Не все данные удалось спарсить на странице url=", url)
            return {'error': f"Не все данные удалось спарсить на странице url=url"}
    except Exception as e:
        print(f"Ошибка при парсинге страницы\n{url}\n", e)
        driver.quit()


if __name__ == "__main__":
    url = 'https://market.yandex.ru/product--arturia-minifuse-1-black-zvukovaia-karta/892852822?sku=103671161771&uniqueId=82703763&do-waremd5=C6YUSoCLj81Jre4GRHaKoQ&sponsored=1&cpc=325ZcYO_vjRiiXwJ5MTu0Jzl7I0r0CPH2Jze3cnEBEAnfx2ni5Fp2eOQV1Cow0v8VHKz9KZHq3HsP0P93lkAo5W1zPmlFh1PAozcTPToyHlkZo3OeW71AEU2u_iudX9m4NwNCZhBaHX9dfudYqZOYktNezUoPnxCfzeU8jvO2Zymtsylg_wMUqysc8fTQ0ZM2cBvWvtxWRTNxHI5LQr_IWK4v40yyqRJfCjJHWa8839ku9e9VcKJEC1KPpbZI5JnOna9K3hB6rEMpvfng7m1oRGM3_K0Wld-t1Bdl9zGMlbFJki7f_GYAsFdHhqXa9Og4Yx2OWPUSdGk7a7g_FtUIkzUjxV73ND736Tv__H9i8oLW_fm12n-IIu8PwTXirfPxxud7WjPK_Z9_YlN7n4uoeuUi8Z7JMoJ9I5obAFNHJfMLOLGhFLia3B0kHgQ0P2fZjIks5ZomQIklp9P50KePyY1v1nEkkugvmiHu37kG9dv3Xv6_H_CiIoFjaWnA1lc&nid=26912870'
    url2 = 'https://market.yandex.ru/product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/762813300?sku=103565245584&uniqueId=833949&do-waremd5=ZXXFBGZLSwihSchXNc3zhA&sponsored=1&cpc=jUD-3oBzPEL8hobEMupkL9VjxJQAtnocAI1KTB1JX_g-SKcKxIN3Z5Q_2Xl16gyahEBlwTxL-vpeIz8vp8lrfmIWY-dmvL5qqTCMs6hPvZbdAajJF6vh2d9-RLJo9_26Tuc5ZmJmC8nfclO2HmMioXeMcHPXTzgEu4kvjQGkIFIw-ayaJrGYjIN6yhA0XfgqsuTHBGdKbMg_1zG8XEGGah7YJwSzr4s8hnM8yI8k3DSNJthVtgk4xi92W8UmqVmEUugvaC-6xs30aRvztz1e3vR8ISOJwrYjkdvl_drpfAebkjxnE1yz372o_aJHWoPxVxEOseBuUXqBE4KAPw9BXAy8g2WCTtTyBTaGjcpLOj_YdSL2NK-djJXL93Wa-pVHogepkBZUJEp7tQugtpIWI5qftm0tUzdL42xM9HRRKCkKPDz06C-1bkscRznCBj6I8yo0sKXPRcNfUF9CB0iYv5JBzZEEjJ7-Kq7JOv670M7a9wjxwdxfzQaVfaHcCZrN&nid=26912770'
    url3 = 'https://market.yandex.ru/product--operativnaia-pamiat-dlia-pk-hyperx-fury-ddr3-2-po-8-gb-1866-mgts-1-5v-cl10-dimm/273917631?hid=90401&sku=103251969466&show-uid=17396338556334185986716004&from=search&cpa=1&do-waremd5=jdoz9XeIp4bCRurxSNQIKA&sponsored=1&cpc=Ineu5np4zhdrzIS8KJHTym5jlQ-hgzQ10R01330_QWrzsn94yqeopDRkNFtRZyLrV7MKtkaTml0M-LEI-WhOCYuZxBR5uDyba6grWVF6OU4GRX6ZKWnnnggpkh5nwp693Dmoyr2yGLewthAkhoNJgUIgHHchKR8zKYTdI70H5FxFhcx1iv1CGmHxtccCYoL7Ar8MBFIB5etx7IoiuW2b2cQ84v19le1zq9YkXp7qV40Q1_Imx2AhVRassVUyChInjD5MwieKrPLDJPSJJj_AVXhAd544jkuoN58q2e0YurnMfPEFkQLI2XuH6IHMEjt4S0lI0YbAF11wnxcBh_DnvFOBlhlaM-fys0lSPRVqEeAxJ25DPMuuFKedd9VGDnIfhgb4y2GjGqkimZ4X8Rn8GIVeFOg9WJKnEk79IAuiO2X5LQ1cBLOIiU4MhIK4vMOUDGAdejqwKT5R4UJ-351NU43hoOhXSyyjwy5C9sgKluRPkyQ_MhlMUg%2C%2C&cc=CjIxNzM5NjMzODU0ODcxL2U5NDBiZTU0MDViZDcwMThiMjc3ZjUxMTMwMmUwNjAwLzEvMRDnAYB95u0G&uniqueId=681499'
    url = 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/896261145?hid=90401&sku=103674681358&show-uid=17397231487408394058616001&from-show-uid=17397231487408394058616001&cpa=1&do-waremd5=pPVcukcbSnqTz20f3ba1Rw&cpc=CXSMTylTSEjkPmiAn75abHzJjx5bsWB1_zwb_AnBzPekS9W8h3H2NDDSkDydcyD5QgYAJXSDJgzJqjAKYIJSIoCktXjA5VPnByrAY9pWPXtBTfFktWxEvavYscagpZ60YLg6ZgONMAAYMa4IzRkEgUv7Tkjvf6FTRbw7oy4bYnJuI5ApSEAk60OKkcjTAvlMqVVFDprSiLXo1Po3-n7d-BEV_aLlIqbukim_ycInpKA%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'
    parse_card_component(url)
