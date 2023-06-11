import os
from dotenv import load_dotenv


class ParseEnv:

    RABBIT_PASS = None
    RABBIT_USER = None
    JWT_REFRESH_KEY = None
    REFRESH_TIME = None
    ACCESS_TIME = None
    ALGORITHM = None
    JWT_SECRET_KEY = None
    AUTH_PATH = None
    API_HOST = None
    API_PORT = None
    EMAIL_ = None
    EMAIL_PASS = None

    @property
    def db_name(self):
        return self._db

    @db_name.setter
    def db_name(self, name):
        self._db = name

    @property
    def host_value(self):
        return self._host

    @property
    def user_name(self):
        return self._user

    @property
    def passwd(self):
        return self._passwd

    def __init__(self):
        load_dotenv()
        self._db = os.getenv("DB")
        self._host = os.getenv("HOST")
        self._user = os.getenv("USER_PG")
        self._passwd = os.getenv("PASSWD")
        ParseEnv.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        ParseEnv.ALGORITHM = os.getenv("ALGORITHM")
        ParseEnv.ACCESS_TIME = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
        ParseEnv.REFRESH_TIME = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
        ParseEnv.JWT_REFRESH_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
        ParseEnv.AUTH_PATH = os.getenv('AUTH_PATH')
        ParseEnv.API_HOST = os.getenv('API_HOST')
        ParseEnv.API_PORT = os.getenv('API_PORT')
        ParseEnv.RABBIT_USER = os.getenv('RABBIT_USER')
        ParseEnv.RABBIT_PASS = os.getenv('RABBIT_PASS')
        ParseEnv.EMAIL_ = os.getenv('EMAIL_')
        ParseEnv.EMAIL_PASS = os.getenv('EMAIL_PASS')