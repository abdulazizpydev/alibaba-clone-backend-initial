from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path("", views.GetItemsView.as_view(), name='get-cart-items'),
    path("add/", views.AddItemView.as_view(), name='add-item'),
    path('update/', views.UpdateItemQuantityView.as_view(), name='update_item_quantity'),
    path('total/', views.GetCartTotalView.as_view(), name='get-cart-total'),
    path('remove/<uuid:product_id>/', views.RemoveItemView.as_view(), name='remove-item'),
    path('empty/', views.EmptyCartView.as_view(), name='empty-cart'),
]
