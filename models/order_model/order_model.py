import uuid
from typing import Union

from pydantic import Field

from pydantic import BaseModel


class BuyTariff(BaseModel):
    order_summ: int = Field(gt=0)
    tarif_id: Union[str, uuid.UUID] = Field(default=None)
    cass_stantion_count: int = Field(gt=-1)
    mobile_cass_count: int = Field(gt=-1)
    mobile_manager_count: int = Field(gt=-1)
    web_manager_count: int = Field(gt=-1)
    interval: int = Field(gt=-1,default=1)