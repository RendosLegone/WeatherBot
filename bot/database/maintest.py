from dataclasses import dataclass

from psycopg2 import connect
from datetime import timedelta


class database:
    def __init__(self, db_name, password, user="postgres", host="localhost"):
        self.db_name = db_name
        self.connect = connect(database=db_name, host=host, user=user, password=password)
        self.cursor = self.connect.cursor()

    def close(self):
        pass
# @dataclass
# class UserDB:
#     user_id: int
#     location: str
#     username: int
#     notifyTime: str
#     paid_subscription: str
#     discount: int
#
#     def delUser(self):
#         return subscribersDB.delUser(self.user_id)
#
#     def updateUser(self, **kwargs):
#         return subscribersDB.updateUser(self.user_id, **kwargs)
#
#
# class dbScheduler:
#     def __init__(self):
#         self.connect = connect(database="botdb", user="Rendos", password="120903Rendos", host="localhost")
#         self.cursor = self.connect.cursor()
#
#     def timeExist(self, time):
#         self.cursor.execute(f"SELECT time FROM scheduler WHERE time = ?", (time,))
#         exist = self.cursor.fetchone()
#         if not exist:
#             return False
#         return True
#
#     def addTime(self, time):
#         self.cursor.execute(f"INSERT INTO scheduler VALUES(?, ?)", (time, 0))
#         return self.connect.commit()
#
#     def decreaseCount(self, time):
#         self.cursor.execute(f"SELECT count FROM scheduler WHERE time = ?", (str(time),))
#         count = self.cursor.fetchone()
#         if count[0] == 1:
#             return self.cursor.execute(f"DELETE FROM scheduler WHERE time = ?", (time,))
#         self.cursor.execute(f"UPDATE scheduler SET count = {count[0] - 1} WHERE time = ?", (time,))
#         return self.connect.commit()
#
#     def increaseCount(self, time):
#         self.cursor.execute(f"SELECT count FROM scheduler WHERE time = ?", (time,))
#         count = self.cursor.fetchone()[0]
#         self.cursor.execute(f"UPDATE scheduler SET count = {count + 1} WHERE time = ?", (time,))
#         return self.connect.commit()
#
#     def getAllTime(self):
#         self.cursor.execute(f"SELECT time FROM scheduler")
#         allTime = self.cursor.fetchall()
#         returnTime = []
#         for time in allTime:
#             returnTime.append(time)
#         return returnTime
#
#
# schedulerDB = dbScheduler()
#
#
# class dbSubscribers:
#
#     def __init__(self):
#         self.connect = connect(database="botdb", user="Rendos", password="120903Rendos", host="localhost")
#         self.cursor = self.connect.cursor()
#
#     def addUser(self, user_id, location, username, notifyTime, paid_subscription, discount):
#         if not schedulerDB.timeExist(notifyTime):
#             schedulerDB.addTime(notifyTime)
#         schedulerDB.increaseCount(notifyTime)
#         self.cursor.execute(f"INSERT INTO subscribers VALUES(?, ?, ?, ?, ?, ?)",
#                             (user_id, location, username, notifyTime,
#                              paid_subscription, discount))
#         self.connect.commit()
#
#     def delUser(self, user_id):
#         self.cursor.execute(f"SELECT paid_subscription FROM subscribers WHERE user_id = ?", (user_id,))
#         paidSubscription = self.cursor.fetchone()
#         if paidSubscription[0] != "0":
#             self.cursor.execute(f"INSERT INTO old_subscribers VALUES(?, ?)", (user_id, paidSubscription[0],))
#         self.cursor.execute(f"SELECT notifyTime FROM subscribers WHERE user_id = ?", (user_id,))
#         time = self.cursor.fetchone()
#         schedulerDB.decreaseCount(time)
#         self.cursor.execute(f"DELETE FROM subscribers WHERE user_id = ?", (user_id,))
#         self.connect.commit()
#
#     def delOldUser(self, user_id):
#         self.cursor.execute(f"DELETE FROM old_subscribers WHERE user_id = {user_id}")
#         self.connect.commit()
#
#     def getOldUser(self, user_id):
#         oldUser = self.cursor.execute(f"SELECT * FROM old_subscribers WHERE user_id = ?", (user_id,)).fetchone()
#         if oldUser:
#             return oldUser
#         return False
#
#     def updateUser(self, user_id, **kwargs):
#         for kwarg in kwargs:
#             editParam = kwargs[kwarg]
#             self.cursor.execute(f"UPDATE subscribers SET {kwarg} = ? WHERE user_id = ?", (editParam, user_id,))
#         self.connect.commit()
#
#     def getUser(self, user_id):
#         userData = self.cursor.execute(f"SELECT * FROM subscribers WHERE user_id = ?", (user_id,)).fetchone()
#         if userData:
#             return UserDB(*userData)
#         return False
#
#     def getTimeUsers(self, time):
#         users = self.cursor.execute(f"SELECT * FROM subscribers WHERE notifyTime = ?", (time,))
#         usersReturn = []
#         for user in users:
#             usersReturn.append(user)
#         return usersReturn
#
#
# subscribersDB = dbSubscribers(file)
