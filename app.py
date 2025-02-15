from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', name="name")


@app.route('/about')
def about():
    return render_template('about.html', name="name")


@app.route('/contact')
def contact():
    return render_template('contact.html',)

# new comment

@app.route('/result')
def result():
    result = {
        'user': 'name',
        'components': [
            {
                'component_name': 'Видеокарта KFA2 GeForce GTX 1060 EX, 6GB GDDR5, PCI-E, 6144MB, 192 Bit',
                'price': 1500.00,
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

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
