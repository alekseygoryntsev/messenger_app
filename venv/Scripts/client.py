#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from socket import *
#import json
from functions.message import *
import logging
import log.client_log_config
loggerclient = logging.getLogger('clientside')
#------------------------------------РАБОТА С СООБЩЕНИЯМИ

def read_messages(client): #-----------------СКРИПТ ТОЛЬКО ДЛЯ ЧТЕНИЯ СООБЩЕНИЙ
    """
    Клиент читает входящие сообщения в бесконечном цикле
    :param client: сокет клиента
    """
    while True:
        print('Read Only')
        message = receive_message(client)
        print(message)
        # там должно быть сообщение всем
        print(message[MESSAGE])

def create_message(message_to, text, account_name='Guest'):
    return {ACTION: MSG, TIME: time.time(), TO: message_to, FROM: account_name, MESSAGE: text}

def write_messages(client): #-----------------СКРИПТ ТОЛЬКО ДЛЯ ПЕРЕДАЧИ СООБЩЕНИЙ
    """Клиент пишет сообщение в бесконечном цикле"""
    while True:
        # Вводим сообщение с клавиатуры
        text = input('Write this')
        # Создаем сообщение формата JSON
        message = create_message('#all', text)
        #print(client)
        # отправляем на сервер
        send_message(client, message)
#------------------------------------------ЗАПУСК
if __name__ == '__main__':
    clientside = socket(AF_INET, SOCK_STREAM)     # создаем аналогичный сокет, как у сервера
# Пытаемся получить параметры скрипта
    # Получаем аргументы скрипта
    #------------ip-адрес-----------#
    # если ip-адрес указан в параметрах -p <addr>
    try:
        addr = sys.argv[1]
    # если ip-адрес не указан в параметрах
    except IndexError:
        addr = 'localhost'
        loggerclient.info(IndexError)
    #--------------порт-------------#
    # если порт указан в параметрах
    try:
        port = int(sys.argv[2])
    # если порт не указан в параметрах
    except IndexError:
        port = 7777
        loggerclient.info(IndexError)
    # если порт - не целое число
    except ValueError:
        loggerclient.info(ValueError)
        #print('Порт должен быть целым числом')
        sys.exit(0)
    # ДАННЫЕ ПОЛУЧИЛИ -> СОЕДИНЯЕМСЯ С СЕРВЕРОМ
    # Соединиться с сервером

    clientside.connect(('localhost', 7777))       # коннектимся с сервером
    presence = send_presence()                    # создаем приветствие
    send_message(clientside,presence)             # отправляем приветствие
    response_from_server = receive_message_presence(clientside)                   # получаем сообщение
    print(response_from_server)



# message = json.dumps(presence)                   # Переводим словарь в формат json
# message_to_bytes = message.encode('utf-8')       # Пакуем это дело в байты
# s.send(message_to_bytes)                         # Отправляем серверу
#
#
# data = s.recv(1024)                    # Принимаем не более 1024 байт данных
# s.close()                              # закрываем соединение
# print(data.decode('utf-8'))            # получаем данные, декодировав байты