from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Presupuesto, Item, Lugar, Tipo, Revestimiento, Color, DetalleInsumo
from .forms import PresupuestoForm, ItemForm
from decimal import Decimal
from collections import defaultdict
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Sum, F, ExpressionWrapper, Case, When, DecimalField

@login_required
def dashboard(request):
    """
    Vista para mostrar el dashboard principal.
    Lista todos los presupuestos existentes con opciones para crear nuevos.
    """
    presupuestos = Presupuesto.objects.all().order_by('-fecha')  # Ordenar por fecha

    # Agregar el total para cada presupuesto
    presupuestos_con_totales = []
    for presupuesto in presupuestos:
        # Obtener todos los ítems del presupuesto
        items = presupuesto.items.all()

        # Calcular sub_total sumando el costo de cada ítem
        sub_total = sum(item.calcular_costo() for item in items)

        # Calcular subtotal de insumos con tipo_insumo_id=1
        insumos = DetalleInsumo.objects.filter(presupuesto=presupuesto)
        subtotal_tipo_1 = insumos.filter(insumo__tipo_insumo_id=1).aggregate(
            subtotal=Sum('precio_total')
        )['subtotal'] or Decimal(0)

        # Calcular subtotal de insumos con tipo_insumo_id en [1, 3, 4, 5, 6]
        subtotal_tipo_2 = insumos.filter(insumo__tipo_insumo_id__in=[1, 3, 4, 5, 6]).aggregate(
            subtotal=Sum('precio_total')
        )['subtotal'] or Decimal(0)

        # Calcular costos adicionales
        mano_obra = subtotal_tipo_1 * Decimal("0.30")
        venta = subtotal_tipo_1 * Decimal("0.15")
        utilidad = subtotal_tipo_1 * Decimal("0.80")
        flete = subtotal_tipo_2 * Decimal("0.08")

        # Calcular total
        total = sub_total + mano_obra + venta + utilidad + flete

        presupuestos_con_totales.append((presupuesto,total))

    return render(request, 'dashboard.html', {'presupuestos': presupuestos_con_totales})

@login_required
def presupuesto_nuevo(request):
    if request.method == 'POST':
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            presupuesto = form.save()
            return redirect('nuevo_item', presupuesto_id=presupuesto.numero)
    else:
        form = PresupuestoForm()

    # Agregar lugares al contexto
    lugares = Lugar.objects.all()

    return render(request, 'presupuesto_nuevo.html', {'form': form, 'lugares': lugares})

@login_required
def nuevo_item(request, presupuesto_id):
    """
    Vista para agregar un nuevo ítem a un presupuesto existente.
    Permite ingresar cantidad, dimensiones, tipo, color y revestimiento.
    """
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)  # Cambiado "id" por "numero"

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.presupuesto = presupuesto
            item.save()
            item.calcular_insumos()
            return redirect('detalle_presupuesto', presupuesto_id=presupuesto.numero)
    else:
        form = ItemForm()

    # Obtener datos de Tipo, Color y Revestimiento
    tipos = Tipo.objects.all()
    colores = Color.objects.all()
    revestimientos = Revestimiento.objects.all()

    return render(request, 'nuevo_item.html', {
        'form': form,
        'presupuesto': presupuesto,
        'tipos': tipos,
        'colores': colores,
        'revestimientos': revestimientos,
    })

@login_required
def editar_item(request, item_id):
    """
    Vista para editar un ítem existente.
    """
    item = get_object_or_404(Item, id=item_id)  # Obtén el ítem a editar
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)  # Inicializa el formulario con el ítem existente
        if form.is_valid():
            item = form.save()
            
            # Eliminar los insumos previamente calculados y recalcular
            item.calcular_insumos()
            
            # Redirigir al detalle del presupuesto
            return redirect('detalle_presupuesto', presupuesto_id=item.presupuesto.numero)
    else:
        form = ItemForm(instance=item)

    # Obtener datos adicionales
    tipos = Tipo.objects.all()
    colores = Color.objects.all()
    revestimientos = Revestimiento.objects.all()

    return render(request, 'nuevo_item.html', {
        'form': form,
        'presupuesto': item.presupuesto,
        'tipos': tipos,
        'colores': colores,
        'revestimientos': revestimientos,
        'item': item,
    })



@login_required
def eliminar_item(request, item_id):
    """
    Vista para eliminar un ítem.
    """
    item = get_object_or_404(Item, id=item_id)
    presupuesto_id = item.presupuesto.numero
    item.delete()
    return redirect('detalle_presupuesto', presupuesto_id=presupuesto_id)

@login_required
def eliminar_presupuesto(request, presupuesto_id):
    """
    Vista para eliminar un presupuesto.
    """
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)  # Cambia a `Presupuesto` y usa `numero`
    presupuesto.delete()  # Esto eliminará el presupuesto y en cascada todos los ítems asociados
    return redirect('dashboard')  # Redirige directamente al dashboard


