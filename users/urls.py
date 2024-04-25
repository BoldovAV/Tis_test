from django.urls import path
from rest_framework import routers

from users.views import UserViewSet, VerifyEmailView, UserPasswordDropAPIView
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('verify_email/<int:pk>/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('drop_password/<int:pk>/', UserPasswordDropAPIView.as_view(), name='drop_password')
    ]
router = routers.SimpleRouter()
router.register(r'user', UserViewSet)

urlpatterns += router.urls
