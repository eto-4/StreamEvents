# events/urls.py
from django.urls import path
from . import views

app_name='events'

urlpatterns=[
    # Descripció - Llistat d'esdeveniments
    path('', views.event_list_view, name='event_list' ),
    # Descripció - Crear esdeveniment
    path('create/', views.event_create_view, name='event_create'),
    # Descripció - Detall d'esdeveniment
    path('<int:pk>/', views.event_detail_view, name='event_detail'),
    # Descripció - Editar esdeveniment
    path('<int:pk>/edit/', views.event_update_view, name='event_update'),
    # Descripció - Eliminar esdeveniment
    path('<int:pk>/delete/', views.event_delete_view, name='event_delete'),
    # Descripció - Els meus esdeveniments
    path('my-events/', views.my_events_view, name='my_events'),
    # Descripció - Esdeveniments per categoria
    path('category/<str:category>', views.events_by_category_view, name='events_by_category')
]