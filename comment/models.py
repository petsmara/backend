from django.db import models

from user.models  import User
from product.models import Product

class Comment(models.Model):
    user        = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
    product     = models.ForeignKey(Product, on_delete = models.CASCADE, null = True)
    content     = models.TextField()
    created_at  = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'comments'

