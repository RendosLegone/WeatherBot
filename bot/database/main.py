import datetime
from dataclasses import dataclass
from datetime import date, time
from psycopg2 import connect
from psycopg2.extras import register_json

register_json(oid=3802, array_oid=3807)
connectdb = connect(database="telegram_db", host="localhost", user="rendos", password="120903")


class Database:
    def __init__(self, table):
        self.connect = connectdb
        self.cursor = self.connect.cursor()
        self.table = table
        self.str_args, self.str_format, self.list_args = self.gen_args()

    def gen_args(self):
        query_get_columns = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{self.table}' " \
                            f"ORDER BY ordinal_position"
        self.cursor.execute(query_get_columns)
        list_args = []
        str_args = ""
        str_format = ""
        column_names = self.cursor.fetchall()
        for row in column_names:
            list_args.append(row[0])
        for arg in list_args:
            if str_args != "":
                str_args += ", "
                str_format += ", "
            str_args += f'"{arg}"'
            str_format += "%s"
        return str_args, str_format, list_args

    def _get_records(self, count=None, **kwargs):
        if kwargs:
            conditions = ""
            for kwarg in kwargs:
                conditions += f'"{kwarg}" = %s, '
            conditions = conditions[:-2]
            list_values = [kwargs[kwarg] for kwarg in kwargs]
            self.cursor.execute(f"SELECT * FROM {self.table} WHERE {conditions}", list_values)
        else:
            self.cursor.execute(f"SELECT * FROM {self.table}")
        record = self.cursor.fetchall()
        if record:
            if count:
                record = record[:count]
                record = record[0]
            return_record = []
            for row in record:
                return_record.append(row)
            return return_record
        return None

    def _create_record(self, **kwargs):
        list_values = []
        for arg in self.list_args:
            if arg in kwargs:
                list_values.append(kwargs[arg])
            else:
                list_values.append(None)
        self.cursor.execute(f'INSERT INTO {self.table}({self.str_args}) VALUES({self.str_format})', list_values)
        return self.connect.commit()

    def _update_records(self, search_value, search_key, **kwargs):
        query_part_1 = f"UPDATE {self.table} SET "
        query_part_2 = ""
        for kwarg in kwargs:
            query_part_2 += f'{kwarg} = %s, '
        query_part_2 = query_part_2[:-2]
        query_part_3 = f'WHERE "{search_key}" = %s'
        query = query_part_1 + query_part_2 + query_part_3
        self.cursor.execute(query, [kwargs[kwarg] for kwarg in kwargs] + [search_value])
        return self.connect.commit()

    def _delete_records(self, **kwargs):
        conditions = ""
        for kwarg in kwargs:
            conditions += f'"{kwarg}" = %s, '
        conditions = conditions[:-2]
        list_values = [kwargs[kwarg] for kwarg in kwargs]
        self.cursor.execute(f"DELETE FROM {self.table} WHERE {conditions}", list_values)
        return self.connect.commit()

    def close(self):
        return self.connect.close()


class SubscribersDatabase(Database):
    def __init__(self, table="subscribers"):
        super().__init__(table)

    def getUser(self, **kwargs):
        user = self._get_records(1, **kwargs)
        if user:
            return UserDB(*user)
        return None

    def getUsers(self, **kwargs):
        users = self._get_records(**kwargs)
        users_return = []
        if users:
            for user in users:
                users_return.append(UserDB(*user))
            return users_return
        return None

    def addUser(self, user_id, location, username, notify_time, paid_subscription=None, discounts=None,
                invited_from=None):
        if not dbScheduler.getTime(time=notify_time):
            dbScheduler.addTime(notify_time)
        return self._create_record(user_id=user_id, location=location, username=username, notify_time=notify_time,
                                   paid_subscription=paid_subscription, discounts=discounts, invited_from=invited_from)

    def updateUser(self, search_value, search_key="user_id", **kwargs):
        return self._update_records(search_value, search_key, **kwargs)

    def deleteUser(self, **kwargs):
        user = self.getUser(**kwargs)
        if user.paid_subscription:
            dbOldSubscribers.addUser(user.user_id, user.paid_subscription)
        self._delete_records(**kwargs)
        return dbScheduler.decreaseCount(user.notify_time)

    def giveDiscount(self, user_id, discount_name):
        user_discounts = self.getUser(user_id=user_id).discounts
        if user_discounts:
            user_discounts.append(discount_name)
        else:
            user_discounts = [discount_name]
        return self.updateUser(user_id, discounts=user_discounts)

    def removeDiscount(self, user_id, discount):
        user_discounts = self.getUser(user_id=user_id).discounts
        user_discounts.remove(discount)
        return self.updateUser(user_id, discount=user_discounts)


