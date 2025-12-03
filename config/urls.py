# Importacions essencials de Django per a la configuració de rutes (URLs)
from django.contrib import admin              # Permet accedir al panell d’administració de Django
from django.urls import path, include         # Eines per definir rutes i incloure altres fitxers de rutes
from django.conf import settings              # Importa la configuració global del projecte (settings.py)
from django.conf.urls.static import static    # Necessari per servir fitxers multimèdia en mode DEBUG

# Definició principal de les rutes del projecte
urlpatterns = [
    # Ruta per accedir al panell d’administració de Django
    path('', include('events.urls', namespace='events')),
    path('users/', include('users.urls', namespace='users')),
    path('admin/', admin.site.urls)
]

# Configuració addicional per servir fitxers multimèdia (imatges d’avatars, etc.)
# Només s’activa quan el mode DEBUG és True (és a dir, durant el desenvolupament)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
