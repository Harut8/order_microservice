from pydantic import Field

from pydantic import BaseModel


class BuyTariff(BaseModel):
    order_summ: int
    tarif_id: str = Field(default=None)
    cass_stantion_count: int
    mobile_cass_count: int
    mobile_manager_count: int
    web_manager_count: int
    interval: int = 1