class SchedulerDatabase(Database):
    def __init__(self):
        super().__init__("scheduler")

    def getTime(self, **kwargs):
        if not kwargs:
            return_time = []
            records = self._get_records()
            if records:
                for record in records:
                    return_time.append(TimeDB(*record))
                return return_time
            return None
        record = self._get_records(1, **kwargs)
        if record:
            return TimeDB(*record)
        return None

    def addTime(self, notify_time):
        return self._create_record(time=notify_time, count=1)

    def timeExist(self, notify_time):
        if self._get_records(time=notify_time):
            return True
        return False

    def increaseCount(self, notify_time):
        count = self._get_records(time=notify_time)[1] + 1
        return self._update_records(search_key="time", search_value=notify_time, count=count)

    def decreaseCount(self, notify_time):
        count = self._get_records(1, time=notify_time)[1] - 1
        if count == 0:
            return self._delete_records(time=notify_time)
        return self._update_records(search_key="time", search_value=notify_time, count=count)


class OldSubscribersDatabase(SubscribersDatabase):
    def __init__(self):
        super().__init__("old_subscribers")

    def addUser(self, user_id, paid_subscription):
        return self._create_record(user_id=user_id, paid_subscription=paid_subscription)

    def getUser(self, **kwargs):
        return self._get_records(1, **kwargs)

    def getUsers(self, **kwargs):
        return self._get_records(**kwargs)


class DiscountsDatabase(Database):
    def __init__(self):
        super().__init__("discounts")

    def getDiscount(self, **kwargs):
        discount = self._get_records(1, **kwargs)
        if discount:
            return DiscountDB(*discount)
        return None

    def getDiscounts(self, **kwargs):
        discounts = self._get_records(**kwargs)
        discounts_return = []
        if discounts:
            for discount in discounts:
                discounts_return.append(DiscountDB(*discount))
            return discounts_return
        return None

    def deleteDiscount(self, **kwargs):
        return self._delete_records(**kwargs)

    def updateDiscounts(self, search_value, search_key="name", **kwargs):
        return self._update_records(search_value, search_key, **kwargs)

    def decreaseLimit(self, **kwargs):
        discount = self.getDiscount(**kwargs)
        current_limit = discount.limit_count
        if current_limit == 1:
            return self.deleteDiscount(**kwargs)
        return self.updateDiscounts(discount.name, limit_count=current_limit - 1)


dbSubscribers = SubscribersDatabase()
dbScheduler = SchedulerDatabase()
dbOldSubscribers = OldSubscribersDatabase()
dbDiscounts = DiscountsDatabase()


@dataclass
class UserDB:
    user_id: int
    location: str
    username: int
    notify_time: time
    paid_subscription: date | None
    discounts: list[str] | None
    invited_from: str | None

    def delUser(self):
        return dbSubscribers.deleteUser(user_id=self.user_id)

    def updateUser(self, **kwargs):
        return dbSubscribers.updateUser(self.user_id, **kwargs)


@dataclass
class DiscountDB:
    name: str
    label: str
    amount: int
    limit_count: int | None
    summed_up: bool | None
    trigger: dict | None

    def decreaseLimit(self):
        return dbDiscounts.decreaseLimit(name=self.name)

    def deleteDiscount(self):
        return dbDiscounts.deleteDiscount(name=self.name)

    def updateDiscount(self, **kwargs):
        return dbDiscounts.updateDiscounts(self.name, **kwargs)

    def giveDiscount(self, user_id):
        return dbSubscribers.giveDiscount(user_id, self.name)


@dataclass
class TimeDB:
    time: datetime.time
    count: int

    def decrease_count(self):
        dbScheduler.decreaseCount(self.time)

    def increase_count(self):
        dbScheduler.increaseCount(self.time)
