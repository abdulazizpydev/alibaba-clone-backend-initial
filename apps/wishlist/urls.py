from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.WishlistListCreateView.as_view(), name='wishlist_list_create'),
    path('<uuid:pk>/', views.WishlistRetrieveDeleteView.as_view(), name='wishlist_delete'),
]
