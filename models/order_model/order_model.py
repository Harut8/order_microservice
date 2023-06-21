import uuid
from typing import Union
import re
from email_validator import validate_email
from pydantic import Field, validator, ValidationError

from pydantic import BaseModel


class BuyTariff(BaseModel):
    order_summ: int = Field(gt=0)
    tarif_id: Union[str, uuid.UUID] = Field(default=None)
    cass_stantion_count: int = Field(gt=-1)
    mobile_cass_count: int = Field(gt=-1)
    mobile_manager_count: int = Field(gt=-1)
    web_manager_count: int = Field(gt=-1)
    interval: int = Field(gt=-1,default=1)


class CompanyZayavka(BaseModel):
    acc_contact_name: str = Field(regex=r'^[A-Za-z0-9\s]+$')
    acc_org_name: str = Field(regex=r'^[A-Za-z0-9\s]+$')
    acc_email: str
    acc_phone: str
    acc_address: str | None = Field(regex=r'^[A-Za-z0-9\/*.%$^#@\s]+$')
    acc_country: str
    acc_inn: str = Field(default=None, description="Идентификационный номер налогоплательщика", regex=r'^\d{1,15}$')

    @validator('acc_phone')
    def check_acc_phone(cls, acc_phone):
        try:
            if re.match(r'^\+(374|7|8)\d{8}$', acc_phone):
                return acc_phone
        except Exception:
            raise ValidationError('PHONE ERROR')

    @validator('acc_email')
    def check_acc_email(cls, acc_email):
        try:
            if validate_email(acc_email):
                return acc_email
        except Exception:
            raise ValidationError('EMAIL ERROR')


class PartnerZayavka(BaseModel):
    fio: str | None = Field(regex=r'^[A-Za-z0-9\s]+$', default=None)
    phone: str | None = None
    email: str | None = None
    country: str | None = Field(regex=r'^[A-Za-z0-9\s]+$', default=None)
    company_name: str | None = Field(regex=r'^[A-Za-z0-9\s]+$', default=None)
    costumer_count: str | None = Field(regex=r'^[A-Za-z0-9]+$', default=None)
    comments: str | None = Field(regex=r'^[A-Za-z0-9\s]+$', default=None)

    @validator('phone')
    def check_acc_phone(cls, acc_phone):
        try:
            if re.match(r'^\+(374|7|8)\d{8}$', acc_phone):
                return acc_phone
        except Exception:
            raise ValidationError('PHONE ERROR')

    @validator('email')
    def check_acc_email(cls, acc_email):
        try:
            if validate_email(acc_email):
                return acc_email
        except Exception:
            raise ValidationError('EMAIL ERROR')