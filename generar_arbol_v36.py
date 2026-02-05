"""
generar_arbol_v36.py
Generador Visual del Árbol de la Vida Personal v3.6

MEJORAS v3.6:
- Tamaños de nodos según peso (ponderación v3.6)
- Colores diferenciados por pilar
- Senderos críticos destacados en rojo
- Retrógrados marcados con ℞
- Convergencias resaltadas
- Export SVG mejorado
- HTML interactivo con tooltips

SAVP v3.6 - Sistema Árbol de la Vida Personal
Fecha: Febrero 2025
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch
import numpy as np
from typing import Dict, List, Optional


# ============================================================================
# CONFIGURACIÓN VISUAL
# ============================================================================

# Posiciones Sephiroth (normalizadas 0-10 x, 0-14 y)
POSICIONES_SEPHIROTH = {
    'Kether': (5, 13),
    'Chokmah': (7.5, 11.5),
    'Binah': (2.5, 11.5),
    'Daath': (5, 10.5),
    'Chesed': (7.5, 9),
    'Geburah': (2.5, 9),
    'Tiphareth': (5, 7.5),
    'Netzach': (7.5, 5),
    'Hod': (2.5, 5),
    'Yesod': (5, 3),
    'Malkuth': (5, 0.5)
}

# Colores por pilar (v3.6)
COLORES_PILARES = {
    'derecho': '#1e90ff',    # Azul (Chesed-Netzach)
    'izquierdo': '#dc143c',  # Rojo (Binah-Geburah-Hod)
    'central': '#ffd700'     # Dorado (Kether-Tiphareth-Yesod-Malkuth)
}

# Colores base Sephiroth (cuando no hay planeta)
COLORES_SEPHIROTH_BASE = {
    'Kether': '#f0f0f0',
    'Chokmah': '#e0e0e0',
    'Binah': '#4a4a4a',
    'Daath': '#707070',
    'Chesed': '#6bb6ff',
    'Geburah': '#ff6b6b',
    'Tiphareth': '#ffed4e',
    'Netzach': '#90ee90',
    'Hod': '#ffa500',
    'Yesod': '#ba55d3',
    'Malkuth': '#8b7355'
}

# Símbolos planetarios
SIMBOLOS_PLANETAS = {
    'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀',
    'Marte': '♂', 'Jupiter': '♃', 'Saturno': '♄', 'Urano': '♅',
    'Neptuno': '♆', 'Pluton': '♇'
}

# 22 Senderos
SENDEROS_22 = [
    ('Kether', 'Chokmah', 11, 0, 'El Loco'),
    ('Kether', 'Binah', 12, 1, 'El Mago'),
    ('Kether', 'Tiphareth', 13, 2, 'La Sacerdotisa'),
    ('Chokmah', 'Binah', 14, 3, 'La Emperatriz'),
    ('Chokmah', 'Tiphareth', 15, 4, 'El Emperador'),
    ('Chokmah', 'Chesed', 16, 5, 'El Hierofante'),
    ('Binah', 'Tiphareth', 17, 6, 'Los Enamorados'),
    ('Binah', 'Geburah', 18, 7, 'El Carro'),
    ('Chesed', 'Geburah', 19, 8, 'La Fuerza'),
    ('Chesed', 'Tiphareth', 20, 9, 'El Ermitaño'),
    ('Chesed', 'Netzach', 21, 10, 'La Rueda'),
    ('Geburah', 'Tiphareth', 22, 11, 'La Justicia'),
    ('Geburah', 'Hod', 23, 12, 'El Colgado'),
    ('Tiphareth', 'Netzach', 24, 13, 'La Muerte'),
    ('Tiphareth', 'Yesod', 25, 14, 'La Templanza'),
    ('Tiphareth', 'Hod', 26, 15, 'El Diablo'),
    ('Netzach', 'Hod', 27, 16, 'La Torre'),
    ('Netzach', 'Yesod', 28, 17, 'La Estrella'),
    ('Netzach', 'Malkuth', 29, 18, 'La Luna'),
    ('Hod', 'Yesod', 30, 19, 'El Sol'),
    ('Hod', 'Malkuth', 31, 20, 'El Juicio'),
    ('Yesod', 'Malkuth', 32, 21, 'El Mundo')
]


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class ArbolVidaV36:
    """Generador visual del Árbol de la Vida con refinamientos v3.6."""
    
    def __init__(self, ancho=18, alto=20):
        """Inicializar canvas."""
        self.fig, self.ax = plt.subplots(figsize=(ancho, alto))
        self.ax.set_xlim(-2, 16)  # Más ancho para panel lateral
        self.ax.set_ylim(-1, 15)
        self.ax.axis('off')
        self.ax.set_aspect('equal')
        
        # Datos del análisis
        self.planetas_savp = {}
        self.senderos_criticos = []
        self.convergencias = []
        self.diagnostico = {}
        self.porcentajes = {}
    
    
    def cargar_analisis(self, analisis_savp: dict):
        """Carga análisis SAVP v3.6."""
        self.planetas_savp = analisis_savp.get('planetas_savp', {})
        self.senderos_criticos = analisis_savp.get('senderos_criticos_resumen', [])
        self.convergencias = analisis_savp.get('cadena_dispositores', {}).get('convergencias', [])
        self.diagnostico = analisis_savp.get('diagnostico', {})
        self.porcentajes = analisis_savp.get('porcentajes', {})
    
    
    def dibujar_senderos(self):
        """Dibuja los 22 senderos con priorización de críticos."""
        
        # Obtener números de senderos críticos
        numeros_criticos = set()
        for sc in self.senderos_criticos:
            num = sc.get('sendero', {}).get('numero')
            if num:
                numeros_criticos.add(num)
        
        for seph1, seph2, num_sendero, arcano, nombre in SENDEROS_22:
            pos1 = POSICIONES_SEPHIROTH.get(seph1)
            pos2 = POSICIONES_SEPHIROTH.get(seph2)
            
            if pos1 and pos2:
                # Color y grosor según si es crítico
                if num_sendero in numeros_criticos:
                    color = '#ff0000'  # Rojo para críticos
                    linewidth = 3.5
                    alpha = 0.8
                    zorder = 10  # Al frente
                else:
                    color = '#cccccc'  # Gris para normales
                    linewidth = 1.5
                    alpha = 0.4
                    zorder = 1  # Al fondo
                
                # Línea del sendero
                self.ax.plot(
                    [pos1[0], pos2[0]],
                    [pos1[1], pos2[1]],
                    color=color,
                    linewidth=linewidth,
                    alpha=alpha,
                    zorder=zorder
                )
                
                # Número del arcano en punto medio (solo críticos)
                if num_sendero in numeros_criticos:
                    mid_x = (pos1[0] + pos2[0]) / 2
                    mid_y = (pos1[1] + pos2[1]) / 2
                    
                    self.ax.text(
                        mid_x, mid_y,
                        str(arcano),
                        fontsize=9,
                        weight='bold',
                        color='red',
                        bbox=dict(boxstyle='circle', facecolor='white', edgecolor='red', linewidth=1.5),
                        ha='center',
                        va='center',
                        zorder=11
                    )
    
    
    def dibujar_sephiroth(self):
        """Dibuja las Sephiroth con tamaño según peso."""
        
        for seph_nombre, pos in POSICIONES_SEPHIROTH.items():
            # Buscar planeta en esta Sephirah
            planeta_en_seph = None
            planeta_data = None
            
            for nombre_planeta, data in self.planetas_savp.items():
                if data.get('sephirah') == seph_nombre:
                    planeta_en_seph = nombre_planeta
                    planeta_data = data
                    break
            
            if planeta_en_seph:
                # HAY PLANETA: Tamaño según peso
                peso = planeta_data.get('ponderacion', {}).get('peso_final', 1.0)
                
                # Escalar tamaño (0.3 - 1.2)
                radio = 0.3 + (peso / 4.0) * 0.9  # peso máx ~4 → radio 1.2
                
                # Color según pilar
                pilar = planeta_data.get('pilar', 'central')
                color = COLORES_PILARES.get(pilar, '#ffd700')
                
                # Marcador si es convergencia
                es_convergencia = planeta_en_seph in self.convergencias
                edgecolor = '#ff00ff' if es_convergencia else '#333333'
                linewidth = 4 if es_convergencia else 2
                
            else:
                # NO HAY PLANETA: Tamaño base pequeño
                radio = 0.25
                color = COLORES_SEPHIROTH_BASE.get(seph_nombre, '#e0e0e0')
                edgecolor = '#999999'
                linewidth = 1.5
            
            # Dibujar círculo
            circle = Circle(
                pos, radio,
                facecolor=color,
                edgecolor=edgecolor,
                linewidth=linewidth,
                zorder=20,
                alpha=0.9
            )
            self.ax.add_patch(circle)
            
            # Texto: Nombre Sephirah
            self.ax.text(
                pos[0], pos[1] + radio + 0.3,
                seph_nombre.upper(),
                fontsize=10,
                weight='bold',
                ha='center',
                va='bottom',
                zorder=21
            )
            
            # Si hay planeta: Símbolo + Peso
            if planeta_en_seph:
                simbolo = SIMBOLOS_PLANETAS.get(planeta_en_seph, planeta_en_seph[:3])
                retro = " ℞" if planeta_data.get('astronomico', {}).get('retrogrado') else ""
                
                self.ax.text(
                    pos[0], pos[1],
                    f"{simbolo}{retro}",
                    fontsize=14 + (radio * 4),  # Más grande si más peso
                    weight='bold',
                    ha='center',
                    va='center',
                    zorder=22,
                    color='#000000'
                )
                
                # Peso debajo
                self.ax.text(
                    pos[0], pos[1] - radio - 0.25,
                    f"{peso:.2f}",
                    fontsize=9,
                    ha='center',
                    va='top',
                    zorder=21,
                    style='italic',
                    color='#555555'
                )
    
    
    def dibujar_pilares(self):
        """Dibuja indicadores de pilares con porcentajes."""
        
        # Posiciones de pilares (lado derecho del canvas)
        x_base = 12
        y_base = 11
        
        pilares_info = [
            ('derecho', 'PILAR DERECHO', COLORES_PILARES['derecho']),
            ('central', 'PILAR CENTRAL', COLORES_PILARES['central']),
            ('izquierdo', 'PILAR IZQUIERDO', COLORES_PILARES['izquierdo'])
        ]
        
        for i, (pilar, nombre, color) in enumerate(pilares_info):
            y = y_base - (i * 2.5)
            pct = self.porcentajes.get(pilar, 0)
            
            # Barra de porcentaje
            barra_ancho = (pct / 100) * 3
            rect = FancyBboxPatch(
                (x_base, y - 0.3), barra_ancho, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor='#333333',
                linewidth=2,
                alpha=0.8,
                zorder=15
            )
            self.ax.add_patch(rect)
            
            # Texto
            self.ax.text(
                x_base, y + 0.8,
                nombre,
                fontsize=11,
                weight='bold',
                ha='left',
                color='#333333'
            )
            
            self.ax.text(
                x_base + barra_ancho + 0.2, y,
                f"{pct:.1f}%",
                fontsize=10,
                weight='bold',
                ha='left',
                va='center',
                color=color
            )
    
    
    def dibujar_leyenda(self):
        """Dibuja leyenda de elementos."""
        
        x_legend = 12
        y_legend = 4
        
        # Título
        self.ax.text(
            x_legend, y_legend + 1,
            "LEYENDA",
            fontsize=12,
            weight='bold',
            ha='left'
        )
        
        elementos = [
            ("Sendero CRÍTICO", '#ff0000', 3),
            ("Sendero normal", '#cccccc', 1.5),
            ("Convergencia", '#ff00ff', None),  # Solo borde
            ("Retrógrado ℞", None, None)
        ]
        
        for i, (texto, color, lw) in enumerate(elementos):
            y = y_legend - (i * 0.6)
            
            if color and lw:
                # Línea de ejemplo
                self.ax.plot(
                    [x_legend, x_legend + 0.8], [y, y],
                    color=color,
                    linewidth=lw,
                    zorder=5
                )
            elif color and not lw:
                # Círculo con borde
                circle_sample = Circle(
                    (x_legend + 0.4, y), 0.2,
                    facecolor='white',
                    edgecolor=color,
                    linewidth=3,
                    zorder=5
                )
                self.ax.add_patch(circle_sample)
            
            self.ax.text(
                x_legend + 1.2, y,
                texto,
                fontsize=9,
                ha='left',
                va='center'
            )
    
    
    def dibujar_titulo(self, nombre: str = "CONSULTANTE"):
        """Dibuja título del árbol."""
        
        self.ax.text(
            5, 14.5,
            f"ÁRBOL DE LA VIDA PERSONAL",
            fontsize=18,
            weight='bold',
            ha='center',
            va='top'
        )
        
        self.ax.text(
            5, 14.0,
            nombre.upper(),
            fontsize=14,
            ha='center',
            va='top',
            style='italic'
        )
    
    
    def generar(self, nombre: str = "CONSULTANTE", guardar: str = None):
        """
        Genera el árbol completo.
        
        Args:
            nombre: Nombre del consultante
            guardar: Path para guardar (ej: 'arbol.png')
        """
        
        # Orden de dibujado (de fondo a frente)
        self.dibujar_titulo(nombre)
        self.dibujar_senderos()   # Primero senderos (fondo)
        self.dibujar_sephiroth()  # Luego Sephiroth (encima)
        self.dibujar_pilares()    # Panel lateral
        self.dibujar_leyenda()    # Leyenda
        
        # Ajustes finales
        plt.tight_layout()
        
        if guardar:
            plt.savefig(
                guardar,
                dpi=300,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            print(f"✅ Árbol guardado: {guardar}")
        else:
            plt.show()
        
        return self.fig


# ============================================================================
# FUNCIÓN DE CONVENIENCIA
# ============================================================================

def generar_arbol_desde_analisis(
    analisis_savp: dict,
    nombre: str = "CONSULTANTE",
    guardar: str = None
) -> plt.Figure:
    """
    Genera árbol directamente desde análisis SAVP v3.6.
    
    Args:
        analisis_savp: Output de procesar_carta_savp_v36_completa()
        nombre: Nombre del consultante
        guardar: Path para guardar imagen
    
    Returns:
        matplotlib.Figure
    
    Ejemplo:
        >>> from savp_v36_core_completo import procesar_carta_savp_v36_completa
        >>> analisis = procesar_carta_savp_v36_completa(None, planetas)
        >>> fig = generar_arbol_desde_analisis(analisis, "Estefanía", "arbol.png")
    """
    
    arbol = ArbolVidaV36()
    arbol.cargar_analisis(analisis_savp)
    return arbol.generar(nombre, guardar)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("✅ GENERADOR VISUAL DEL ÁRBOL v3.6")
    print("=" * 70)
    print("\nMejoras v3.6:")
    print("  • Tamaños de nodos según peso")
    print("  • Colores por pilar")
    print("  • Senderos críticos en rojo")
    print("  • Convergencias resaltadas")
    print("  • Retrógrados marcados ℞")
    print("  • Panel lateral con pilares")
    print("  • Export PNG alta calidad (300 dpi)")
    print("=" * 70)
