import uuid
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi import BackgroundTasks
from starlette.responses import RedirectResponse
from mailing.zayavka_mailing.send_zayavka_company import send_zayavka_company_email_
from mailing.zayavka_mailing.send_zayavka_partner import send_zayavka_partner_email_
from auth.auth import auth_required
from models.order_model.order_model import BuyTariff, PartnerZayavka, CompanyZayavka
from service.order_service_manager.order_service_manager import OrderServiceManager


def send_zayavka_company_email(receiver, message):
    send_zayavka_company_email_(receiver, message)


def send_zayavka_partner_email(message):
    send_zayavka_partner_email_(message)


order_router = APIRouter(tags=["ORDER API"], prefix="/order")


@order_router.get('/ping')
async def order_ping():
    return {"status": "ORDER PINGING"}


@order_router.get("/verify-order")
async def _verify_order(order_token: Union[str, uuid.UUID]):
    _state = await OrderServiceManager.verify_order(order_token)
    if not _state:
        return HTTPException(400)
    return RedirectResponse("https://pcassa.ru")


@order_router.get("/verify-payment")
async def verify_payment(orderId: Union[str, uuid.UUID], lang: str, order_id: Union[str, uuid.UUID]):
    _pay_state = await OrderServiceManager.check_payment_state(orderId, order_id)
    if isinstance(_pay_state, bool):
        return RedirectResponse('https://pcassa.ru')
    return _pay_state


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
    if _bank_order_state:
        #return RedirectResponse(_bank_order_state)
        return _bank_order_state
    return HTTPException(400)


@order_router.post('/order-email-company')
async def order_email(order_model: CompanyZayavka, back_task: BackgroundTasks):
    back_task.add_task(send_zayavka_company_email_, order_model.acc_email, order_model)
    return {"status": "success"}


@order_router.post("/order-email-partner")
async def zayavka_company(partner_zayavka: PartnerZayavka, back_task: BackgroundTasks):
    back_task.add_task(send_zayavka_partner_email, partner_zayavka)
    return {"status": "ok"}