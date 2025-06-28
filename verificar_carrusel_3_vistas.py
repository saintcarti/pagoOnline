#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar el carrusel de 3 vistas con estilos uniformes
"""

import os
import re

def verificar_carrusel_3_vistas():
    """Verifica la implementación del carrusel de 3 vistas"""
    
    print("🔍 VERIFICANDO CARRUSEL DE 3 VISTAS CON ESTILOS UNIFORMES")
    print("=" * 70)
    
    # Ruta del archivo template
    template_path = "ecommerce/templates/ecommerce/index.html"
    
    if not os.path.exists(template_path):
        print(f"❌ El archivo {template_path} no existe")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    verificaciones = []
    
    # Verificar estructura del carrusel
    verificaciones.append(("Contenedor del carrusel", 'id="simpleCarousel"' in content))
    verificaciones.append(("Indicadores del carrusel", 'carousel-indicators' in content))
    verificaciones.append(("Tres botones indicadores", content.count('data-bs-slide-to=') >= 3))
    
    # Verificar las 3 vistas
    verificaciones.append(("Vista 1: Productos Destacados", "Productos Destacados" in content))
    verificaciones.append(("Vista 2: Sucursal", "Nuestra Sucursal" in content))
    verificaciones.append(("Vista 3: Info FERREMAS", "Acerca de FERREMAS" in content))
    
    # Verificar altura uniforme
    verificaciones.append(("Clase de altura uniforme", "carousel-slide-content" in content))
    verificaciones.append(("Altura fija 450px", "height: 450px" in content))
    verificaciones.append(("Flexbox centrado", "display: flex" in content and "align-items: center" in content))
    
    # Verificar indicadores estilo líneas
    verificaciones.append(("Indicadores estilo líneas", "width: 30px" in content and "height: 4px" in content))
    verificaciones.append(("Indicadores sin bordes", "border: none" in content))
    verificaciones.append(("Indicador activo expandido", "width: 40px" in content))
    
    # Verificar responsividad
    verificaciones.append(("Media query tablet", "@media (max-width: 768px)" in content))
    verificaciones.append(("Media query móvil", "@media (max-width: 576px)" in content))
    verificaciones.append(("Altura responsive tablet", "height: 350px" in content))
    verificaciones.append(("Altura responsive móvil", "height: 300px" in content))
    
    # Verificar controles
    verificaciones.append(("Controles prev/next", "carousel-control-prev" in content and "carousel-control-next" in content))
    
    # Verificar contenido específico
    verificaciones.append(("Productos con fallback", "Martillo Profesional" in content))
    verificaciones.append(("Info sucursal completa", "Av. Providencia 1234" in content))
    verificaciones.append(("Estadísticas empresa", "25+" in content and "500+" in content))
    verificaciones.append(("Backdrop blur effect", "backdrop-filter: blur" in content))
    
    print("📊 RESULTADOS DE LA VERIFICACIÓN")
    print("=" * 50)
    
    exitosas = 0
    total = len(verificaciones)
    
    for descripcion, resultado in verificaciones:
        if resultado:
            print(f"  ✅ {descripcion}")
            exitosas += 1
        else:
            print(f"  ❌ {descripcion}")
    
    print("\n" + "=" * 50)
    print(f"✅ Verificaciones exitosas: {exitosas}")
    print(f"❌ Errores encontrados: {total - exitosas}")
    
    if exitosas == total:
        print("\n🎊 ¡TODAS LAS VERIFICACIONES PASARON EXITOSAMENTE!")
        print("El carrusel de 3 vistas ha sido implementado correctamente con:")
        print("  • Altura uniforme de 450px en todas las vistas")
        print("  • Indicadores estilo líneas modernas (30x4px)")
        print("  • Contenido centrado con flexbox")
        print("  • Responsividad completa (350px tablet, 300px móvil)")
        print("  • Efectos visuales mejorados")
        print("  • Transiciones suaves")
        return True
    else:
        print(f"\n🔧 Revisa los archivos y corrige los {total - exitosas} errores antes de continuar.")
        return False

if __name__ == "__main__":
    verificar_carrusel_3_vistas()
