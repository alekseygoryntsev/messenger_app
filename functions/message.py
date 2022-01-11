#!/usr/bin/env python
# -*- coding: utf-8 -*-

#функции, связанные с отправкой/приемом сообщений

import json
from functions.config import *
import time
import logging
import log.client_log_config
import log.server_log_config
from log.decorators import Log_Server
from log.decorators import Log_Client
import logging
import threading
from meta import ClientMeta
from client_db import ClientBigData
# серверный логгер
loggerserv = logging.getLogger('serverside')
# клиентский логгер
loggerclient = logging.getLogger('clientside')
logclient = Log_Client(loggerclient)
logserv = Log_Server(loggerserv)

#----------------ПРИЁМ СООБЩЕНИЙ ОТ СЕРВЕРА
# @logclient
def receive_message (clientside):
    datareceive = clientside.recv(1024)                   #получаем данные от сервера
    if isinstance(datareceive, bytes):           #проверяем, что данные относятся к типу данных bytes
        response_message = datareceive.decode('utf-8')       #bytes -> в JSON
        message2receive = json.loads(response_message)       #JSON -> в юникод
        if isinstance(message2receive, dict):
            # Возвращаем сообщение
            # logthis = 'args: ({},) = {}'.format(message2receive, message2receive)
            # loggerclient.info('{} - {} - {}'.format(logthis, receive_message.__name__, __name__))
            loggerclient.info("Клиент получил данные от севера")
            return message2receive
        else:
            # Нам прислали неверный тип
            loggerclient.info(TypeError)
            raise TypeError
    else:
        raise TypeError                            #иначе ошибка неверный тип данных

def receive_message_user_list (clientside):
    datareceive = clientside.recv(100000)                   #получаем данные от сервера
    if isinstance(datareceive, bytes):           #проверяем, что данные относятся к типу данных bytes
        response_message = datareceive.decode('utf-8')       #bytes -> в JSON
        message2receive = json.loads(response_message)       #JSON -> в юникод
        if isinstance(message2receive, dict):
            # Возвращаем сообщение
            # logthis = 'args: ({},) = {}'.format(message2receive, message2receive)
            # loggerclient.info('{} - {} - {}'.format(logthis, receive_message.__name__, __name__))
            loggerclient.info("Клиент получил данные от севера")
            return message2receive
        else:
            # Нам прислали неверный тип
            loggerclient.info(TypeError)
            raise TypeError
    else:
        raise TypeError                            #иначе ошибка неверный тип данных

#----------------ОТПРАВКА СООБЩЕНИЙ СЕРВЕРУ
# @logclient
def send_message (sock, message_dict):
    if isinstance(message_dict, dict):             #проверяем, что данные относятся к типу данных dict
        message = json.dumps(message_dict)         #Словарь -> в JSON
        message2send = message.encode('utf-8')     #JSON -> в байты
        sock.send(message2send)                   #Отправляем данные
        # logthis = '= {}'.format(message)
        # loggerclient.info('{} - {} - {}'.format(logthis, send_message.__name__, __name__))
    else:
        loggerclient.info(TypeError)
        raise TypeError                            #Иначе ошибка "Неверный тип данных"


#----------------ОТПРАВКА КЛИЕНТУ НА ЗАПРОС PRESENCE-СООБЩЕНИЯ
@logserv
def presence_response(presence_message):
    if ACTION in presence_message and \
                    presence_message[ACTION] == PRESENCE and \
                    TIME in presence_message and \
            isinstance(presence_message[TIME], float):
        # Если всё хорошо шлем ОК
        return {RESPONSE: 200}
    else:
        # Шлем код ошибки
        return {RESPONSE: 400, ERROR: 'Не верный запрос'}


#----------------ПОЛУЧЕНИЕ КЛИЕНТОМ ОТВЕТА СЕРВЕРА НА PRESENCE

def receive_message_presence(sock):
    load_answer = sock.recv(100000)
    answer = load_answer.decode('utf-8')
    loggerclient.info('Клиент получил ответ на запрос presence')
    return answer

