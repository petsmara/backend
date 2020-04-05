import json
import http

from django.views import View
from django.db    import IntegrityError
from django.http  import JsonResponse, HttpResponse

from user.utils   import login_decorator
from image.models import Image
from .models      import Product, ProductCategory

class SingleProductView(View):
    def _product_info(self, product):
            result                = {}
            result['id']          = product.id
            result['seller']      = product.seller.nickname
            result['title']       = product.title
            result['content']     = product.content
            result['price']       = product.price
            result['category']    = product.category.id
            result['places']      = product.places
            result['on_sale']     = product.on_sale
            result['created_at']  = product.created_at
            result['modified_at'] = product.modified_at
            result['images']      = [
                                        product.image.image_1,
                                        product.image.image_2,
                                        product.image.image_3,
                                        product.image.image_4,
                                        product.image.image_5
                                    ] if product.image else None
            return result

    def get(self, request, product_id):
        try:
            product = Product.objects.select_related('image').get(id=product_id)
            result  = self._product_info(prodcut)
            return JsonResponse({'result':result}, status = 200)
        
        except Product.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 401)

    @login_decorator
    def put(self, request, product_id):
        try:
            product    = Product.objects.select_related('image').get(id=product_id)

            if product.seller == request.user:
                product.on_sale = False
                product.save()
                result = self._product_info(product)
                return JsonResponse({'result':result}, status = 200)
            else:
                return JsonResponse({'message':'INVALID_ACCESS'}, status = 401)

        except Product.DoesNotExist:
            return JsonResponse({'message':'INVALID_ID'}, status = 401)

class ProductView(View):
    categories = ProductCategory.objects.all()

    @login_decorator
    def post(self, request):
        data = json.loads(request.body)

        try:
            images = dict()
            for index, image in enumerate(data['images']):
                images[index] = image
            image = Image(
                    image_1 = images.get(0),
                    image_2 = images.get(1),
                    image_3 = images.get(2),
                    image_4 = images.get(3),
                    image_5 = images.get(4)
                )
            image.save()

            product  = Product(
                seller   = request.user,
                title    = data['title'],
                content  = data['content'],
                price    = data['price'],
                places   = data['places'],
                image    = image,
                category = self.categories.get(id = data['category'])
                )
            product.save()

            return JsonResponse({'product_id':product.id}, status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)

    def get(self, request):
        offset = int(request.GET['offset'])
        limit  = int(request.GET['limit'])
        result = list()

        products = Product.objects.select_related('image').filter(on_sale=True).order_by('-created_at')[offset:(offset+limit)].all()
        for product in products:
            result.append(
                {
                    "id"          : product.id,
                    "title"       : product.title,
                    "content"     : product.content,
                    "price"       : product.price,
                    "places"      : product.places,
                    "on_sale"     : product.on_sale,
                    "category"    : product.category.id,
                    "created_at"  : product.created_at,
                    "modified_at" : product.modified_at,
                    "images"      : [
                                        product.image.image_1,
                                        product.image.image_2,
                                        product.image.image_3,
                                        product.image.image_4,
                                        product.image.image_5
                                    ] if product.image else None
                }
            )
        
        return JsonResponse({'result':result}, status = 200)


