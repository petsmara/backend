from django.contrib import admin
from django.urls    import path

from .views import UserView

urlpatterns = [
   # path('admin/', admin.site.urls),
    path('/account/signup',UserView.as_view()),
]
