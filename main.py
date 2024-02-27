
import random
import math
import time
import ru_local as ru

def translate_time(time): # Перевод количества минут в часы
    time_str = ''

    if time // 60 < 10:
        time_str += '0' + str(time // 60) + ':' 
        
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
        return translate_time(actual_time + 1), 1
    else:
        return translate_time(actual_time + math.ceil(demand / 10) + random.choice([1, 0]) * random.choice([-1, 1])), \
            math.ceil(demand / 10) + random.choice([1, 0]) * random.choice([-1, 1])


def find_short_queue(avl_lst, aut_lst):
    min_queue = float('inf')
    min_que_col = ''

    for column in avl_lst: # проверяем колонки, на которых доступна эта марка топлива
        if aut_lst[int(column) - 1][ru.queue] < min_queue and aut_lst[int(column) - 1][ru.queue] < int(aut_lst[int(column) - 1][ru.queue_max]): # если очередь меньше минимальной и при этом не максимальна
            min_queue = aut_lst[int(column) - 1][ru.queue]
            min_que_col = column

    return min_que_col


clients = [] # Все клиенты
missed_clients = [] # Потерянные клиенты
automats = [] # Основная инфа по автоматам
arr_time_lst = [] # время прибытия клиентов
gas_price = {ru.ai_80: 49, ru.ai_92: 50, ru.ai_95: 55, ru.ai_98: 68} # цены на бензин
gas_avail = {} # на каких колонках доступна каждая марка топлива
cash = 0 # выручка
sold_gas = {ru.ai_80: 0, ru.ai_92: 0, ru.ai_95: 0, ru.ai_98: 0} # объем проданного топлива по маркам
time_deoccup = {} # время, в которое освобождается каждый автомат в форме словаря
column_queue = {} # очередь с информацией о клиентах у каждой колонки
current_client = {} # клиенты, которые обслуживаются в данный момент у колонки

with open('input_automats.txt', encoding='utf-8') as file:
    for x in file:
        automat = {}
        seq = x.split()
        automat[ru.aut_num] = seq[0] # заполняем словарь по каждому автомату и формируем список из таких словарей
        automat[ru.queue_max] = seq[1]
        automat[ru.gas_types] = [x for x in seq[2:]]
        automat[ru.queue] = 0
        automats.append(automat)

        time_deoccup[seq[0]] = None # создаем ключ для каждого автомата в следующих трех словарях
        column_queue[seq[0]] = []
        current_client[seq[0]] = None

        for elem in automat[ru.gas_types]: # формируем словарь, в котором будет информация о том, у какого автомата доступна каждая марка бензина
            if elem in gas_avail:
                gas_avail[elem].append(seq[0])
            else:
                gas_avail[elem] = [seq[0]]


with open('input_clients.txt', encoding='utf-8') as file:
    for x in file:
        clients.append(tuple(x.split())) # добавляем кортеж с инфой о клиенте в список

for client in clients:
    arr_time_lst.append(client[0]) # создаем список, содержащий время прибытия каждого клиента

for mnt in range(1440): # главный цикл
    curr_time = translate_time(mnt) # переводим минуты в часы

    for k, v in time_deoccup.items(): # идем по словарю освобождения колонок
        if curr_time == v: # если данная минута совпадает с одним из значений словаря освобождения колонки, то запускается следующий код
            automats[int(k) - 1][ru.queue] -= 1 # уменьшаем очередь на единицу
            client_left_out = ''
            for x in current_client[automats[int(k) - 1][ru.aut_num]]:
                client_left_out += x + ' '
            print(f'{ru.client_up} {client_left_out} {ru.left_at} {curr_time}')
            print()
            
            #time.sleep(0.3)

            if automats[int(k) - 1][ru.queue] > 0: # смотрим, есть ли кто в очереди к этой колонке
                next_client_demand = column_queue[k][0][1] # смотрим, сколько литров нужно следующему клиенту
                next_deoccup_time = client_time(next_client_demand, mnt)[0] # считаем время освобождения колонки этим клиентом
                time_deoccup[k] = next_deoccup_time # заменяем значение в словаре на время нового клиента

                fueling_start_out = ''
                for x in column_queue[k][0]:
                    fueling_start_out += x + ' '
                print(f'{ru.at} {curr_time} {ru.client_low} {column_queue[k][0]} {fueling_start_out}')
                print()
                
                current_client[k] = column_queue[k].pop(0) # уменьшаем очередь и записываем нового клиента в качестве обслуживаемого
            else: # если в очереди никого нет
                time_deoccup[k] = 0
            

    if curr_time in set(arr_time_lst): # смотрим, прибывает ли новый клиент в это время
        client = clients[arr_time_lst.index(curr_time)] # смотрим, что за клиент
        time_for_client = client_time(client[1], mnt) 

        client_new_out = ''
        for x in client:
            client_new_out += x + ' '
        print(f'{ru.at} {curr_time} {ru.new_client} {client_new_out} {time_for_client[1]}', end=' ')

        gas_type = client[2] # смотрим, какой бензин ему нужен
        
        client_column = find_short_queue(gas_avail[gas_type], automats)

        if client_column != '': # если нашлось место в очереди
            automats[int(client_column) - 1][ru.queue] += 1 # увеличиеваем очередь
            cash += int(client[1]) * gas_price[client[2]] # кэш на базе
            sold_gas[client[2]] += int(client[1]) # увеличиваем количество проданного топлива
            #time.sleep(0.2)

            if automats[int(client_column) - 1][ru.queue] == 1: # если в очереди никого нет
                current_client[automats[int(client_column) - 1][ru.aut_num]] = client
                time_deoccup[client_column] = time_for_client[0]
            else: # если есть
                column_queue[client_column].append(client)

            msg_out = ''
            for x in automats[int(client_column) - 1][ru.aut_num]:
                msg_out += x + ' '
            msg = f'{ru.queue_entry} {msg_out}'
            print(msg)

        else:  # если колонка не нашлась
            missed_clients.append(client)
            print(ru.client_left)

        #time.sleep(0.5)

        msg_gas_types_out = ''
        for elem in automats:
            for x in elem[ru.gas_types]:
                msg_gas_types_out += x + ' '
            msg = f'{ru.aut_num_msg}{elem[ru.aut_num]} {ru.queue_max_msg} {elem[ru.queue_max]} {ru.gas_types}: {msg_gas_types_out}->{elem[ru.queue] * "*"}'
            print(msg)
            
        print()

# Итоги
print(ru.sold_gas_vol)
for mark in sold_gas:
    print(f'{ru.gas_type} {mark} {ru.sold} {sold_gas[mark]} {ru.litres}')

print(f'{ru.total_revenue} {cash} {ru.rubles}')
print(ru.missed_clients_qnt, len(missed_clients))
