import jwt , datetime
from rest_framework import exceptions

def access_token(user_id):
    payload = {
            'id': user_id,
            'token_type':'access_token',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=6),
            'iat': datetime.datetime.utcnow()
            }
    allowed_token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')        
    return allowed_token


def decode_access_token(token):
    try:
        payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
        return payload['id']
    except:
        raise exceptions.AuthenticationFailed("invalid credentils...!")


def refresh_token(user_id):
    payload = {
            'id': user_id,
            'token_type':'refresh_token',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
            }
    new_token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')        
    return new_token

def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
        return payload['id']
    except:
        raise exceptions.AuthenticationFailed("invalid credentils...!")    