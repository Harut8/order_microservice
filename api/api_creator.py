import asyncio
import os
import threading
from fastapi import FastAPI
from api.order_api import order_router
from uvicorn import run
from repository.core.core import DbConnection
from amqp_service.rabbit_app.pika_app import RabbitMQ


app = FastAPI(version="1.0.0")
app.include_router(order_router, prefix="/api/v1")


async def _create_rabbit():
    from service.saga.saga_pattern import _SAGA_RABBIT
    _CHECK_REDIRECTED_PAYMENT = RabbitMQ("redirect_payment", "redirect_exchange")
    _SAGA_RABBIT["_CHECK_PAYMENT_STATE"] = _CHECK_REDIRECTED_PAYMENT
    await _CHECK_REDIRECTED_PAYMENT.consume(RabbitMQ.check_payment_state_callback)
    #  await _ADD_BANK_ORDER_QUEUE.consume(RabbitMQ.add_order_bank_callback)


@app.on_event("startup")
async def on_start_server():
    await DbConnection.create_connection()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(_create_rabbit())
    # aio_pika_thread = threading.Thread(target=_create_rabbit)
    # aio_pika_thread.start()


@app.on_event("shutdown")
async def on_shutdown():
    await DbConnection.abort_connection()
    os.abort()


@app.get("/")
def ping():
    return {"status": "SERVER RUNNING"}


def run_server():
    run(app, port=8000, host='192.168.0.121')
