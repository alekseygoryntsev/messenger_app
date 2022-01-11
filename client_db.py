from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from functions.config import *
import datetime

class ClientBigData:
    # БД всех пользователей
    class AllUsers:
        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory:
        def __init__(self, contact, direction, message):
            self.id = None
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    # БД списка контактов
    class Contacts:
        def __init__(self, contact):
            self.id = None
            self.name = contact

    # Конструктор
    def __init__(self, name):
        # Создаём движок базы данных, поскольку разрешено несколько клиентов одновременно, каждый должен иметь свою БД
        # Поскольку клиент мультипоточный необходимо отключить проверки на подключения с разных потоков,
        # иначе sqlite3.ProgrammingError
        self.database_engine = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
                                             connect_args={'check_same_thread': False})

        # Вызов MetaData() - это конструктор, который описывает вашу БД. Создаем объект этого класса
        # Вся информация о таблицах будет лежать здесь
        self.metadata = MetaData()

        # Создание таблицы всех пользователей
        users = Table('allusers', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String)
                      )

        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('contact', String),
                        Column('direction', String),
                        Column('message', Text),
                        Column('date', DateTime)
                        )

        # Создаём таблицу контактов
        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String, unique=True)
                         )
        # Чтобы создать наши таблицы используется команда экземпляра metadata - create_all()
        self.metadata.create_all(self.database_engine)

        # Настройка отображения
        # Связаваем наши классы-посредники и наши таблицы
        # Функция mapper() создаст новый Mapper-объект и сохранит его
        # для дальнейшего применения, ассоциирующегося с нашим классом
        mapper(self.AllUsers, users)
        mapper(self.MessageHistory, history)
        mapper(self.Contacts, contacts)

        # Создаём сессию c помощью "Фабрики сессий" - команду sessionmaker
        # Session-объект, привязанный к нашей базе
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Эта часть необходима, если контакты необходимо подгружать с сервеной части
        # self.session.query(self.Contacts).delete()
        self.session.commit()

    # Функция сохраняющяя сообщения
    def save_message(self, contact, direction, message):
        message_row = self.MessageHistory(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    # Функция возвращающая историю переписки
    def get_history(self, contact):
        query = self.session.query(self.MessageHistory).filter_by(contact=contact)
        return [(history_row.contact, history_row.direction, history_row.message, history_row.date)
                for history_row in query.all()]

    # Функция добавления контактов
    def add_contact(self, contact):
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    # Функция удаления контакта
    def del_contact(self, contact):
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    # Функция добавления известных пользователей.
    # Пользователи получаются только с сервера, поэтому таблица очищается.
    def add_users(self, users_list):
        self.session.query(self.AllUsers).delete()
        for user in users_list:
            user_row = self.AllUsers(user)
            self.session.add(user_row)
        self.session.commit()

    # Функция возвращающяя контакты
    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    # Функция возвращающяя список известных пользователей
    def get_users(self):
        return [user[0] for user in self.session.query(self.AllUsers.username).all()]

    # Функция проверяющяя наличие пользователя в известных
    def check_user(self, user):
        if self.session.query(self.AllUsers).filter_by(username=user).count():
            return True
        else:
            return False

    # Функция проверяющяя наличие пользователя контактах
    def check_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False


