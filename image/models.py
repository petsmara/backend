from django.db import models

from product.models import Product

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    image_1 = models.URLField(max_length = 2500, null = True)
    image_2 = models.URLField(max_length = 2500, null = True)
    image_3 = models.URLField(max_length = 2500, null = True)
    image_4 = models.URLField(max_length = 2500, null = True)
    image_5 = models.URLField(max_length = 2500, null = True)

    class Meta:
        db_table = 'images'

