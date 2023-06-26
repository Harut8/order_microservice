import asyncio

from celery import Celery
from celery.schedules import crontab
from service.parser import ParseEnv

ParseEnv()


celery_decor: Celery = Celery(
    'celery_app',
    #broker='amqp://'+ParseEnv.RABBIT_USER + ':'+ParseEnv.RABBIT_PASS+'@localhost:5672/pcassa_order',
    broker='redis://localhost:6379/3',
    backend='redis://localhost:6379/3',
    include=[
        'mailing.verify_mailing.send_order_verify_link',
        'mailing.download_mailing.send_download_links',
        'repository.order_db_manager.order_db_manager'])


celery_decor.conf.enable_utc = False


@celery_decor.task
def cron_for_payment_check():
    loop = asyncio.get_event_loop()
    from service.order_service_manager.order_service_manager import OrderServiceManager
    _payment_list = loop.run_until_complete(OrderServiceManager.cron_check_pay_state())
    print(_payment_list)
    if not _payment_list:
        print(5)
        return
    for i in _payment_list:
        print(i)


celery_decor.conf.beat_schedule = {
    "check-state-task": {
        "task": "amqp_service.celery_app.celery_app.cron_for_payment_check",
        "schedule": crontab()
    }
}
