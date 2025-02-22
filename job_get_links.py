import copy
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from dotenv import load_dotenv
# from pickle import NEWOBJ_EX
# import json
# import re
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver import Chrome
# from selenium.webdriver.common.proxy import Proxy, ProxyType


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
URL_LOGIN = os.getenv("URL_LOGIN")


URL = [
    ("Материнские платы",
     "https://market.yandex.ru/catalog--materinskie-platy/26912770/list?hid=91020&rs=eJwzYgAAAGYAMw%2C%2C&allowCollapsing=1&local-offers-first=0",
     "materinskie-platy"),
    ("Видеокарты",
     "https://market.yandex.ru/catalog--videokarty/26912670/list?hid=91031&rs=eJwzYgAAAGYAMw%2C%2C&allowCollapsing=1&local-offers-first=0",
     "videokarty"),
    ("Процессоры (CPU)",
     "https://market.yandex.ru/catalog--protsessory-cpu/26912730/list?hid=91019&allowCollapsing=1&local-offers-first=0",
     "protsessory-cpu"),
    ("Внутренние твердотельные накопители (SSD)",
     "https://market.yandex.ru/catalog--vnutrennie-tverdotelnye-nakopiteli-ssd/26912750/list?hid=16309373&rs=eJwzYgAAAGYAMw%2C%2C&allowCollapsing=1&local-offers-first=0",
     "vnutrennie-tverdotelnye-nakopiteli-ssd"),
    ("Модули памяти",
     "https://market.yandex.ru/catalog--moduli-pamiati/26912790/list?hid=191211&rs=eJwzYgAAAGYAMw%2C%2C&allowCollapsing=1&local-offers-first=0",
     "moduli-pamiati"),
    ("Внутренние жесткие диски",
     "https://market.yandex.ru/catalog--vnutrennie-zhestkie-diski/55316/list?hid=91033&allowCollapsing=1&local-offers-first=0",
     "vnutrennie-zhestkie-diski"),
    ("Корпуса",
     "https://market.yandex.ru/catalog--kompiuternye-korpusa/55319/list?hid=91028&allowCollapsing=1&local-offers-first=0",
     "kompiuternye-korpusa"),
    ("Блоки питания",
     "https://market.yandex.ru/catalog--bloki-pitaniia-dlia-kompiuterov/26912850/list?hid=857707&allowCollapsing=1&local-offers-first=0",
     "bloki-pitaniia-dlia-kompiuterov"),
    ("Кулеры и системы охлаждения",
     "https://market.yandex.ru/catalog--kulery-i-sistemy-okhlazhdeniia-dlia-kompiuterov/26912910/list?hid=818965&rs=eJwzYgAAAGYAMw%2C%2C&allowCollapsing=1&local-offers-first=0",
     "kulery-i-sistemy-okhlazhdeniia-dlia-kompiuterov"),
]

# ("Звуковые карты",
#      "https://market.yandex.ru/catalog--zvukovye-karty/55317/list?hid=91027&rs=eJwdUCurQkEY3KNJ_AWCwpoNos0XHE3CRRAxXuEk8T9YDj7AICabZbMoaLD4wHODiE0QwwXBgyI2g3AV292ZMgwz3zfz7cYb3qKxMYSoZjRa5ZRG55bWaF4WGu1jUqPbg-I84YoRdNMm_4EuOkAVXGK-wK07FHcCbs3pRuCqPpUjuPwCihJ6zTBzWnDllvMzoP2dQM6H90yB1h963foafAdXxrhbYeMQmWaemW_qPnDZBKo0bzDoRtGlunxvm10v9h740jHdAXv3_IER-S8nT9iyrrxHUg-toOfY6GG-n5OKaQEmn_k_Nmey4M6DLbXUP1YoiHA%2C&allowCollapsing=1&local-offers-first=0",
#      "zvukovye-karty"),
#     ("Видеозахват",
#      "https://market.yandex.ru/catalog--videozakhvat/26912950/list?hid=17444162",
#      "videozakhvat"),
#     ("Платы ввода-вывода",
#      "https://market.yandex.ru/catalog--platy-vvoda-vyvoda/26912990/list?hid=91030",
#      "platy-vvoda-vyvoda"),
#     ("Корпуса и док-станции для накопителей",
#      "https://market.yandex.ru/catalog--korpusa-i-dok-stantsii-dlia-nakopitelei/26913010/list?hid=6374360",
#      "korpusa-i-dok-stantsii-dlia-nakopitelei"),
#     ("Оптические приводы",
#      "https://market.yandex.ru/catalog--opticheskie-privody/26913030/list?hid=91035",
#      "opticheskie-privody"),
#     ("Рэковые корпуса",
#      "https://market.yandex.ru/catalog--rekovye-korpusa/26913050/list?hid=7683962",
#      "rekovye-korpusa"),
#     ("Термопаста",
#      "https://market.yandex.ru/catalog--termopasta/26913070/list?hid=7969496",
#      "termopasta"),
#     ("Накопители FDD, MOD, ZIP, Jazz, стримеры",
#      "https://market.yandex.ru/catalog--nakopiteli-fdd-mod-zip-jazz-strimery/26914251/list?hid=857712",
#      "nakopiteli-fdd-mod-zip-jazz-strimery"),


