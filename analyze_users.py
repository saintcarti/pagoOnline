#!/usr/bin/env python
"""
Script para actualizar usuarios existentes que no tienen first_name/last_name
"""

import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import CustomUser

def update_users_without_names():
    """Actualiza usuarios que no tienen nombres"""
    print("Buscando usuarios sin nombres...")
    
    users_without_names = CustomUser.objects.filter(
        first_name__in=['', None], 
        last_name__in=['', None]
    )
    
    if not users_without_names:
        print("✅ Todos los usuarios tienen nombres completos")
        return
    
    print(f"📊 Usuarios sin nombres: {users_without_names.count()}")
    
    for user in users_without_names:
        print(f"\n👤 Usuario: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nombre actual: '{user.first_name}' '{user.last_name}'")
        
        # Sugerir nombres basados en el username o email
        suggested_first = user.username.capitalize()
        suggested_last = "Usuario"
        
        if '@' in user.email:
            email_part = user.email.split('@')[0]
            if '.' in email_part:
                parts = email_part.split('.')
                suggested_first = parts[0].capitalize()
                if len(parts) > 1:
                    suggested_last = parts[1].capitalize()
        
        print(f"   Sugerencia: '{suggested_first}' '{suggested_last}'")
        
        # No actualizar automáticamente, solo mostrar la información
        print(f"   → El usuario puede actualizar su perfil desde la página de perfil")

def show_stats():
    """Muestra estadísticas de usuarios"""
    total_users = CustomUser.objects.count()
    users_with_names = CustomUser.objects.exclude(
        first_name__in=['', None]
    ).exclude(
        last_name__in=['', None]
    ).count()
    
    users_without_names = total_users - users_with_names
    
    print(f"📊 Estadísticas de usuarios:")
    print(f"   Total de usuarios: {total_users}")
    print(f"   Con nombres completos: {users_with_names}")
    print(f"   Sin nombres completos: {users_without_names}")
    print(f"   Porcentaje completo: {(users_with_names/total_users*100):.1f}%")

if __name__ == "__main__":
    print("=" * 60)
    print("ANÁLISIS DE USUARIOS SIN NOMBRES")
    print("=" * 60)
    
    show_stats()
    update_users_without_names()
    
    print("\n" + "=" * 60)
    print("RECOMENDACIONES:")
    print("1. Los nuevos usuarios ahora pueden registrarse con nombres completos")
    print("2. Los usuarios existentes pueden actualizar su perfil desde la página de perfil")
    print("3. El template ahora maneja correctamente usuarios sin nombres")
    print("=" * 60)
