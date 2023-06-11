import asyncio
import json

import aio_pika
from service.parser import ParseEnv
from fastapi.responses import RedirectResponse

class RabbitMQ:

    def __init__(self, queue, exchange):
        self._exchange = exchange
        self._queue = queue
        self.__connection_url = 'amqp://'+ParseEnv.RABBIT_USER + ':'+ParseEnv.RABBIT_PASS+'@localhost:5672/pcassa_'
        #asyncio.run(self._connection_open())

    async def _connection_open(self):
        self._conn = await aio_pika.connect(self.__connection_url)
        await self._open_channel()

    async def _open_channel(self):
        self._channel = await self._conn.channel()

    @staticmethod
    async def check_payment_state_callback(body, message_id):
        from service.saga.saga_pattern import _SAGA_PATTERN
        from service.order_service_manager.order_service_manager import OrderServiceManager
        from mailing.verify_mailing.send_order_verify_link import send_order_verify_link_email
        from service.url_token_generator.token_creator import generate_url_for_verify_order
        bank_and_order = json.loads(body.decode('utf-8'))
        #  here need to create safe system for backup pay
        await _SAGA_PATTERN['add_bank_order_to_temp'](
            bank_and_order["bank_order_id"],
            bank_and_order["order_id"]
        )
        _email = await _SAGA_PATTERN['check_payment_state'](bank_and_order["bank_order_id"])
        if not _email:
            return
        _email = _email["c_email"]
        send_order_verify_link_email.delay(receiver_email=_email, message=generate_url_for_verify_order(bank_and_order["bank_order_id"]))
        await OrderServiceManager.update_rabbit_task(message_id)

    async def produce(self, routing_key: str, body: str) -> None:
        try:
            import uuid
            message = aio_pika.Message(body=body.encode(), message_id=str(uuid.uuid4()))
            from service.order_service_manager.order_service_manager import OrderServiceManager
            await self._channel.default_exchange.publish(
                message,
                routing_key=routing_key,
            )
            await OrderServiceManager.add_task_for_track(message.message_id)
            await self.close()
        except Exception as e:
            print(e)
            return

    async def consume(self, callback):
        #  callback is check_payment_state
        try:
            from service.order_service_manager.order_service_manager import OrderServiceManager
            await self._connection_open()
            queue = await self._channel.declare_queue(self._queue)
            async with queue.iterator() as iterator:
                async for message in iterator:
                    _track_task_id = await OrderServiceManager.track_rabbit_task(message.message_id)
                    if not _track_task_id:
                        await callback(message.body, message.message_id)
        except Exception as e:
            print(e)
            return

    async def close(self):
        await self._conn.close()


