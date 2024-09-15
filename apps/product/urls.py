from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
app_name = "product"

urlpatterns = [
    # path("categories/", views.CategoryViewSet.as_view()),
    # path("categories/<uuid:pk>/", views.CategoryAPIView.as_view()),
    path("", views.ProductListAPIView.as_view()),
    path("<uuid:pk>/", views.ProductDetailView.as_view()),
    path("", include(router.urls)),
]
