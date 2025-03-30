from django.urls import path
from . import views

app_name = 'kitchen'

urlpatterns = [
    path('', views.kitchen_dashboard, name='dashboard'),
    path('history/', views.order_history, name='history'),
    path('order/<int:order_id>/ready/', views.mark_order_ready, name='mark_ready'),
]