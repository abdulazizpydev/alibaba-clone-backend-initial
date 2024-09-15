from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "user"

router = routers.SimpleRouter()
router.register(r'login', views.LoginViewSet, basename='login')

urlpatterns = [
    path("register/", views.SignUpView.as_view(), name='register'),
    path("register/verify/<str:otp_secret>/", views.VerifyView.as_view(), name='verify'),
    path("me/", views.UsersMeView.as_view()),
    path('', include(router.urls)),
]
