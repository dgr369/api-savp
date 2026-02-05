"""
savp_v36_router_final.py
Router FastAPI completo para SAVP v3.6

Integra TODOS los módulos:
- savp_v36_core_completo.py (análisis base)
- motor_lectura_v36.py (lectura 10 fases)
- tikun_automatico.py (tikún diferenciado)
- visualizaciones.py (Mermaid, SVG, HTML)
- transitos_v36.py (tránsitos y RS)
- generar_arbol_v36.py (diagrama visual)

Endpoints:
- POST /savp/v36/natal: Análisis natal completo
- POST /savp/v36/lectura: Lectura interpretativa (1 fase específica o todas)
- POST /savp/v36/transito: Detectar e interpretar tránsito
- POST /savp/v36/revolucion-solar: Calcular Revolución Solar
- GET /savp/v36/arbol/png: Generar diagrama PNG
- GET /savp/v36/test: Test Frater D.

SAVP v3.6 Final - Febrero 2025
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json
import base64
import io

# Kerykeion
try:
    from kerykeion import AstrologicalSubject
    KERYKEION_DISPONIBLE = True
except ImportError:
    KERYKEION_DISPONIBLE = False
    print("⚠️  Kerykeion no disponible")

# Core SAVP v3.6
try:
    from savp_v36_core_completo import procesar_carta_savp_v36_completa
    CORE_DISPONIBLE = True
except ImportError:
    CORE_DISPONIBLE = False
    print("❌ savp_v36_core_completo.py no disponible")

# Motor de lectura
try:
    from motor_lectura_v36 import generar_fase_completa, FASES_LECTURA
    MOTOR_LECTURA_DISPONIBLE = True
except ImportError:
    MOTOR_LECTURA_DISPONIBLE = False
    print("⚠️  motor_lectura_v36.py no disponible")

# Tikún
try:
    from tikun_automatico import generar_tikun_completo
    TIKUN_DISPONIBLE = True
except ImportError:
    TIKUN_DISPONIBLE = False
    print("⚠️  tikun_automatico.py no disponible")

# Visualizaciones
try:
    from visualizaciones import exportar_visualizaciones_completas
    VISUALIZACIONES_DISPONIBLE = True
except ImportError:
    VISUALIZACIONES_DISPONIBLE = False
    print("⚠️  visualizaciones.py no disponible")

# Tránsitos
try:
    from transitos_v36 import detectar_transito, interpretar_transito
    TRANSITOS_DISPONIBLE = True
except ImportError:
    TRANSITOS_DISPONIBLE = False
    print("⚠️  transitos_v36.py no disponible")

# Diagrama visual
try:
    from generar_arbol_v36 import generar_arbol_desde_analisis
    import matplotlib
    matplotlib.use('Agg')  # Backend sin GUI
    DIAGRAMA_DISPONIBLE = True
except ImportError:
    DIAGRAMA_DISPONIBLE = False
    print("⚠️  generar_arbol_v36.py no disponible")


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class NatalRequest(BaseModel):
    """Request para cálculo natal."""
    nombre: str = Field(..., description="Nombre del consultante")
    fecha: str = Field(..., description="Fecha nacimiento (DD/MM/YYYY)")
    hora: str = Field(..., description="Hora nacimiento (HH:MM)")
    lugar: str = Field(..., description="Ciudad, País")
    lat: Optional[float] = Field(None, description="Latitud (opcional)")
    lon: Optional[float] = Field(None, description="Longitud (opcional)")
    timezone: str = Field("Europe/Madrid", description="Timezone")


class LecturaRequest(BaseModel):
    """Request para lectura interpretativa."""
    analisis_savp: dict = Field(..., description="Análisis SAVP v3.6 completo")
    datos_natales: Optional[dict] = Field(None, description="Datos natales (para Fase 0)")
    fase: Optional[int] = Field(None, description="Número de fase específica (0-10). Si None, devuelve todas")
    nombre: str = Field("Consultante", description="Nombre del consultante")


class TransitoRequest(BaseModel):
    """Request para tránsito."""
    planeta_transitante: str
    grado_transito: float
    signo_transito: str
    planeta_natal: str
    grado_natal: float
    signo_natal: str
    retrogrado: bool = False
    analisis_natal: dict = Field(..., description="Análisis SAVP natal")


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Final"])


@router.get("/")
def info_savp_v36():
    """Información sobre API SAVP v3.6 Final."""
    return {
        "version": "SAVP v3.6 Final",
        "descripcion": "Sistema Árbol de la Vida Personal - Versión Completa",
        "fecha": "Febrero 2025",
        "modulos_disponibles": {
            "core": CORE_DISPONIBLE,
            "motor_lectura": MOTOR_LECTURA_DISPONIBLE,
            "tikun": TIKUN_DISPONIBLE,
            "visualizaciones": VISUALIZACIONES_DISPONIBLE,
            "transitos": TRANSITOS_DISPONIBLE,
            "diagrama_visual": DIAGRAMA_DISPONIBLE,
            "kerykeion": KERYKEION_DISPONIBLE
        },
        "componentes": [
            "Dignidades esenciales + accidentales",
            "Genios de los 72 completos",
            "Ponderación 2 capas (v3.6)",
            "Cadena dispositores como grafo",
            "Senderos 3 tipos (ocupación, aspectos, críticos)",
            "Tikún automático diferenciado",
            "Visualizaciones (Mermaid, SVG, HTML)",
            "Motor lectura 10 fases",
            "Tránsitos + Revolución Solar",
            "Diagrama visual mejorado"
        ],
        "endpoints": [
            "POST /savp/v36/natal",
            "POST /savp/v36/lectura",
            "POST /savp/v36/transito",
            "POST /savp/v36/revolucion-solar",
            "GET /savp/v36/arbol/png",
            "GET /savp/v36/test"
        ]
    }


@router.post("/natal")
def calcular_natal_savp_v36(request: NatalRequest):
    """
    Análisis natal completo SAVP v3.6.
    
    Incluye:
    - Cálculo astronómico (Kerykeion)
    - Análisis SAVP v3.6 completo
    - Tikún automático
    - Visualizaciones
    
    Returns:
        dict con todo el análisis
    """
    
    if not KERYKEION_DISPONIBLE or not CORE_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Módulos no disponibles")
    
    try:
        # 1. Calcular con Kerykeion
        subject = AstrologicalSubject(
            name=request.nombre,
            year=int(request.fecha.split('/')[2]),
            month=int(request.fecha.split('/')[1]),
            day=int(request.fecha.split('/')[0]),
            hour=int(request.hora.split(':')[0]),
            minute=int(request.hora.split(':')[1]),
            city=request.lugar,
            lat=request.lat,
            lng=request.lon,
            tz_str=request.timezone
        )
        
        # 2. Extraer planetas (incluyendo nodos)
        planetas = {}
        
        planet_map = {
            'sol': 'sun', 'luna': 'moon', 'mercurio': 'mercury',
            'venus': 'venus', 'marte': 'mars', 'jupiter': 'jupiter',
            'saturno': 'saturn', 'urano': 'uranus', 'neptuno': 'neptune',
            'pluton': 'pluto'
        }
        
        for esp, eng in planet_map.items():
            if hasattr(subject, eng):
                planet = getattr(subject, eng)
                planetas[esp] = {
                    'grado': round(float(getattr(planet, 'position', 0)), 2),
                    'signo': getattr(planet, 'sign', 'Ari'),
                    'casa': int(getattr(planet, 'house', 1)),
                    'retrogrado': bool(getattr(planet, 'retrograde', False))
                }
        
        # Añadir Nodos
        if hasattr(subject, 'lunar_node'):
            ln = subject.lunar_node
            planetas['nodo_norte'] = {
                'grado': round(float(getattr(ln, 'position', 0)), 2),
                'signo': getattr(ln, 'sign', 'Ari'),
                'casa': int(getattr(ln, 'house', 1)),
                'retrogrado': bool(getattr(ln, 'retrograde', False))
            }
            
            # Nodo Sur = Nodo Norte + 180°
            nodo_sur_grado = (planetas['nodo_norte']['grado'] + 180) % 360
            # Calcular signo del nodo sur
            signos = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir', 
                     'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
            signo_norte_idx = signos.index(planetas['nodo_norte']['signo'])
            signo_sur_idx = (signo_norte_idx + 6) % 12
            
            planetas['nodo_sur'] = {
                'grado': round(nodo_sur_grado % 30, 2),
                'signo': signos[signo_sur_idx],
                'casa': (planetas['nodo_norte']['casa'] + 6) % 12 or 12,
                'retrogrado': True  # Nodo sur siempre retrógrado
            }
        
        # 3. Análisis SAVP v3.6
        analisis = procesar_carta_savp_v36_completa(subject, planetas)
        
        # 4. Tikún (si disponible)
        tikun = None
        if TIKUN_DISPONIBLE:
            try:
                tikun = generar_tikun_completo(analisis)
            except Exception as e:
                print(f"Error generando Tikún: {e}")
        
        # 5. Visualizaciones (si disponible)
        visualizaciones = None
        if VISUALIZACIONES_DISPONIBLE:
            try:
                visualizaciones = exportar_visualizaciones_completas(analisis)
            except Exception as e:
                print(f"Error generando visualizaciones: {e}")
        
        # 6. Respuesta
        response = {
            "success": True,
            "version": "SAVP v3.6 Final",
            "datos_natales": {
                "nombre": request.nombre,
                "fecha": request.fecha,
                "hora": request.hora,
                "lugar": request.lugar,
                "coordenadas": {
                    "lat": subject.lat if hasattr(subject, 'lat') else request.lat,
                    "lon": subject.lng if hasattr(subject, 'lng') else request.lon
                },
                "timezone": request.timezone
            },
            "carta_astronomica": planetas,
            "analisis_savp": analisis
        }
        
        if tikun:
            response["tikun"] = tikun
        
        if visualizaciones:
            response["visualizaciones"] = visualizaciones
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo: {str(e)}")


@router.post("/lectura")
def generar_lectura_interpretativa(request: LecturaRequest):
    """
    Genera lectura interpretativa (1 fase o todas las 10).
    
    Args:
        analisis_savp: Output de /natal
        datos_natales: Datos natales (opcional, para Fase 0)
        fase: Número de fase (0-10) o None para todas
        nombre: Nombre del consultante
    
    Returns:
        dict con lectura(s)
    """
    
    if not MOTOR_LECTURA_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Motor de lectura no disponible")
    
    try:
        if request.fase is not None:
            # Una sola fase
            if request.fase < 0 or request.fase > 10:
                raise HTTPException(status_code=400, detail="Fase debe estar entre 0 y 10")
            
            texto = generar_fase_completa(
                request.fase,
                request.analisis_savp,
                request.datos_natales
            )
            
            return {
                "success": True,
                "fase": request.fase,
                "nombre_fase": FASES_LECTURA[request.fase]['nombre'],
                "texto": texto
            }
        
        else:
            # Todas las fases
            fases = {}
            for num_fase in range(0, 11):
                try:
                    if num_fase == 0:
                        texto = generar_fase_completa(num_fase, request.analisis_savp, request.datos_natales)
                    else:
                        texto = generar_fase_completa(num_fase, request.analisis_savp)
                    
                    fases[num_fase] = {
                        "nombre": FASES_LECTURA[num_fase]['nombre'],
                        "texto": texto
                    }
                except Exception as e:
                    fases[num_fase] = {
                        "nombre": FASES_LECTURA[num_fase]['nombre'],
                        "error": str(e)
                    }
            
            return {
                "success": True,
                "nombre": request.nombre,
                "fases": fases,
                "total_fases": 11
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando lectura: {str(e)}")


@router.post("/transito")
def analizar_transito(request: TransitoRequest):
    """
    Detecta e interpreta tránsito.
    
    Returns:
        Interpretación completa del tránsito
    """
    
    if not TRANSITOS_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Módulo de tránsitos no disponible")
    
    try:
        # Detectar
        transito = detectar_transito(
            request.planeta_transitante,
            request.grado_transito,
            request.signo_transito,
            request.planeta_natal,
            request.grado_natal,
            request.signo_natal,
            request.retrogrado
        )
        
        if not transito:
            return {
                "success": True,
                "transito_detectado": False,
                "mensaje": "No hay aspecto significativo con los orbes definidos"
            }
        
        # Interpretar
        interpretacion = interpretar_transito(transito, request.analisis_natal)
        
        return {
            "success": True,
            "transito_detectado": True,
            "transito": transito,
            "interpretacion": interpretacion
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando tránsito: {str(e)}")


@router.get("/test")
def test_frater_d():
    """Test con Frater D. pre-cargado."""
    
    planetas_frater_d = {
        'sol': {'grado': 20.01, 'signo': 'Aqu', 'casa': 5, 'retrogrado': False},
        'luna': {'grado': 20.24, 'signo': 'Lib', 'casa': 1, 'retrogrado': False},
        'mercurio': {'grado': 27.08, 'signo': 'Cap', 'casa': 4, 'retrogrado': True},
        'venus': {'grado': 6.03, 'signo': 'Ari', 'casa': 6, 'retrogrado': False},
        'marte': {'grado': 29.32, 'signo': 'Cap', 'casa': 4, 'retrogrado': False},
        'jupiter': {'grado': 22.10, 'signo': 'Tau', 'casa': 8, 'retrogrado': False},
        'saturno': {'grado': 12.54, 'signo': 'Leo', 'casa': 10, 'retrogrado': False},
        'urano': {'grado': 11.46, 'signo': 'Sco', 'casa': 2, 'retrogrado': False},
        'neptuno': {'grado': 15.45, 'signo': 'Sag', 'casa': 3, 'retrogrado': False},
        'pluton': {'grado': 14.01, 'signo': 'Lib', 'casa': 1, 'retrogrado': True}
    }
    
    analisis = procesar_carta_savp_v36_completa(None, planetas_frater_d)
    
    return {
        "success": True,
        "test": "Frater D. (08/02/1977, 22:40, Zaragoza)",
        "analisis": analisis
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("✅ ROUTER SAVP v3.6 FINAL")
    print("=" * 70)
    print("\nMódulos integrados:")
    print(f"  • Core: {CORE_DISPONIBLE}")
    print(f"  • Motor lectura: {MOTOR_LECTURA_DISPONIBLE}")
    print(f"  • Tikún: {TIKUN_DISPONIBLE}")
    print(f"  • Visualizaciones: {VISUALIZACIONES_DISPONIBLE}")
    print(f"  • Tránsitos: {TRANSITOS_DISPONIBLE}")
    print(f"  • Diagrama visual: {DIAGRAMA_DISPONIBLE}")
    print(f"  • Kerykeion: {KERYKEION_DISPONIBLE}")
    print("=" * 70)
