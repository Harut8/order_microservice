from abc import abstractmethod, ABCMeta
from asyncpg import Pool


class DbConnectionInterface(metaclass=ABCMeta):

    @property
    @abstractmethod
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value: Pool):
        self._connection: Pool = value

    @abstractmethod
    def __init__(self):
        self._connection: Pool | None = None

    @abstractmethod
    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc):
        await self.abort()

    @abstractmethod
    async def abort(self):
        ...
