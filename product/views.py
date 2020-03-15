import json
import http

from django.views import View
from django.http  import JsonResponse, HttpResponse
from django.db    import IntegrityError

from .models import Product, ProductCategory

class ProductView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            Product(
                title = data['title'],
                content = data['content'],
                price = data['price'],
                deal_spot = data['deal_spot']                
            ).save()

            return HttpResponse(status = 200)

        except KeyError:
            return JsonResponse({'message':'INVALID_KEYS'}, status = 400)
