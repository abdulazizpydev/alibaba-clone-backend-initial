from django.urls import path
from . import views

app_name = 'coupon'

urlpatterns = [
    path('', views.CouponListView.as_view(), name='coupon-list'),
    path('<uuid:pk>/', views.CouponDetailView.as_view(), name='coupon-detail'),
    path('apply/', views.ApplyCouponView.as_view(), name='coupon-apply'),
]
