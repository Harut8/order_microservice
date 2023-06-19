import uuid
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Header
from starlette.responses import RedirectResponse

from auth.auth import auth_required
from models.order_model.order_model import BuyTariff
from service.order_service_manager.order_service_manager import OrderServiceManager


order_router = APIRouter(tags=["ORDER API"], prefix="/order")


@order_router.get('/ping')
async def order_ping():
    return {"status": "ORDER PINGING"}


@order_router.get("/verify-order")
async def _verify_order(order_token):
    _state = await OrderServiceManager.verify_order(order_token)
    if not _state:
        return HTTPException(400)
    return RedirectResponse("https://pcassa.ru")


@order_router.get("/verify-payment")
async def verify_payment(orderId: Union[str, uuid.UUID], lang: str, order_id):
    await OrderServiceManager.check_payment_state(orderId, order_id)
    return RedirectResponse("https://pcassa.ru")


@order_router.post("/buy-by-card")
@auth_required
async def buy_by_card(tariff_body: BuyTariff, authorize=Header(None)):
    from auth.auth import decode_token
    c_uuid = await decode_token(authorize)
    c_uuid = c_uuid.sub
    _bank_order_state = await OrderServiceManager.buy_by_card(tariff_body, c_uuid)
    if _bank_order_state == -1:
        return HTTPException(400, 'WRONG COUNTRY PAYMENT SYSTEM')
    if isinstance(_bank_order_state, dict):
        return HTTPException(400, _bank_order_state)
    print(_bank_order_state)
    if _bank_order_state:
        return RedirectResponse(_bank_order_state)
    return HTTPException(400)


@order_router.get('/redirect')
async def redirect_to_bank_url():
    print("ok")

#
