from supabase import create_client, Client
from flask_supabase import create_client, Client
from config import Config
from models import Links, Characteristics
from datetime import datetime
import pytz
from check import is_valid

class SupabaseService:
    def __init__(self):
        self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

    def _get_current_datetime(self):
        """
        Получение текущей даты и времени в UTC
        """
        return datetime.now(pytz.UTC)

    def insert_unique_link(self, link_data: Links):
        """
        Вставка только уникальных ссылок
        Если ссылка уже существует, возвращается None
        """
        # Устанавливаем текущую дату при создании
        current_datetime = self._get_current_datetime()

        data = {
            "link": link_data.link,
            "title": link_data.title,
            "component": link_data.component,
            "is_parsed": link_data.is_parsed,
            "date_parse": current_datetime.isoformat(),
            "image_url": link_data.image_url,
            "price": link_data.price,
            "articul_yandex": link_data.articul_yandex,
            "is_actual": link_data.is_actual
        }

        try:
            # Проверка существования ссылки
            existing_link = (
                self.client.table('links')
                .select('*')
                .eq('link', link_data.link)
                .execute()
            )

            # Если ссылка уже существует, возвращаем None
            if existing_link.data:
                print(f"Ссылка уже существует: {link_data.link}")
                return None

            # Вставка новой уникальной ссылки
            response = (
                self.client.table('links')
                .insert(data)
                .execute()
            )

            print(f"Новая уникальная ссылка добавлена")  # : {link_data.link}")
            if response:
                return response.data[0]

        except Exception as e:
            print(f"Ошибка добавления уникальной ссылки: {e}")
            return None

    def insert_or_update_link(self, link_data: Links):
        """
        Вставка или обновление ссылки с проверкой уникальности
        """
        # Устанавливаем текущую дату при создании/обновлении
        current_datetime = self._get_current_datetime()

        data = {
            "link": link_data.link,
            "title": link_data.title,
            "component": link_data.component,
            "is_parsed": link_data.is_parsed,
            "date_parse": current_datetime.isoformat(),  # Всегда устанавливаем текущую дату
            "image_url": link_data.image_url,
            "price": link_data.price,
            "articul_yandex": link_data.articul_yandex,
            "is_actual": link_data.is_actual
        }

        try:
            # Проверка существования ссылки
            existing_link = (
                self.client.table('links')
                .select('*')
                .eq('link', link_data.link)
                .execute()
            )

            if existing_link.data:
                # Обновление существующей ссылки
                response = (
                    self.client.table('links')
                    .update(data)
                    .eq('link', link_data.link)
                    .execute()
                )
                print(f"Ссылка обновлена: {link_data.title}")
                return existing_link.data[0]
            else:
                # Вставка новой ссылки
                response = (
                    self.client.table('links')
                    .insert(data)
                    .execute()
                )
                print(f"Ссылка добавлена: {link_data.title}")
                return response.data[0]

        except Exception as e:
            print(f"Ошибка сохранения ссылки: {e}")
            return None

    def set_non_active_link(self, url: str, is_actual=False):
        """
        Обновление у ссылки поля is_actual
        """
        try:
            # Находим нужную ссылку по url
            existing_link = (
                self.client.table('links')
                .select('*')
                .eq('link', url)
                .execute()
            )

            if existing_link.data:
                # Обновление существующей ссылки
                response = (
                    self.client.table('links')
                    .update({"is_actual": is_actual})
                    .eq('link', url)
                    .execute()
                )
                # print(f"Поле is_actual={is_actual} для ссылки: {url}")
                return existing_link.data[0]
            else:
                print(f"Ссылки нет в базе: {url}")
                return response.data[0]

        except Exception as e:
            print(f"Ошибка обновления ссылки: {e}")
            return None

    # С сортировкой по дате
    def  get_unparsed_links_sorted(self, limit: int = 100) -> dict:
        try:
            response = (
                self.client.table('links')
                .select('*')
                #.eq('is_parsed', False)
                .eq('is_actual', True)
                # .eq('component', 'materinskie-platy')
                #.order('date_parse', desc=True)  # Сортировка по дате создания в порядке убывания (самые новые)
                .order('date_parse', desc=False)  # Сортировка по дате создания (самые старые)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Ошибка получения отсортированных неразобранных ссылок: {e}")
            return []

    # С фильтрацией по компоненту
    def get_unparsed_links_by_component(self, component: str, limit: int = 100):
        try:
            response = (
                self.client.table('links')
                .select('*')
                .eq('is_parsed', False)
                .eq('is_actual', True)
                .eq('component', component)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Ошибка получения неразобранных ссылок компонента {component}: {e}")
            return []

    def materinskie_to_materinskay(self, old_value, new_value):
        response = (
            self.client.table('links')
            .update({'component': new_value})
            .eq('component', old_value)
            .execute()
        )
        return response.data

    def insert_or_update_characteristics(self, characteristics_data: Characteristics):
        """
        Вставка или обновление характеристик с проверкой уникальности
        """
        data = {
            "link_id": characteristics_data.link_id,
            "group": characteristics_data.group,
            "name": characteristics_data.name,
            "value": characteristics_data.value
        }

        try:
            # Проверка существования характеристики
            existing_characteristic = (
                self.client.table('characteristics')
                .select('*')
                .eq('link_id', characteristics_data.link_id)
                .eq('group', characteristics_data.group)
                .eq('name', characteristics_data.name)
                .eq('value', characteristics_data.value)
                .execute()
            )

            if existing_characteristic.data:
                # print(f"Характеристика уже существует: {characteristics_data.name}")
                return existing_characteristic.data[0]

            # Вставка новой характеристики
            response = (
                self.client.table('characteristics')
                .insert(data)
                .execute()
            )
            # print(f"Характеристика добавлена: {characteristics_data.name}-{characteristics_data.value}")
            if response:
                return response.data[0]

        except Exception as e:
            print(f"Ошибка сохранения характеристики: {e}")
            return None

    def get_links(self, is_actual: bool = True, is_parsed: bool = True, limit = 10):
        """Получение ссылок из Supabase"""
        response = (
            self.client.table('links')
            .select("*")
            .eq('is_actual', is_actual)
            .eq('is_parsed', is_parsed)
            .limit(limit)
            .execute()
        )
        if response:
            return response.data

    def get_characteristics_by_link_id(self, link_id: int):
        """Получение характеристик по ID ссылки"""
        response = (
            self.client.table('characteristics')
            .select("*")
            .eq('link_id', link_id)
            .execute()
        )
        if response:
            return response.data

    def get_statistic(self):
        """
        Вывод информации о спрасенных и неспарсенных ссылках
        """
        # Все ссылки
        total_links = (
            self.client.table('links')
            .select("*", count='exact')
            .execute().count
        )

        # Спарсенные ссылки
        parsed_links = (
            self.client.table('links')
            .select("*", count='exact')
            .eq('is_parsed', True)
            .execute().count
        )

        # Неспарсенные ссылки
        unparsed_links = total_links - parsed_links

        return {
            'total_links': total_links,
            'parsed_links': parsed_links,
            'unparsed_links': unparsed_links
        }

    def get_components_by_type_and_price(
        self,
        component_type: str,
        min_price: int = 0,
        max_price: int = None
    ) -> list:
        """
        Получение компонентов определенного типа с фильтрацией по цене

        :param component_type: Тип компонента
        :param min_price: Минимальная цена (по умолчанию 0)
        :param max_price: Максимальная цена (по умолчанию None)
        :return: Список компонентов с подробными характеристиками
        """    
        try:
            query = (
               self.client.table('links')
                .select('*')
                .eq('component', component_type)
                .eq('is_actual', True)
                #.order('date_parse', desc=True)  # Сортировка по дате создания
                .order('price', desc=True)
            )

            # Добавление фильтра по цене
            if max_price is not None:
                query = query.filter('price', 'gte', min_price)
                query = query.filter('price', 'lte', max_price)
            else:
                # Если максимальная цена не указана, используем только нижний порог
                query = query.filter('price', 'gte', min_price)

            print(f"Параметры запроса: component={component_type}, min_price={min_price}, max_price={max_price}")

            # Выполнение запроса
            links_response = query.execute()

            # Список для хранения обработанных данных
            link_data = []

            # Обработка каждой ссылки
            for link in links_response.data:
                # Получение характеристик для текущей ссылки
                characteristics_response = (
                    self.client.table('characteristics')
                    .select('*')
                    .eq('link_id', link['id'])
                    .execute()
                )

                # Группировка характеристик
                items = {}
                for characteristic in characteristics_response.data:
                    if characteristic['group'] not in items:
                        items[characteristic['group']] = {'items': []}

                    items[characteristic['group']]['items'].append({
                        'name': characteristic['name'],
                        'value': characteristic['value']
                    })

                # Преобразование сгруппированных характеристик
                characteristics_grouped = [
                    {
                        'name': key,
                        'items': value['items']
                    }
                    for key, value in items.items()
                ]

                # Подготовка списка URL изображений
                image_urls = [link['image_url']] if link.get('image_url') else []

                # Формирование структуры компонента
                link_data.append({
                    'component_name': link['title'],
                    'component_type': link['component'],
                    'url': link['link'],
                    'image_url': image_urls,
                    'price': link['price'],
                    'articul_yandex': link['articul_yandex'],
                    'fullSpecsGrouped': {'groups': characteristics_grouped}
                })

            return link_data

        except Exception as e:
            print(f"Ошибка при получении компонентов: {e}")
            return []

    def get_components_by_type_and_price_once(
        self,
        component_type: str,
        min_price: int = 0,
        max_price: int = None,
        is_parsed: bool = True,
        limit: int = 100,
    ) -> list:
        """
        Получение компонентов определенного типа с фильтрацией по цене

        :param component_type: Тип компонента
        :param min_price: Минимальная цена (по умолчанию 0)
        :param max_price: Максимальная цена (по умолчанию None)
        :return: Список компонентов с подробными характеристиками
        """
        try:
            query = (
                # self.client.from_('links').select('id, title, component, link, image_url, price, articul_yandex, date_parse, is_actual, is_parsed, characteristics(group, name, value)')
                self.client.from_('links').select('id, title, component, link, image_url, price, articul_yandex, characteristics(group, name, value)')
                .eq('component', component_type)
                .eq('is_actual', True)
                .eq('is_parsed', is_parsed)
                .filter('price', 'gte', min_price)
                .order('date_parse', desc=True)  # Сортировка по дате создания
                .limit(limit)
            )

            if max_price is not None:
                query = query.filter('price', 'lte', max_price)
            print(f"Параметры запроса: component={component_type}, min_price={min_price}, max_price={max_price}, limit={limit}")
            
            # Выполнение запроса
            attemp_count = 0
            is_succsesful = False
            while not(is_succsesful) and attemp_count <= 3:
                try:
                    response = query.execute()
                    is_succsesful = True
                except Exception as e:
                    print(f'ошибка получения данных {e}')
                    attemp_count += 1

            if response:
                # Список для хранения обработанных данных
                link_data = []

                
                # Обработка каждой ссылки
                for link in response.data:
                    # Получение характеристик для текущей ссылки
                    # Группировка характеристик
                    # print(f"{link['title']}, date_parse={link['date_parse']}, is_actual={link['is_actual']}, is_parsed={link['is_parsed']}")
                    items = {}
                    for characteristic in link['characteristics']:
                        if characteristic['group'] not in items:
                            items[characteristic['group']] = {'items': []}

                        items[characteristic['group']]['items'].append({
                            'name': characteristic['name'],
                            'value': characteristic['value']
                        })

                    # Преобразование сгруппированных характеристик
                    characteristics_grouped = [
                        {
                            'name': key,
                            'items': value['items']
                        }
                        for key, value in items.items()
                    ]

                    # Подготовка списка URL изображений
                    image_urls = [link['image_url']] if link.get('image_url') else []

                    # Формирование структуры компонента
                    link_data.append({
                        'id': link['id'],
                        'component_name': link['title'],
                        'component_type': link['component'],
                        'url': link['link'],
                        'image_url': image_urls,
                        'price': link['price'],
                        'articul_yandex': link['articul_yandex'],
                        'fullSpecsGrouped': {'groups': characteristics_grouped}
                    })

                return link_data

        except Exception as e:
            print(f"Ошибка при получении компонентов: {e}")
            return []


    def get_component_statistic(self):
        """
        Вывод статистики о спарсенных и неспарсенных ссылках по компонентам

        :return: Словарь со статистикой по компонентам
        """
        # Получаем уникальные компоненты
        components = (
            self.client.table('links')
            .select('component', count='exact')
            .execute()
        )

        # Словарь для хранения статистики
        component_stats = {}

        # Обходим каждый компонент
        for component in set(row['component'] for row in components.data):
            # Все ссылки компонента
            total_links = (
                self.client.table('links')
                .select("*", count='exact')
                .eq('component', component)
                .execute().count
            )

            # Спарсенные ссылки компонента
            parsed_links = (
                self.client.table('links')
                .select("*", count='exact')
                .eq('component', component)
                .eq('is_parsed', True)
                .execute().count
            )

            # Активные ссылки компонента
            active_links = (
                self.client.table('links')
                .select("*", count='exact')
                .eq('component', component)
                .eq('is_actual', True)
                .execute().count
            )

            # Неспарсенные ссылки
            unparsed_links = total_links - parsed_links

            # Неактивные ссылки компонента
            unactive_links = total_links - active_links

            # Процент спарсенных ссылок
            parsing_percentage = (parsed_links / total_links * 100) if total_links > 0 else 0

            # Процент активных ссылок
            active_percentage = (active_links / total_links * 100) if total_links > 0 else 0

            # Сохраняем статистику
            component_stats[component] = {
                'total_links': total_links,
                'parsed_links': parsed_links,
                'unparsed_links': unparsed_links,
                'parsing_percentage': round(parsing_percentage, 2),
                'active_links': active_links,
                'unactive_links': unactive_links ,
                'active_percentage': round(active_percentage, 2)
            }

        return component_stats 

    def get_link_by_url(self, url, is_actual: bool = True, is_parsed: bool = True):
        response = (
            self.client.table('links')
            .select("*")
            .eq('link',url)
            .eq('is_actual', is_actual)
            .eq('is_parsed', is_parsed)
            .execute()
        )
        if response:
            return response.data

    def check_valid_components(self, limit = 100):
        """
        Проверка компонентов, что у компонента есть все характеристики, которые нужны для проверки совместимости
        и установка у не подходящих is_active=False
        """
        components = [''
        # 'kulery-i-sistemy-okhlazhdeniia',
        # 'bloki-pitaniia',
        'materinskaia-plata',
        'protsessory-cpu',
        # 'operativnaia-pamiat',
        # 'videokarty',
        # 'korpusa',
        # 'vnutrennie-tverdotelnye-nakopiteli-ssd',
        ]
        result_text = ''
        for component in components:
            passed = 0
            not_passed = 0
            component_count = 0
            for i in range(0, 200000, 1000):
                min_price = i
                max_price = i + 1000
                responce_components = self.get_components_by_type_and_price_once(
                    min_price=min_price,
                    max_price=max_price,
                    component_type=component, 
                    limit=limit
                    )
                if responce_components:
                    component_count += len(responce_components)
                    print(f"Найдено {len(responce_components)} в диапазоне {min_price}-{max_price}")
                for responce_component in responce_components:
                    if not(is_valid(responce_component)):
                        if "url" in responce_component:
                            self.set_non_active_link(responce_component["url"], False)
                            not_passed += 1
                        else:
                            print("Неверная структура ответа", responce_component)
                        #print(responce_component)
                    else:
                        passed += 1

            if responce_components is None:
                print(f'нет данных для проверки {component}')
            # result_text += f'{component} не прошло - {passed}, прошло - {not_passed}'+'\n'
            print(f'{component} не прошло - {passed}, прошло - {not_passed} из {component_count}'+'\n')
        return None

def print_component_statistic(component_stats):
    """
    Вывод статистики в читаемом формате

    :param component_stats: Словарь со статистикой по компонентам
    """
    print("\n=== Статистика парсинга по компонентам ===")

    # Переменные для общей статистики
    total_total_links = 0
    total_parsed_links = 0
    total_unparsed_links = 0
    total_active_links = 0
    total_unactive_links = 0

    # Сортируем компоненты по количеству неспарсенных ссылок (по убыванию)
    sorted_components = sorted(
        component_stats.items(),
        key=lambda x: x[1]['unparsed_links'],
        reverse=True
    )

    for component, stats in sorted_components:
        text = f"\nКомпонент: {component}"
        text += f"  Всего ссылок: {stats['total_links']}"
        text += f"  Спарсено: {stats['parsed_links']}"
        text += f"  Не спарсено: {stats['unparsed_links']}"
        text += f"  Процент парсинга: {stats['parsing_percentage']}%"
        text += f"  Актуальных: {stats['active_links']}"
        text += f"  Неактуальных: {stats['unactive_links']}"
        text += f"  Процент актуальных: {stats['active_percentage']}%"
        print(text)

        # Обновляем общую статистику
        total_total_links += stats['total_links']
        total_parsed_links += stats['parsed_links']
        total_unparsed_links += stats['unparsed_links']
        total_active_links += stats['active_links']
        total_unactive_links += stats['unactive_links']

    # Общая статистика
    print("\n=== Общая статистика ===")
    text = f"Всего ссылок: {total_total_links} "
    text += f"Спарсено: {total_parsed_links} "
    text += f"Не спарсено: {total_unparsed_links} "
    text += f"Общий процент парсинга: {round(total_parsed_links / total_total_links * 100, 2)}%"
    text += f" Актуальных: {total_active_links}"
    text += f" Неактуальных: {total_active_links}"
    print(text)

def check_components():
    supabase_service = SupabaseService()
    components = supabase_service.get_components_by_type_and_price_once('materinskaia-plata',limit = 250)
    #components = supabase_service.get_components_by_type_and_price_once('korpusa',limit = 250)
    #components = supabase_service.get_components_by_type_and_price_once('videokarty',limit = 250)
    a = 0
    for comp in components:
        if not(is_valid(comp)):
            print(comp)
            a += 1
 #       else:
#            a.append(comp)
    print(a)
    return None

def statitics():
    supabase_service = SupabaseService()
    data = supabase_service.get_component_statistic()
    print_component_statistic(data)


def main():
    try:
        supabase_service = SupabaseService()
        # # Создание таблиц
        # supabase_service.create_links_table()
        # supabase_service.create_characteristics_table()

        # # Пример создания ссылки
        # new_link = Links(
        #     link="https://example3.com",
        #     title="Пример ссылки3",
        #     component="Test3",
        #     is_parsed=False,
        #     date_parse=datetime.now(),
        #     image_url="https://example.com/image3.jpg",
        #     price=3000,
        #     articul_yandex="TEST1233",
        #     is_actual=True
        # )

        # Вставка ссылки
        # inserted_link = supabase_service.insert_or_update_link(new_link)

        # if inserted_link:
        #     # Создание характеристики для ссылки
        #     new_characteristic = Characteristics(
        #         link_id=inserted_link['id'],
        #         group="Общие",
        #         name="Цвет",
        #         value="Синий"
        #     )

        #     # Вставка характеристики
        #     supabase_service.insert_or_update_characteristics(new_characteristic)

        # Получение данных
        # links = supabase_service.get_links()
        # print("Ссылки:", links)

        # if links:
        #     characteristics = supabase_service.get_characteristics_by_link_id(links[0]['id'])
        #     print("Характеристики:", characteristics)

        # unparsed_links_sorted = supabase_service.get_unparsed_links_sorted(10)
        # if unparsed_links_sorted:
        #     for link in unparsed_links_sorted:
        #         print(link['date_parse'])

        # Получение видеокарт с ценой от 1000 до 5000
        # components = supabase_service.get_components_by_type_and_price(
            # component_type="videokarty",
            # min_price=1000,
            # max_price=100000
        # )
        # Вывод результатов
        # print("Найдено ", len(components))
        # for component in components:
        #     print(f"Название: {component['component_name']}")
        #     print(f"Цена: {component['price']}")
        # print(supabase_service.get_statistic())
        print_component_statistic(supabase_service.get_component_statistic())
    except Exception as e:
        print("Ошибка", e)

def get_components():

    supabase_service = SupabaseService()
    # Получение видеокарт с ценой от 1000 до 5000
    components = supabase_service.get_components_by_type_and_price_once(
            # component_type="videokarty",
            component_type="kulery-i-sistemy-okhlazhdeniia",
            min_price=0,
            max_price=1500,
            limit=100
    )
    if components:
    # Вывод результатов
        print("Найдено ", len(components))
        for component in components:
            print(f"Название: {component['component_name']}")
            print(f"Цена: {component['price']}")
            # print(component)
    else:
        print("Ничего не найдено")

def check_valid_components():
    supabase_service = SupabaseService()
    supabase_service.check_valid_components(100)

if __name__ == "__main__":
    # main()
    #check_components()
    # check_valid_components()
    #get_components()
    statitics()
