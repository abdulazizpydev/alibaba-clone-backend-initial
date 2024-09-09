from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "user"

router = routers.SimpleRouter()

urlpatterns = [
    path("register/", views.SignUpView.as_view(), name='register'),
    path('', include(router.urls)),
]
