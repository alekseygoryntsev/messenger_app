#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import socket
from functions.message import *
from settings import *
import logging
import threading
import select
import log.server_log_config
from descriptors import CheckPort
from meta import ServerMeta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer
loggerserv = logging.getLogger('serverside') #серверный логгер
from server_interface import *
from server_db import *
new_connection = False
conflag_lock = threading.Lock()

class Server(threading.Thread, metaclass=ServerMeta):
    port = CheckPort()

    def __init__(self, addr, port, database):  # сетап сервера

        self.addr = addr
        self.port = port
        self.database = database
        self.clients = []  # список клиентских сокетов
        self.names = {}
        # Конструктор предка
        super().__init__()

    def connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создается сокет протокола TCP
        s.bind((self.addr, self.port))  # Присваиваем ему порт 7777
        s.settimeout(5)  # Таймаут на выполнение функций приёма/передачи
        self.sock = s
        self.sock.listen(20)  # Максимальное количество одновременных запросов

    try:
        addr = sys.argv[1]
    # если ip-адрес не указан в параметрах
    except IndexError:
        addr = ''
    # --------------порт-------------#
    # если порт указан в параметрах
    try:
        port = int(sys.argv[2])
    # если порт не указан в параметрах
    except IndexError:
        port = 7777
    # если порт - не целое число
    except ValueError:
        loggerserv.info(ValueError)
        # print('Порт должен быть целым числом')
        sys.exit(0)

    def run(self):
        self.connection()
        while True:
            try:  # ------------------------------РУКОПОЖАТИЕ
                client, addr = self.sock.accept()  # Проверка подключений
                # receive_presence(s)
                # получаем сообщение от клиента
                presence = receive_message(client)
                print (presence)
                # формируем ответ
                client_name = presence['user']['account_name']
                print("Запрос отправлен")
                response = presence_response(presence)
                send_message(client, response)
                with conflag_lock:
                    new_connection = True
            except OSError as e:
                pass  # timeout вышел
            else:
                print("Получен запрос на соединение от %s" % str(
                    addr))  # вывод и форматирование переменной adr в строку
                self.names[client_name] = client
                self.database.user_login(client_name, 'localhost', 7777)
                print(client)
                print("Запрос мы точно получаем")
                # Добавляем клиента в список
                self.clients.append(client)
                print("Проверка списка клиентов")
                print(self.clients)
                print("Список заполняется")
            finally:
                # Проверить наличие событий ввода-вывода
                wait = 5
                r = []
                w = []

            try:
                r, w, e = select.select(self.clients, self.clients, [], wait)
            except:
                pass

            def read_requests(read_from_clients, all_clients):  # читаем клиенткие сообщения
                # Список входящих сообщений
                messages = []

                for sock in read_from_clients:  # парсим клиентские сокеты в списке "на чтение"
                    try:
                        message = receive_message(sock)
                        messages.append((message, sock))
                    except:
                        print(f'Клиент {sock.fileno()} {sock.getpeername()} отключился')
                        self.database.user_logout(client_name)
                        all_clients.remove(sock)


                return messages

            def write_responses(messages):  # ответы клиентам на их запросы
                for message, sender in messages:
                    if message['action'] == MSG:
                        to = message['to']
                        sock = self.names[to]
                        msg = message['message']
                        send_message(sock, message)
                    if message['action'] == KWNOWNUSERS:
                        response = RESPONSE_202
                        response[LIST_INFO] = [user[0] for user in self.database.users_list()]
                        send_message(client, response)
                    if message['action'] == CONTACTLIST:
                        response = RESPONSE_202
                        response[LIST_INFO] = self.database.get_contacts(message[USER])
                        send_message(client, response)


            requests = read_requests(r, self.clients)  # Получаем входящие сообщения
            write_responses(requests)  # Выполняем отправку сообщений


def go():
    database = ServerBigData()
    server = Server(addr=SERVER_ADDR, port=SERVER_PORT, database=database)
    server.daemon = True
    server.start()
    GUI = QApplication(sys.argv)
    interface = ServerGUI()

    def view_config():
        global stat_window
        stat_window = ConfigWindow()
        stat_window.db_path.insert(SERVER_DB_NAME)
        stat_window.port.insert(str(SERVER_PORT))
        stat_window.ip.insert(SERVER_ADDR)

    def view_history():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def view_users():
        global stat_window
        stat_window = UsersWindow()
        stat_window.user_table.setModel(create_model_users(database))
        stat_window.user_table.resizeColumnsToContents()
        stat_window.user_table.resizeRowsToContents()
        stat_window.show()



    # Связываем кнопки с процедурами
    interface.config_button.triggered.connect(view_config)
    interface.history_button.triggered.connect(view_history)
    interface.users_button.triggered.connect(view_users)
    GUI.exec_()



if __name__ == '__main__':
    go()
