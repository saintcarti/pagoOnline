#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from random import choice, randint

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import ContactMessage, CustomUser

# Datos de prueba para mensajes de contacto
messages_data = [
    {
        'name': 'Juan Pérez',
        'email': 'juan.perez@gmail.com',
        'phone': '+56912345678',
        'reason': 'ventas',
        'message': 'Hola, me interesa conocer más sobre sus productos de ferretería. ¿Tienen catálogo disponible?',
        'status': 'pendiente'
    },
    {
        'name': 'María González',
        'email': 'maria.gonzalez@hotmail.com',
        'phone': '+56987654321',
        'reason': 'soporte',
        'message': 'Compré una herramienta la semana pasada y tengo dudas sobre su uso. ¿Podrían ayudarme?',
        'status': 'en_proceso'
    },
    {
        'name': 'Carlos Rodríguez',
        'email': 'carlos.rod@yahoo.com',
        'phone': '+56956781234',
        'reason': 'reclamo',
        'message': 'El producto que recibí no corresponde a lo que pedí. Quiero hacer la devolución correspondiente.',
        'status': 'pendiente'
    },
    {
        'name': 'Ana López',
        'email': 'ana.lopez@gmail.com',
        'phone': '+56934567890',
        'reason': 'ventas',
        'message': '¿Hacen envíos a regiones? Necesito cotizar unas herramientas para mi taller.',
        'status': 'resuelto'
    },
    {
        'name': 'Diego Martínez',
        'email': 'diego.martinez@outlook.com',
        'phone': '+56923456789',
        'reason': 'otro',
        'message': 'Me gustaría saber si tienen programas de descuentos para empresas constructoras.',
        'status': 'en_proceso'
    },
    {
        'name': 'Laura Herrera',
        'email': 'laura.herrera@gmail.com',
        'phone': '+56945678123',
        'reason': 'ventas',
        'message': 'Necesito una cotización urgente para materiales de construcción. ¿Cuánto demoran en responder?',
        'status': 'pendiente'
    },
    {
        'name': 'Roberto Silva',
        'email': 'roberto.silva@empresa.cl',
        'phone': '+56978912345',
        'reason': 'soporte',
        'message': 'La garantía de mi taladro está por vencer. ¿Qué debo hacer para extenderla?',
        'status': 'cerrado'
    },
    {
        'name': 'Francisca Morales',
        'email': 'fran.morales@hotmail.com',
        'phone': '+56967894321',
        'reason': 'reclamo',
        'message': 'El delivery llegó tarde y algunos productos venían dañados. Necesito una solución.',
        'status': 'resuelto'
    }
]

print("Creando mensajes de contacto de prueba...")

# Obtener usuarios admin para asignar como "atendido por"
admin_users = CustomUser.objects.filter(is_staff=True)

for i, msg_data in enumerate(messages_data):
    # Crear fechas aleatorias en los últimos 30 días
    days_ago = randint(0, 30)
    created_date = datetime.now() - timedelta(days=days_ago)
    
    message, created = ContactMessage.objects.get_or_create(
        email=msg_data['email'],
        defaults={
            'name': msg_data['name'],
            'phone': msg_data['phone'],
            'reason': msg_data['reason'],
            'message': msg_data['message'],
            'status': msg_data['status'],
            'created_at': created_date,
        }
    )
    
    # Si el mensaje ya está resuelto o cerrado, asignar un admin
    if message.status in ['resuelto', 'cerrado'] and admin_users.exists():
        message.attended_by = choice(admin_users)
        if message.status == 'resuelto':
            message.response = f"Estimado/a {message.name}, hemos revisado su consulta y ya está solucionado. Gracias por contactarnos."
        message.save()
    
    if created:
        print(f"✓ Mensaje creado: {msg_data['name']} - {msg_data['reason']}")
    else:
        print(f"- Mensaje ya existe: {msg_data['name']}")

print(f"\nTotal mensajes de contacto: {ContactMessage.objects.count()}")
print(f"Mensajes pendientes: {ContactMessage.objects.filter(status='pendiente').count()}")
print(f"Mensajes en proceso: {ContactMessage.objects.filter(status='en_proceso').count()}")
print(f"Mensajes resueltos: {ContactMessage.objects.filter(status='resuelto').count()}")
print(f"Mensajes cerrados: {ContactMessage.objects.filter(status='cerrado').count()}")

print("\n¡Datos de prueba creados exitosamente!")