@login_required
def detalle_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)
    items = presupuesto.items.all()
    colores = Color.objects.all()  # Agregar los colores disponibles

    # Calcular los costos totales y los costos filtrados por tipo_insumo
    items_con_costos = [
        {'item': item, 
         'costo': item.calcular_costo(),
         'desperdicio': item.desperdicio} 
         for item in items
    ]
    sub_total = sum(entry['costo'] for entry in items_con_costos)

    # Calcular el total de m²
    total_m2 = sum(
        (item.ancho / 100) * (item.alto / 100) * item.cantidad
        for item in items
    )

    # Obtener todos los insumos del presupuesto
    insumos = DetalleInsumo.objects.filter(presupuesto=presupuesto)

    # Cálculos específicos
    tipo_insumos_totales = defaultdict(Decimal)
    for insumo in insumos:
        tipo_insumo_nombre = insumo.insumo.tipo_insumo.nombre if insumo.insumo.tipo_insumo else "Sin Tipo"
        tipo_insumos_totales[tipo_insumo_nombre] += insumo.precio_total

    # Calcular subtotal de insumos con tipo_insumo_id=1
    subtotal_tipo_1 = insumos.filter(insumo__tipo_insumo_id=1).aggregate(
        subtotal=Sum('precio_total')
    )['subtotal'] or Decimal(0)

    # Calcular subtotal de insumos con tipo_insumo_id en [1, 3, 4, 5, 6]
    subtotal_tipo_2 = insumos.filter(insumo__tipo_insumo_id__in=[1, 3, 4, 5, 6]).aggregate(
        subtotal=Sum('precio_total')
    )['subtotal'] or Decimal(0)

    # Calcular costos adicionales
    mano_obra = subtotal_tipo_1 * Decimal("0.30")
    venta = subtotal_tipo_1 * Decimal("0.15")
    utilidad = subtotal_tipo_1 * Decimal("0.80")  # Utilidad solo sobre tipo_insumo_id=1
    flete = subtotal_tipo_2 * Decimal("0.08") # Utilidad solo sobre tipo_insumo_id=1+3+4+5+6
    total = sub_total + mano_obra + venta + utilidad + flete

    # Evitar división por cero
    precio_por_m2 = total / total_m2 if total_m2 > 0 else 0

    return render(request, 'detalle_presupuesto.html', {
        'presupuesto': presupuesto,
        'items_con_costos': items_con_costos,
        'colores': colores,
        'sub_total': sub_total,
        'mano_obra': mano_obra,
        'venta': venta,
        'utilidad': utilidad,
        'flete': flete,
        'total': total,
        'total_m2': total_m2,  # Agregar Total m2 al contexto
        'precio_por_m2': precio_por_m2,  # Agregar el precio por m² al contexto
        'tipo_insumos_totales': dict(tipo_insumos_totales),
    })



