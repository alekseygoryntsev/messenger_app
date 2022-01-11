#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QDialog, QListView, \
    QLabel, QComboBox, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from client_ui import Ui_MainClientWindow
import sys
import socket
from functions.message import *
import logging
import threading
from client_db import ClientBigData
loggerclient = logging.getLogger('clientside')

sock_lock = threading.Lock()
database_lock = threading.Lock()

class AddContactDialog(QDialog):
    def __init__(self, database, account_name):
        super().__init__()
        self.database = database
        self.account_name = account_name

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для добавления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для добавления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Добавить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        # Заполняем список возможных контактов
        self.possible_contacts_update()

    # Заполняем список возможных контактов разницей между всеми пользователями и
    def possible_contacts_update(self):
        self.selector.clear()
        # множества всех контактов и контактов клиента
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        # Удалим сами себя из списка пользователей, чтобы нельзя было добавить самого себя
        users_list.remove(self.account_name)
        self.selector.addItems(users_list - contacts_list)

# Диалог выбора контакта для удаления
class DelContactDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для удаления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        # заполнитель контактов для удаления
        self.selector.addItems(sorted(self.database.get_contacts()))

#---------------------Класс, отправляющий сообщение серверу


class ClientMsgWrite(QMainWindow, threading.Thread):
    def __init__(self, account_name, sock, database):
        threading.Thread.__init__(self)
        QMainWindow.__init__(self)
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

        # Загружаем конфигурацию окна из дизайнера
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # Кнопка "Выход"
        self.ui.menu_exit.triggered.connect(qApp.exit)

        # Кнопка отправить сообщение
        self.ui.btn_send.clicked.connect(self.send_message)

        # "добавить контакт"
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        # Удалить контакт
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        # Даблклик по листу контактов отправляется в обработчик
        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    # Деактивировать поля ввода
    def set_disabled_input(self):
        # Надпись  - получатель.
        self.ui.label_new_message.setText('Для выбора получателя дважды кликните на нем в окне контактов.')
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        # Поле ввода и кнопка отправки неактивны до выбора получателя.
        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    # Заполняем историю сообщений.
    def history_list_update(self):
        # Получаем историю сортированную по дате
        list = sorted(self.database.get_history(self.current_chat), key=lambda item: item[3])
        # Если модель не создана, создадим.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        # Очистим от старых записей
        self.history_model.clear()
        # Берём не более 20 последних записей.
        length = len(list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Заполнение модели записями, так-же стоит разделить входящие и исходящие выравниванием и разным фоном.
        # Записи в обратном порядке, поэтому выбираем их с конца и не более 20
        for i in range(start_index, length):
            item = list[i]
            if item[1] == 'in':
                mess = QStandardItem(f'Входящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Исходящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    # Функция обработчик даблклика по контакту
    def select_active_user(self):
        # Выбранный пользователем (даблклик) находится в выделеном элементе в QListView
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        # вызываем основную функцию
        self.set_active_user()

    # Функция устанавливающяя активного собеседника
    def set_active_user(self):
        # Ставим надпись и активируем кнопки
        self.ui.label_new_message.setText(f'Введите сообщенние для {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
        self.history_list_update()

    # Функция обновляющяя контакт лист
    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.database, self.account_name)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    # Функция - обработчик добавления, сообщает серверу, обновляет таблицу и список контактов
    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    # Функция добавляющяя контакт в базы
    def add_contact(self, new_contact):
        self.database.add_contact(new_contact)
        new_contact = QStandardItem(new_contact)
        new_contact.setEditable(False)
        self.contacts_model.appendRow(new_contact)
        self.messages.information(self, 'Операция выполнена', 'Контакт успешно добавлен.')

    # Функция удаления контакта
    def delete_contact_window(self):
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    # Функция обработчик удаления контакта, сообщает на сервер, обновляет таблицу контактов
    def delete_contact(self, item):
        selected = item.selector.currentText()
        self.database.del_contact(selected)
        print(selected)
        self.clients_list_update()
        self.messages.information(self, 'Операция выполнена', 'Контакт успешно удален.')
        item.close()
        # Если удалён активный пользователь, то деактивируем поля ввода.
        if selected == self.current_chat:
            self.current_chat = None
            self.set_disabled_input()

    # Функция отправки собщения пользователю.
    def send_message(self):
        # Текст в поле, проверяем что поле не пустое затем забирается сообщение и поле очищается
        message_text = self.ui.text_message.toPlainText()
        message_dict = {
            ACTION: MSG,
            FROM: self.account_name,
            TO: self.current_chat,
            TIME: time.time(),
            MESSAGE: message_text
        }
        self.ui.text_message.clear()
        try:
            with database_lock:
                self.database.save_message(self.account_name, self.current_chat, message_text)
            with sock_lock:
                send_message(self.sock, message_dict)
            pass
        except IndexError as err:
            self.messages.critical(self, 'Ошибка')
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            self.history_list_update()

    def update(self):
        self.history_list_update()

    def run(self):
        while True:
            time.sleep(0.2)
            # with sock_lock:
            message = receive_message(self.sock)
            print(f"\nСообщение: {message['message']} от {message['from']}")
            with database_lock:
                self.database.save_message(message['from'], 'in', message['message'])
            self.update()


def send_presence (account_name):
    if not isinstance(account_name, str):
        # Генерируем ошибку передан неверный тип
        raise TypeError
    # Если длина имени пользователя больше 25 символов
    if len(account_name) > 25:
        # генерируем нашу ошибку имя пользователя слишком длинное
        raise Exception('Имя должно быть не более 25 символов')
    message = {
        ACTION: "presence",
        TIME: time.time(),
        USER: {
            USERNAME: account_name,
        }
    }
    # logthis = 'args: ({},) = {}'.format(message, message)
    # loggerserv.info('{} - {} - {}'.format(logthis, send_presence.__name__, __name__))
    loggerserv.info("Сформировано presence-сообщение")
    return message


try:
    addr = sys.argv[1]
# если ip-адрес не указан в параметрах
except IndexError:
    addr = 'localhost'
    loggerclient.info(IndexError)
# --------------порт-------------#
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
    # print('Порт должен быть целым числом')
    sys.exit(0)
try:
    account_name = sys.argv[3]
    print(account_name)
except IndexError:
    print('Укажите получателя')

def user_list_request(sock, username):
    req = {
        ACTION: KWNOWNUSERS,
        TIME: time.time(),
        USERNAME: username
    }
    send_message(sock, req)
    ans = receive_message_user_list(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        print ("Ошибка в запросе")

def contact_list_request(sock, username):
    req = {
        ACTION: CONTACTLIST,
        TIME: time.time(),
        USERNAME: username
    }
    send_message(sock, req)
    ans = receive_message_user_list(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        print ("Ошибка в запросе")

def start():
    try:
        clientside = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientside.connect(('localhost', 7777))  # коннектимся с сервером
        print ("Соединение прошло успешно")
        presence = send_presence(account_name)  # создаем приветствие
        print ("Приветствие создается")
        send_message(clientside, presence)  # отправляем приветствие
        print ("Приветствие отправляется")
        checkresponse = receive_message(clientside)
        print (f'Ответ сервера: {checkresponse}')
    except IndexError:
        print('Проблемы с запуском')
    else:
        users_list = user_list_request(clientside, account_name)
        database = ClientBigData(account_name)
        database.add_users(users_list)
        client_app = QApplication(sys.argv)
        main_window = ClientMsgWrite(account_name, clientside, database)
        main_window.setWindowTitle(f'Мессенджер для {account_name}')
        main_window.daemon = True
        main_window.start()
        client_app.exec_()
        while True:
            time.sleep(0.2)
            if main_window.is_alive():
                continue
            break
if __name__ == '__main__':
    start()



