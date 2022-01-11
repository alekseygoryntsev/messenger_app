from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
import datetime
from settings import *
from server import Server
import os


class ServerBigData:
    # Класс-посредник для записи в базу
    # Все его параметры будут соответствовать колонкам нашей таблицы AllClients
    class AllClients:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None


    # Класс-посредник для записи в базу
    # Все его параметры будут соответствовать колонкам нашей таблицы OnlineClients
    class OnlineClients:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Класс-посредник для записи в базу
    # Все его параметры будут соответствовать колонкам нашей таблицы AuthHistory
    class AuthHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    def __init__(self):
        # Подключаемся к базе данных
        # echo == False (отключаем ведение лога (вывод sql-запросов))
        # pool_recycle == 3600 (обновение соединения каждый час (время указано в секундах))
        self.server_engine = create_engine(f'sqlite:///{SERVER_DB_NAME}.db3',
                                           echo=False, pool_recycle=3600, connect_args={'check_same_thread': False})

        # Вызов MetaData() - это конструктор, который описывает вашу БД. Создаем объект этого класса
        # Вся информация о таблицах будет лежать здесь
        self.metadata = MetaData()

        # Создаём таблицу пользователей
        clients_table = Table('Clients', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        # Создаём таблицу активных пользователей
        online_clients_table = Table('Online_Clients', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Clients.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создаём таблицу истории входов
        auth_history = Table('Auth_History', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Clients.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Clients.id')),
                         Column('contact', ForeignKey('Clients.id'))
                         )

        # Чтобы создать наши таблицы используется команда экземпляра metadata - create_all()
        self.metadata.create_all(self.server_engine)

        # Настройка отображения
        # Связаваем наши классы-посредники и наши таблицы
        # Функция mapper() создаст новый Mapper-объект и сохранит его
        # для дальнейшего применения, ассоциирующегося с нашим классом
        mapper(self.AllClients, clients_table)
        mapper(self.OnlineClients, online_clients_table)
        mapper(self.AuthHistory, auth_history)
        mapper(self.UsersContacts, contacts)

        # Создаём сессию c помощью "Фабрики сессий" - команду sessionmaker
        # Session-объект, привязанный к нашей базе
        Session = sessionmaker(bind=self.server_engine)
        self.session = Session()

        # Обнуляем таблицу активных клиентов, когда устанавливаем соединение
        # Если в таблице активных пользователей есть записи, то их необходимо удалить
        # Когда устанавливаем соединение, очищаем таблицу активных пользователей
        self.session.query(self.OnlineClients).delete()

        # Подтверждаем транзакцию (применяем изменения в базе данных)
        self.session.commit()

    def user_login(self, username, ip_address, port):
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(self.AllClients).filter_by(name=username)

        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        # Если нету, то создаздаём нового пользователя
        else:
            # Создаем экземпляр класса self.AllUsers, через который передаем данные в таблицу
            user = self.AllClients(username)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()

        # Теперь можно создать запись в таблицу активных пользователей о факте входа.
        # Создаем экземпляр класса self.ActiveUsers, через который передаем данные в таблицу
        new_active_user = self.OnlineClients(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # и сохранить в историю входов
        # Создаем экземпляр класса self.LoginHistory, через который передаем данные в таблицу
        history = self.AuthHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохраняем изменения
        self.session.commit()

    # Функция фиксирующая отключение пользователя
    def user_logout(self, username):
        # Запрашиваем пользователя, что покидает нас
        # получаем запись из таблицы AllUsers
        user = self.session.query(self.AllClients).filter_by(name=username).first()

        # Удаляем его из таблицы активных пользователей.
        # Удаляем запись из таблицы ActiveUsers
        self.session.query(self.OnlineClients).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    # Функция возвращает список известных пользователей со временем последнего входа.
    def users_list(self):
        query = self.session.query(
            self.AllClients.name,
            self.AllClients.last_login,
        )
        # Возвращаем список кортежей
        return query.all()


    # Функция возвращает список активных пользователей
    def active_users_list(self):
        # Запрашиваем соединение таблиц и собираем кортежи имя, адрес, порт, время.
        query = self.session.query(
            self.AllClients.name,
            self.OnlineClients.ip_address,
            self.OnlineClients.port,
            self.OnlineClients.login_time
        ).join(self.AllClients)
        # Возвращаем список кортежей
        return query.all()

    # Функция возвращающая историю входов по пользователю или всем пользователям
    def login_history(self, username=None):
        # Запрашиваем историю входа
        query = self.session.query(self.AllClients.name,
                                   self.AuthHistory.date_time,
                                   self.AuthHistory.ip,
                                   self.AuthHistory.port
                                   ).join(self.AllClients)
        # Если было указано имя пользователя, то фильтруем по нему
        if username:
            query = query.filter(self.AllClients.name == username)
        return query.all()
    def get_contacts(self, username):
        # Запрашивааем указанного пользователя
        user = self.session.query(self.AllClients).filter_by(name=username).one()

        # Запрашиваем его список контактов
        query = self.session.query(self.UsersContacts, self.AllClients.name). \
            filter_by(user=user.id). \
            join(self.AllClients, self.UsersContacts.contact == self.AllClients.id)

        # выбираем только имена пользователей и возвращаем их.
        return [contact[1] for contact in query.all()]
    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllClients).filter_by(name=user).first()
        contact = self.session.query(self.AllClients).filter_by(name=contact).first()

        # Проверяем что не дубль и что контакт может существовать (полю пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # Функция удаляет контакт из базы данных
    def remove_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllClients).filter_by(name=user).first()
        contact = self.session.query(self.AllClients).filter_by(name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы доверяем)
        if not contact:
            return

        # Удаляем требуемое
        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()