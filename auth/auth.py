from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Union, Any, Callable
import httpx
from fastapi import Depends, HTTPException
from pydantic import ValidationError
from starlette import status

from models.auth_model.auth_model import PayloadToken
from service.parser import ParseEnv


def auth_required(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any):
        try:
            _LOGIN_URL = "http://"+ParseEnv.API_HOST+":"+'8000'+ParseEnv.AUTH_PATH
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=_LOGIN_URL,
                    headers={
                        "Authorization": "Bearer " + kwargs["authorize"],
                    },
                )
                if response.status_code == 200:
                    return await func(*args, **kwargs)
                raise HTTPException(status_code=403)
        except httpx.HTTPError as error:
            return HTTPException(status_code=500)

    return wrapper


async def decode_token(token):
    try:
        from jose import jwt
        payload = jwt.decode(
            token,
            ParseEnv.JWT_SECRET_KEY,
            algorithms=ParseEnv.ALGORITHM
        )
        token_data = PayloadToken(**payload)
        if token_data.exp < datetime.utcnow().replace(tzinfo=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

