from celery import Celery

from service.parser import ParseEnv

ParseEnv()


celery_decor: Celery = Celery(
    __name__,
    broker='amqp://'+ParseEnv.RABBIT_USER + ':'+ParseEnv.RABBIT_PASS+'@localhost:5672/pcassa_',
    backend='redis://127.0.0.1:6379/0',
    include=['mailing.verify_mailing.send_order_verify_link'])

