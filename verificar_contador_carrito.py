#!/usr/bin/env python3
"""
Script para verificar el funcionamiento del contador de carrito en el navbar
"""

import os
import sys
import django

# Configurar Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from miPaypal.models import Product, Cart, CartItem, Category, Brand
from django.urls import reverse

def test_cart_counter():
    print("🔧 INICIANDO VERIFICACIÓN DEL CONTADOR DE CARRITO")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Verificar que existan productos
    products = Product.objects.all()
    if not products.exists():
        print("❌ No hay productos en la base de datos")
        return False
    
    product = products.first()
    print(f"✅ Producto encontrado: {product.name}")
    
    # 1. Verificar página de inicio sin productos en carrito
    print("\n1️⃣ Verificando página de inicio sin productos en carrito...")
    response = client.get(reverse('index-page'))
    if response.status_code == 200:
        print("✅ Página de inicio carga correctamente")
        # Verificar que cart_count esté en el contexto
        if 'cart_count' in response.context:
            cart_count = response.context['cart_count']
            print(f"✅ cart_count en contexto: {cart_count}")
        else:
            print("❌ cart_count no está en el contexto")
    else:
        print(f"❌ Error al cargar página de inicio: {response.status_code}")
        return False
    
    # 2. Añadir producto al carrito
    print(f"\n2️⃣ Añadiendo producto {product.name} al carrito...")
    add_to_cart_url = reverse('add_to_cart', args=[product.id]) + '?next=' + reverse('index-page')
    response = client.post(add_to_cart_url)
    
    if response.status_code == 302:  # Redirección esperada
        print("✅ Producto añadido al carrito correctamente")
    else:
        print(f"❌ Error al añadir producto al carrito: {response.status_code}")
        return False
    
    # 3. Verificar contador después de añadir producto
    print("\n3️⃣ Verificando contador después de añadir producto...")
    response = client.get(reverse('index-page'))
    if response.status_code == 200:
        if 'cart_count' in response.context:
            cart_count = response.context['cart_count']
            print(f"✅ cart_count después de añadir: {cart_count}")
            if cart_count > 0:
                print("✅ Contador actualizado correctamente")
            else:
                print("❌ Contador no se actualizó")
        else:
            print("❌ cart_count no está en el contexto")
    
    # 4. Verificar página de productos
    print("\n4️⃣ Verificando página de productos...")
    response = client.get(reverse('products-page'))
    if response.status_code == 200:
        print("✅ Página de productos carga correctamente")
        if 'cart_count' in response.context:
            cart_count = response.context['cart_count']
            print(f"✅ cart_count en página de productos: {cart_count}")
        else:
            print("❌ cart_count no está en el contexto de productos")
    
    # 5. Añadir otro producto desde página de productos
    print(f"\n5️⃣ Añadiendo otro producto desde página de productos...")
    if products.count() > 1:
        second_product = products[1]
        add_url = reverse('add_to_cart', args=[second_product.id]) + '?next=' + reverse('products-page')
        response = client.post(add_url)
        
        if response.status_code == 302:
            print("✅ Segundo producto añadido correctamente")
            
            # Verificar contador
            response = client.get(reverse('products-page'))
            if 'cart_count' in response.context:
                cart_count = response.context['cart_count']
                print(f"✅ cart_count después del segundo producto: {cart_count}")
            
        else:
            print(f"❌ Error al añadir segundo producto: {response.status_code}")
    
    # 6. Verificar carrito
    print("\n6️⃣ Verificando vista del carrito...")
    response = client.get(reverse('view_cart'))
    if response.status_code == 200:
        print("✅ Vista del carrito carga correctamente")
        if 'cart_count' in response.context:
            cart_count = response.context['cart_count']
            print(f"✅ cart_count en vista del carrito: {cart_count}")
        else:
            print("❌ cart_count no está en el contexto del carrito")
        
        # Verificar items en el carrito
        if 'cart_items' in response.context:
            cart_items = response.context['cart_items']
            print(f"✅ Items en carrito: {len(cart_items)}")
            total_items = sum(item.quantity for item in cart_items)
            print(f"✅ Total de productos: {total_items}")
        
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    return True

if __name__ == "__main__":
    test_cart_counter()
