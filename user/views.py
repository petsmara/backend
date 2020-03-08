import jwt
import json
import http
import bcrypt

from .models           import User
from petsmara.settings import SECRET_KEY

from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.db              import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class UserView(View):
    def _validate(self, data):
        if (len(data['password']) < 8) or (len(data['password']) > 20):
            return JsonResponse({'message':'INVALID_PASSWORD'}, status = 400)
        if User.objects.filter(email = data['email']).exists():
            return JsonResponse({'message':'DUPLICATE_EMAIL'}, status = 400)
        # if (len(data['nickname']) > 0) and (User.objects.filter(nickname = data['nickname']).exists()):
        #    return JsonResponse({'message':'DUPLICATE_NICKNAME'}, status = 400)

        return None

    def post(self, request):
        data = json.loads(request.body)

        try:
            validation_error = self._validate(data)

            if validation_error:
                return validation_error

            validate_email(data['email'])
            
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

            User(
                email        = data['email'],
                nickname     = data['nickname'] if data['nickname'] else data['email'][0:data['email'].find('@')],
                phone_number = data['phone_number'],
                password     = hashed_password.decode('utf-8')
            ).save()

            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)
        except IntegrityError:
            return JsonResponse({'message':'REDUNDANT_EMAIL'}, status = 400)
        except ValidationError:
            return JsonResponse({'message':'INVALID_EMAIL'}, status = 400)

class AuthView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            user = User.objects.get(email = data['email'])

            if bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
                access_token = jwt.encode({'id':user.id}, SECRET_KEY, algorithm = 'HS256')
                return JsonResponse(
                    {
                        'access_token' : access_token.decode('utf-8'),
                        'email'        : user.email,
                        'nickname'     : user.nickname
                    }, 
                    status = 200
                )

            return JsonResponse({'message':'INVALID_PASSWORD'}, status = 401)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

