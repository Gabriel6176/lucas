from django.contrib import admin
from .models import Lugar, Tipo, Revestimiento, Color, Presupuesto, Item, Insumo

# Registrar los modelos
@admin.register(Lugar)
class LugarAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Muestra los campos en la tabla del admin
    search_fields = ('nombre',)  # Permite buscar por nombre

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'detalle')
    search_fields = ('detalle',)

@admin.register(Revestimiento)
class RevestimientoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'lugar', 'fecha')
    search_fields = ('cliente',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'presupuesto', 'tipo', 'color', 'cantidad', 'ancho', 'alto')
    search_fields = ('presupuesto__cliente', 'tipo__detalle')

@admin.register(Insumo)
class LugarAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion', 'precio', 'unidad_medida', 'color', 'formula')  # Muestra los campos en la tabla del admin
    search_fields = ('codigo', 'descripcion')  # Permite buscar por nombre