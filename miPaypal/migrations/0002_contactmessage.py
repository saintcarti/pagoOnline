# Generated by Django 5.2.3 on 2025-06-28 17:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miPaypal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre completo')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo electrónico')),
                ('phone', models.CharField(max_length=15, verbose_name='Teléfono')),
                ('reason', models.CharField(choices=[('ventas', 'Consulta de productos'), ('soporte', 'Soporte técnico'), ('reclamo', 'Reclamo'), ('otro', 'Otro')], max_length=20, verbose_name='Motivo')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('status', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En proceso'), ('resuelto', 'Resuelto'), ('cerrado', 'Cerrado')], default='pendiente', max_length=20, verbose_name='Estado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('response', models.TextField(blank=True, null=True, verbose_name='Respuesta')),
                ('attended_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Atendido por')),
            ],
            options={
                'verbose_name': 'Mensaje de Contacto',
                'verbose_name_plural': 'Mensajes de Contacto',
                'ordering': ['-created_at'],
            },
        ),
    ]
