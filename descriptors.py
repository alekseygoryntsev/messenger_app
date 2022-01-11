# Дескриптор для проверки порта (server.py)


class CheckPort:                                           # создаем свой класс и пишем протокол дескриптора
    def __get__(self, instance, owner):                    # owner - это класс, instance - это экземпляр
        return instance.__dict__[self.my_attr]
    def __set__(self, instance, value):
        if value != 7777:                                  # проверяем на исключение
            raise ValueError("Порт по умолчанию = 7777")
        instance.__dict__[self.my_attr] = value            # добавляем атрибут в список атрибутов класса
    def __set_name__(self, owner, my_attr):                # привязываем имя атрибута к дескриптору
        self.my_attr = my_attr