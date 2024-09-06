from django.contrib import admin
from django.urls import path
from django.http import JsonResponse


def index(request):
    return JsonResponse({"detail": "Healthy!"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", index),
]
