from django.contrib import admin
from django.urls    import path

from .views import (
                    UserView, 
                    AuthView, 
                    UserProfile,
                    UserProductView,
                    PasswordRecoveryView,
                    )

urlpatterns = [
   # path('admin/', admin.site.urls),
    path('/account/signup', UserView.as_view()),
    path('/account/login', AuthView.as_view()),
    path('/account/profile', UserProfile.as_view()),
    path('/account/product/<int:sale_status>', UserProductView.as_view()),
    path('/account/recovery', PasswordRecoveryView.as_view()),
]
