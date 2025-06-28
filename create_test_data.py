#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pagoOnline.settings')
django.setup()

from miPaypal.models import Brand, Category

# Crear marcas de prueba
brands_data = [
    'Samsung',
    'Apple',
    'Nike',
    'Adidas',
    'Sony'
]

categories_data = [
    'Electrónicos',
    'Ropa',
    'Deportes',
    'Hogar',
    'Libros'
]

print("Creando marcas...")
for brand_name in brands_data:
    brand, created = Brand.objects.get_or_create(name=brand_name)
    if created:
        print(f"✓ Marca creada: {brand_name}")
    else:
        print(f"- Marca ya existe: {brand_name}")

print("\nCreando categorías...")
for category_name in categories_data:
    category, created = Category.objects.get_or_create(name=category_name)
    if created:
        print(f"✓ Categoría creada: {category_name}")
    else:
        print(f"- Categoría ya existe: {category_name}")

print(f"\nTotal marcas: {Brand.objects.count()}")
print(f"Total categorías: {Category.objects.count()}")
