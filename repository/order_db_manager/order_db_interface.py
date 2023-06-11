from abc import abstractmethod, ABCMeta

from asyncpg import Record


class TariffDbInterface(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    async def buy_by_card():
        ...

