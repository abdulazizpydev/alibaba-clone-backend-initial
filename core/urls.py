from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def index(request):
    return JsonResponse({"detail": "Healthy!"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("health/", index),
    # path("api/users/", include("user.urls", namespace="user")),
    path("api/products/", include("product.urls", namespace="product")),
    path("api/cart/", include("cart.urls", namespace="cart")),
    path("api/orders/", include("order.urls", namespace="order")),
    path("api/payment/", include("payment.urls", namespace="payment")),
    path("api/notifications/", include("notification.urls", namespace="notification")),
    path("api/coupons/", include("coupon.urls", namespace="coupon")),
    path("api/wishlists/", include("wishlist.urls", namespace="wishlist")),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
