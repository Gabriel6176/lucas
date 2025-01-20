from django.db import models
from sympy import sympify
from decimal import Decimal, ROUND_HALF_UP
from sympy import N,Piecewise


class Lugar(models.Model):
    """
    Modelo para definir los lugares disponibles.
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Tipo(models.Model):
    """
    Modelo para los tipos de ventanas y puertas.
    """
    numero = models.IntegerField(unique=True)  # Número identificador del tipo
    detalle = models.CharField(max_length=100)  # Descripción del tipo

    def __str__(self):
        return self.detalle


class Revestimiento(models.Model):
    """
    Modelo para definir los tipos de revestimientos disponibles.
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Color(models.Model):
    """
    Modelo para los colores disponibles.
    """
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Presupuesto(models.Model):
    numero = models.AutoField(primary_key=True)  # Clave primaria definida explícitamente
    cliente = models.CharField(max_length=255)
    lugar = models.ForeignKey('Lugar', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Presupuesto {self.numero} - {self.cliente}"

class TipoInsumo(models.Model):
    """
    Modelo para definir los tipos de insumo disponibles.
    """
    nombre = models.CharField(max_length=50, unique=True)  # Nombre del tipo de insumo (por ejemplo, 'Material', 'Herramienta')
    
    def __str__(self):
        return self.nombre


class Insumo(models.Model):
    """
    Modelo para definir los insumos necesarios.
    """
    codigo = models.CharField(max_length=50)  # Código único del insumo
    descripcion = models.TextField()  # Descripción del insumo
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio por unidad
    unidad_medida = models.CharField(max_length=50)  # Unidad de medida (por ejemplo, METRO)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)  # Color asociado, si aplica
    formula = models.TextField()  # Fórmula para calcular la cantidad del insumo
    tipo_insumo = models.ForeignKey(TipoInsumo, on_delete=models.CASCADE, null=True, blank=True)  # Relación con TipoInsumo

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class DetalleInsumo(models.Model):
    """
    Modelo para almacenar los detalles de insumos utilizados en un presupuesto.
    """
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)  # Relación con el presupuesto
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='detalles')  # Relación con el ítem
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)  # Relación con el insumo
    cantidad_usada = models.DecimalField(max_digits=10, decimal_places=2)  # Cantidad calculada del insumo
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio unitario del insumo
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)  # Precio total (cantidad x precio unitario)

    def __str__(self):
        return f"Presupuesto {self.presupuesto.numero} - Insumo {self.insumo.codigo}"


class Item(models.Model):
    """
    Modelo para los ítems asociados a cada presupuesto.
    """
    presupuesto = models.ForeignKey(Presupuesto, related_name='items', on_delete=models.CASCADE)  # Relación con el presupuesto
    cantidad = models.PositiveIntegerField()  # Cantidad del ítem
    ancho = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ancho en unidades
    alto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Alto en unidades
    ancho_hoja = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ancho de hoja en unidades
    alto_lama = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)  # Tipo de ítem (ventana, puerta, etc.)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)  # Color del ítem
    revestimiento = models.ForeignKey(Revestimiento, on_delete=models.CASCADE)  # Tipo de revestimiento
    desperdicio = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Porcentaje de desperdicio

    

    @property
    def cantidad_desperdicio(self):
        """
        Calcula la cantidad considerando el desperdicio.
        Solo aplica el cálculo para tipo_insumo_id=1; para otros, se usa la cantidad original.
        """
        if hasattr(self.tipo, 'tipo_insumo_id') and self.tipo.tipo_insumo_id == 1:
            return self.cantidad * (1 + self.desperdicio / 100)
        return self.cantidad

    def calcular_insumos(self):
        """
        Recalcula las cantidades y los precios de los insumos asociados al ítem.
        """
        # Eliminar insumos previamente calculados
        DetalleInsumo.objects.filter(item=self).delete()

        # Filtrar insumos por color
        if self.color.id in [1, 2, 3]:  # Ejemplo: Blanco, Simil Madera, Negro
            insumos = Insumo.objects.filter(color=self.color)
        else:
            insumos = Insumo.objects.filter(color__isnull=True)

        if not insumos.exists():
            return

        detalles = []
        for insumo in insumos:
            formula_context = {
                'CANTIDAD': float(self.cantidad_desperdicio),  # Usa cantidad con desperdicio
                'ANCHO': float(self.ancho) / 100,
                'ALTO': float(self.alto) / 100,
                'ANCHO_HOJA': float(self.ancho_hoja or 0) / 100,
                'TIPO': int(self.tipo.numero),
                'DESPERDICIO': float(self.desperdicio) / 100,
                'REVESTIMIENTO': int(self.revestimiento.id),
                'ALTO_LAMA': (
                    float(self.alto) / 100 if self.revestimiento.id == 6
                    else float(self.alto_lama or 0) if self.revestimiento.id == 8
                    else 0
                ),
            }

            try:
                # Calcular cantidad basada en fórmula
                cantidad = eval(insumo.formula, {}, formula_context)
                cantidad = max(0, round(float(cantidad), 2))
            except Exception as e:
                cantidad = 0

            if cantidad > 0:
                # Condicional para calcular cantidad_desperdicio solo para tipo_insumo_id=1
                if insumo.tipo_insumo and insumo.tipo_insumo.id == 1:
                    cantidad_desperdicio = Decimal(cantidad) * Decimal(1 + self.desperdicio / 100)
                else:
                    cantidad_desperdicio = Decimal(cantidad)  # Para otros, cantidad_desperdicio es igual a cantidad

                # Calcular el precio total usando cantidad_desperdicio
                precio_total = cantidad_desperdicio * insumo.precio
                print(insumo.codigo, insumo.descripcion, precio_total)
                detalle = DetalleInsumo(
                    presupuesto=self.presupuesto,
                    item=self,
                    insumo=insumo,
                    cantidad_usada=Decimal(cantidad),
                    precio_unitario=insumo.precio,
                    precio_total=precio_total,
                )
                detalles.append(detalle)

        # Crear los nuevos detalles de insumos en la base de datos
        DetalleInsumo.objects.bulk_create(detalles)

    def calcular_costo(self):
        """
        Calcula el costo total del ítem sumando los costos de sus insumos.
        """
        insumos = DetalleInsumo.objects.filter(item=self)
        total = sum(insumo.precio_total for insumo in insumos)
        return total

