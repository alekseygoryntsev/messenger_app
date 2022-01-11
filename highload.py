# тест приложения в режиме многопоточности

from subprocess import Popen, CREATE_NEW_CONSOLE
import time

# В переменную запишем все операции с процессами
process = []

# Запускаем цикл, который выполняется пока есть подключения
while True:
    user_request = input("For start server input start (start) / For close all process input close (close)")
    if user_request == 'start':
        #-----------------------------------СЕРВЕРНАЯ ЧАСТЬ
        process.append(Popen('python server.py',
                            creationflags=CREATE_NEW_CONSOLE)) # запускаем сервер, добавляем его в список процессов
        print('Server is RUN!')
        time.sleep(1)                                          # ждем секунду
        #-----------------------------------КЛИЕНТСКИЕ ПРИЛОЖЕНИЯ
        volume_clients_read = input("Введите количество клиентов: ")
        try:
            val = int(volume_clients_read)
        except ValueError:
            print("Введите числовое значение")
        else:
            for i in range (val):
                client_name = f'client{format(i)}'                # задаем имя клиента
                process.append(Popen('python -i client.py localhost 7777 {}'.format(client_name),
                                creationflags=CREATE_NEW_CONSOLE))
            print('Clients is RUN!')
    elif user_request == 'close':
        print(f'Количество процессов для завершения: {len(process)}')
        for all_process in process:
            print(f'Drop the {all_process}')
            all_process.kill()
        process.clear()
        print('Готово')
    else:
        print("Ошибка ввода. Введите start или close, чтобы начать")