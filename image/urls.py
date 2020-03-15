from django.urls    import path

from .views import ImageView

urlpatterns = [
    path('', ImageView.as_view()),
    # path('/account/login', AuthView.as_view())
]
