import uuid
from typing import Union

from pydantic import BaseModel


class UserInfo(BaseModel):
    """DATA CLASS USED FOR RETURNING INFO AFTER CHECKING PASSWORD
       WITH THIS WE CREATE TOKENS"""
    u_uuid: Union[str, uuid.UUID]
    u_username: str


class UserRegistration(BaseModel):
    user_name: str
    user_phone: str
