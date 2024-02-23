
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
        return translate_time(actual_time + math.ceil(demand / 5) + random.choice([1, 0]) * random.choice([-1, 1]))
    

clients = [] # Все клиенты
missed_clients = [] # Потерянные клиенты
automats = [] # Основная инфа по автоматам
arr_time_lst = [] # время прибытия клиентов
gas_price = {'АИ-80': 49, 'АИ-92': 50, 'АИ-95': 55, 'АИ-98': 68} # цены на бензин
gas_avail = {} # на каких колонках доступна каждая марка топлива
cash = 0 # выручка
sold_gas = {'АИ-80': 0, 'АИ-92': 0, 'АИ-95': 0, 'АИ-98': 0} # объем проданного топлива по маркам
time_deoccup = {} # время, в которое освобождается каждый автомат 
column_queue = {} # очередь с информацией о клиентах у каждой колонки
current_client = {} # клиенты, которые обслуживаются в данный момент у колонки

with open('input_automats.txt', encoding='utf-8') as file:
    for x in file:
        automat = {}
        seq = x.split()
        automat['Номер автомата'] = seq[0]
        automat['Максимальная очередь'] = seq[1]
        automat['Марки бензина'] = [x for x in seq[2:]]
        automat['Очередь'] = 0
        automats.append(automat)
        time_deoccup[seq[0]] = None
        column_queue[seq[0]] = []
        current_client[seq[0]] = None

        for elem in automat['Марки бензина']:
            if gas_avail.get(elem):
                gas_avail[elem].append(seq[0])
            else:
                gas_avail[elem] = [seq[0]]


with open('input_clients.txt', encoding='utf-8') as file:
    for x in file:
        clients.append(tuple(x.split()))

for client in clients:
    arr_time_lst.append(client[0])

for mnt in range(1000, 1440):
    time.sleep(0.5)
    curr_time = translate_time(mnt)

    for k, v in time_deoccup.items():
        if curr_time == v:
            automats[int(k) - 1]['Очередь'] -= 1
            print(f'Клиент {current_client[automats[int(k) - 1]["Номер автомата"]]} покинул автозаправку в {curr_time}')
            print()
            
            time.sleep(0.3)

            if automats[int(k) - 1]['Очередь'] > 0:
                next_client_demand = column_queue[k][0][1]
                next_deoccup_time = client_time(next_client_demand, mnt)
                time_deoccup[k] = next_deoccup_time
                print(time_deoccup)
                print(f'В {curr_time} клиент {column_queue[k][0]} начал заправку.')
                print()
                current_client[k] = column_queue[k].pop(0)
            else:
                time_deoccup[k] = 0
            
            time.sleep(0.3)

    if curr_time in set(arr_time_lst):
        client = clients[arr_time_lst.index(curr_time)]
        print(f'В {curr_time} новый клиент {client}', end=' ')
        gas_type = client[2]

        for column in gas_avail[gas_type]:
            if automats[int(column) - 1]['Очередь'] < int(automats[int(column) - 1]['Максимальная очередь']):
                automats[int(column) - 1]['Очередь'] += 1
                cash +=  int(client[1]) * gas_price[client[2]]
                sold_gas[client[2]] += int(client[1])
                msg = f'встал в очередь к автомату №{automats[int(column) - 1]["Номер автомата"]}'
                print(msg)

                if automats[int(column) - 1]['Очередь'] == 1:
                    current_client[automats[int(column) - 1]["Номер автомата"]] = client
                    time_deoccup[column] = client_time(client[1], mnt)
                else:
                    column_queue[column].append(client)
                break
        else:
            missed_clients.append(client)
            print('Клиент покинул заправку, не заправившись...')

        time.sleep(0.5)

        for elem in automats:
            msg = f'Автомат №{elem["Номер автомата"]} максимальная очередь: {elem["Максимальная очередь"]} Марки бензина: {elem["Марки бензина"]} ->{elem["Очередь"] * "*"}'
            print(msg)
            time.sleep(0.5)
        print()

# Итоги
print('Количество проданного бензина по маркам:', end='')
for mark in sold_gas:
    print(f'Бензина марки {mark} продано {sold_gas[mark]} литров')

print('Общая выручка:', cash)
print('Количество потерянных клиентов:', len(missed_clients))
