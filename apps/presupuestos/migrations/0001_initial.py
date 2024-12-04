# Generated by Django 5.1.3 on 2024-12-03 21:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Color",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Lugar",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Revestimiento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Tipo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("numero", models.IntegerField(unique=True)),
                ("detalle", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Insumo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("codigo", models.CharField(max_length=50)),
                ("descripcion", models.TextField()),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                ("unidad_medida", models.CharField(max_length=50)),
                ("formula", models.TextField()),
                (
                    "color",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="presupuestos.color",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Presupuesto",
            fields=[
                ("numero", models.AutoField(primary_key=True, serialize=False)),
                ("cliente", models.CharField(max_length=255)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                (
                    "lugar",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.lugar",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cantidad", models.PositiveIntegerField()),
                ("ancho", models.DecimalField(decimal_places=2, max_digits=10)),
                ("alto", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "desperdicio",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "color",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.color",
                    ),
                ),
                (
                    "presupuesto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="presupuestos.presupuesto",
                    ),
                ),
                (
                    "revestimiento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.revestimiento",
                    ),
                ),
                (
                    "tipo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.tipo",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DetalleInsumo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cantidad_usada",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "precio_unitario",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("precio_total", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "insumo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.insumo",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.item",
                    ),
                ),
                (
                    "presupuesto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="presupuestos.presupuesto",
                    ),
                ),
            ],
        ),
    ]
