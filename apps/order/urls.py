from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('checkout/', views.CheckoutCreateView.as_view(), name='checkout'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('history/', views.OrderHistoryView.as_view(), name='order-history'),
]
