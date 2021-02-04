import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import os.path

# Переменные для управления выводом
print_info = save_csv = save_pdf = False

region_dict = {
    'kamchatskiy_kray': 'Камчатский край', 'primorskiy_kray': 'Приморский край',
    'kaluzhskaya_oblast': 'Калужская область', 'moskovskaya_oblast': 'Московская область',
    'kaliningradskaya_oblast': 'Калининградская область', 'pskovskaya_oblast': 'Псковская область',
    'kareliya': 'Республика Карелия', 'ryazanskaya_oblast': 'Рязанская область',
    'tyumenskaya_oblast': 'Тюменская область', 'moskva': 'Москва',
    'hanty-mansiyskiy_ao': 'Ханты-Мансийский автономный округ — Югра', 'sankt-peterburg': 'Санкт-Петербург',
    'orenburgskaya_oblast': 'Оренбургская область', 'murmanskaya_oblast': 'Мурманская область',
    'sahalinskaya_oblast': 'Сахалинская область', 'hakasiya': 'Республика Хакасия',
    'belgorodskaya_oblast': 'Белгородская область', 'krasnodarskiy_kray': 'Краснодарский край',
    'tverskaya_oblast': 'Тверская область', 'leningradskaya_oblast': 'Ленинградская область',
    'smolenskaya_oblast': 'Смоленская область',
    'orlovskaya_oblast': 'Орловская область', 'novgorodskaya_oblast': 'Новгородская область',
    'samarskaya_oblast': 'Самарская область', 'magadanskaya_oblast': 'Магаданская область'
}


# проверяет корректность ввода
def check_input():
    mistake = True
    correct_values = ['y', 'n']
    while mistake:
        user_input = str(input()).casefold()
        if user_input in correct_values:
            return user_input
        else:
            print('Wrong input, try again!')


def get_autoru_data(regions):
    if os.path.isfile('Auto_ru_cache.csv'):
        dat = pd.read_csv('Auto_ru_cache.csv', sep=';')
    else:

        url_start = 'https://auto.ru/'
        url_end = '/cars/all/'

        car_for_sale = []
        all_list = []
        replace_list = ['Â', 'ÐÐ¾ÐºÐ°Ð·Ð°ÑÑ ', ' Ð¿ÑÐµÐ´Ð»Ð¾Ð¶ÐµÐ½Ð¸Ñ', ' ', '\xa0', 'Ð¿Ñ\x80ÐµÐ´Ð»Ð¾Ð¶ÐµÐ½Ð¸Ð¹',
                        '1Ð¿Ñ\x80ÐµÐ´Ð»Ð¾Ð¶ÐµÐ½Ð¸Ðµ']
        region_list = list(regions.keys())

        for region in region_list:
            # Делаем запрос к сайту
            try:
                page = requests.get(url_start + region + url_end)
            except:
                print(f'Can\'t get data about {region}')

            # Приводим к более менее опрятному виду
            soup = BeautifulSoup(page.text, 'html.parser')
            # Находим Просмотры
            html = soup.find_all('span', {'class': 'ButtonWithLoader__content'})
            num = str(html[0].text)

            print(region)

            for char in replace_list:
                num = num.replace(char, '')
            car_for_sale.append(int(num))

        for i in range(len(car_for_sale)):
            all_list.append([regions[region_list[i]], car_for_sale[i]])

        # Сохраняем в датафрейм
        dat = pd.DataFrame(all_list, columns=['Регион', 'Число машин на продажу'])
        dat.set_index('Регион').to_csv('Auto_ru_cache.csv', sep=';')

    # Сортируем
    dat.sort_values(by=['Число машин на продажу'], ascending=False, inplace=True)

    return dat


