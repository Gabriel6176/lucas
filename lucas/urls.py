from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para el panel de administración
    path('', include('apps.presupuestos.urls')),  # Incluye las rutas definidas en apps/presupuestos.urls.py
]

