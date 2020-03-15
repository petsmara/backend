from django.db import models

from  user.models import User

class ProductCategory(models.Model):
    category_name = models.CharField(max_length = 500)

    class Meta:
        db_table = 'product_categories'

class Product(models.Model):
    seller_id   = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
    title       = models.CharField(max_length = 500)
    content     = models.TextField()
    price       = models.DecimalField(max_digits=11, decimal_places=2)
    places      = models.CharField(max_length                  = 1000)
    # category_id = models.ForeignKey(ProductCategory, on_delete = models.CASCADE, null = True)
    created_at  = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'products'
    
