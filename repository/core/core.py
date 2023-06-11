import asyncpg
from repository.core.core_interface import DbConnectionInterface
from asyncpg import Pool
from service.parser import ParseEnv


async def fetch_row_transaction(query, *args):
    info = None
    async with DbConnection() as connection:
        async with connection.acquire() as db:
            async with db.transaction():
                if args:
                    info = await db.fetchrow(query, *args)
                else:
                    info = await db.fetchrow(query)
    return info


async def fetch_transaction(query, *args):
    info = None
    async with DbConnection() as connection:
        async with connection.acquire() as db:
            async with db.transaction():
                if args:
                    info = await db.fetch(query, *args)
                else:
                    info = await db.fetch(query)
    return info


async def insert_row_transaction(query, *args):
    info = None
    async with DbConnection() as connection:
        async with connection.acquire() as db:
            async with db.transaction():
                if args:
                    await db.execute(query, *args)
                    return 1
                else:
                    await db.execute(query)
                    return 1


async def executemany_transaction(query, *args):
    info = None
    async with DbConnection() as connection:
        async with connection.acquire() as db:
            async with db.transaction():
                if args:
                    await db.executemany(query, *args)
                    return 1
                else:
                    await db.executemany(query)
                    return 1


async def execute_transaction(query, *args):
    info = None
    async with DbConnection() as connection:
        async with connection.acquire() as db:
            async with db.transaction():
                if args:
                    await db.execute(query, *args)
                    return 1
                else:
                    await db.execute(query)
                    return 1


class DbConnection(DbConnectionInterface):

    @staticmethod
    async def create_connection():
        print("ENV PARSED")
        await DbConnection()._set_connection()

    @staticmethod
    async def abort_connection():
        await DbConnection().abort()

    async def _set_connection(self):
        try:
            __db: str = self._parser.db_name
            __host: str = self._parser.host_value
            __username: str = self._parser.user_name
            __passwd: str = self._parser.passwd
            __dsn = "postgres://"+__username+":"+__passwd+"@"+__host+":5432"+"/"+__db
            self.connection = await asyncpg.pool.create_pool(
                dsn=__dsn
            )
        except Exception as e:
            print(e)
            raise e

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value: Pool):
        self._connection: Pool = value

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'single'):
            cls.single = super(DbConnection, cls).__new__(cls, *args, **kwargs)
            cls.single._parser = ParseEnv()
        return cls.single

    def __init__(self):
        if not self.single:
            self._connection: Pool | None = None

    async def __aenter__(self) -> Pool:
        print("CONNECTION CREATED")
        return self.connection

    async def __aexit__(self, *arg):
        # await self.abort()
        ...

    async def abort(self):
        try:
            if self.connection is not None:
                await self.connection.close()
                print("CONNECTION CLOSED")
        except Exception as e:
            print(e)
            raise e

