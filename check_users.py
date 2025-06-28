#!/usr/bin/env python
"""
Script para verificar usuarios existentes y sus campos first_name/last_name
"""

import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser

def check_existing_users():
    """Verifica los usuarios existentes y sus campos de nombre"""
    print("Verificando usuarios existentes...")
    
    users = CustomUser.objects.all()
    
    if not users:
        print("❌ No hay usuarios en la base de datos")
        return
    
    print(f"📊 Total de usuarios: {users.count()}")
    print()
    
    for user in users:
        print(f"👤 Usuario: {user.username}")
        print(f"   - First name: '{user.first_name}'")
        print(f"   - Last name: '{user.last_name}'")
        print(f"   - get_full_name(): '{user.get_full_name()}'")
        print(f"   - Email: {user.email}")
        print(f"   - Es staff: {user.is_staff}")
        print(f"   - Es superuser: {user.is_superuser}")
        
        # Mostrar lo que mostraría el template
        display_name = user.get_full_name() if user.get_full_name() else user.username
        print(f"   - Nombre a mostrar: '{display_name}'")
        print("-" * 40)

def create_test_user_with_names():
    """Crea un usuario de prueba con nombres para verificar el template"""
    print("\nCreando usuario de prueba para verificar template...")
    
    # Verificar si ya existe
    if CustomUser.objects.filter(username='testuser').exists():
        print("⚠️ Usuario 'testuser' ya existe, eliminando...")
        CustomUser.objects.filter(username='testuser').delete()
    
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='María',
        last_name='González',
        rut='98.765.432-1',
        telefono='+56987654321',
        direccion='Calle Test 456, Valparaíso, Chile',
        rol='cliente'
    )
    
    print(f"✅ Usuario creado:")
    print(f"   - Username: {user.username}")
    print(f"   - Nombre completo: '{user.get_full_name()}'")
    print(f"   - Email: {user.email}")
    print(f"   - RUT: {user.rut}")
    print(f"   - Teléfono: {user.telefono}")
    print(f"   - Dirección: {user.direccion}")
    
    print("\n🔍 Ahora puedes probar el login con:")
    print("   Username: testuser")
    print("   Password: testpass123")
    
    return user

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE USUARIOS EXISTENTES")
    print("=" * 60)
    
    check_existing_users()
    create_test_user_with_names()
    
    print("\n" + "=" * 60)
    print("VERIFICACIÓN COMPLETADA")
    print("=" * 60)
