import asyncio
import json
import uuid
from typing import Union

import httpx

from repository.order_db_manager.order_db_manager import OrderDbManager
from models.order_model.order_model import BuyTariff
from service.order_service_manager.order_service_interface import OrderServiceInterface


class OrderServiceManager(OrderServiceInterface):

    @staticmethod
    async def buy_by_card(tariff_body: BuyTariff, company_id):
        try:
            from service.saga.saga_pattern import _SAGA_PATTERN
            _temp_order_id = await _SAGA_PATTERN["add_order_to_temp"](tariff_body, company_id)
            _bank_url = await OrderServiceManager.get_request_url(_temp_order_id["order_id"])
            if not _bank_url:
                return -1
            _bank_url = _bank_url + "order_id="+str(_temp_order_id["order_id"])
            _form_url = await _SAGA_PATTERN["request_to_bank"](_bank_url)
            print(_form_url)
            return _form_url
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def add_order_to_temp(tariff_body: BuyTariff, company_id):
        try:
            _temp_order_id = await OrderDbManager.add_order_to_temp(tariff_body,company_id)
            if not _temp_order_id:
                return
            return _temp_order_id
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def get_request_url(temp_order_id: Union[str, uuid.UUID]):
        try:
            _request_url = await OrderDbManager.get_request_url(temp_order_id)
            if not _request_url:
                return
            return _request_url["get_alpha_bank_url"]
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def add_bank_order_to_temp(bank_order_id: Union[str, uuid.UUID], order_id: Union[str, uuid.UUID]):
        try:
            _bank_order_id = await OrderDbManager.add_bank_order_to_temp(bank_order_id, order_id)
            if not _bank_order_id:
                return
            return _bank_order_id
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def request_to_bank(bank_url):
        try:
            async with httpx.AsyncClient() as client:
                _form_state = await client.post(bank_url)
                _form_state = _form_state.json()
                _form_error = _form_state.get("errorCode", None)
                _form_error_message = _form_state.get("errorMessage", None)
                _form_url = _form_state.get("formUrl", None)
                if _form_url and not _form_error:
                    return _form_url
                return _form_error_message
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def check_payment_state(bank_order_id: Union[str, uuid.UUID], order_id):
        try:
            from service.saga.saga_pattern import _SAGA_RABBIT
            from amqp_service.rabbit_app.pika_app import RabbitMQ
            info = {'bank_order_id': bank_order_id, 'order_id': order_id}
            bank_and_order = info
            message_id = str(uuid.uuid4())
            await OrderServiceManager.add_task_for_track(message_id, info)
            bank_url = await OrderDbManager.get_payment_status_check_url(order_id, by_order=1)
            async with httpx.AsyncClient() as client:
                bank_url = bank_url['check_status_url']+bank_order_id+"&token="+bank_url["bank_token"]
                _pay_state = await client.post(bank_url)
                _pay_state = _pay_state.json()
                print(_pay_state)
                if _pay_state["errorCode"] == '0' and _pay_state['orderStatus'] == 2:
                    task1 = asyncio.create_task(OrderServiceManager.add_task_for_track(message_id, info))
                    task2 = asyncio.create_task(RabbitMQ.check_payment_state_callback(info, message_id))
                    await asyncio.gather(task1, task2)
                    return True
            return {"status": _pay_state['actionCodeDescription']}
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def check_payment_state_and_verify(bank_order_id, step=0):
        try:
            if step == 1:
                _email = await OrderDbManager.get_email_for_sending_after_fail(bank_order_id)
                return _email
            bank_url = await OrderDbManager.get_payment_status_check_url(bank_order_id)
            if not bank_url:
                return
            async with httpx.AsyncClient() as client:
                bank_url = bank_url['check_status_url']+bank_order_id+"&token="+bank_url["bank_token"]
                _pay_state = await client.post(bank_url)
                _pay_state = _pay_state.json()
                print(_pay_state)
                await OrderDbManager.check_pay_state(bank_order_id)
                # actionCodeDescription mail
                if _pay_state["errorCode"] == '0' and _pay_state['orderStatus'] == 2:
                    return await OrderDbManager.add_tariff_to_user_after_verify(bank_order_id)
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def verify_order(order_id):
        try:
            _state = await OrderDbManager.verify_order(order_id)
            return _state
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def add_task_for_track(task_id, bank_order_id):
        try:
            # _order_info = json.loads(bank_order_id.decode('utf-8'))
            _bank_order_id = bank_order_id["bank_order_id"]
            _add_state = await OrderDbManager.add_task_for_track(task_id, _bank_order_id)
            return _add_state
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def track_rabbit_task(task_id):
        try:
            _track_task_id = await OrderDbManager.track_rabbit_task(task_id)
            return _track_task_id
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def update_rabbit_task(task_id):
        try:
            await OrderDbManager.update_rabbit_task(task_id)
            return True
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def get_download_links_for_email(order_id):
        try:
            _links = await OrderDbManager.get_download_links_for_email(order_id)
            return _links
        except Exception as e:
            print(e)
            return

    @staticmethod
    async def cron_check_pay_state():
        try:
            _pay_list = await OrderDbManager.cron_check_pay_state()
            return _pay_list
        except Exception as e:
            print(e)
            return
