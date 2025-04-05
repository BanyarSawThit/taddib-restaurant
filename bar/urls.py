from django.urls import path
from . import views

app_name = 'bar'

urlpatterns = [
    path('', views.bar_view, name='bar_view'),
    path('history/', views.bar_history_view, name='bar_history_view'),
    path('order/<int:order_id>/ready', views.bar_order_ready, name='bar_order_ready'),
]