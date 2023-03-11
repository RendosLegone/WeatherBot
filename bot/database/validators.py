from os.path import exists, isfile


class dbFile:
    @staticmethod
    def validate(value):
        if not exists(value) and isfile(value):
            raise FileNotFoundError(f"Параметр db_file задан неверно! Файла {value} не существует!")
        if "db" not in value.split(".")[-1]:
            raise ValueError(f"Параметр db_file задан неверно! Файл {value} имеет неверный формат!")

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        print(instance)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value
