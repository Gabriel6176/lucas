import os
import django
from django.db.models import F, ExpressionWrapper, DecimalField, When, Case, FloatField, Value
from decimal import Decimal


# Configurar el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lucas.settings')  # Asegúrate de que 'lucas.settings' sea correcto
django.setup()

from apps.presupuestos.models import DetalleInsumo, Item, Insumo

# Filtrar los DetalleInsumo con el tipo_insumo_id deseado
detalles = (
    DetalleInsumo.objects.filter(insumo__tipo_insumo__id=1)
    .select_related('item', 'insumo')
    .values('item__presupuesto__numero', 'item__id', 'insumo__codigo', 'insumo__tipo_insumo__id', 'item__desperdicio')
)

# Evaluar los valores y realizar cálculos
for detalle in detalles:
    item_codigo = detalle['item__presupuesto__numero']
    insumo_codigo = detalle['insumo__codigo']
    tipo_insumo_id = detalle['insumo__tipo_insumo__id']
    desperdicio = detalle['item__desperdicio']
    
    # Calcular cantidad con desperdicio
    cantidad_usada = Decimal('8.0')  # Reemplaza este valor con tu consulta real si lo necesitas
    cantidad_desperdicio = cantidad_usada * Decimal(1 + desperdicio / 100)

    # Imprimir resultados
    print(f"Item Código: {item_codigo}, Insumo Código: {insumo_codigo}, Tipo Insumo ID: {tipo_insumo_id}")
    print(f"Desperdicio: {desperdicio}, Cantidad Usada: {cantidad_usada}, Cantidad Desperdicio: {cantidad_desperdicio}")