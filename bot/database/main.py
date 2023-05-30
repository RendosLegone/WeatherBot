from dataclasses import dataclass
from datetime import date, time, datetime
from psycopg2 import connect
from psycopg2.extras import register_json
from bot.misc.env import TgKeys

register_json(oid=3802, array_oid=3807)
connectdb = connect(database=TgKeys.DB_NAME, host=TgKeys.DB_HOST, user=TgKeys.DB_USER, password=TgKeys.DB_PASSWORD)


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
        column_names = self.cursor.fetchall()
        for row in column_names:
            list_args.append(row[0])
        str_args = ", ".join(list_args)
        str_format = ", ".join(["%s" for _ in range(len(list_args))])
        return str_args, str_format, list_args

    def _get_records(self, count=None, **kwargs):
        if kwargs:
            conditions = ", ".join([f'"{kwarg}" = %s' for kwarg in kwargs])
            list_values = [kwargs[kwarg] for kwarg in kwargs]
            self.cursor.execute(f"SELECT * FROM {self.table} WHERE {conditions}", list_values)
        else:
            self.cursor.execute(f"SELECT * FROM {self.table}")
        if count:
            record = self.cursor.fetchmany(count)
        else:
            record = self.cursor.fetchall()
        if record:
            return record
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
        query_part_2 = ", ".join([f'"{kwarg}" = %s' for kwarg in kwargs])
        query_part_3 = f' WHERE "{search_key}" = %s'
        query = query_part_1 + query_part_2 + query_part_3
        self.cursor.execute(query, [kwargs[kwarg] for kwarg in kwargs] + [search_value])
        return self.connect.commit()

    def _delete_records(self, **kwargs):
        conditions = ", ".join([f'"{kwarg}" = %s' for kwarg in kwargs])
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
            return UserDB(*user[0])
        return None

    def getUsers(self, **kwargs):
        users = self._get_records(**kwargs)
        users_return = []
        if users:
            for user in users:
                users_return.append(UserDB(*user))
            return users_return
        return None

    def addUser(self, user_id, location, username, notify_time, paid_subscription_id=None, discounts=None,
                invited_from=None):
        if not dbScheduler.getTime(time=notify_time):
            dbScheduler.addTime(notify_time)
        return self._create_record(user_id=user_id, location=location, username=username, notify_time=notify_time,
                                   paid_subscription_id=paid_subscription_id, discounts=discounts,
                                   invited_from=invited_from)

    def updateUser(self, search_value, search_key="user_id", **kwargs):
        return self._update_records(search_value, search_key, **kwargs)

    def deleteUser(self, **kwargs):
        user = self.getUser(**kwargs)
        if user.paid_subscription_id:
            dbOldSubscribers.addOldUser(user.user_id)
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
    def __init__(self, table="scheduler"):
        super().__init__(table)

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
        count = self._get_records(1, time=notify_time)[0][1] - 1
        if count == 0:
            return self._delete_records(time=notify_time)
        return self._update_records(search_key="time", search_value=notify_time, count=count)


class OldSubscribersDatabase(SubscribersDatabase):
    def __init__(self, table="old_subscribers"):
        super().__init__(table)

    def addOldUser(self, user_id):
        return self._create_record(user_id=user_id)

    def getUser(self, **kwargs):
        return self._get_records(1, **kwargs)

    def getUsers(self, **kwargs):
        return self._get_records(**kwargs)


class DiscountsDatabase(Database):
    def __init__(self, table="discounts"):
        super().__init__(table)

    def getDiscount(self, **kwargs):
        discount = self._get_records(1, **kwargs)
        if discount:
            return DiscountDB(*discount[0])
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


class PaidSubscriptionsDatabase(Database):
    def __init__(self, table="paid_subscriptions"):
        super().__init__(table)

    def addSubscription(self, name, label, price, period, description, photo_url=None):
        return self._create_record(name=name, label=label, price=price, period=period,
                                   description=description, photo_url=photo_url)

    def delSubscription(self, **kwargs):
        return self._delete_records(**kwargs)

    def updateSubscription(self, search_value, search_key="name", **kwargs):
        return self._update_records(search_value, search_key, **kwargs)

    def getSubscription(self, **kwargs):
        record = self._get_records(1, **kwargs)
        if record:
            return PaidSubscriptionDB(*record[0])

    def getSubscriptions(self, **kwargs):
        subscriptions = self._get_records(**kwargs)
        return_subscriptions = []
        if subscriptions:
            for subscription in subscriptions:
                return_subscriptions.append(PaidSubscriptionDB(*subscription))
            if return_subscriptions:
                return return_subscriptions
        return None


class PurchaseReceiptsDatabase(Database):
    def __init__(self, table="purchase_receipts"):
        super().__init__(table)

    def addReceipt(self, subscription_name, currency, total_amount, telegram_purchase_id,
                   provider_purchase_id, user_id, date_time, shipping_option_id=None, order_info=None):
        return self._create_record(subscription_name=subscription_name, currency=currency, total_amount=total_amount,
                                   telegram_purchase_id=telegram_purchase_id, provider_purchase_id=provider_purchase_id,
                                   user_id=user_id, date_time=date_time, shipping_option_id=shipping_option_id,
                                   order_info=order_info)

    def getReceipt(self, **kwargs):
        return ReceiptDB(*self._get_records(1, **kwargs)[0])


dbSubscribers = SubscribersDatabase()
dbScheduler = SchedulerDatabase()
dbOldSubscribers = OldSubscribersDatabase()
dbDiscounts = DiscountsDatabase()
dbSubscriptions = PaidSubscriptionsDatabase()
dbReceipts = PurchaseReceiptsDatabase()


@dataclass
class UserDB:
    user_id: int
    location: str
    username: int
    notify_time: time
    paid_subscription_id: str | None
    discounts: list[str] | None
    invited_from: str | None

    def delUser(self):
        return dbSubscribers.deleteUser(user_id=self.user_id)

    def updateUser(self, **kwargs):
        return dbSubscribers.updateUser(self.user_id, **kwargs)

    def giveDiscount(self, discount_name):
        return dbSubscribers.giveDiscount(self.user_id, discount_name)

    def removeDiscount(self, discount_name):
        return dbSubscribers.removeDiscount(self.user_id, discount_name)


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


@dataclass
class PaidSubscriptionDB:
    name: str
    label: str
    price: dict
    period: date
    description: str | None
    photo_url: str | None


@dataclass
class ReceiptDB:
    subscription_name: str
    currency: str
    total_amount: int
    telegram_purchase_id: str
    provider_purchase_id: str
    user_id: int
    shipping_option_id: str
    order_info: dict
    date_time: datetime
