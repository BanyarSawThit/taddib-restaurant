from django.urls import path
from . import views

app_name = 'bar'

urlpatterns = [
    path('', views.bar_dashboard, name='dashboard'),
    path('history/', views.drink_history, name='history'),
    path('order/<int:order_id>/ready/', views.mark_drinks_ready, name='mark_ready'),
]