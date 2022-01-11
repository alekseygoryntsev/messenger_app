import dis

'''
Чеклист по проверке серверных функций
Создаем метакласс. Все экземпляры класса Server будут иметь это поведение
    # clsname - экземпляр метакласса - Server
    # bases - кортеж базовых классов - ()
    # clsdict - словарь атрибутов и методов экземпляра метакласса
'''

class ServerMeta(type):         # наследуемся от type
    def __init__(self, clsname, bases, clsdict):
        # Список методов, которые используются в функциях класса:
        methods = []
        # Список атрибутов, которые используются в функциях класса:
        attrs = []
        # Cоздаем цикл для перебора ключей в словаре
        for func in clsdict:
            '''
            Возвращает итератор по инструкциям в предоставленной функции
            методе, строке исходного кода или объекте кода.
            '''
            try:
                ret = dis.get_instructions(clsdict[func])
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEAD7C8>
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEADF48>
            except TypeError:
                pass
            # Если ключ = функция, то...
            else:
                # ...запускам цикл на поиск методов и атрибутов
                for i in ret:
                    # i - Instruction(opname='LOAD_GLOBAL',
                    # opcode=116, arg=9, argval='send_message',
                    # argrepr='send_message', offset=308, starts_line=201,
                    # is_jump_target=False)
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)
        # Если обнаружено использование недопустимого метода connect, бросаем исключение:
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        # Если сокет не инициализировался константами SOCK_STREAM(TCP) AF_INET(IPv4), тоже исключение.
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(clsname, bases, clsdict)

'''
Чеклист по проверке серверных функций
Создаем метакласс. Все экземпляры класса Client будут иметь это поведение
'''

class ClientMeta(type):
    def __init__(self, clsname, bases, clsdict):
        # Список методов, которые используются в функциях класса:
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            # Если мы спарсили НЕ функцию, то получаем исключение
            except TypeError:
                pass
            # Если функция разбираем код, получая используемые методы.
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Вызов receive_message или send_message из utils считаем корректным использованием сокетов
        if 'receive_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)