import json
import http

from django.views import View
from django.db    import IntegrityError
from django.http  import JsonResponse, HttpResponse

from user.utils   import login_decorator
from image.models import Image
from .models      import Product, ProductCategory

class ProductView(View):
    categories = ProductCategory.objects.all()

    @login_decorator
    def post(self, request):
        data = json.loads(request.body)

        try:
            product  = Product(
                seller   = request.user,
                title    = data['title'],
                content  = data['content'],
                price    = data['price'],
                places   = data['places'],
                category = categories.get(id = data['category'])
            )
            product.save()

            images = {}
            for index, image in enumerate(data['images']):
                images[index] = image
            Image(
                product = product,
                image_1 = images.get(0),
                image_2 = images.get(1),
                image_3 = images.get(2),
                image_4 = images.get(3),
                image_5 = images.get(4)
            ).save()

            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)
