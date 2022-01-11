# Конфиг для переменных
# Ключи
# тип сообщения между клиентом и сервером
ACTION = 'action'
# время запроса
TIME = 'time'
# тип запроса
TYPE = 'type'
# статус пользователя
STATUS = 'status'
# данные о пользователе - клиенте (вложенный словарь)
USER = 'user'
# имя пользователя - чата
USERNAME = 'account_name'
# код ответа
RESPONSE = 'response'
# текст ошибки
ERROR = 'error'

LIST_INFO = 'data_list'


# Значения
PRESENCE = 'presence'
MSG = 'msg'
KWNOWNUSERS = 'get_users'
CONTACTLIST = 'get_contacts'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
ADD_USER = 'add'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
EXIT = 'exit'


# Коды ответов (будут дополняться)
BASIC_NOTICE = 100   # Уведомления
OK = 200             # Успешный запрос
ACCEPTED = 202       # Запрос принят
WRONG_REQUEST = 400  # Неверный запрос
SERVER_ERROR = 500   # Ошибка сервера

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)

# Словари - ответы:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }
# 400
RESPONSE_400 = {
            RESPONSE: 400,
            ERROR: None
        }
