import copy
import os
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
from supabase_service import SupabaseService
from models import Links, Characteristics

'''
<a data-t="button:pseudo:passp:exp-register" id="passp:exp-register" aria-expanded="true" aria-haspopup="true" href="https://passport.yandex.ru/registration?retpath=https%3A%2F%2Fsso.passport.yandex.ru%2Fprepare%3Fuuid%3D11a1612d-0db8-4975-9e1d-e35f9d694dc2%26goal%3Dhttps%253A%252F%252Fya.ru%252F%26finish%3Dhttps%253A%252F%252Fid.yandex.ru%252F&amp;process_uuid=58718bfa-ec91-4905-8e0d-e55bbd1623cf" class="Button2 Button2_type_link Button2_size_xxl Button2_view_contrast-pseudo Button2_width_max"><span class="Button2-Text">Ещё</span></a>
<button class="RegistrationButtonPopup-itemButton" type="button">Войти по&nbsp;логину</button>
'''

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
    ("Звуковые карты",
     "https://market.yandex.ru/catalog--zvukovye-karty/55317/list?hid=91027&rs=eJwdUCurQkEY3KNJ_AWCwpoNos0XHE3CRRAxXuEk8T9YDj7AICabZbMoaLD4wHODiE0QwwXBgyI2g3AV292ZMgwz3zfz7cYb3qKxMYSoZjRa5ZRG55bWaF4WGu1jUqPbg-I84YoRdNMm_4EuOkAVXGK-wK07FHcCbs3pRuCqPpUjuPwCihJ6zTBzWnDllvMzoP2dQM6H90yB1h963foafAdXxrhbYeMQmWaemW_qPnDZBKo0bzDoRtGlunxvm10v9h740jHdAXv3_IER-S8nT9iyrrxHUg-toOfY6GG-n5OKaQEmn_k_Nmey4M6DLbXUP1YoiHA%2C&allowCollapsing=1&local-offers-first=0",
     "zvukovye-karty"),
    ("Видеозахват",
     "https://market.yandex.ru/catalog--videozakhvat/26912950/list?hid=17444162",
     "videozakhvat"),
    ("Платы ввода-вывода",
     "https://market.yandex.ru/catalog--platy-vvoda-vyvoda/26912990/list?hid=91030",
     "platy-vvoda-vyvoda"),
    ("Корпуса и док-станции для накопителей",
     "https://market.yandex.ru/catalog--korpusa-i-dok-stantsii-dlia-nakopitelei/26913010/list?hid=6374360",
     "korpusa-i-dok-stantsii-dlia-nakopitelei"),
    ("Оптические приводы",
     "https://market.yandex.ru/catalog--opticheskie-privody/26913030/list?hid=91035",
     "opticheskie-privody"),
    ("Рэковые корпуса",
     "https://market.yandex.ru/catalog--rekovye-korpusa/26913050/list?hid=7683962",
     "rekovye-korpusa"),
    ("Термопаста",
     "https://market.yandex.ru/catalog--termopasta/26913070/list?hid=7969496",
     "termopasta"),
    ("Накопители FDD, MOD, ZIP, Jazz, стримеры",
     "https://market.yandex.ru/catalog--nakopiteli-fdd-mod-zip-jazz-strimery/26914251/list?hid=857712",
     "nakopiteli-fdd-mod-zip-jazz-strimery"),
]


def init_driver():
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0')
    # chrome_options.add_argument(f'--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Mobile/15E148 Safari/604.1')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_cookies(driver):
    # Загружаем куки для повторного входа
    # driver = webdriver.Chrome()
    driver.get('https://market.yandex.ru/')
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
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

    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'Button2') and contains(., 'Ещё')]")))
    element.click()
    WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Войти по')]")))
    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти по')]")
    login_button.click()

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
    for url_for_pasrsing in URL[:9]:
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
        items = soup.find_all('a')  #, data-auto='snippet-link')
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
                    # print(f'Title: {title.text}, Link: https://market.yandex.ru/{link}')
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
            parts[component] = copy.deepcopy(list_components)
        print("Найдено", count, "элементов", component)
        # cookies = driver.get_cookies()
        # with open('cookies.json', 'w') as file:
        #     json.dump(cookies, file)

        # print("parts=", parts)
    return parts


def parse_first_links():
    driver = init_driver()
    driver = first_login(driver)
    # driver = get_cookies(driver)
    time.sleep(20)
    parts = get_links(driver)
    driver.quit()
    return parts


