import urllib


def create_token_for_order_verify(subject_id: str):
    from jose import jwt
    from service.parser import ParseEnv
    from datetime import datetime, timedelta
    to_encode = {"sub": subject_id, "exp": datetime.utcnow() + timedelta(minutes=60)}
    encoded_jwt = jwt.encode(to_encode, ParseEnv.JWT_SECRET_KEY, ParseEnv.ALGORITHM)
    return encoded_jwt


def generate_url_for_verify_order(order_id_token: str):
    """ GENERATE URL FOR VERIFYING ACCOUNT"""
    from service.parser import ParseEnv
    #url = 'https://armenia.pcassa.ru:443/verifypayment/?'
    url = ParseEnv.API_HOST+":"+ParseEnv.API_PORT+'/api/v1/order/verify-order?'
    params = {'order_token': order_id_token}
    return url + urllib.parse.urlencode(params)

