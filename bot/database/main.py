import sqlite3
from dataclasses import dataclass
from .validators import dbFile
file = "F:/Программирование/Python проекты/Bot-Site Project/bot/database/data.db"


@dataclass
class UserDB:
    user_id: int
    location: str
    username: int
    notifyTime: str
    paid_subscription: str


class dbScheduler:
    db_file = dbFile()

    def __init__(self, db_file):
        self.__db_file = db_file
        self.connect = sqlite3.connect(self.__db_file, isolation_level=None)
        self.cursor = self.connect.cursor()

    def timeExist(self, time):
        exist = self.cursor.execute(f"SELECT time FROM scheduler WHERE time = ?", (time,)).fetchone()
        if not exist:
            return False
        return True

    def addTime(self, time):
        self.cursor.execute(f"INSERT INTO scheduler VALUES(?, ?)", (time, 0))
        return self.connect.commit()

    def decreaseCount(self, time):
        count = self.cursor.execute(f"SELECT count FROM scheduler WHERE time = ?", (str(time),)).fetchone()
        if count[0] == 1:
            return self.cursor.execute(f"DELETE FROM scheduler WHERE time = ?", (time,))
        self.cursor.execute(f"UPDATE scheduler SET count = {count[0] - 1} WHERE time = ?", (time,))
        return self.connect.commit()

    def increaseCount(self, time):
        count = self.cursor.execute(f"SELECT count FROM scheduler WHERE time = ?", (time,)).fetchone()[0]
        self.cursor.execute(f"UPDATE scheduler SET count = {count + 1} WHERE time = ?", (time,))
        return self.connect.commit()

    def getAllTime(self):
        allTime = self.cursor.execute(f"SELECT time FROM scheduler")
        returnTime = []
        for time in allTime:
            returnTime.append(time)
        return returnTime


schedulerDB = dbScheduler(file)


class dbSubscribers:
    __db_file = dbFile()

    def __init__(self, db_file):
        self.__db_file = db_file
        self.connect = sqlite3.connect(self.__db_file)
        self.cursor = self.connect.cursor()

    def addUser(self, user_id, location, username, notifyTime, paid_subscription):
        if not schedulerDB.timeExist(notifyTime):
            schedulerDB.addTime(notifyTime)
        schedulerDB.increaseCount(notifyTime)
        self.cursor.execute(f"INSERT INTO subscribers VALUES(?, ?, ?, ?, ?)", (user_id, location, username, notifyTime,
                                                                               paid_subscription,))
        self.connect.commit()

    def delUser(self, user_id):
        time = self.cursor.execute(f"SELECT notifyTime FROM subscribers WHERE user_id = ?", (user_id,)).fetchone()[0]
        schedulerDB.decreaseCount(time)
        self.cursor.execute(f"DELETE FROM subscribers WHERE user_id = ?", (user_id,))
        self.connect.commit()

    def updateUser(self, user_id, **kwargs):
        for kwarg in kwargs:
            editParam = kwargs[kwarg]
            self.cursor.execute(f"UPDATE subscribers SET {kwarg} = ? WHERE user_id = ?", (editParam, user_id,))
        self.connect.commit()

    def getUser(self, user_id):
        userData = self.cursor.execute(f"SELECT * FROM subscribers WHERE user_id = ?", (user_id,)).fetchone()
        if userData:
            return UserDB(*userData)
        return False

    def getTimeUsers(self, time):
        users = self.cursor.execute(f"SELECT * FROM subscribers WHERE notifyTime = ?", (time,))
        usersReturn = []
        for user in users:
            usersReturn.append(user)
        return usersReturn


subscribersDB = dbSubscribers(file)
