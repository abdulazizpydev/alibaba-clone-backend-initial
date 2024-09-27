from django.urls import path
from .views import NotificationListView, RetrieveUpdateView

app_name = 'notification'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', RetrieveUpdateView.as_view(), name='notification-update'),
]
