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

    # Eliminar Presupuesto
    path('presupuesto/<int:presupuesto_id>/eliminar/', presupuestos_views.eliminar_presupuesto, name='eliminar_presupuesto'),

    path('item/<int:item_id>/detalle_insumos/', presupuestos_views.detalle_insumos, name='detalle_insumos'),

    path('presupuesto/<int:presupuesto_id>/recalcular/', presupuestos_views.recalcular_presupuesto, name='recalcular_presupuesto'),

    path('detalle_insumos_presupuesto/<int:presupuesto_id>/', presupuestos_views.detalle_insumos_presupuesto, name='detalle_insumos_presupuesto'),

    path('presupuesto/<int:presupuesto_id>/cambiar_color/', presupuestos_views.cambiar_color_presupuesto, name='cambiar_color_presupuesto'),

    path('presupuesto/<int:presupuesto_id>/cambiar_desperdicio/', presupuestos_views.cambiar_desperdicio_presupuesto, name='cambiar_desperdicio_presupuesto'),


    
]
