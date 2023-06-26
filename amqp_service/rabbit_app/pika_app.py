import asyncio
import json

import aio_pika
from service.parser import ParseEnv
from fastapi.responses import RedirectResponse


class RabbitMQ:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'object'):
            cls.object  = super().__new__(cls)
        return cls.object

    def __init__(self, queue, exchange):
        self._exchange = exchange
        self._queue = queue
        #self.__connection_url = 'amqp://rabbit:5672/'
        #asyncio.run(self._connection_open())

    @classmethod
    async def connection_open(self):
        try:
            print('connect')
            self.object._conn = await aio_pika.connect_robust(host='rabbit', login=ParseEnv.RABBIT_USER, password=ParseEnv.RABBIT_PASS, port=5672)
            print('end connection')
            self.object._channel = await self.object._conn.channel()
        except Exception as e:
            print(e)
            return
    async def _open_channel(self):
        self._channel = await self.channel()

    @staticmethod
    async def send_mails_after_check(bank_order_id, email, message_id):
        try:
            from service.order_service_manager.order_service_manager import OrderServiceManager
            from mailing.verify_mailing.send_order_verify_link import send_order_verify_link_email
            from service.url_token_generator.token_creator import generate_url_for_verify_order
            from mailing.download_mailing.send_download_links import send_download_links
            send_order_verify_link_email.delay(receiver_email=email,
                                               message=generate_url_for_verify_order(bank_order_id))
            _update_state = await OrderServiceManager.update_rabbit_task(message_id)
            _links = await OrderServiceManager.get_download_links_for_email(bank_order_id)
            send_download_links.delay(receiver_email=email, message=_links)
        except Exception as e:
            print(e, 'MAILING ERROR')
            return

    @staticmethod
    async def check_payment_state_callback(body, message_id, step=0):
        _update_state = False
        _email = None
        from service.saga.saga_pattern import _SAGA_PATTERN
        bank_and_order = body
        #  here need to create safe system for backup pay
        if step == 0:
            await _SAGA_PATTERN['add_bank_order_to_temp'](
                bank_and_order["bank_order_id"],
                bank_and_order["order_id"]
            )
            _email = await _SAGA_PATTERN['check_payment_state'](bank_and_order["bank_order_id"])
            if not _email:
                return
            _email = _email["c_email"]
            print(_email)
            await RabbitMQ.send_mails_after_check(bank_and_order["bank_order_id"], _email, message_id)
        elif step == 1:
            _email = await _SAGA_PATTERN['check_payment_state'](bank_and_order["bank_order_id"], step=1)
            await RabbitMQ.send_mails_after_check(bank_and_order["bank_order_id"], _email, message_id)

    async def produce(self, routing_key: str, body: str) -> None:
        import uuid
        message = aio_pika.Message(body=body.encode(), message_id=str(uuid.uuid4()))
        from service.order_service_manager.order_service_manager import OrderServiceManager
        try:
            await self._channel.default_exchange.publish(
                message,
                routing_key=routing_key,
            )
            # await self.close()
        except Exception as e:
            print(e, 'RABBIT ERROR')
            return
        finally:
            await OrderServiceManager.add_task_for_track(message.message_id, message.body)

    async def consume(self, callback):
        #  callback is check_payment_state
        try:
            # await self._connection_open()
            # await asyncio.sleep(1)
            from service.order_service_manager.order_service_manager import OrderServiceManager
            queue = await self._channel.declare_queue(self._queue)
            print("CONSUME")
            async with queue.iterator() as iterator:
                async for message in iterator:
                    _track = await OrderServiceManager.track_rabbit_task(message.message_id)
                    _track_id = None
                    _track_state = None
                    if _track:
                        _track_id = _track[0]
                        _track_state = _track[1]
                    if not _track_id:
                        await callback(message.body, message.message_id)
                    if _track_id and not _track_state:
                        await callback(message.body, message.message_id, step=1)

        except Exception as e:
            print(e)
            return

    async def close(self):
        await self._conn.close()


