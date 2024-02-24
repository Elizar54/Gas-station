
import random
import math
import time

def translate_time(time): # Перевод количества минут в часы
    time_str = ''

    if time // 60 < 10:
        time_str += '0' + str(time // 60) + ':' 
        time = time % 60

        if time < 10:
            time_str += '0' + str(time)
        else:
            time_str += str(time)
    else:
        time_str += str(time // 60) + ':'
        time = time % 60

        if time < 10:
            time_str += '0' + str(time)
        else:
            time_str += str(time)

    return time_str


def client_time(demand, actual_time): # Время, в которое клиент освободит бензоколонку
    demand = int(demand)
    if demand <= 10:
        return translate_time(actual_time + 1)
    else:
        return translate_time(actual_time + math.ceil(demand / 10) + random.choice([1, 0]) * random.choice([-1, 1]))


def find_short_queue(avl_lst, aut_lst):
    min_queue = float('inf')

    for column in avl_lst: # проверяем колонки, на которых доступна эта марка топлива
        if aut_lst[int(column) - 1]['Очередь'] < min_queue and aut_lst[int(column) - 1]['Очередь'] < int(aut_lst[int(column) - 1]['Максимальная очередь']): # если очередь меньше минимальной и при этом не максимальна
            min_queue = aut_lst[int(column) - 1]['Очередь']
            min_que_col = column

    return min_que_col


clients = [] # Все клиенты
missed_clients = [] # Потерянные клиенты
automats = [] # Основная инфа по автоматам
arr_time_lst = [] # время прибытия клиентов
gas_price = {'АИ-80': 49, 'АИ-92': 50, 'АИ-95': 55, 'АИ-98': 68} # цены на бензин
gas_avail = {} # на каких колонках доступна каждая марка топлива
cash = 0 # выручка
sold_gas = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0} # объем проданного топлива по маркам
time_deoccup = {} # время, в которое освобождается каждый автомат в форме словаря
column_queue = {} # очередь с информацией о клиентах у каждой колонки
current_client = {} # клиенты, которые обслуживаются в данный момент у колонки

with open('input_automats.txt', encoding='utf-8') as file:
    for x in file:
        automat = {}
        seq = x.split()
        automat['Номер автомата'] = seq[0] # заполняем словарь по каждому автомату и формируем список из таких словарей
        automat['Максимальная очередь'] = seq[1]
        automat['Марки бензина'] = [x for x in seq[2:]]
        automat['Очередь'] = 0
        automats.append(automat)

        time_deoccup[seq[0]] = None # создаем ключ для каждого автомата в следующих трех словарях
        column_queue[seq[0]] = []
        current_client[seq[0]] = None

        for elem in automat['Марки бензина']: # формируем словарь, в котором будет информация о том, у какого автомата доступна каждая марка бензина
            if gas_avail.get(elem):
                gas_avail[elem].append(seq[0])
            else:
                gas_avail[elem] = [seq[0]]


with open('input_clients.txt', encoding='utf-8') as file:
    for x in file:
        clients.append(tuple(x.split())) # добавляем кортеж с инфой о клиенте в список

for client in clients:
    arr_time_lst.append(client[0]) # создаем список, содержащий время прибытия каждого клиента

for mnt in range(1440): # главный цикл
    time.sleep(0.5)
    curr_time = translate_time(mnt) # переводим минуты в часы

    for k, v in time_deoccup.items(): # идем по словарю освобождения колонок
        if curr_time == v: # если данная минута совпадает с одним из значений словаря освобождения колонки, то запускается следующий код
            automats[int(k) - 1]['Очередь'] -= 1 # уменьшаем очередь на единицу
            print(f'Клиент {current_client[automats[int(k) - 1]["Номер автомата"]]} покинул автозаправку в {curr_time}')
            print()
            
            time.sleep(0.3)

            if automats[int(k) - 1]['Очередь'] > 0: # смотрим, есть ли кто в очереди к этой колонке
                next_client_demand = column_queue[k][0][1] # смотрим, сколько литров нужно следующему клиенту
                next_deoccup_time = client_time(next_client_demand, mnt) # считаем время освобождения колонки этим клиентом
                time_deoccup[k] = next_deoccup_time # заменяем значение в словаре на время нового клиента
                print(f'В {curr_time} клиент {column_queue[k][0]} начал заправку.')
                print()
                current_client[k] = column_queue[k].pop(0) # уменьшаем очередь и записываем нового клиента в качестве обслуживаемого
            else: # если в очереди никого нет
                time_deoccup[k] = 0
            
            time.sleep(0.3)

    if curr_time in set(arr_time_lst): # смотрим, прибывает ли новый клиент в это время
        client = clients[arr_time_lst.index(curr_time)] # смотрим, что за клиент
        print(f'В {curr_time} новый клиент {client}', end=' ')
        gas_type = client[2] # смотрим, какой бензин ему нужен
        time.sleep(0.3)

        client_column = find_short_queue(gas_avail[gas_type], automats)
        if client_column != float('inf'): # если нашлось место в очереди
            automats[int(client_column) - 1]['Очередь'] += 1 # увеличиеваем очередь
            cash +=  int(client[1]) * gas_price[client[2]] # кэш на базе
            sold_gas[client[2]] += int(client[1]) # увеличиваем количество проданного топлива
            msg = f'встал в очередь к автомату №{automats[int(client_column) - 1]["Номер автомата"]}'
            print(msg)

            time.sleep(0.2)

            if automats[int(client_column) - 1]['Очередь'] == 1: #если в очереди никого нет
                current_client[automats[int(client_column) - 1]["Номер автомата"]] = client
                time_deoccup[client_column] = client_time(client[1], mnt)
            else: # если есть
                column_queue[client_column].append(client)

        else:  # если колонка не нашлась
            missed_clients.append(client)
            print('Клиент покинул заправку, не заправившись...')

        time.sleep(0.5)

        for elem in automats:
            msg = f'Автомат №{elem["Номер автомата"]} максимальная очередь: {elem["Максимальная очередь"]} Марки бензина: {elem["Марки бензина"]} ->{elem["Очередь"] * "*"}'
            print(msg)
            time.sleep(0.5)
        print()

# Итоги
print('Количество проданного бензина по маркам:')
for mark in sold_gas:
    print(f'Бензина марки {mark} продано {sold_gas[mark]} литров')

print(f'Общая выручка: {cash} рублей')
print('Количество потерянных клиентов:', len(missed_clients))