@login_required
def detalle_insumos_presupuesto(request, presupuesto_id):
    """
    Calcula y muestra los detalles de insumos para todos los ítems de un presupuesto,
    agrupando los insumos por código y sumando cantidades y precios.
    """
    # Obtener el presupuesto
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)

    # Obtener solo los ítems asociados al presupuesto
    items = presupuesto.items.all()

    # Eliminar los insumos previamente calculados para los ítems de este presupuesto
    DetalleInsumo.objects.filter(item__in=items).delete()

    # Iterar sobre los ítems para calcular los insumos
    for item in items:
        item.calcular_insumos()  # Recalcular insumos para cada ítem

    # Obtener y agrupar todos los detalles de insumos generados para el presupuesto
    detalles = (
        DetalleInsumo.objects.filter(item__in=items)
        .values('insumo__codigo', 'insumo__descripcion', 'precio_unitario', 'insumo__tipo_insumo__id')
        .annotate(
            total_cantidad=Sum('cantidad_usada'),
            total_precio=Sum('precio_total'),
            total_cantidad_desperdicio=Sum(
                Case(
                    When(
                        insumo__tipo_insumo__id=1,  # Condición para tipo_insumo_id=1
                        then=ExpressionWrapper(
                            F('cantidad_usada') * ((F('item__desperdicio') / 100.0) + 1.0),
                            output_field=DecimalField(max_digits=10, decimal_places=2)
                        )
                    ),
                    default=F('cantidad_usada'),  # Para otros casos
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            )
        )
        .order_by('insumo__tipo_insumo__id', 'insumo__codigo')  # Orden descendente por tipo_insumo_id, luego por código
    )

    # Agrupar por tipo_insumo y sumar los valores
    resumen_tipo_insumo = (
        DetalleInsumo.objects.filter(item__in=items)
        .values('insumo__tipo_insumo__nombre')
        .annotate(total_valor=Sum('precio_total'))
        .order_by('insumo__tipo_insumo__id')
    )

    return render(request, 'detalle_insumos_presupuesto.html', {
        'presupuesto': presupuesto,
        'detalles': detalles,  # Detalles agrupados por código de insumo
        'resumen_tipo_insumo': resumen_tipo_insumo,  # Resumen por tipo de insumo
    })





@login_required
def detalle_insumos(request, item_id):
    """
    Vista para mostrar los insumos asociados a un ítem.
    """
    item = get_object_or_404(Item, id=item_id)

    # Obtener los detalles con todos los campos necesarios y calcular cantidad_desperdicio y precio_total
    detalles = (
        DetalleInsumo.objects.filter(item=item)
        .values(
            'insumo__codigo',  # Código del insumo
            'insumo__descripcion',  # Descripción del insumo
            'cantidad_usada',  # Cantidad usada
            'precio_unitario',  # Precio unitario
        )
        .annotate(
            # Calcular cantidad_desperdicio
            cantidad_desperdicio=Case(
                # Solo aplica cálculo con desperdicio si tipo_insumo_id=1
                When(insumo__tipo_insumo__id=1, then=ExpressionWrapper(
                    F('cantidad_usada') * ((F('item__desperdicio') / 100.0) + 1.0),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )),
                # Caso contrario, simplemente usa la cantidad usada
                default=F('cantidad_usada'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            # Calcular precio_total como cantidad_desperdicio * precio_unitario
            precio_total = ExpressionWrapper(
                F('cantidad_desperdicio') * F('precio_unitario'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
        .order_by('id')  # Orden por ID del detalle
    )

    # Agrupar por tipo_insumo y sumar los valores
    resumen_tipo_insumo = (
        DetalleInsumo.objects.filter(item=item)
        .values('insumo__tipo_insumo__nombre')
        .annotate(total_valor=Sum('precio_total'))
        .order_by('insumo__tipo_insumo__id')
    )

    return render(request, 'detalle_insumos.html', {
        'item': item,
        'detalles': detalles,  # Incluye los detalles con cantidad_desperdicio y precio_total
        'resumen_tipo_insumo': resumen_tipo_insumo,
    })

@login_required
def recalcular_presupuesto(request, presupuesto_id):
    """
    Vista para recalcular los insumos de los ítems de un presupuesto específico.
    """
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)  # Obtener el presupuesto
    items = presupuesto.items.all()  # Obtener todos los ítems del presupuesto

    # Eliminar todos los insumos previamente calculados del presupuesto
    DetalleInsumo.objects.filter(presupuesto=presupuesto).delete()

    # Recalcular insumos para cada ítem
    for item in items:
        item.calcular_insumos()

    # Actualizar la fecha y hora del presupuesto
    presupuesto.fecha = now()
    presupuesto.save()

    # Mensaje de éxito
    messages.success(request, f"Los insumos del presupuesto {presupuesto.numero} se han recalculado correctamente.")

    # Redirigir al detalle del presupuesto
    return redirect('detalle_presupuesto', presupuesto_id=presupuesto_id)

def cambiar_color_presupuesto(request, presupuesto_id):
    """
    Cambia el color de todos los ítems de un presupuesto y recalcula insumos.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        nuevo_color_id = data.get('color_id')  # ID del nuevo color
        presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)

        # Validar que el color exista
        nuevo_color = get_object_or_404(Color, id=nuevo_color_id)

        # Actualizar el color de todos los ítems del presupuesto
        items = presupuesto.items.all()
        items.update(color=nuevo_color)

        # Recalcular los insumos de cada ítem
        for item in items:
            item.calcular_insumos()

        # Devolver respuesta JSON indicando éxito
        return JsonResponse({'status': 'success', 'message': 'Color actualizado correctamente.'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)

@login_required
def cambiar_desperdicio_presupuesto(request, presupuesto_id):
    """
    Cambia el porcentaje de desperdicio de todos los ítems de un presupuesto y recalcula insumos.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        nuevo_desperdicio = data.get('desperdicio')  # Nuevo porcentaje de desperdicio
        presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)

        try:
            # Convertir a Decimal y validar que sea un número positivo
            nuevo_desperdicio = Decimal(nuevo_desperdicio)
            if nuevo_desperdicio < 0:
                return JsonResponse({'status': 'error', 'message': 'El desperdicio no puede ser negativo.'}, status=400)
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'Valor de desperdicio inválido.'}, status=400)

        # Actualizar el desperdicio en todos los ítems del presupuesto
        items = presupuesto.items.all()
        items.update(desperdicio=nuevo_desperdicio)

        # Recalcular los insumos de cada ítem
        for item in items:
            item.calcular_insumos()

        return JsonResponse({'status': 'success', 'message': 'Desperdicio actualizado correctamente.'})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'}, status=405)
