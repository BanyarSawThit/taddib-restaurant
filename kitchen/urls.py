from django.urls import path
from . import views

app_name = 'kitchen'

urlpatterns = [
    path('', views.kitchen_view, name='kitchen_view'),
    path('history/', views.history_view, name='history_view'),
    path('order/<int:order_id>/ready', views.mark_order_ready, name='mark_order_ready'),
]