def get_wiki_data():
    # ссылочка на страницу для парсинга
    url = 'https://ru.wikipedia.org/wiki/%D0%90%D0%B2%D1%82%D0%BE%D0%BC' \
          '%D0%BE%D0%B1%D0%B8%D0%BB%D0%B8%D0%B7%D0%B0%D1%86%D0%B8%D1%8F'

    # Делаем запрос к сайту
    try:
        page = requests.get(url)
    except:
        print('Can\'t get data')

    # Приводим к более менее опрятному виду
    soup = BeautifulSoup(page.text, 'html.parser')
    # Находим таблицу
    soup = soup.find_all('table', {'class': 'standard sortable'})
    # Берём из таблицы список областей
    region = soup[0].find_all('a')

    region_list = []
    for i in region:
        if i.text[0] != '[':
            region_list.append(i.text)

    # Находим номер последней интересующей нас область
    region_list.index('Тамбовская область')
    # Забираем данные из таблицы
    data = soup[0].find_all('td', {'align': 'right'})
    # Сохраняем их в список
    data_list = []
    for i in data:
        data_list.append(i.text.replace(',', '.').replace('\n', '').replace('…', ''))

    i = 0
    j = 0

    all_list = []

    # Создаём список данных для датафрейма
    while j <= 27:
        tmp = [region_list[j]]
        for x in range(10):
            if data_list[i + x] == '':
                tmp.append(np.nan)
            else:
                tmp.append(data_list[i + x])
        all_list.append(tmp)
        i += 10
        j += 1

    # Сохраняем в датафрейм
    dat = pd.DataFrame(all_list,
                      columns=['Регион', '1970',
                               '1985', '1993',
                               '1997', '2000',
                               '2002', '2010',
                               '2013', '2014',
                               '2016'])

    # Сортируем
    dat.sort_values(by=['2016'], ascending=False, inplace=True)

    region = dat['Регион']
    # Транспонируем таблицу
    dat = dat.T
    dat.columns = region
    dat.drop(['Регион'], axis=0, inplace=True)

    # Приводим к типу данных float
    dat = dat.astype('float')

    # Заполняем пустые знаяения
    dat = dat.interpolate()

    return dat


# Парсит эксель в датафрейм
def get_ross_data(path, colname):
    try:
        dat = pd.read_excel(path, skiprows=2)
    except:
        print('Can\'t read data_url')

    index_to_del = [0, 1, 20, 24, 25, 33, 42, 50, 65, 69, 70, 71, 72, 74, 85, 97, 98]
    dat.drop(index_to_del, axis=0, inplace=True)

    dat.rename(columns={'Unnamed: 0': 'Region', 2018: colname}, inplace=True)

    columns_to_leave = ['Region', colname]
    dat = dat[columns_to_leave]
    return dat


# Начало кода
# тут пользователь задаёт параметры работы программы
print('Hello, this is data visualization project \nLet\'s Start!')

print('Do you want to print info? (Y/N)')
answer = check_input()
if answer == 'y':
    print_info = True
else:
    print_info = False

print('Do you want to save csv? (Y/N)')
answer = check_input()
if answer == 'y':
    save_csv = True

    print('Do you want to name csv? (Y/N)')
    answer = check_input()
    if answer == 'y':
        print('Enter csv name:')
        csv_name = str(input())
    else:
        csv_name = 'motorization'

else:
    save_csv = False

print('Do you want to save pdf plot? (Y/N)')
answer = check_input()
if answer == 'y':
    save_pdf = True

    print('Do you want to name pdf? (Y/N)')
    answer = check_input()
    if answer == 'y':
        print('Enter pdf name:')
        pdf_name = str(input())
    else:
        pdf_name = 'motorization'

else:
    save_pdf = False

# Загрузка данных
# получаем данные росстата
dat_1 = get_ross_data('http://www.gks.ru/free_doc/new_site/business/trans-sv/t3-2.xls', 'RTFR_2018')
dat_2 = get_ross_data('http://www.gks.ru/free_doc/new_site/business/trans-sv/t3-4.xls', 'Cars_2018')
dat_ros = pd.merge(dat_1, dat_2, on='Region')
# Получаем данные из википедии
dat_wiki = get_wiki_data()
# Получае данные из автору.ру
dat_auto = get_autoru_data(region_dict)