def init_driver():
    chrome_options = webdriver.ChromeOptions()

    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)
    # chrome_options.add_argument(f'--user-agent={user_agent}')

    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0')
    # chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def first_login(driver):
    url = URL_LOGIN
    driver.get(url)

    # action = ActionChains(driver)
    # action.move_by_offset(2300, 300).click().perform()
    # time.sleep(300000)

    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    login_field = soup.find_all('div')  #, data-auto='snippet-link')

    # <input type="text" data-t="field:input-login" dir="ltr" aria-invalid="false" autocorrect="off" autocapitalize="off" autocomplete="username" class="Textinput-Control"
    # id="passp-field-login" name="login" placeholder="Логин или email" value="">
    # Ожидание загрузки элемента
    try:
        login_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "passp-field-login"))
        )
        # Ввод текста в поле логина
        login_field.send_keys(LOGIN)
        print("Элемент login найден")
    except:
        print("Элемент login не найден")
    time.sleep(1)
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "passp:sign-in"))
        )
        button.click()
        print("Кнопка ВОЙТИ найдена и кликабельна")
    except:
        print("Кнопка ВОЙТИ не найдена или не кликабельна")

    time.sleep(1)
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".PasswordButton"))
        )
        button.click()
        print("Кнопка PasswordButton найдена и кликабельна")
    except:
        print("Кнопка PasswordButton не найдена или не кликабельна")
    time.sleep(1)
     # Ожидание загрузки элемента
    # try:
    #     password_field = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.ID, "password-toggle"))
    #     )
    #     # Ввод текста в поле пароля
    #     password_field.send_keys(PASSWORD)
    #     print("Элемент password найден")
    # except:
    try:
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "passp-field-passwd"))
        )
        # Ввод текста в поле пароля
        password_field.send_keys(PASSWORD)
        print("Элемент password найден 2 попытка")
    except:
        print("Элемент password не найден со 2 попытки")
        # print("Элемент password не найден")
    time.sleep(1)

    try:
        # Явное ожидание, пока кнопка станет кликабельной
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "passp:sign-in"))
        )
        button.click()
        print("Кнопка 'Продолжить' нажата успешно.")
    except Exception as e:
        print(f"Ошибка при нажатии на кнопку Продолжить: {e}")
    time.sleep(5)

    return driver


def get_links(driver):
    count = 0

    parts = {}
    URL_REVERSE = URL[::-1]
    for url_for_pasrsing in URL_REVERSE[:9]:
        component = url_for_pasrsing[2]
        list_components = []
        # url = f"https://market.yandex.ru/search?text={component}"
        url = url_for_pasrsing[1]

        print("component=", component, " url_for_pasrsing=", url)
        # print("url=", url)

        driver.get(url)
        # try:
        #     element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'min')]"))
        #     )
        #     element.clear()
        #     element.send_keys('100')
        #     element = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'max')]"))
        #     )
        #     element.clear()
        #     element.send_keys('3500')
        # except:
        #     print("Не сработало указание цены")
        #     driver.save_screenshot("screenshot.png")
        # time.sleep(60)
        # action = ActionChains(driver)
        # action.move_by_offset(100, 300).click().perform()
        time.sleep(30)

        # Задаем количество прокруток
        scroll_count = 30
        scroll_distance = 500  # Расстояние прокрутки в пикселях

        for i in range(scroll_count):
            # Прокручиваем вниз
            driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

            # Ждем некоторое время, чтобы страница успела загрузить новые элементы
            time.sleep(3)

            # Теперь собираем ссылки

        html = driver.page_source
        time.sleep(5)
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('a') #, data-auto='snippet-link')
        time.sleep(5)
        for item in items:
            if item:
                title = item.find('span', {'data-auto': 'snippet-title'})
                link = None
                if "product--" in item['href']:
                    link = "https://market.yandex.ru/" + item['href']
                    # print("link=", link)
                if link and title:
                    list_components.append(
                        {
                            "title": title.text,
                            "link": link,
                        }
                            )
                    #print(f'Title: {title.text}, Link: https://market.yandex.ru/{link}')
                    count += 1
                    # print("count=", count)
            if not items:
                print("Первый шаблон поиска не сработал, пробуем второй.")
                try:
                    selector = "cia-cs _1yYdn"
                    elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((
                            By.CSS_SELECTOR, selector
                            ))
                    )
                    items = [element.find_element(By.TAG_NAME, "a").get_attribute("href") for element in elements if element.find_elements(By.TAG_NAME, "a")]

                except Exception as e:
                    print("Элементы не найдены. Ошибка ", e)
                for item in items:
                    if item:
                        title = item.find('span', {'data-auto': 'snippet-title'})
                        link = None
                        if "product--" in item['href']:
                            link = "https://market.yandex.ru/" + item['href']
                        if link and title:
                            list_components.append(
                                {
                                    "title": title.text,
                                    "link": link,
                                }
                                    )
                            #print(f'Title: {title.text}, Link: https://market.yandex.ru/{link}')
                            count += 1
                            # print("count=", count)
            print("Найдено", count, "элементов", component)
            parts[component] = copy.deepcopy(list_components)
            # print("parts=", parts)
    return parts


def parse_first_links():
    driver = init_driver()
    driver = first_login(driver)
    parts = get_links(driver)
    driver.quit()
    return parts


if __name__ == "__main__":
    parse_first_links()
