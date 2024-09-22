from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('<uuid:pk>/initiate/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('<uuid:pk>/success/', views.PaymentSuccessView.as_view(), name='payment-success'),
    path('<uuid:pk>/confirm/', views.PaymentConfirmView.as_view(), name='payment-confirm'),
    path('<uuid:pk>/status/', views.PaymentStatusView.as_view(), name='payment-status'),
    path('<uuid:pk>/cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
    path('<uuid:pk>/create/link/', views.PaymentLinkView.as_view(), name='payment-link'),
]