# Организуем пространство графика
fig = plt.figure(figsize=(16, 26), dpi=150)

ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)

# Считываем индексы таблицы DAT (Датаферйма)
indices = dat_ros.index
# Находим конечный индекс
max_index = indices.get_indexer(indices)[-1]
# Инициализируем пару пустых массивов
reg_x = []
reg_y = []

# Проходимся по таблице
for i in range(0, max_index + 1):
    # Считываем данные из таблицы
    x = float(dat_ros.loc[indices[i], 'Cars_2018'])
    y = float(dat_ros.loc[indices[i], 'RTFR_2018'])
    # Сохраняем координаты точек
    reg_x.append(x)
    reg_y.append(y)
    # Добавляем точку на график
    ax1.scatter(x, y,
                alpha=0.7, edgecolors='none')

# Делаем регрессию
r = stats.linregress(reg_x, reg_y)

# Выводим данные по регресси (если интересно)

if print_info:
    print('\n', r)

# Переводим обычные массивы в массивы numpy,
# чтобы потом можно было умножать сразу весь массив
# на кожэффициент типа float
np_y = np.array(reg_y)
np_x = np.array(reg_x)

# Дорисовываем регрессию на график
ax1.plot(np_x, r.intercept + r.slope * np_x, 'r', label='line regression')
ax1.legend(fontsize=10)

# Активируем сетку на графике
ax1.grid(True)

# Подписи к графику
ax1.set_title('Зависимость смертности на дорогах от числа автомобилей', fontsize=15)
ax1.set_xlabel('Число автомобилей на дорогах', fontsize=15)
ax1.set_ylabel('Смертность от автомобилей', fontsize=15)

# Обрезаем таблицу из википедии для графика
dat_cut = dat_wiki.iloc[:, :15]

# Выводим на него данные
for name in dat_cut.columns:
    ax2.plot(range(10), dat_cut[name], linestyle='-', linewidth=2, label=name)

# Задаём значения для оси Х
ax2.set_xticks(range(10))
ax2.set_xticklabels(dat_wiki.index)

# Добавляем легенду
ax2.legend(fontsize=10, loc='upper left')

# Доабавляем сетку
ax2.grid(True)

# Добавляем подписи
ax2.set_ylabel('Число автомобилей на 1000 человек', fontsize=15)
ax2.set_xlabel('Год', fontsize=15)
ax2.set_title('Автомобилизация в России с 1970 по  2016', fontsize=15)

# Визуализируем данные с авто.ру
dat_auto_cut = dat_auto[dat_auto['Регион'].isin(dat_cut.columns)]

ax3.bar(dat_auto_cut['Регион'], dat_auto_cut['Число машин на продажу'], color='orangered')
ax3.set_title('Статистика объявлений Авто.ру по регионам', fontsize=20)
ax3.set_xlabel('Регионы', fontsize=15)
ax3.set_ylabel('Колличество объявлений', fontsize=15)
ax3.set_xticklabels(dat_auto_cut['Регион'], rotation=45, ha='right')

# выводи инфу о датафрейме
if print_info:
    print(dat_wiki.info())
    print(dat_auto.info())
    print(dat_ros.info())

# сохраняем пдф
if save_pdf:
    plt.savefig(pdf_name + '.pdf')

# сохраняем cs
if save_csv:
    dat_wiki.to_csv(csv_name + '_Wiki.csv', sep=';')
    dat_auto.to_csv(csv_name + '_Auto.csv', sep=';')
    dat_ros.to_csv(csv_name + '_Rosstat.csv', sep=';')

# Расстояние между графиками
plt.subplots_adjust(hspace=0.3)

plt.show()