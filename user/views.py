import jwt
import json
import http
import bcrypt

from django.views           import View
from django.http            import JsonResponse, HttpResponse
from django.db              import IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from my_settings    import SECRET_KEY
from product.models import Product
from image.models   import Image
from .models        import User
from .utils         import login_decorator    

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

