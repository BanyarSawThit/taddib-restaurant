from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.table_view, name='table_select'),
    path('table/<int:table_id>/', views.menu_page, name='menu_page'),
    path("table/<int:table_id>/item/<int:item_id>", views.customization_page, name="customization_page"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
