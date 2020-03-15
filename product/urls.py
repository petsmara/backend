from django.contrib import admin
from django.urls    import path

from .views import ProductView

urlpatterns = [
   path('', ProductView.as_view()),
   # path('/account/signup', UserView.as_view()),
]
