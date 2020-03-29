from django.contrib import admin

from .models import Product, ProductCategory

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title','created_at']

admin.site.register(Product, ProductAdmin)
# admin.site.register(ProductCategory, ProductCategoryAdmin)


