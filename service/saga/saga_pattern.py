from service.order_service_manager.order_service_manager import OrderServiceManager


_SAGA_PATTERN = {
    'add_order_to_temp': OrderServiceManager.add_order_to_temp,
    'request_to_bank': OrderServiceManager.request_to_bank,
    'add_bank_order_to_temp': OrderServiceManager.add_bank_order_to_temp,
    'redirect_to_payment_url': 4,  # endpoint
    'check_payment_state': OrderServiceManager.check_payment_state_and_verify,
}


_SAGA_RABBIT = {}