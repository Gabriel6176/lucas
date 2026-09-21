from django.contrib import admin
from .models import Lugar, Tipo, Revestimiento, Color, Presupuesto, Item, Insumo, TipoInsumo, PorcentajeConfiguracion

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
    list_display = ('id', 'codigo', 'descripcion', 'precio', 'unidad_medida', 'color', 'formula', 'tipo_insumo')  # Muestra los campos en la tabla del admin
    search_fields = ('codigo', 'descripcion')  # Permite buscar por nombre

@admin.register(TipoInsumo)
class TipoInsumoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    list_filter = ('nombre',)
    ordering = ('id',)

@admin.register(PorcentajeConfiguracion)
class PorcentajeConfiguracionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mano_obra_porcentaje', 'venta_porcentaje', 'utilidad_porcentaje', 'flete_porcentaje', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'activo')
        }),
        ('Porcentajes de Cálculo', {
            'fields': (
                ('mano_obra_porcentaje', 'venta_porcentaje'),
                ('utilidad_porcentaje', 'flete_porcentaje'),
            ),
            'description': 'Los porcentajes se especifican como números enteros (ej: 40 para 40%)'
        }),
        ('Información de Registro', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Cuando se guarda una configuración activa, desactivar todas las demás"""
        super().save_model(request, obj, form, change) 