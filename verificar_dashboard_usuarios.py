#!/usr/bin/env python
"""
Script para verificar el funcionamiento del dashboard de usuarios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from miPaypal.models import CustomUser

def verificar_usuarios():
    """Verificar que los usuarios tienen todos los campos necesarios"""
    print("=== VERIFICACIÓN DE USUARIOS DEL DASHBOARD ===\n")
    
    # Contar usuarios por rol
    usuarios_admin = CustomUser.objects.filter(rol='admin').count()
    usuarios_staff = CustomUser.objects.filter(rol='staff').count() 
    usuarios_cliente = CustomUser.objects.filter(rol='cliente').count()
    
    print(f"📊 Estadísticas de usuarios:")
    print(f"   - Administradores: {usuarios_admin}")
    print(f"   - Staff: {usuarios_staff}")
    print(f"   - Clientes: {usuarios_cliente}")
    print(f"   - Total: {CustomUser.objects.count()}\n")
    
    # Verificar algunos usuarios de ejemplo
    print("👥 Usuarios de ejemplo:")
    usuarios_muestra = CustomUser.objects.all()[:5]
    
    for user in usuarios_muestra:
        print(f"   - {user.username}")
        print(f"     Nombre: {user.get_full_name() or 'No especificado'}")
        print(f"     Email: {user.email}")
        print(f"     Rol: {user.get_rol_display()}")
        print(f"     RUT: {user.rut or 'No especificado'}")
        print(f"     Teléfono: {user.telefono or 'No especificado'}")
        print(f"     Activo: {'Sí' if user.is_active else 'No'}")
        print(f"     Último acceso: {user.last_login or 'Nunca'}")
        print()
    
    print("✅ Verificación completada. Los formularios de edición deberían mostrar todos los campos correctamente.")

if __name__ == '__main__':
    verificar_usuarios()
