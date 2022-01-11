import os
import sys
from functions.config import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
# from server import Server


def create_model_users(database):
    list_users = database.users_list()
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(['Имя Клиента'])
    for row in list_users:
        user, last_login = row
        user = QStandardItem(user)
        user.setEditable(False)
        list.appendRow([user])
    return list

def config_server():
    pass
    # print(SERVER_ADDR, SERVER_PORT, SERVER_DB_NAME)

# GUI - Функция реализующая заполнение таблицы историей сообщений.
def create_stat_model(database):
    # Список записей из базы
    hist_list = database.login_history()

    # Объект модели данных:
    list = QStandardItemModel()
    list.setHorizontalHeaderLabels(
        ['Имя Клиента', 'Дата последней авторизации', 'Сервер', 'Порт'])
    for row in hist_list:
        user, last_seen, serv, port = row
        user = QStandardItem(user)
        user.setEditable(False)
        last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        last_seen.setEditable(False)
        serv = QStandardItem(str(serv))
        serv.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        list.appendRow([user, last_seen, serv, port])
    return list

class ServerGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # action - это то действие, которое будет выполняться при нажатии
        self.history_button = QAction(QIcon("stat.png"),'История входов',self)
        self.history_button.setShortcut('Ctrl+S')

        self.users_button = QAction(QIcon("user.png"),'Список пользователей',self)
        self.users_button.setShortcut('Ctrl+U')

        self.config_button = QAction(QIcon("conf.png"),'Текущие настройки сервера',self)
        self.config_button.setShortcut('Ctrl+R')

        exitAction = QAction(QIcon("exit.png"), 'Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        self.toolbar = self.addToolBar('Main')
        self.toolbar.addAction(self.history_button)
        self.toolbar.addAction(self.users_button)
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(exitAction)


        cal = QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.move(200, 200)
        cal.setGeometry(150, 50, 400, 200)



        self.setGeometry(300, 200, 700, 400)
        self.setWindowTitle('Server_config')
        self.show()

class UsersWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Список всех пользователей')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)


        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)


        self.user_table = QTableView(self)
        self.user_table.move(10, 10)
        self.user_table.setFixedSize(580, 620)

        self.show()

class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        self.db_path_label = QLabel ('Имя базы данных',self)
        self.db_path_label.move(10, 10)
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.port_label = QLabel ('Порт подключения',self)
        self.port_label.move(10, 60)
        self.port = QLineEdit(self)
        self.port.setFixedSize(250, 20)
        self.port.move(10, 80)
        self.port.setReadOnly(True)

        self.ip_label = QLabel ('Адрес подключения',self)
        self.ip_label.move(10, 110)
        self.ip = QLineEdit(self)
        self.ip.setFixedSize(250, 20)
        self.ip.move(10, 130)
        self.ip.setReadOnly(True)

        def open_file():
            os.startfile('settings.py')

        self.close_button = QPushButton('Редактировать', self)
        self.close_button.move(175, 220)
        self.close_button.clicked.connect(open_file)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()

class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Список авторизаций')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнопка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # Лист с собственно историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()