from django.db import models
from sympy import sympify


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

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class DetalleInsumo(models.Model):
    """
    Modelo para almacenar los detalles de insumos utilizados en un presupuesto.
    """
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)  # Relación con el presupuesto
    item = models.ForeignKey('Item', on_delete=models.CASCADE)  # Relación con el ítem
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
    ancho = models.DecimalField(max_digits=10, decimal_places=2)  # Ancho en unidades
    alto = models.DecimalField(max_digits=10, decimal_places=2)  # Alto en unidades
    ancho_hoja = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ancho de hoja en unidades
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)  # Tipo de ítem (ventana, puerta, etc.)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)  # Color del ítem
    revestimiento = models.ForeignKey(Revestimiento, on_delete=models.CASCADE)  # Tipo de revestimiento
    desperdicio = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Porcentaje de desperdicio

    def calcular_insumos(self):
        """
        Calcula la cantidad y el costo de cada insumo asociado al ítem.
        """
        insumos = Insumo.objects.all()  # Obtén todos los insumos
        detalles = []

        for insumo in insumos:
            # Evaluar la fórmula del insumo de forma segura
            formula_context = {
                'ANCHO': self.ancho,
                'ALTO': self.alto,
                'ANCHO_HOJA': self.ancho_hoja or 0,  # Considerar el Ancho Hoja si está presente
                'TIPO': self.tipo.numero,
                'DESPERDICIO': self.desperdicio / 100,
            }
            try:
                formula = sympify(insumo.formula)  # Convierte la fórmula en una expresión simbólica
                cantidad = formula.evalf(subs=formula_context)  # Evalúa la fórmula con el contexto
            except Exception:
                cantidad = 0  # Si hay un error en la fórmula, asumimos 0

            if cantidad > 0:
                precio_total = cantidad * insumo.precio
                detalle = DetalleInsumo(
                    presupuesto=self.presupuesto,
                    item=self,
                    insumo=insumo,
                    cantidad_usada=cantidad,
                    precio_unitario=insumo.precio,
                    precio_total=precio_total,
                )
                detalles.append(detalle)

        # Guardar los detalles en la base de datos
        DetalleInsumo.objects.bulk_create(detalles)

    def calcular_costo(self):
        """
        Calcula el costo total del ítem sumando los costos de sus insumos.
        """
        insumos = DetalleInsumo.objects.filter(item=self)
        total = sum(insumo.precio_total for insumo in insumos)
        return total

    def __str__(self):
        return f"Item {self.presupuesto.numero} - {self.tipo.detalle}"

