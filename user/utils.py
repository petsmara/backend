import jwt
import json

from django.http            import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from my_settings import SECRET_KEY
from .models     import User

def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            if access_token:
                payload = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
                request.user = User.objects.get(id=payload["id"])
                return func(self, request, *args, **kwargs)
            else:
                return JsonResponse({'message':'INVALID_AUTHORIZATION'}, status = 400)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEY'}, status = 400)

    return wrapper


