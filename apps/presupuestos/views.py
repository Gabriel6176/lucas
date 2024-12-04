from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Presupuesto, Item, Lugar, Tipo, Revestimiento, Color, DetalleInsumo
from .forms import PresupuestoForm, ItemForm

@login_required
def dashboard(request):
    """
    Vista para mostrar el dashboard principal.
    Lista todos los presupuestos existentes con opciones para crear nuevos.
    """
    presupuestos = Presupuesto.objects.all().order_by('-fecha')  # Ordenar por fecha
    return render(request, 'dashboard.html', {'presupuestos': presupuestos})

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
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('detalle_presupuesto', presupuesto_id=item.presupuesto.numero)
    else:
        form = ItemForm(instance=item)

    return render(request, 'nuevo_item.html', {'form': form, 'presupuesto': item.presupuesto})



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
def detalle_presupuesto(request, presupuesto_id):
    """
    Vista para ver o editar los detalles de un presupuesto existente.
    Muestra un desglose de los ítems asociados y permite editar/eliminar ítems.
    """
    presupuesto = get_object_or_404(Presupuesto, numero=presupuesto_id)
    items = presupuesto.items.all()

    # Agregar el total de cada ítem al contexto
    items_con_costos = [
        {'item': item, 'costo': item.calcular_costo()} for item in items
    ]

    # Calcular el costo total del presupuesto
    total = sum(entry['costo'] for entry in items_con_costos)

    return render(request, 'detalle_presupuesto.html', {
        'presupuesto': presupuesto,
        'items': items,  # Esto permite que puedas usarlo si lo necesitas
        'items_con_costos': items_con_costos,
        'total': total,
    })
