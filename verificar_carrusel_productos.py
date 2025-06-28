#!/usr/bin/env python3
"""
Script de verificación para las mejoras del carrusel de productos destacados en index.html
Verifica la implementación de imágenes responsivas, estilos CSS y funcionalidad mejorada.
"""

import os
import re
from pathlib import Path

def verificar_carrusel_productos():
    """Verifica las mejoras implementadas en el carrusel de productos destacados"""
    
    print("🔍 VERIFICANDO MEJORAS DEL CARRUSEL DE PRODUCTOS DESTACADOS")
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
            
        # Verificaciones del HTML
        verificaciones_html = [
            (r'carousel-image-container', "Contenedor de imagen del carrusel"),
            (r'class="d-block w-100 carousel-image"', "Clase CSS para imagen del carrusel"),
            (r'loading="lazy"', "Carga lazy de imágenes"),
            (r'default-product\.jpg', "Imagen de fallback para errores"),
            (r'class="carousel-overlay"', "Overlay para mejor contraste"),
            (r'class="carousel-content"', "Contenedor de contenido adaptado"),
            (r'product-badge', "Badge de producto destacado"),
            (r'price-container', "Contenedor de precio mejorado"),
            (r'class="carousel-actions"', "Contenedor de acciones"),
            (r'class="carousel-control-custom"', "Controles personalizados"),
            (r'col-12 col-lg-10 col-xl-8', "Responsividad mejorada del carrusel"),
            (r'd-none d-sm-inline', "Texto adaptativo para móviles"),
            (r'd-sm-none', "Texto específico para móviles"),
            (r'overflow-hidden', "Prevención de desbordamiento")
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
            
        # Verificaciones del CSS
        verificaciones_css = [
            (r'\.carousel-image-container', "Estilos del contenedor de imagen"),
            (r'\.carousel-image', "Estilos de la imagen del carrusel"),
            (r'object-fit: cover', "Object-fit para imágenes"),
            (r'object-position: center', "Posicionamiento centrado de imágenes"),
            (r'transform: scale\(1\.05\)', "Efecto hover en imágenes"),
            (r'\.carousel-overlay', "Estilos del overlay"),
            (r'linear-gradient', "Gradiente para mejor contraste"),
            (r'\.carousel-caption', "Estilos del caption mejorado"),
            (r'\.price-container', "Estilos del contenedor de precio"),
            (r'backdrop-filter: blur', "Efecto de desenfoque"),
            (r'\.carousel-control-custom', "Estilos de controles personalizados"),
            (r'@media \(max-width: 768px\)', "Media query para tablets"),
            (r'@media \(max-width: 576px\)', "Media query para móviles"),
            (r'transition:', "Transiciones suaves"),
            (r'\.carousel-indicators.*border-radius: 50%', "Indicadores circulares"),
            (r'\.text-white-75', "Clase de texto semi-transparente"),
            (r'height: 450px', "Altura del carrusel en desktop"),
            (r'height: 300px', "Altura del carrusel en tablet"),
            (r'height: 250px', "Altura del carrusel en móvil")
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
        print("El carrusel de productos destacados ha sido mejorado correctamente con:")
        print("  • Imágenes responsivas con object-fit")
        print("  • Overlay de gradiente para mejor contraste")
        print("  • Controles personalizados")
        print("  • Adaptabilidad móvil completa")
        print("  • Efectos hover y transiciones")
        print("  • Carga lazy de imágenes")
        print("  • Imagen de fallback para errores")
        print("  • Indicadores mejorados")
        print("  • Precios destacados con efectos")
        print("  • Botones adaptativos")
        return True

def main():
    """Función principal"""
    verificar_carrusel_productos()

if __name__ == "__main__":
    main()
