from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from .token_authentication import *
from .models import User
import jwt

# class JWTAuthentication(BaseAuthentication):

    # def authenticate(self, request):
        
    #     auth_header = get_authorization_header(request).split()
    #     print(auth_header)
    #     if not auth_header:
    #         return None
    #     try:
    #         token = auth_header[1]
    #         allowed_token = jwt.decode(token, 'access_token', algorithms=['HS256'])
    #         if get_authorization_header(request).startswith(b'Bearer') and allowed_token['token_type'] == 'access_token':
    #             if allowed_token['id']:
    #                 user = User.objects.get(id=allowed_token['id'])
    #                 return (user, None)
            
    #     except jwt.exceptions.ExpiredSignatureError:
    #         raise AuthenticationFailed(('Token signature has expired'))

class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
   
        if not auth_header:
            return None

        try:
            token = auth_header[1]

            # Check if the token is a refresh token, in which case authentication is not needed
            decoded_token = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'], options={'verify_exp': False})
            if decoded_token.get('token_type') == 'refresh_token':
                return None

            # Check if the token is a valid access token
            payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])

            user = User.objects.get(id=payload['id'])
            print(user)
            return (user, None)

        # except (jwt.exceptions.DecodeError, User.DoesNotExist, IndexError):
        #     raise AuthenticationFailed('Invalid token')
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed('Token signature has expired')
