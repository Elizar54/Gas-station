
import random
import math
import time
import ru_local as ru

def translate_time(time):
    time_str = ''

    if time // 60 < 10:
        time_str += '0' + str(time // 60) + ':' 
        
    else:
        time_str += str(time // 60) + ':'
    
    time %= 60

    if time < 10:
        time_str += '0' + str(time)
    else:
        time_str += str(time)

    return time_str


def client_time(demand, actual_time): 
    demand = int(demand)
    if demand <= 10:
        return translate_time(actual_time + 1), 1
    else:
        return translate_time(actual_time + math.ceil(demand / 10) + random.choice([1, 0]) * random.choice([-1, 1])), \
            math.ceil(demand / 10) + random.choice([1, 0]) * random.choice([-1, 1])


def find_short_queue(avl_lst, aut_lst):
    min_queue = float('inf')
    min_que_col = ''

    for column in avl_lst: 
        if aut_lst[int(column) - 1][ru.queue] < min_queue and aut_lst[int(column) - 1][ru.queue] < int(aut_lst[int(column) - 1][ru.queue_max]):
            min_queue = aut_lst[int(column) - 1][ru.queue]
            min_que_col = column

    return min_que_col


clients = []
missed_clients = [] 
automats = [] 
arr_time_lst = [] 
gas_price = {ru.ai_80: 49, ru.ai_92: 50, ru.ai_95: 55, ru.ai_98: 68} 
gas_avail = {} 
cash = 0 
sold_gas = {ru.ai_80: 0, ru.ai_92: 0, ru.ai_95: 0, ru.ai_98: 0}
time_deoccup = {} 
column_queue = {} 
current_client = {} 

with open('input_automats.txt', encoding='utf-8') as file:
    for x in file:
        automat = {}
        seq = x.split()
        automat[ru.aut_num] = seq[0]
        automat[ru.queue_max] = seq[1]
        automat[ru.gas_types] = seq[2:]
        automat[ru.queue] = 0
        automats.append(automat)

        time_deoccup[seq[0]] = None 
        column_queue[seq[0]] = []
        current_client[seq[0]] = None

        for elem in automat[ru.gas_types]: 
            if elem in gas_avail:
                gas_avail[elem].append(seq[0])
            else:
                gas_avail[elem] = [seq[0]]


with open('input_clients.txt', encoding='utf-8') as file:
    for x in file:
        clients.append(tuple(x.split())) 

for client in clients:
    arr_time_lst.append(client[0]) 

for mnt in range(1440): 
    curr_time = translate_time(mnt) 

    for k, v in time_deoccup.items(): 
        if curr_time == v: 
            automats[int(k) - 1][ru.queue] -= 1
            client_left_out = ''

            for x in current_client[automats[int(k) - 1][ru.aut_num]]:
                client_left_out += x + ' '

            print(f'{ru.client_up} {client_left_out}{ru.left_at} {curr_time}')
            print()

            if automats[int(k) - 1][ru.queue] > 0: 
                next_client_demand = column_queue[k][0][1] 
                next_deoccup_time = client_time(next_client_demand, mnt)[0] 
                time_deoccup[k] = next_deoccup_time

                fueling_start_out = ''

                for x in column_queue[k][0][1:]:
                    fueling_start_out += x + ' '

                print(f'{ru.at} {curr_time} {ru.client_low} {fueling_start_out}{ru.fueling_start}')
                print()
                
                current_client[k] = column_queue[k].pop(0) 
            else: 
                time_deoccup[k] = 0
            

    if curr_time in set(arr_time_lst): 
        client = clients[arr_time_lst.index(curr_time)] 
        time_for_client = client_time(client[1], mnt) 
        client_new_out = ''

        for x in client:
            client_new_out += x + ' '

        print(f'{ru.at} {curr_time} {ru.new_client} {client_new_out}{time_for_client[1]}', end=' ')

        gas_type = client[2] 
        
        client_column = find_short_queue(gas_avail[gas_type], automats)

        if client_column != '': 
            automats[int(client_column) - 1][ru.queue] += 1 
            cash += int(client[1]) * gas_price[client[2]] 
            sold_gas[client[2]] += int(client[1]) 

            if automats[int(client_column) - 1][ru.queue] == 1: 
                current_client[automats[int(client_column) - 1][ru.aut_num]] = client
                time_deoccup[client_column] = time_for_client[0]
            else: 
                column_queue[client_column].append(client)

            msg_out = ''
            for x in automats[int(client_column) - 1][ru.aut_num]:
                msg_out += x + ' '
            msg = f'{ru.queue_entry}{msg_out}'
            print(msg)

        else:  
            missed_clients.append(client)
            print(ru.client_left)

        for elem in automats:
            msg_gas_types_out = ''
            for x in elem[ru.gas_types]:
                msg_gas_types_out += x + ' '
            msg = f'{ru.aut_num_msg}{elem[ru.aut_num]} {ru.queue_max_msg} {elem[ru.queue_max]} {ru.gas_types}: {msg_gas_types_out}->{elem[ru.queue] * "*"}'
            print(msg)
            
        print()

print(ru.sold_gas_vol)

for mark in sold_gas:
    print(f'{ru.gas_type} {mark} {ru.sold} {sold_gas[mark]} {ru.litres}')

print(f'{ru.total_revenue} {cash} {ru.rubles}')
print(ru.missed_clients_qnt, len(missed_clients))

lost_revenue = 0
for client in missed_clients:
    lost_revenue += client[1] * gas_price[client[2]]

print(ru.lost_revenue, lost_revenue)
