
import unittest
from functions.config import *
from functions.message import *
from client import *
import socket


#------------------------------------------------------------ЗАГЛУШКИ ДЛЯ СОКЕТА
class ClientSocketPresence():
    """Класс-заглушка для операций с сокетом"""

    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        pass

    def recv(self, n):
        # Наш класс заглушка будет всегда отправлять одинаковый ответ при вызов sock.recv
        message2 = OK
        message = json.dumps(message2)
        message2send = message.encode('utf-8')
        return message2send

    def send(self, message2send):
        # можно переопределить метод send просто pass
        pass

class ClientSocketMessage():
    """Класс-заглушка для операций с сокетом"""

    def __init__(self, sock_type=socket.AF_INET, sock_family=socket.SOCK_STREAM):
        pass

    def recv(self, n):
        # Наш класс заглушка будет всегда отправлять одинаковый ответ при вызов sock.recv
        message2 = {'response': 200}
        message = json.dumps(message2)
        message2send = message.encode('utf-8')
        return message2send

    def send(self, bmessage):
        # можно переопределить метод send просто pass
        pass


#------------------------------------------------------------CLIENT SIDE
#
#------Проверка отправки presence-сообщения
#
class TestSendPresence(unittest.TestCase):

    def test_send_presence_action(self):                          # проверяем корректный атрибут action
        self.assertEqual(send_presence()['action'], "presence")

    def test_send_presence_param(self):                           # проверяем, что корректно передаем имя клиента
        self.assertEqual(send_presence('test_user_name')["user"]["account_name"], 'test_user_name')

    def test_send_presence_time(self):                          # проверяем разницу во времени
        self.assert_(abs(send_presence()['time'] - time.time()) < 0.1)

    def test_send_presence_acc_int(self):                       # проверяем, чтобы тип аккаунта не был числом
        with self.assertRaises(TypeError):
            send_presence(200)

    def test_send_presence_acc_none(self):                     # проверяем, чтобы тип аккаунта не был None
        with self.assertRaises(TypeError):
            send_presence(None)

    def test_send_presence_acc_toolong(self):                  # Проверяем длину аккаунта (не более 25 символов)
        self.assert_(len(send_presence()["user"]["account_name"]) < 26)          #26 символов

#
#------Получение клиентом ответа на precence-сообщение

class TestReceiveMessagePresence(unittest.TestCase):
    def test_receive_message_presence(self):
        sock = ClientSocketPresence()
        self.assertEqual(receive_message_presence(sock), '200')

#--------Отправка сообщений серверу (send_message)

class TestSendMessage(unittest.TestCase):
    def test_send_message(self):
        # подменяем настоящий сокет нашим классом заглушкой
        # зоздаем сокет, он уже был подменен
        sock = ClientSocketMessage()
        # т.к. возвращаемого значения нету, можно просто проверить, что метод отрабатывает без ошибок
        self.assert_(send_message(sock, {'test': 'test'}) is None)
        # и проверяем, чтобы обязательно передавали словарь на всякий пожарный
        with self.assertRaises(TypeError):
            send_message(sock, 'test')

#---------------------------------------------------SERVER SIDE

#----Получение сообщений от клиента (receive_message)

class TestReceiveMessage(unittest.TestCase):
    def test_receive_message(self):
        # подменяем настоящий сокет нашим классом заглушкой
        sock = ClientSocketMessage()
        # теперь можем протестировать работу метода
        self.assertEqual(receive_message(sock), {'response': 200})


if __name__ == "__main__":
    unittest.main()