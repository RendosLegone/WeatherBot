from os import environ
from typing import Final
from dotenv import load_dotenv
load_dotenv()


class TgKeys:
    TOKEN: Final = environ.get("BOT_TOKEN")
    PAY_TOKEN: Final = environ.get("PAY_TOKEN")
    DB_HOST: Final = environ.get("DB_HOST")
    DB_NAME: Final = environ.get("DB_NAME")
    DB_USER: Final = environ.get("DB_USER")
    DB_PASSWORD: Final = environ.get("DB_PASSWORD")
    PROJECT_PATH: Final = environ.get("PROJECT_PATH")
