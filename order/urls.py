from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.table_view, name='table_view'),

    # Menu view for a specific table.
    path('table/<int:table_id>/', views.menu_view, name='menu_view'),

    # Selection view for an item on a specific table.
    # The view will allow the user to customize the item (choose meat or spicy level if available).
    path("table/<int:table_id>/item/<int:item_id>", views.selection_view, name="selection_view"),
]

# Serve media files during development.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
