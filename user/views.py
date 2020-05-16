import jwt
import json
import http
import bcrypt

from django.views               import View
from django.http                import JsonResponse, HttpResponse
from django.db                  import IntegrityError
from django.core.validators     import validate_email
from django.core.exceptions     import ValidationError
from django.core.mail           import EmailMessage
from django.utils.encoding      import force_bytes, force_text
from django.utils.http          import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding      import force_text
from django.utils.http          import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.tokens import default_token_generator

from my_settings    import SECRET_KEY
from product.models import Product
from image.models   import Image
from .models        import User
from .utils         import login_decorator    

class PasswordResetView(View):
    reset_pwd_link = 'https://petsbab.com/reset-your-password'
    
    def _send_pwd_reset_email(self, user, uid=None, token=None):
        subject = "팻츠밥 패스워드 복구 이메일"
        message = "아래의 링크를 클릭하여 패스워드를 복구하세요.\n"
        message += (PasswordResetView.reset_pwd_link+"?uid="+uid+"&token="+token)
        email = EmailMessage(subject, message, to=[user.email])
        email.send()

    def post(self, request):
        data = json.loads(request.body)
        
        try:
            email = data['email']
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            self._send_pwd_reset_email(user, uid=uid, token=token)
            rlt = dict()
            rlt['uid'] = uid
            rlt['token'] = token
            return JsonResponse({'url':rlt}, status = 200)

        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

    def patch(self, request):
        data = json.loads(request.body)

        try:
            token = data['token']
            uid = force_text(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(id=uid)
            password = data['password']

            if PasswordResetTokenGenerator().check_token(user, token):
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user = User(password = hashed_password.decode('utf-8'))
                user.save()
                return JsonResponse({'message':'Password Reset Success'}, status = 200)
            else:
                return JsonResponse({'message':'Invalid Token'}, status = 401)

        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)


class UserProductView(View):
    @login_decorator
    def get(self, request, sale_status):
        offset = int(request.GET.get('offset',0))
        limit  = int(request.GET.get('limit',10))

        on_sale = sale_status
        products = Product.objects.select_related('seller'
                            ).prefetch_related('image'
                            ).filter(seller=request.user
                            ).filter(on_sale=on_sale
                            ).order_by('-created_at')[offset:(offset+limit)
                            ].values('id','title','category','places','price','on_sale','image__image_1','created_at'
                            )

        return JsonResponse({'products':list(products)}, status = 200)

class UserProfile(View):
    @login_decorator
    def get(self, request):
        result = dict()
        result['nickname'] = request.user.nickname
        result['has_dog']  = request.user.has_dog
        result['has_cat']  = request.user.has_cat
        
        return JsonResponse({'result':result}, status = 200)

class UserView(View):
    def _validate(self, data):
        if (len(data['password']) < 8) or (len(data['password']) > 20):
            return JsonResponse({'message':'INVALID_PASSWORD'}, status = 400)
        if User.objects.filter(email = data['email']).exists():
            return JsonResponse({'message':'DUPLICATE_EMAIL'}, status = 400)
        
        return None

    def post(self, request):
        data = json.loads(request.body)

        try:
            validation_error = self._validate(data)

            if validation_error:
                return validation_error

            validate_email(data['email'])
            
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            nickname = data['nickname'] if data['nickname'] else data['email'][0:data['email'].find('@')]

            user = User(
                        email        = data['email'],
                        nickname     = nickname,
                        phone_number = data['phone_number'],
                        has_dog      = data['has_dog'],
                        has_cat      = data['has_cat'],
                        password     = hashed_password.decode('utf-8')
                    )
            user.save()

            access_token = jwt.encode({'id':user.id}, SECRET_KEY, algorithm = 'HS256')

            return JsonResponse(
                {
                    'email'        : data['email'],
                    'nickname'     : nickname,
                    'access_token' : access_token.decode('utf-8'),
                    'has_dog'      : user.has_dog,
                    'has_cat'      : user.has_cat
                },
                status = 200
            )

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
                        'nickname'     : user.nickname,
                        'has_dog'      : user.has_dog,
                        'has_cat'      : user.has_cat
                    }, 
                    status = 200
                )

            return JsonResponse({'message':'INVALID_PASSWORD'}, status = 401)
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

