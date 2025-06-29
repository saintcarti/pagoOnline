# Generated by Django 5.2.3 on 2025-06-29 02:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miPaypal', '0004_auto_20250628_2112'),
    ]

    operations = [
        # Agregar nuevos choices al campo order_status
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pendiente'),
                    ('confirmed', 'Confirmada'),
                    ('processing', 'En Proceso'),
                    ('packed', 'Empacada'),
                    ('shipped', 'Enviada'),
                    ('delivered', 'Entregada'),
                    ('cancelled', 'Cancelada'),
                ],
                default='pending',
                max_length=20
            ),
        ),
        
        # Agregar campo order_type
        migrations.AddField(
            model_name='order',
            name='order_type',
            field=models.CharField(
                choices=[
                    ('online', 'Compra Online'),
                    ('manual', 'Orden Manual'),
                    ('phone', 'Orden Telefónica'),
                ],
                default='online',
                max_length=20
            ),
        ),
        
        # Agregar campo created_by
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='created_orders',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Creada por'
            ),
        ),
        
        # Agregar campo notes
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notas adicionales'),
        ),
        
        # Agregar campo tracking_number
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Número de seguimiento'),
        ),
        
        # Agregar campo estimated_delivery
        migrations.AddField(
            model_name='order',
            name='estimated_delivery',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Entrega estimada'),
        ),
    ]
