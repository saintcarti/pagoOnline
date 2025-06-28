#!/usr/bin/env python
"""
Script de prueba para verificar que first_name y last_name se guardan correctamente
"""

import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser
from miPaypal.forms import CustomUserCreationForm

def test_full_registration():
    """Prueba el formulario completo incluyendo first_name y last_name"""
    print("Probando registro completo con nombre y apellido...")
    
    # Datos de prueba
    form_data = {
        'first_name': 'Juan',
        'last_name': 'Pérez',
        'username': 'juanperez',
        'email': 'juan.perez@test.com',
        'password1': 'contraseñasegura123',
        'password2': 'contraseñasegura123',
        'rut': '12.345.678-9',
        'telefono': '+56912345678',
        'direccion': 'Calle Falsa 123, Santiago, Chile'
    }
    
    form = CustomUserCreationForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulario válido")
        
        # Verificar que el usuario no existe previamente
        if not CustomUser.objects.filter(username=form_data['username']).exists():
            # Crear y guardar el usuario
            user = form.save(commit=False)
            user.rol = 'cliente'
            user.save()
            
            print(f"✅ Usuario guardado:")
            print(f"   - Nombre completo: {user.get_full_name()}")
            print(f"   - First name: '{user.first_name}'")
            print(f"   - Last name: '{user.last_name}'")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - RUT: {user.rut}")
            print(f"   - Teléfono: {user.telefono}")
            print(f"   - Dirección: {user.direccion}")
            print(f"   - Rol: {user.rol}")
            
            # Verificar get_full_name
            full_name = user.get_full_name()
            if full_name == "Juan Pérez":
                print("✅ get_full_name() funciona correctamente")
            else:
                print(f"❌ get_full_name() devuelve: '{full_name}' (esperado: 'Juan Pérez')")
            
            # Verificar el método __str__ del template
            display_name = user.get_full_name() if user.get_full_name() else user.username
            print(f"✅ Nombre a mostrar en template: '{display_name}'")
            
            # Limpiar: eliminar el usuario de prueba
            user.delete()
            print("🧹 Usuario de prueba eliminado")
        else:
            print("⚠️ El usuario ya existe, no se guardó")
    else:
        print("❌ Formulario inválido:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def test_form_fields():
    """Verifica que el formulario incluye todos los campos necesarios"""
    print("\nVerificando campos del formulario...")
    
    form = CustomUserCreationForm()
    expected_fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'rut', 'telefono', 'direccion']
    
    for field in expected_fields:
        if field in form.fields:
            print(f"✅ Campo '{field}' presente en formulario")
        else:
            print(f"❌ Campo '{field}' faltante en formulario")

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE REGISTRO CON NOMBRE Y APELLIDO")
    print("=" * 60)
    
    test_form_fields()
    test_full_registration()
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)
