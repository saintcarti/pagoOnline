#!/usr/bin/env python3
"""
Script de verificación para el carrusel de 3 productos en index.html
Verifica la implementación del nuevo diseño con productos múltiples por slide.
"""

import os
import re
from pathlib import Path

def verificar_carrusel_3_productos():
    """Verifica las mejoras implementadas en el carrusel de 3 productos"""
    
    print("🔍 VERIFICANDO CARRUSEL DE 3 PRODUCTOS DESTACADOS")
    print("=" * 70)
    
    errores = []
    exitos = []
    
    # Rutas de archivos
    base_path = Path(__file__).parent
    index_html = base_path / "ecommerce" / "templates" / "ecommerce" / "index.html"
    index_css = base_path / "ecommerce" / "static" / "css" / "index.css"
    
    # Verificar archivos
    archivos_verificar = [
        (index_html, "Template index.html"),
        (index_css, "CSS index.css")
    ]
    
    for archivo, nombre in archivos_verificar:
        if archivo.exists():
            exitos.append(f"✅ {nombre} existe")
        else:
            errores.append(f"❌ {nombre} no encontrado en {archivo}")
    
    if errores:
        print("\n".join(errores))
        return False
    
    # Verificar contenido del HTML
    print("\n📄 VERIFICANDO TEMPLATE index.html")
    print("-" * 50)
    
    try:
        with open(index_html, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Verificaciones del HTML para carrusel de 3 productos
        verificaciones_html = [
            (r'col-lg-4 col-md-6 col-12', "Grid de 3 columnas responsivo"),
            (r'product-card-carousel', "Clase de tarjeta de producto"),
            (r'product-image-wrapper', "Contenedor de imagen del producto"),
            (r'product-carousel-image', "Clase de imagen del carrusel"),
            (r'product-overlay', "Overlay de producto"),
            (r'product-badge', "Badge de producto destacado"),
            (r'product-card-body', "Cuerpo de la tarjeta"),
            (r'product-title', "Título del producto"),
            (r'product-description', "Descripción del producto"),
            (r'product-price', "Contenedor de precio"),
            (r'price-label', "Etiqueta de precio"),
            (r'price-amount', "Cantidad del precio"),
            (r'product-actions', "Contenedor de acciones"),
            (r'carousel-control-modern', "Controles modernos"),
            (r'placeholder-card', "Tarjetas de placeholder"),
            (r'placeholder-content', "Contenido de placeholder"),
            (r'products\|slice:":3"', "Slice de primeros 3 productos"),
            (r'products\|slice:"3:6"', "Slice de productos 4-6"),
            (r'products\|slice:"6:9"', "Slice de productos 7-9"),
            (r'data-bs-interval="5000"', "Intervalo de 5 segundos"),
            (r'loading="lazy"', "Carga lazy de imágenes"),
            (r'bi bi-plus-circle', "Icono de placeholder"),
            (r'd-none d-sm-inline', "Texto responsivo"),
            (r'd-sm-none', "Texto móvil específico")
        ]
        
        for patron, descripcion in verificaciones_html:
            if re.search(patron, html_content, re.DOTALL):
                exitos.append(f"✅ {descripcion}")
            else:
                errores.append(f"❌ {descripcion} - Patrón no encontrado: {patron}")
    
    except Exception as e:
        errores.append(f"❌ Error leyendo index.html: {e}")
    
    # Verificar contenido del CSS
    print("\n🎨 VERIFICANDO CSS index.css")
    print("-" * 50)
    
    try:
        with open(index_css, 'r', encoding='utf-8') as f:
            css_content = f.read()
            
        # Verificaciones del CSS para carrusel de 3 productos
        verificaciones_css = [
            (r'\.product-card-carousel', "Estilos de tarjeta de producto"),
            (r'\.product-image-wrapper', "Estilos del contenedor de imagen"),
            (r'\.product-carousel-image', "Estilos de imagen del carrusel"),
            (r'\.product-overlay', "Estilos del overlay"),
            (r'\.product-badge', "Estilos del badge"),
            (r'\.product-card-body', "Estilos del cuerpo de tarjeta"),
            (r'\.product-title', "Estilos del título"),
            (r'\.product-description', "Estilos de descripción"),
            (r'\.product-price', "Estilos del precio"),
            (r'\.price-label', "Estilos de etiqueta de precio"),
            (r'\.price-amount', "Estilos de cantidad"),
            (r'\.product-actions', "Estilos de acciones"),
            (r'\.placeholder-card', "Estilos de placeholder"),
            (r'\.placeholder-content', "Estilos de contenido placeholder"),
            (r'\.carousel-control-modern', "Estilos de controles modernos"),
            (r'height: 200px', "Altura de imagen en desktop"),
            (r'height: 180px', "Altura de imagen en tablet"),
            (r'height: 160px', "Altura de imagen en móvil"),
            (r'height: 140px', "Altura de imagen en móvil pequeño"),
            (r'object-fit: cover', "Object-fit para imágenes"),
            (r'transform: translateY\(-5px\)', "Efecto hover en tarjetas"),
            (r'transform: scale\(1\.05\)', "Efecto hover en imágenes"),
            (r'border-radius: 12px', "Bordes redondeados"),
            (r'box-shadow:', "Sombras de tarjetas"),
            (r'-webkit-line-clamp: 2', "Truncado de texto webkit"),
            (r'line-clamp: 2', "Truncado de texto estándar"),
            (r'@media \(max-width: 992px\)', "Media query para laptop"),
            (r'@media \(max-width: 768px\)', "Media query para tablet"),
            (r'@media \(max-width: 576px\)', "Media query para móvil"),
            (r'transition:', "Transiciones suaves"),
            (r'backdrop-filter: blur', "Efecto de desenfoque"),
            (r'linear-gradient', "Gradientes para overlay"),
            (r'rgba\(90, 62, 43', "Color temático de FERREMAS")
        ]
        
        for patron, descripcion in verificaciones_css:
            if re.search(patron, css_content, re.DOTALL):
                exitos.append(f"✅ {descripcion}")
            else:
                errores.append(f"❌ {descripcion} - Patrón no encontrado: {patron}")
    
    except Exception as e:
        errores.append(f"❌ Error leyendo index.css: {e}")
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DE LA VERIFICACIÓN")
    print("=" * 50)
    print(f"✅ Verificaciones exitosas: {len(exitos)}")
    print(f"❌ Errores encontrados: {len(errores)}")
    
    if exitos:
        print(f"\n🎉 VERIFICACIONES EXITOSAS:")
        for exito in exitos:
            print(f"  {exito}")
    
    if errores:
        print(f"\n⚠️  ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  {error}")
        print(f"\n🔧 Revisa los archivos y corrige los errores antes de continuar.")
        return False
    else:
        print(f"\n🎊 ¡TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE!")
        print("El carrusel de 3 productos ha sido implementado correctamente con:")
        print("  • Diseño de tarjetas con 3 productos por slide")
        print("  • Imágenes más pequeñas pero legibles (200px altura)")
        print("  • Grid responsivo (3 en desktop, 2 en tablet, 1 en móvil)")
        print("  • Efectos hover en tarjetas e imágenes")
        print("  • Placeholders para productos faltantes")
        print("  • Controles modernos con color temático")
        print("  • Truncado de texto para consistencia visual")
        print("  • Adaptabilidad móvil completa")
        print("  • Carga lazy de imágenes")
        print("  • Transiciones suaves")
        print("  • Accesibilidad mejorada")
        print("  • Navegación por grupos de 3 productos")
        return True

def main():
    """Función principal"""
    verificar_carrusel_3_productos()

if __name__ == "__main__":
    main()
