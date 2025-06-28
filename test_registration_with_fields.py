#!/usr/bin/env python
"""
Script de prueba para verificar que el registro incluye los campos RUT, teléfono y dirección
"""

import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser
from miPaypal.forms import CustomUserCreationForm

def test_user_creation_form():
    """Prueba el formulario de creación de usuario con los nuevos campos"""
    print("Probando el formulario CustomUserCreationForm...")
    
    # Datos de prueba
    form_data = {
        'username': 'usuarioprueba',
        'email': 'usuario@test.com',
        'password1': 'contraseñasegura123',
        'password2': 'contraseñasegura123',
        'rut': '12.345.678-9',
        'telefono': '+56912345678',
        'direccion': 'Calle Falsa 123, Santiago, Chile'
    }
    
    form = CustomUserCreationForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulario válido")
        
        # Crear el usuario (pero no guardarlo en la BD)
        user = form.save(commit=False)
        print(f"Usuario creado: {user.username}")
        print(f"Email: {user.email}")
        print(f"RUT: {user.rut}")
        print(f"Teléfono: {user.telefono}")
        print(f"Dirección: {user.direccion}")
        print(f"Rol: {user.rol}")
        
        # Verificar que el usuario no existe previamente
        if not CustomUser.objects.filter(username=user.username).exists():
            user.save()
            print("✅ Usuario guardado en la base de datos")
            
            # Verificar que se guardó correctamente
            saved_user = CustomUser.objects.get(username=user.username)
            print(f"✅ Usuario recuperado de BD:")
            print(f"   - Username: {saved_user.username}")
            print(f"   - Email: {saved_user.email}")
            print(f"   - RUT: {saved_user.rut}")
            print(f"   - Teléfono: {saved_user.telefono}")
            print(f"   - Dirección: {saved_user.direccion}")
            print(f"   - Rol: {saved_user.rol}")
            
            # Limpiar: eliminar el usuario de prueba
            saved_user.delete()
            print("🧹 Usuario de prueba eliminado")
        else:
            print("⚠️ El usuario ya existe, no se guardó")
    else:
        print("❌ Formulario inválido:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")

def test_model_fields():
    """Verifica que el modelo CustomUser tiene los campos esperados"""
    print("\nVerificando campos del modelo CustomUser...")
    
    fields = [field.name for field in CustomUser._meta.get_fields()]
    required_fields = ['rut', 'telefono', 'direccion', 'rol']
    
    for field in required_fields:
        if field in fields:
            print(f"✅ Campo '{field}' presente")
        else:
            print(f"❌ Campo '{field}' faltante")

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA DE REGISTRO CON CAMPOS ADICIONALES")
    print("=" * 60)
    
    test_model_fields()
    test_user_creation_form()
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)
