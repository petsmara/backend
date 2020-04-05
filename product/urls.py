from django.contrib import admin
from django.urls    import path

from .views import ProductView, SingleProductView, ProductListView

urlpatterns = [
    path('', ProductView.as_view()),
    path('/list', ProductListView.as_view()),
    path('/<int:product_id>', SingleProductView.as_view()),
]