def find_new_links():
    try:
        parts = parse_first_links()
        # parts = {'materinskaia-plata': [{'title': 'Материнская плата Gigabyte X870E AORUS ELITE WIFI7, AM5, AMD X870E, ATX, RTL (X870E AORUS ELITE WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/896261145?hid=90401&sku=103674681358&show-uid=17397231487408394058616001&from-show-uid=17397231487408394058616001&cpa=1&do-waremd5=pPVcukcbSnqTz20f3ba1Rw&cpc=CXSMTylTSEjkPmiAn75abHzJjx5bsWB1_zwb_AnBzPekS9W8h3H2NDDSkDydcyD5QgYAJXSDJgzJqjAKYIJSIoCktXjA5VPnByrAY9pWPXtBTfFktWxEvavYscagpZ60YLg6ZgONMAAYMa4IzRkEgUv7Tkjvf6FTRbw7oy4bYnJuI5ApSEAk60OKkcjTAvlMqVVFDprSiLXo1Po3-n7d-BEV_aLlIqbukim_ycInpKA%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}]}
        #, {'title': 'Материнская плата Gigabyte X870E AORUS PRO, AM5, AMD X870E, ATX, RTL (X870E AORUS PRO)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-pro-rtl/865839269?hid=90401&sku=103642422487&show-uid=17397231487408394058616002&from-show-uid=17397231487408394058616002&cpa=1&do-waremd5=ZfceagZG-XUxgsFDiUwZPg&cpc=CXSMTylTSEiFuPxIOnwlYDZ1HTJEBJmJ3aE7LYYvsjFKUdbR68OAPzb4RlVNJtq4Ag51rUaTrTAm99DZSswhVarWJuGsGfikbsyUFx0p67nDf21JcwahNH5_YRhgigIrvjsuC2QIC1LACfZqSiuQZV9sCYIBDjWX4BHylCMKBTHuVdbXeFI-9YLAUd41cVMruQb0obiM00ePlf4agXqZsXBCbXPBBQUVwaWNLmOgsIs%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE WIFI7, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-wifi7-rtl/860729485?hid=90401&sku=103638107353&show-uid=17397231487408394058616003&from-show-uid=17397231487408394058616003&cpa=1&do-waremd5=1waB_dchmRaJvVgagFUOlw&cpc=CXSMTylTSEiTJdFT11lkQyrY47jLk2TYUwPHmM0Zq-frNGRH1syqX0Wyk8k5cxK2vxemjwZHjML9jLKbfbT3nfHEVUJyEM6NbyQH_T7sUAjAVSXY6cBB2mSkCG8u97eT7a_W0H1__zG-aCEXNnXX6nVd1odaEFEYdERtI_UXR1ZzR0djIYAeG5_SCzgc9ygMVcoKr_5mYOjmPCyCkzT8gbyUc0to9rQ5of-MocOKnZI%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE WIFI7 ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE WIFI7 ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-wf7-ice-rtl/860725692?hid=90401&sku=103638103565&show-uid=17397231487408394058616004&from-show-uid=17397231487408394058616004&cpa=1&do-waremd5=UX7xf_wtvA8V6Vz5nJib8A&cpc=CXSMTylTSEihVz2AncGsru2aJgdQ26hhRtKz0jGb-8G52RRjCE0i8CpQuCS1LLal8UXXvKBKc75YYO8FUquUIEQJ7xPRTC0Rpdg4oONWs-S3ttvQ7aSvgK1rH_CVOVJHaUGQC33q6VveFtRpqp-kLrO1kA62XeQ-9hv99c-vnNK8eu1iuwykOZ34VTNlHkJ2WweOu82GhBrSTR3piF4w4LzLn3ixHMSBLuMJWNDoHDk%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890 AORUS ELITE X ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS ELITE X ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-elite-x-ice-rtl/860739555?hid=90401&sku=103638117406&show-uid=17397231487408394058616005&from-show-uid=17397231487408394058616005&cpa=1&do-waremd5=DDiRMJPnbiuCv7Pn0oGhsw&cpc=CXSMTylTSEhUGnCL4Emv4gP1Bd8LnQPE5v-V4Rz1AoUZh_I3wNU76BFqzk9TyShS4eqw8sHrp3b1WPuzx8LQ3dmtCvJSSKyv01Syeze5LLTl96bZMdwhYe-3fphScnYAlXhyOM7VghHKP_1A6LiMyvSfJmM1f5si5jD7iT3Mi2pwpFo5iz7lM9HSENimV8bCdpBfpWDws_rL65Vp-ZA_K5ZOGwkPq_jk0VsU1JgKTqc%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890I AORUS ULTRA, LGA1851, Intel Z890, Mini-ITX, RTL (Z890I AORUS ULTRA)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890i-aorus-ultra-rtl/841947043?hid=90401&sku=103618765338&show-uid=17397231487408394058616006&from-show-uid=17397231487408394058616006&cpa=1&do-waremd5=kS5YN4VZFGVDNiLjwJhPig&cpc=CXSMTylTSEgNcQNkkuTkA3z6tMv5RL-6U1Fqf95pe9orXbmVX9sVfHV2wwh-XcrCEjJIl4bBvuUdg4q3Y0DXKzurZm6ZqlCoYJo_5di1yY_iTS35q3eUQS9gYSc6BztyMTDhfbiOMIDIwlG6AwWBhWSCVj4puGcLbJAxLZKyHwSqrrTdP6TF1NjQs8mnWBmA8QtehvIdyEoltMyT7srzdfkF5G1_AyekRYT1_scpYM0%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890 AORUS PRO ICE, LGA1851, Intel Z890, ATX, RTL (Z890 AORUS PRO ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-aorus-pro-ice-rtl/841060181?hid=90401&sku=103617752018&show-uid=17397231487408394058616007&from-show-uid=17397231487408394058616007&cpa=1&do-waremd5=2QDAK5a0K_l4awzS1sIPcA&cpc=CXSMTylTSEicqSVYFaloLTsLrbe1_VlPu5iCguUf6yH9FaiSRQA4KB5vF6wJHYeVm2IZzlApkqleRies22rOJqkyOiPHqN0reqnJe61sNFgr32RMkN9l4DlB17gJSOnam2g9DfC8T1krhxarDzJSR_jnBIz6rfFXIBuNBAaokXI88e0X65Ssmvlo5JzQ9fCZA_qRVHvbEwUiL4KCLaFXBc40YUSu3aMJMlj6dnkdnlE%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154', 'component': 'materinskaia-plata'}, {'title': 'Материнская плата Gigabyte Z890 UD WIFI6E, LGA1851, Intel Z890, ATX, RTL (Z890 UD WIFI6E)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-ud-wifi6e-rtl/831162034?hid=90401&sku=103605455831&show-uid=17397231487408394058616008&from-show-uid=17397231487408394058616008&cpa=1&do-waremd5=o8onj8YRR1vtXDBikWTGGQ&cpc=CXSMTylTSEiZNdu8KBXsf2wIq2d_GpbkJE4earjmHOJiNPKda05n1uGlxmN7t5vhkBdGUgVE5ndJaf4QwI3DRBmuyXFAavwQtchDyVPa912TekY4n4vi9DKVAwZGy-pjNRcFi4Zsa7LHPpu0MPhve5XnDKm_sUHs0RNL70E5E45FiIcHHSRoltpBV4swZC7ENt6UY7RqaMwl9dOoWPNnoWNsp9yA9BA3E_0PW9uHlRU%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890 GAMING X WIFI7, LGA1851, Intel Z890, ATX, RTL (Z890 GAMING X WIFI7)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890-gaming-x-wifi7/860742497?hid=90401&sku=103638119347&show-uid=17397231487408394058616009&from-show-uid=17397231487408394058616009&cpa=1&do-waremd5=qbc7x-R_RGTMccDgOiGacw&cpc=CXSMTylTSEjPTEzD39QNFkr24_hBhcfhQ12lB8x_OKm6KjosLa7LmCTJpd6dGpJHJ9xfmd10Sxn9LwgDBIFCevwEtQEZpFdhHcKjE9GeVsu8pZSOA9lF-VsOMHa4iXQEPno7QOs9VnuEoYainjX6WlggUHLh75iZmHPt1A2MJsbyN6kVRi4liuJLL2Rmc9t_ynqxDYDDBbXGkeFqe6zDfZn-We1Hp-FBVBzb4wcWsHU%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890M GAMING X, LGA1851, Intel Z890, Micro-ATX, RTL (Z890M GAMING X)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890m-gaming-x-rtl/829959465?hid=90401&sku=103604154371&show-uid=17397231487408394058616010&from-show-uid=17397231487408394058616010&cpa=1&do-waremd5=Vs6oMkGw7OP4sm2fcZzxkg&cpc=CXSMTylTSEidSnohFzC6enQc8FOYKZvPbb9BGcKVo87DlRwDGxZphcoiZMrgp4obHVjTljiDnkieqMa2z4iP7n8cz7Pi6syBf8AZ-LjBm91FDqRi277bOPRMlEooQqlUkIybEvE1AaAW2e0_fx8I1CsBKLhftUL_ErnLNyoM-cpGDKzYG7cBBxJCHFpiYCb8kldl8cMIdzfB8Vn6oUiHTUvrs2ml9VxsRXTiGEvfoqI%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte Z890M AORUS ELITE WIFI7 ICE, LGA1851, Intel Z890, Micro-ATX, RTL (Z890M AORUS ELITE WIFI7 ICE)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-z890m-aorus-elite-wf7-ice-rtl/836196877?hid=90401&sku=103611771458&show-uid=17397231487408394058616011&from-show-uid=17397231487408394058616011&cpa=1&do-waremd5=pMwIAUE2r7Q9K9wb0PSbwg&cpc=CXSMTylTSEiBPbRvp5-ijdPj_11bA-cCvCRRTYllNXU1Zg4J7xzoTt5L1UNlsxvLBDpEV434xgyAluFbzbn9eruH5y08ybnbFkPESJSit6voPTvuqQlFNTiZsn1AuFH0f9ANdfLLvPWh561LV_96c3QjoviIsalIZPufwjEZsioSzeeav5dBSHeDHebstQjkogLVgJtbyKrjfRUdq6h7gks4jrPVbEe6yHFJveN-j_Q%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIOnW8gEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte H610M H V2 DDR4, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-h610m-h-v2-ddr4-rtl/826066619?hid=90401&sku=103599862406&show-uid=17397231487800507513016001&nid=26912770&from=search&cpa=1&do-waremd5=m2BigUyKAu9HbRTzPgMPJg&sponsored=1&cpc=CXSMTylTSEh7UNODMUfoK3_2MXa9alixnveLXuYbdxHUFf5Xqz83EaTtiXT0g0PIn5gnMMBvY6lqQ38HeevCgQYafTLL60hqfaUFJ_kn2tycd-KLNTWAFAydwy1ALX-QpGkEws0dRTInWET0w7-vMhV88wBk_TUcRIk1zPP4kZ6YlXSmOrkX2i5l8ZCCKDXP4TMhdOIDt4bhU_FYSmqC2uBh7RlP5UuWXNWbgNYH96i8J5kCp9IosJJXjLhdPFhMhzBYKnKdquy9ZN61aOTHrLjlnK5sj-sUCeK_0o6z7HAYnlU_lf0opHqWLg2Ue0T8_aiK0T8b4jw4TtFaZKXZgNk788KWkENleZZRjDWJOr1ArDug9I5nsDz9oQlaspKOLZZBuQ2-U-0ZOdNmDL9LaV5NPW_2CJpT2VEa8kGF7J9WXrxOEHLEFYvR1dgDiSrCRCfprjbxoxMQ7lvGADJWRwNT7yb-edmJbz2BEfambmjbGxwEkHB8qtPsWpJyX36C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата Gigabyte A520M K V2', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-a520m-k-v2/1820745178?hid=90401&sku=101951780938&show-uid=17397231487800507513016002&nid=26912770&from=search&cpa=1&do-waremd5=8zYiTD_nFlvXtiKiT8YFaw&cpc=CXSMTylTSEh8NX8scEz7ZDG8JIDe4hyMe6byg_zyYQNbcV-_WH-rDHMaELKmgroHYU9VQJGG5rnBIRrldG16HlqET-rZQD_fDR1A29mqHfol5GVP-k0In7MiVqfY6pJvIdorzqBx4760rAOBtcf12wmrOQs_IKO8dUKc6TJ9C_Y5-XvdYnfRFqxGZo80H8fRVj8iOCB1yKRxfZZlGHhFQvM1NBs8ZoAVDovHfwzVYZTAdcBpr3IS1K3h7YMI95Idbj1NL4YfUj0iXZmHlb5QKnbaidTxk6p8dahqa4jljw0-VVKgViJUERTT4u8sqMS_TtAARD_UwzZ0HMTXs1WdTxo5KqPBFITF3rsrhSrQ2iGkvg5DX5sniGgngPu_FTMhTYjwYipMGrb44qbrGOVLUXzSN6r_tk30gaC8RCUnkFkbnOI196GXmGIfYfr9wI6Jz7EO23tb0onOxA-YkYpIvw%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Msi MPG B550 GAMING PLUS (AM4, ATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mpg-b550-gaming-plus-am4-atx/1779555126?hid=90401&sku=733855138&show-uid=17397231487800507513016003&nid=26912770&from=search&cpa=1&do-waremd5=9wndwHYlm4r1Hd3WMOfaAw&sponsored=1&cpc=CXSMTylTSEgP34BjhXAetRxVqJkw5Mf9_VC3dFOAmQZWQKmI3ZaaUKWumuRS-4xQCQCFyexokuZQKb-ZvNNVVRqLrmEVvFvsnUaCwWD-RRzOnjhSSnyVNgPf6VjhpbZu-jz21GHJcSB3lr3krJKkTry2nQTGXXCKI0KzxHK99u0DTvmfW26AZ50NnssshUBZpwybvAQ9Opwli4A3dqn1yr3fa1GY7HLqAGv2r2hheKYQ7fgdVANqxX0TcHeeUiZ7WWBl3qUSeYFIvksFrH7R2F-fJS8uA_3ia75LHlDE5gGZcJ3Jsi_qWQ8ZbkU_FktgQsWapTBZ80qOvv5Ulu53PMNWRpBWe1YEpi_rddvGgdSESauniCeIINPl7BOr8RB27Fe_Cyq9WVCNwOBoxczUt4WsYayRjfezSdJIiBcOR6uOtfQZMfvSZcp0hLPWsmvECOUHerNZMdFVDUuGcgR2feUfmxCMKpaqKbNeldcpRG8pIBL2Yyn2V3eDisFzcWfEZ90BUVCjhAwdUwPyq2Nb4KX-_J4nscifn3JSIF3sD89PwM4TNfugEpDYhB7xQBvIP29_w8qpg7rZZxB1uhPtXA1mGOjUBFPUNOl_9dRKBXJfLerIXZtQRRdA2gjsNw2R&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата Supermicro MBD-X13SEM-F-B', 'link': 'https://market.yandex.ru//product--supermicro-materinskaia-plata-supermicro-mbd-x13sem-f-b-mbd-x13sem-f/683317602?hid=90401&sku=103534581332&show-uid=17397231488049511310316001&from-show-uid=17397231488049511310316001&cpa=1&do-waremd5=ZXwWsAvrE5t2r7C5dV6UoQ&cpc=CXSMTylTSEgTsGWgiwKBKFy5m3eMbkgA0LIwsyf4Tx96GzZFXA-uVCLgIur8CRHBA02VfqIZuWRdpub5nw3uDrTKgtmrZ1DcUXMktelrupiDxwDLdsX9Vq-ng6s6dErpjSxAbdukAXPY0M5rOey1jKp3GImhbIGQDQUFuewPlOYMM-IgzfQDPeezHEblTngI5lDQAANc6LvXmYg2chlMqXnjo12iY5kVDxZkySYoc-Y%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS ROG MAXIMUS Z790 DARK HERO, LGA1700, Z790, Intel, DDR5, WiFi, ATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-dark-hero-lga1700-z790-intel-ddr5-wifi-atx/70439847?hid=90401&sku=102785993706&show-uid=17397231488049511310316002&from-show-uid=17397231488049511310316002&cpa=1&do-waremd5=kHRpAA4w1sqgJbg46uS9fA&cpc=CXSMTylTSEgBzZMLpWlXJVPaKRPF318rt6uhktFql_QcbdmpWufKNRwUM4N1schs1_CbSMMCB1mBUPFbDKgLIsD1eRej4TXR-lCpO6ziWkgK87_jtL8e0bq9BartKAJyyJ4C4oE5fQSIErAf0hYttZ-qqhc4jrK4I1fP9lSsx7Rx5YP_m9x5i03Hgw1rNnRCGknQbyB17q-Y8NHBWlJgagjI0I3aepgzdrzAuOUgOrY%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS 90MB1H50-M0EAY0, LGA1700, Intel Z790, ATX, RTL (90MB1H50-M0EAY0)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-hero-btf-90mb1h50-m0eay0/618448638?hid=90401&sku=103513089880&show-uid=17397231488049511310316003&from-show-uid=17397231488049511310316003&cpa=1&do-waremd5=f3cn8AOStZLaloT_H7Fu6g&cpc=CXSMTylTSEgj25cnX1HpSTHH-Lg-1MlwmpPPIZblR6DqynD1zGH0GM7D2GOupMNaJgGQzu39QkjhqAvvAsUOLvpoKCQrxjUnGr9k4QX9YWOVRP9JGFEUvVUZYuOyUE3udZFGA9rsHDY6TRkTk85yZshhSX4iDNyprm60vP2dINQr6v3lGkpyYzxVWyS4lHmiSTDqtNeIzq24PhqyE8fchUFe7bKNiw8hj0FWJ8QUlD0%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата ASUS ROG MAXIMUS Z790 APEX ENCORE', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-rog-maximus-z790-apex-encore-90mb1fx0-m0eay0/217614976?hid=90401&sku=103186893090&show-uid=17397231488049511310316004&from-show-uid=17397231488049511310316004&cpa=1&do-waremd5=mTfZzEobZUWx64PSqjZZTg&cpc=CXSMTylTSEjzUZAys4mhB7IoHGfbA5su0RDii-qVQGaGW75KThQVvLrRYowoKzUS9Hmcp-uAMGOJJuiRu0tYLrAf3-qoZ40sOyKuh_G0HpAmsnJXqD9MK36PZ9QRGLDvwnJXEJw7wO3UWZmC71k0mLYqsEVTQNoU1-vfKCrKM3H3Sn-uIMmYAcl0daaVmJB7PEUnuiAWsg7VWoVNqtMSHGhpFdxOFMdrro64lN0kvUw%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MSI MS-S1251', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-ms-s1251/44265055?hid=90401&sku=102617213909&show-uid=17397231488049511310316005&from-show-uid=17397231488049511310316005&cpa=1&do-waremd5=l_aDEoz1UDVFB9JQmstL6Q&cpc=CXSMTylTSEh6-8q8MOA9aDQjdQ2cq6IFoJgfE8aanfgAGsMUw9oAbZEAy8lie0FUKDXIx50tkPmuO7u-_D3B5nS3QChkzDF-JOoB-6uo5nKXmXDF9_2eL8z8ffxmKZ64_6BZy4p_WevxDVsTbNBFcH8rdstLbrH88WU8g42EWB7c-KAOFFkBUL3tt4-qH1OfpBCXLP6dYbW8wwdLq9BNL90nBSXQ2Of_DJLtyj0jsPo%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MBD-X12SPA-TF-B LGA4189, C621A, 16*DDR4(3200), 4*M.2, 7*PCIE, 10Glan, Glan, IPMI lan, USB Type-C, 4*USB 3.2, VGA, 2*COM', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-x12spa-tf-b/1785038542?hid=90401&sku=101872319278&show-uid=17397231488049511310316006&from-show-uid=17397231488049511310316006&cpa=1&do-waremd5=3XlUhDf8FlCadN0ZGqnlIg&cpc=CXSMTylTSEjttJGD3QrQuqLbtwhWPB-X9g-6EjXJy4CRBEI9gmmPBkOZqcOmApC7wn9AtX7czXA5XEB3DMB_fR_ZCDVfDFRKnVy5yaY2xWGTul47AVPnbfcKMhziA5F6s1goedFMr5uFZpB9NI57ucaGkvsws8Q5VExMcZ_r-VE7F54gYYZ0Bgal_46ZVeZoID6k1lfnrCM%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Supermicro MBD-X13SWA-TF-B', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-mbd-x13swa-tf-b/119770821?hid=90401&sku=103038595827&show-uid=17397231488049511310316007&from-show-uid=17397231488049511310316007&cpa=1&do-waremd5=7aTUMr0uhTryDMTU7CKGGg&cpc=CXSMTylTSEilrr2qvQMagcxkG3VEO1iuKOJ0ynVJYXdtZI7eJveVYFrmBma6HC28dlrQhkUoPKqAkEaFeSxNBUJBoj9qgFGQnADd4OFcfHdyTvfjlwxCLJ9UpDOSIU7JdLCNeaPBYP9iH-RtQvyPL8AdLjMvzFSDx_X37JKxwgFE_LFH5rC4ds5uKwEUgFF5yiBkAOdBJZe67t4UJh8_IluJaAQ2gsOcgvE1ETAlVSo%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Supermicro MBD-X13DAI-T-B, E-ATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-mbd-x13dai-t-b-e-atx/83714367?hid=90401&sku=102871114543&show-uid=17397231488049511310316008&from-show-uid=17397231488049511310316008&cpa=1&do-waremd5=jqS_qE17HxUoWyqWZukH9g&cpc=CXSMTylTSEhH6Ag5kvJ38JiFZTm04aR2lHuA6ztlW0SquidqX5WqtEh9-CHWJaxDraC8dUsVBNKZOgA9Oncv1_M8TtKtdko1wuOHaLREB55jBOlH8P09KuApyk-W8vD0Wx9R9J5zuUyMnVHWDItET3YFo0GoF9UkbhoqXYED1fqB0PIo_S6sa4jLCMB3f_xQiklH99OS4EpSOQH3JYqT_ijWRTxm06Rjtqr28KCC-nw%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата SuperMicro MBD-X12DPI-NT6-B 3rd Gen Intel Xeon Scalable processors Dual Socket LGA-4189 (Socket P+) supported, CPU TDP supports Up to 270W TDP, 3 UPI up to 11.2 GT/s, Intel C621A, Up to 4TB RDIMM, DDR4-3200MHz Up to 4TB', 'link': 'https://market.yandex.ru//product--materinskaia-plata-supermicro-x12dpi-nt6-b/1785038500?hid=90401&sku=101872319224&show-uid=17397231488049511310316009&from-show-uid=17397231488049511310316009&cpa=1&do-waremd5=5fSKcUYV54m5nx-QuATtqw&cpc=CXSMTylTSEiHiAEVyWz5IobBd2joMRrOUMVnetdJoACh-4SBMv9mtp0T4oin0GSsU3v82uJH_6QR9Q23hLv3lNDYhcgF6dsZqgw3RewBPx6ii_DVPloUKWrAo7iqFq3itlsbO2ZNeSNl4aTiEUh-BHxfRtFAwYcOKz33fqD_XH1L7A8bFjEdR2OLoc6Z_pXuhXBzpX3k6FLo9KfWrSabX9Yl95RzCvvwshDbMZtUvjc%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата MSI MPG Z890 CARBON WIFI, LGA1851, Intel Z890, ATX, RTL (MPG Z890 CARBON WIFI)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mpg-z890-carbon-wifi-lga1851-intel-z890-atx-rtl-mpg-z890-carbon-wifi/958831922?hid=90401&sku=103737171222&show-uid=17397231488049511310316010&from-show-uid=17397231488049511310316010&cpa=1&do-waremd5=12_rWD0f8DyO9fav-m1TNA&cpc=CXSMTylTSEjDvIu5Yl4oNlFNQ18kvMHWIfBfsKyWZRd5oKi8ld1tO-apG6_tBk1rLaTlZob0hiStLeItcpzEbVbzCQdANa1K92nSdesUS9-nBQLoYyc-E_twj_R2jcif4aPEmCWgYAv9_7HNWQrhMEQpCvn8UiK82SWcUxOuG0fCY7u9fKz8BejNRTyhqE2Lz_2HUfQDUqE%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRBUIMWo_QEoyuQtgH3m7QY%2C&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B550 GAMING X V2', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550-gaming-x-v2/1779555176?hid=90401&sku=766629016&show-uid=17397231487800507513016004&nid=26912770&from=search&cpa=1&do-waremd5=-XNDB753rINXrYj90xB1tA&cpc=CXSMTylTSEj9qUHLxciI_iWLS8iGnfy6XhmxABOxeclB77XDU0zejh32TCpHWFtPGQ-rdBRjnprbrbYFCqFc7W39p_GSz_y1P6rNr8CrqALp6hTT-VajW38nIUu7QqnL3uiWt0ylm6UUL9_AoW-r_VroCSP81CtqII1nb7dW8Ga5H_HkKzUFmIhOvS_dPqfwS8TEd5aQsRnQzWRNdpATtBtXbw_6uBUe7enbkHMpm8YdovJ-S8qRTISEhpamlCfsHFjjp88FMlZmi_tfObh8BUFfz4x53-KqK4EHU_PqchLHirNFNRDgtbr7dcltizDprQpEjYmyrtxQRGoY8rctOUHuiHwZh8wcjVtqTFNbh5xHCsa9UKC6kiBjA3FjB2ubnC_cyTgIHGHIjuVnojtGdMNvFy-S6Mcvtt4BtpMxE1qkKcj8mbZ8-us_c-Y5kVWPhtAFL4eFkXyMf9n-V9FFyg%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Asus PRIME B650M-K (AM5, mATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asus-prime-b650m-k-am5-matx/1932256909?hid=90401&sku=102296025496&show-uid=17397231487800507513016005&nid=26912770&from=search&cpa=1&do-waremd5=v6lA2lGNpOuMIYEs-bMqzw&sponsored=1&cpc=CXSMTylTSEj9K7E0S2HdF1k5E7khZGm_dNO04FH_lP9a3MNQSJVbfFia5GeHrTduFciq9Uh5Fe7nPKY9T-xewmjJ7CWDP-fTbAro2LpwCy9dY2s60N5HAdM6lg4UNP2PsCOZxaqDHRdDECijDK2dUQz5hYxVetfYedPVbtFm2aEnTm3zXVD3pq_Cov_R1RKVGrbMKMuD_IF3kKgJzt9_SbBiCKHEavifZhuVduQLU5RgrkfJ7FSUnyCzxuIKLcPVVtk5zB2FfZ6Q8esSNt77YwZS2t-XYixpJIB0dqLzSQqwpxzfVxn4v3SlX501k8wLT_-OuzTNNhClZhaa3B018L_7LLY5rZ_GGVhgxNTRGUMNT5UevNX0oYQcj6xihOjRozEkUjsszl01ZTMLehiiUhl6A3t4z_-16zH0mmLaTkwpBmdGE1mBoG3vzrNalayorDnKo3VxX6WSB5J9e3JUqns-SLnIPv9HswSwS-22WN4rWxAXB31hOAmvP6YgLmBn&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата ASRock B760M PRO RS/D4 Socket 1700, Intel®B760, 4xDDR4-3200, HDMI+DP, 2xPCI-Ex16, 1xPCI-Ex1, 4xSATA3(RAID0/1/5/10), 2xM.2, 8 Ch Audio, 1x2.5GLan, (2+4)xUSB2.0, (3+2)xUSB3.2, (1+1)xUSB3.2 Type-C™, ATX, 1xPS/2, RTL {} уц-5-3', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asrock-b760m-pro-rs-d4-rtl/1820740848?hid=90401&sku=101951773019&show-uid=17397231487800507513016006&nid=26912770&from=search&cpa=1&do-waremd5=utl-Uxl-wdvvx53dQFPtqA&sponsored=1&cpc=CXSMTylTSEjqUVKhM1Nq0rPaXbM9c7NoxFHth4IAluAshzTxTm9mODFaLSRiHaltxFJGgemzGvP6jmMRSJ8TpCkKVKxEfTLNGZMRgVyRmmOKynsNlZDX29FCbwxywn-omR2nQ93uF5dELDJMD3V8KnRQqMtku4HozhdriZSE6Gyjf64Q12zm3brtZtZHFWJ_3ouIrKk_QS6ggLMSbVFvzHZ1f2DlirwxkgTrVYRp5JiMm12htvuQezd8ym-bLctjXDDab4NR_8BzMSMXILDeflYb6lflXLZFsYtc0he1tU_rxoU0ImTaIkh5Ofb_A9o62MDRrMbORE_WH6hjZ06BTfXnMIMzdZLHtdHBVOH8aRsm0AuuOilAHRqnrZIHH8lo4SoCJ8JHFpMfi9TqXZ9vCyTSyVdJu6x9U9CNyBk3kYqkqc2O4tkRxtBHaKMyoDm69nBSl8i4NeODbo54tAskCVC1QQEpFBREyDOY2Tpld0XzZSn9jBveEadL8UGQL2le&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B550M DS3H', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550m-ds3h/1779555044?hid=90401&sku=675350012&show-uid=17397231487800507513016007&nid=26912770&from=search&cpa=1&do-waremd5=GvJJIJwJJhlEvYEktbGshg&cpc=CXSMTylTSEj8WhvXn2W-OyKUkv48qDjfFOFlKTYDyW1qu04E0hEJKOjTarDr3ZYgh6ajOdLRU0GtVEzFpF2qs2Z3jVsj0x_Bn_P3YpUCF-3ywDMQ_SOHmv5jCNZWltN8CHoSlBh3XoLiAxsAYHtRpC_hPK9MR0_BGy51_hqwIm_ARhuuvZP4NCq97CyLvv1f3z-6W_ekitNQPn8MtPRWPFz1sVH5iCzT3sn4xk6_PUnZh86fgfHbnoFfcM6JXr51vyz38nqOXdYKWhjKxGNUCfJajwK8rh2OGtzBUkv6VhMZt0zio99aNdTGEnALUYQcBrgHjpjMXpgY15Iuf0P7MuQMujmX5Rn1pN41D_fcROBmQL-dJQk6YkplJPpxZbEQ6DfjVEN-enJMoDnSNdpr2DZS-Y5QOkscabdk4VCYVydlSEvy_LiyoU5AbJC4Pb6gaIEVfVIEnEKVt-xcsqmQXw%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B450M K', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b450m-k/1782318038?hid=90401&sku=101864649749&show-uid=17397231487800507513016008&nid=26912770&from=search&cpa=1&do-waremd5=JPPzEbS4jbfxVK4LWCpz8g&cpc=CXSMTylTSEgSLF-JzKuFZOunx2-qJqhyGm0x2DnlcoktzYQsdrDuY9ZahQOQFeHUxY7UVZf7eH4SyQpxBJL5Cv5TNp0ncoHFbaT-Qf7fKIYWhWet7Gi35o3B4EebpaKPCrxc1lXdyw1g5JQgPsnP9yvMaqGhrOQDq0IXWC-2OJraL3pi-xtV-HeFCd4Yg05dlqP1KoYDghIl5ijEJEBzAcz_RIYxl8Iu-jRF3HiyAz0JV6ffIAVShafQ65npgGexzyFIZg6pGqdBKTuIx1PN3faIxvYGYFuhEVCZdRn5FYqjNS9LSfjFDq8vmCHW4KaTSuwQCzVmWeIhUMc_QphddAEOhkI7tDMUwBvZJ4dHNm-VROMYbGRHSoY67Cg-mGY-UGi5PZhjx649I6P_Iu2krexari52iBc0VCfEV5Ra92PuYlTmZpp4bSKM_tQX4ocKl-UPL9xbrjuiA9oudlDozQ%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B550M AORUS ELITE (AM4, mATX)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b550m-aorus-elite-am4-matx/1779555055?hid=90401&sku=676266211&show-uid=17397231487800507513016009&nid=26912770&from=search&cpa=1&do-waremd5=RQivNFmxyPTcpJcCNiQRaw&sponsored=1&cpc=CXSMTylTSEg7qvP32Eimq8uDgT0OHcQrEEgvZfwX0iUK_--C52Wt4Yrva2dI-sRn6jCTU7ukFswAGEW9lCCXU-S4itjZ_fuhI-mQwJSJaibRGGcs_DrOi6FTol4cQJApz9A9iEqkc6n3wWH73VXcbJeluPP4RrvVfaAylLF-NN1DqciCs5krPYIaH5Oukw7Q-nXphYXxujY115PmqMG4zJocleWIMPX9Zdy9CpdFlXy5WZ-jVwqqP0j2GQb7tPQBrNjH-2epiTpmiLMfICEShYXISm2xZAMCNWcobzYAMhjxBYEczSi-hvBbBW21xI2pZqXRWv11Lv6G9Ump0YvYWL3mySYXMj1QJlZGAN8YUHGbgdIKzE0wxVqvla-HS165h9f8RtFgjhhjtCUYaqJIxODPKrE3y1b2g6Ayu-i_mq6Eakp9satxGxDNnzzN0viPZMt3hxVSxzY7eRBPCcfiZN77Y5_6nxTAxJgDELrpzHyiY_gzFYA8GIChJ2mC857fZRuSslgAxe7ug8JeBHXWmP2HiezPLYckLfTUqKfnOOyns5DgIe33Jlsps1OPyMvf827ix54iEF4_3GyS0Kv9M771wuR-E0okRFV3PsioowldJAleY_Rd7PlECNnu3xQ4&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=892410'}, {'title': 'Материнская плата Gigabyte X870E AORUS ELITE WIFI7, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-x870e-aorus-elite-wifi7-rtl/762813300?hid=90401&sku=103565245584&show-uid=17397231487800507513016010&nid=26912770&from=search&cpa=1&do-waremd5=ZXXFBGZLSwihSchXNc3zhA&sponsored=1&cpc=CXSMTylTSEhj5AzliwWXhoIwd3W1r22BXtTwrCvwpVz-mDx7Bz1zEyij83F81kf7f3SU2Hz1cZh7epeHVs58vO-CyO-2YGx8JD3tzxdeJMQMknXdXzxO04TTfm86fhhR0Dt3jAr5q4_7YseBLJUNrI7ZEnOAfTsxeTOIZs-m37ebGLURNqUCU1zSvXoEu0KfVQRjwc8PAredWMopqEg1SHlLmDvFYB5hETkP0uFAnvZi8hnBa9SSHF3KZo9ZR4QQJF52iRMXQxt4uu5_bTEzq9SKzz3JwqAQehI1Wz-3bY0ogF9blAk2bJ0Jlp0TwKMrnE87ZGCx6jsnvDkPiNj-hVTymMayX1JERW2uXMnzl0YPvMuCmvRzcrqjYNMmrMfYZRR2NgW1QP4NPSUjo5cDlFZ-LwfodmGjs9tN7O2jirqt9UNt5aPnLkfcDhztrPoGEJBCct1dEyYJ5hXIcohqM-ogfEp-wWeZ960PWGAUApz7623YjI3gRlCRQH3MIRGT&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата MSI MAG B550M MORTAR MAX WIFI mATX', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-mag-b550m-mortar-max-wifi-matx/1779556403?hid=90401&sku=1761111537&show-uid=17397231487800507513016011&nid=26912770&from=search&cpa=1&do-waremd5=zMYId93PxSbdhf_t-JIp-g&sponsored=1&cpc=CXSMTylTSEjwnjEnylkCcHGR0tEnjb3_ITWtXLyi-ZPJ_ha_xsDopi69btnH7l5AfkVmk6T2wxyu5SVms2TNIOXK8kw8gKAxoJjEmF-GJj4ldSxFrpSCwsFuW-PonS3Ypgt9D4H276rHPcpb_lbhuY6vP1POQWvxleZ_B8lAtaPeenIhnXfbZyOJKbXdfk5XQX5eGMe6ctM_beiONWjJc1hHdbGaU5eEalliNY6X5T5Yyvm-__U1k8-wVvTkBWsWFd3BXw3A2y2XCDY6oyd5AiAKndw54mVb_9qPEjh4r9I5qeZjBhR3NQ5Nzw_l60fW7WfxG9EOsq3IDT0apHh1Awe1kPDoGODzsJKIN27ptfIuYCE7zpDid_Mh5aPztigiFvJUfNU4qQH_FQC_zWZBM4NXN5r6Y4s3046pe_4z7ujYrM3YAG9Dn-wjviqnnDB6223vJkkad8LXv5-7Q6k_fVm1cebWnJF-zvgvUPEo3BkTl0Wf6S1A1cCzKIzg0f1e&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=12054742'}, {'title': 'Материнская плата Asrock B450M-HDV R4.0', 'link': 'https://market.yandex.ru//product--materinskaia-plata-asrock-b450m-hdv-r4-0/1779554660?hid=90401&sku=334418263&show-uid=17397231487800507513016012&nid=26912770&from=search&cpa=1&do-waremd5=MD_eCfiz5kNP063EUMYILQ&cpc=CXSMTylTSEga3IHuoEwX-qt1lBPzD2_p3UXMZ_OWWA9y2AXgA4b_AWBPLs_kxUXmUtAJDqLxHj4JB9KHPvBPPTYxNc88fPt1ZoIg5DoyWy8tINvaQJn6MFRxjbJ3H9vWxCl8h-moOXhJT7OcA_WgZJHYB2Zeo8yV1EnktT7gdROKxPg1Rx98FCFiu3pc3JyTxCHt92B4W0-UuQxOEu72yvrrZk-JXsVyNR9nvd2H2BYCLq2P_hQTJ2eTb-m6yNeQZYu1bPRV3O6vQsqC7b0nYkDEcz8_-9I998GOcZqDSEBzTWc9IoX2Q8WVakoPHVwWjqQlPB7kKeyl9lJpXWPgH-WJfTFCjDvIRt0kHZoYQt2DY9XX5GpMnZksy45PGBogy5WGtKkPY1j8yBB0uEAk-GuhUAg_JPqKmBU1_4M3UrirpQP0RIT1lDeAs45IBr2OobIGRAdEDsOBHJKhhJ4Uxg%2C%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=1499763'}, {'title': 'Материнская плата Gigabyte B760M AORUS ELITE AX, RTL Socket 1700, WiFi, mATX, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b760m-aorus-elite-ax-rtl-socket-1700-wifi-matx-rtl/42794160?hid=90401&sku=102602962858&show-uid=17397231487800507513016013&nid=26912770&from=search&cpa=1&do-waremd5=h4PQ82F0XSBsKFm4uRf05w&sponsored=1&cpc=CXSMTylTSEiEX0SmkEdEnxN9QeIj3dWf8KqGF3qJJuAT8PvaEMKtCm1a4IUX3WRPu4Y_czHLf7YSU6S_Be_VRDub_Yxy4FhJtctvOWp-t87LGdHM02WcNm8hhjPo8dRRMzxW1kij_QH_k70uNTz6gJV2jEwieL_me4Eb3NNkfnm-4IdSPSPGkUkyQs7z24Kb38Y3cc_HJf8jiFISrBfRAI720AZPy-EJfIK1z9xf19rrG2QpkTZTTbkYXp91f75j411jGX1P2Kf1kgzvX_dYSXmNXtMUgTVxjSthj604SiqxCXp95wkDzz-kWLRy-ouXWjp5EhM4IBwwNToLtFunXHIfh3-KvyrWZd8QVO5J_Yu_0IxOMt-BvngvkNn15OOKE9kEs9EaBkrJaU7d9ajbi-rglvZBXMhwgKzour38TdKiN6FXhxLYfOSMKZt57W54QP04WPOC2Q4us7e_r-uCtYonw9HoSoaT8iWhTpC6h5P2-9CMFDgHNNgXwZUGqRJo&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=833949'}, {'title': 'Материнская плата MSI Z790 GAMING PLUS WIFI LGA1700 Retail Z790 DDR5 ATX HDMI', 'link': 'https://market.yandex.ru//product--materinskaia-plata-msi-z790-gaming-plus-wifi-lga1700-retail-z790-ddr5-atx-hdmi/39574459?hid=90401&sku=102581861759&show-uid=17397231487800507513016014&nid=26912770&from=search&cpa=1&do-waremd5=vVDoTLUCrFd4ajaHGCCJww&cpc=CXSMTylTSEgowN5TVDJyrmOPn_EuslWnt0cXhN5QQ3RzmBIfUJli4WI7Z_RtRkV9Q1v1aZwcm_9WiCIOhf20KaES4TxxB_ApAonB6GCxj7JnFum5U2s2ymmyxz8QsWRPVHNHAE_ZFApuSx8F7LpYNS12OjtPh_rIXD2gqsclwWzxvCK1ForqKZolewhAOyEy9xF6igGiph81MPJJpBp44d_Y--vk4ZAHWQV6RMOKe1pYYvPh5yir9oAvlFj4ybFlgq__9N3I1IL8F_SdEUhEgXpHD-q7SYyeHXKtFskz23d9tfnamLRNkLjQPahifTUJSBC0KGpCtM9otP5-LnfX15Y6m1an0i5ge7wroT3Me-I01b5n__-qdikw4wYSQR5k3RKknrqRXPnEqN56H1on718LiyNwGwn1IVEremn6h1Mbd43DT3kntz_NeJpiDjYrjeFl70EVGIrV5FPvGkvQqN5Oi-I5DVyDcP4flDjVDp6z3FfxDuaj3nlU5Y6436S54Yz7IM9P_JiZh12uyOIJ8X67pAgJqy40hvl2xNTmPnRPzOY31lvZKvzdRQXkyYKAebLwf1ByP3hlPhyit7eoLm1ukXIKPzTftIFdxSnuTgM%2C&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRAHgH3m7QY%2C&uniqueId=924877'}, {'title': 'Материнская плата Colorful CVN B760M FROZEN WIFI D5 V20, LGA1700, Intel B760, Micro-ATX, RTL (CVN B760M FROZEN WIFI D5 V20)', 'link': 'https://market.yandex.ru//product--materinskaia-plata-colorful-cvn-b760m-frozen-wifi-d5-v20-lga1700-intel-b760-micro-atx-rtl-cvn-b760m-frozen-wifi-d5-v20/867552581?hid=90401&sku=103644418508&show-uid=17397231487800507513016015&nid=26912770&from=search&cpa=1&do-waremd5=9AXa9mRhAv55LU8Fc-6pig&sponsored=1&cpc=CXSMTylTSEi9DTZOXyZzxykiM_TVGCf7tSE8h7h0BGwAUMQRHCcRFdwPdcDOy6bk6tdrBVodtwBNmwf71usJUXfYCtuRfxEU8DRFnFPtRgJuFqiOBPYPo40NL5QLmUg7ka3dbXMYHTmi-v0hrEJDru12MZsNFhtFP_Z658vp0KSzP1DtX9sBVeuS00gvIPRmWjHDR7gMOqrNcDdl976jJ0HZ7I8RjsbvKucfTUV3JezTzAlQOgdFbXVonaxUKxwW72GEwMB6UR2TrH8h9FE9oQBTmGyig3dh4A6udC76UxgEDM6zo41lh5bxsSGndQKFYvuJYmCdnQ5JZ0tugzrDJdp3UZiAtU3vQr7u4tw7AQUPbVDY8dxr5Y90AV7JUCoijy-XkGChIJ82h9DIUM8ahHtN49wLgv3o2B_yUPlj3LqBvaF0fYYQqfxd4C8nYT_F_f27PGqmCGTfC6NWub13F0M_UYaab0RH_a-RoJfQOsZbrTXM9VNsa2-zPrHp4Hoy&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}, {'title': 'Материнская плата Gigabyte B760 DS3H DDR4, Socket 1700, Intel B760, 4xDDR4-3200, ATX, RTL', 'link': 'https://market.yandex.ru//product--materinskaia-plata-gigabyte-b760-ds3h-ddr4-socket-1700-intel-b760-4xddr4-3200-atx-rtl/1812468853?hid=90401&sku=101926164825&show-uid=17397231487800507513016016&nid=26912770&from=search&cpa=1&do-waremd5=aZAssmitkw6-KY4qM5jjDg&sponsored=1&cpc=CXSMTylTSEgo2LOtt9NwU-z9USUnO59gwrXfMHhpwmJfnSZreIkD_Ih1bMLNHSY7cenp030jic8SzKSDBWHw2BO-5RtUJJ_skxvLpRI4-jjo2-WElX1AEaPoTd_1of4dDJiZGsA5vDtVCoWF-o3oqvID5wLG24kHkkZ8t0-jhPVYOONKFW1AEkm_H-85ulRTR8Xk5roiU_zj42ojjSd1L-SQK_-CErvbagNHkGBFYNp6QbAUYj1xizL87M_Kih4RvvC5lOkrFBKJsBUcVxVgMJpEOWHQv7XkkQdpIzwKapAEqvXfzeUZuP4Ucmc23zU5i1NVDhdIck0zvlVSpDp5hbNe2tlsK56kb-bS5ExQjPscOb2tAlcWwMmaYUs78zLsSBpnoIKMlgpNsRGjpyCFVFaIZKIW-DUKxzYvd1MXI4m4Noq1wuEu0sCM_JcMXucu5DEBsPLVwPZEt3AaIWMKG6j9J_5grdiBOgEaVZywtTs5pZmwJuPGHSTbelszC-Rz&cc=CjIxNzM5NzIzMTQ4NDQ1LzU4NWU0OTQyNTVjNjRhZjVkNjQ3NDVkYzQ0MmUwNjAwLzEvMRDnAYB95u0G&uniqueId=750154'}]}

        supabase_service = SupabaseService()
        new_links_count = 0
        all_links_found = 0
        for component, links in parts.items():
            for link_data in links:
                new_link = Links(
                    link=link_data['link'],
                    title=link_data['title'],
                    component=component,
                    is_parsed=False,
                    is_actual=True
                )

            # "component": link_data.component,

            # "image_url": None,
            # "price": None,
            # "articul_yandex": None,

                # Вставка ссылки
                inserted_link = supabase_service.insert_unique_link(new_link)
                if inserted_link:
                    new_links_count += 1

        if links:
            all_links_found = len(links)
        print(f"Найдено ссылок: {all_links_found}, добавлено новых: {new_links_count}")
        return (f"Saved {new_links_count} new links")
    except Exception as e:
        print(f"Error parsing links: {e}")


if __name__ == "__main__":
    # parse_first_links()
    find_new_links()
