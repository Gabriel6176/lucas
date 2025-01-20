import os
import django
from django.db.models import F, ExpressionWrapper, DecimalField, When, Case, FloatField, Value
from decimal import Decimal


# Configurar el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lucas.settings')  # Asegúrate de que 'lucas.settings' sea correcto
django.setup()

from apps.presupuestos.models import DetalleInsumo

detalles = (
    DetalleInsumo.objects.filter(insumo__tipo_insumo__id=1)
    .annotate(
        desperdicio_calculado=ExpressionWrapper(
            F('cantidad_usada') * ((F('item__desperdicio') / 100.0) + 1.0),  # Asegúrate de usar 1.0
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )
    .values('cantidad_usada', 'item__desperdicio', 'desperdicio_calculado')
)

for detalle in detalles:
    print(detalle)
