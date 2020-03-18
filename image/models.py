from django.db import models

from product.models import Product

class Image(models.Model):
    product_id = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)

    class Meta:
        db_table = 'images'

