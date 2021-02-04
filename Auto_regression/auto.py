import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

data_url = 'http://www.gks.ru/free_doc/new_site/business/trans-sv/t3-2.xls'
df = pd.read_excel(data_url, skiprows=2)

index_to_del = [0, 1, 20, 24, 25, 33, 42, 50, 65, 69, 70, 71, 72, 74, 85, 97, 98]
df.drop(index_to_del, axis=0, inplace=True)

columns_to_leave = ['Unnamed: 0', 2018]
df_new = df[columns_to_leave]

df_new.rename(columns={'Unnamed: 0': 'Region', 2018: 'RTFR_2018'}, inplace=True)

data_url = 'http://www.gks.ru/free_doc/new_site/business/trans-sv/t3-4.xls'
df_2 = pd.read_excel(data_url, skiprows=2)

index_to_del = [0, 1, 20, 24, 25, 33, 42, 50, 65, 69, 70, 71, 72, 74, 85, 97, 98]
df_2.drop(index_to_del, axis=0, inplace=True)

columns_to_leave = ['Unnamed: 0', 2018]
df_2_new = df_2[columns_to_leave]

df_2_new.rename(columns={'Unnamed: 0': 'Region', 2018: 'Cars_2018'}, inplace=True)

print(df_new)
print(df_2_new)

df = pd.merge(df_new, df_2_new, on='Region')

df.to_csv('Cars_and_deaths.csv', sep=';')

# Организуем пространство графика
fig, ax = plt.subplots()

# Считываем индексы таблицы DF (Датаферйма)
indices = df.index
# Находим конечный индекс
max_index = indices.get_indexer(indices)[-1]
# Инициализируем пару пустых массивов
reg_x = []
reg_y = []

# Проходимся по таблице
for i in range(0, max_index + 1):
    # Считываем данные из таблицы
    x = float(df.loc[indices[i], 'Cars_2018'])
    y = float(df.loc[indices[i], 'RTFR_2018'])
    # Сохраняем координаты точек
    reg_x.append(x)
    reg_y.append(y)
    # Добавляем точку на график
    ax.scatter(x, y,
               alpha=0.7, edgecolors='none')

# Делаем регрессию
r = stats.linregress(reg_x, reg_y)

# Выводим данные по регресси (если интересно)
print(r)

# Переводим обычные массивы в массивы numpy,
# чтобы потом можно было умножать сразу весь массив
# на кожэффициент типа float
np_y = np.array(reg_y)
np_x = np.array(reg_x)

# Дорисовываем регрессию на график
ax.plot(np_x, r.intercept + r.slope*np_x, 'r', label='line regression')

# Активируем сетку на графике
ax.grid(True)

# Подписи к графику
ax.set_title('Зависимость смертей на дорогах от числа грузовых автомобилей', fontsize=15)
ax.set_xlabel('Cars 2018', fontsize=15)
ax.set_ylabel('RTFR 2018', fontsize=15)
ax.legend(fontsize=10)
# Показываем график
plt.show()

# Можем сохранить в пдф
# plt.savefig("Plot.pdf")
