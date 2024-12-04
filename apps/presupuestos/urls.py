from django.urls import path
from django.contrib.auth import views as auth_views
from apps.presupuestos import views as presupuestos_views

urlpatterns = [
    # Ruta para el login
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # Ruta para el logout
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # Ruta para el dashboard (redirige al dashboard después del login)
    path('', presupuestos_views.dashboard, name='dashboard'),

    # Ruta para crear un nuevo presupuesto
    path('presupuesto/nuevo/', presupuestos_views.presupuesto_nuevo, name='presupuesto_nuevo'),

    # Ruta para agregar un ítem a un presupuesto
    path('presupuesto/<int:presupuesto_id>/nuevo_item/', presupuestos_views.nuevo_item, name='nuevo_item'),

    # Ruta para ver o editar un presupuesto existente
    path('presupuesto/<int:presupuesto_id>/', presupuestos_views.detalle_presupuesto, name='detalle_presupuesto'),

    # Editar item
    path('item/<int:item_id>/editar/', presupuestos_views.editar_item, name='editar_item'),

    # Eliminar item
    path('item/<int:item_id>/eliminar/', presupuestos_views.eliminar_item, name='eliminar_item'),

]