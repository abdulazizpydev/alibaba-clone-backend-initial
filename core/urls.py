from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def index(request):
    return JsonResponse({"detail": "Healthy!"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", index),
    path("api/users/", include("user.urls", namespace="user")),
    path("api/products/", include("product.urls", namespace="product")),
    path("api/cart/", include("cart.urls", namespace="cart")),
    path("api/orders/", include("order.urls", namespace="order")),
    path("api/payment/", include("payment.urls", namespace="payment")),
]
