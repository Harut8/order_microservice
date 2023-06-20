import uuid
from typing import Union

from models.order_model.order_model import BuyTariff
from repository.core.core import DbConnection, fetch_row_transaction, insert_row_transaction, fetch_transaction, \
    execute_transaction
from dataclasses import dataclass
from repository.order_db_manager.order_db_interface import TariffDbInterface
from asyncpg import Record


@dataclass
class OrderDbManager(TariffDbInterface):
    @staticmethod
    async def add_task_for_track(task_id, bank_order_id):
        _add_state = await fetch_row_transaction(
            """INSERT INTO rabbit_task(r_m_id, bank_order_id) VALUES($1, $2)""",
            task_id,
            bank_order_id
        )
        return _add_state

    @staticmethod
    async def track_rabbit_task(task_id):
        _add_state = await fetch_row_transaction(
            """SELECT r_t_id, r_m_state FROM rabbit_task WHERE r_m_id = $1""",
            task_id
        )
        if _add_state:
            return _add_state['r_t_id'], _add_state['r_m_state']
        return

    @staticmethod
    async def update_rabbit_task(task_id):
        await fetch_row_transaction(
            """UPDATE rabbit_task SET r_m_state = true WHERE r_m_id = $1""",
            task_id
        )

    @staticmethod
    async def get_download_links_for_email(order_id):
        _links = await fetch_row_transaction(
            """SELECT * from get_links_state($1);""",
            order_id
        )
        if _links is not None:
            return [j for j in _links.values()]

    @staticmethod
    async def add_order_to_temp(tariff_body: BuyTariff, company_id: Union[str, uuid.UUID]):
        _temp_order_id = await fetch_row_transaction(
           f"""
            INSERT INTO saved_order_and_tarif_bank(
            order_summ,
            tarif_id_fk,
            cass_stantion_count,
            mobile_cass_count,
            mobile_manager_count,
            web_manager_count,
            company_id,
            order_ending,
            order_curr_type)
            VALUES(
            $1,
            $2,
            $3,
            $4,
            $5,
            $6,
            $7,
            current_timestamp + interval '{tariff_body.interval} month',
            $8) RETURNING order_id
            """,
            tariff_body.order_summ,
            tariff_body.tarif_id,
            tariff_body.cass_stantion_count,
            tariff_body.mobile_cass_count,
            tariff_body.mobile_manager_count,
            tariff_body.web_manager_count,
            company_id,
            1
        )
        return _temp_order_id

    @staticmethod
    async def get_request_url(temp_order_id: Union[str, uuid.UUID]):
        _url = await fetch_row_transaction(
            """SELECT get_alpha_bank_url($1)""",
            temp_order_id)
        return _url

    @staticmethod
    async def add_bank_order_to_temp(bank_order_id: Union[str, uuid.UUID], order_id: Union[str, uuid.UUID]):
        _bank_order_id = await fetch_transaction(
            """UPDATE saved_order_and_tarif_bank SET bank_order_id = $1 WHERE order_id = $2 RETURNING bank_order_id""",
            bank_order_id,
            order_id
        )
        return _bank_order_id

    @staticmethod
    async def get_payment_status_check_url(bank_order_id):
        _check_status_url = await fetch_row_transaction(
            """
            SELECT check_status_url,bank_token from bank_info where country_code=(
            SELECT mod((select c_unique_id from company where c_id = company_id),100) FROM saved_order_and_tarif_bank WHERE bank_order_id = $1)""",
            bank_order_id
        )
        return _check_status_url

    @staticmethod
    async def add_tariff_to_user_after_verify(order_id):
        async with DbConnection() as connection:
            async with connection.acquire() as db:
                async with db.transaction():
                    tariff_id = await db.fetchrow(
                        """
                                    INSERT INTO saved_order_and_tarif(
                                                order_id,
                                                order_summ,
                                                tarif_id_fk,
                                                cass_stantion_count,
                                                mobile_cass_count,
                                                mobile_manager_count,
                                                web_manager_count,
                                                company_id,
                                                order_ending,
                                                order_curr_type)
                                            SELECT 
                                                bank_order_id::uuid,
                                                order_summ*100,
                                                tarif_id_fk,
                                                cass_stantion_count,
                                                mobile_cass_count,
                                                mobile_manager_count ,
                                                web_manager_count,
                                                company_id,
                                                order_ending,
                                                order_curr_type
                                            from saved_order_and_tarif_bank soatb
                                            where bank_order_id = $1 RETURNING tarif_id_fk;
                                            """, order_id
                    )
                    await db.execute("""select verify_payment($1, $2);""", order_id, tariff_id['tarif_id_fk'])
                    await db.execute("""UPDATE saved_order_and_tarif_bank SET bank_state = 1 WHERE bank_order_id = $1;""", order_id)
                    _email = await db.fetchrow(
                        """SELECT c_email FROM company WHERE c_id =
                         (SELECT company_id FROM saved_order_and_tarif WHERE order_id = $1)""",
                    order_id)
                    return _email

    @staticmethod
    async def get_email_for_sending_after_fail(order_id):
        _email = await fetch_row_transaction(
            """SELECT c_email FROM company WHERE c_id =
             (SELECT company_id FROM saved_order_and_tarif WHERE order_id = $1)""",
            order_id)
        return _email['c_email']

    @staticmethod
    async def verify_order(order_id):
        async with DbConnection() as connection:
            async with connection.acquire() as db:
                async with db.transaction():
                    await db.execute(
                        """update saved_order_and_tarif set order_state = true where order_id =  $1;""",
                        order_id
                    )
                    await db.execute(
                        """
                        INSERT INTO client_tarif(c_t_id, c_t_tarif_id, end_license)
                        select company_id,
                               tarif_id_fk,
                               current_timestamp+
                               concat(
                               date_part('day',(select order_ending -order_date from saved_order_and_tarif
                               where order_id=$1)),
                                      ' days')::interval
                            from saved_order_and_tarif where order_id=$1;""", order_id)
                    return True

    @staticmethod
    async def check_pay_state(bank_order_id):
        await fetch_row_transaction(
            """UPDATE rabbit_task SET check_pay_state = true WHERE bank_order_id = $1""",
            bank_order_id
        )

    @staticmethod
    async def cron_check_pay_state():
        await DbConnection().create_connection()
        _check_pay_list = await fetch_transaction(
            """SELECT r_m_id, bank_order_id FROM rabbit_task WHERE check_pay_state = False"""
        )
        return _check_pay_list