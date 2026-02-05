# ============================================================================
# SAVP v3.6 FINAL — ROUTER COMPLETO (FIX KERYKEION CASAS)
# ============================================================================

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
import sys
import traceback

# ============================================================================
# KERYKEION
# ============================================================================

try:
    from kerykeion import AstrologicalSubject
    KERYKEION_DISPONIBLE = True
except ImportError:
    KERYKEION_DISPONIBLE = False
    print("⚠️  Kerykeion no disponible", file=sys.stderr)

# ============================================================================
# IMPORTAR MÓDULOS SAVP v3.6
# ============================================================================

try:
    from savp_v36_core_completo import procesar_carta_savp_v36_completa
    CORE_DISPONIBLE = True
except ImportError:
    CORE_DISPONIBLE = False
    print("❌ savp_v36_core_completo.py no disponible", file=sys.stderr)

try:
    from motor_lectura_v36 import generar_fase_completa
    MOTOR_LECTURA_DISPONIBLE = True
except ImportError:
    MOTOR_LECTURA_DISPONIBLE = False
    print("⚠️  motor_lectura_v36.py no disponible", file=sys.stderr)

try:
    from tikun_automatico import generar_tikun_completo
    TIKUN_DISPONIBLE = True
except ImportError:
    TIKUN_DISPONIBLE = False
    print("⚠️  tikun_automatico.py no disponible", file=sys.stderr)

try:
    from visualizaciones import exportar_visualizaciones_completas
    VISUALIZACIONES_DISPONIBLE = True
except ImportError:
    VISUALIZACIONES_DISPONIBLE = False
    print("⚠️  visualizaciones.py no disponible", file=sys.stderr)

try:
    from transitos_v36 import detectar_transito, interpretar_transito
    TRANSITOS_DISPONIBLE = True
except ImportError:
    TRANSITOS_DISPONIBLE = False
    print("⚠️  transitos_v36.py no disponible", file=sys.stderr)

try:
    from generar_arbol_v36 import generar_arbol_desde_analisis
    import matplotlib
    matplotlib.use("Agg")
    DIAGRAMA_DISPONIBLE = True
except ImportError:
    DIAGRAMA_DISPONIBLE = False
    print("⚠️  generar_arbol_v36.py no disponible", file=sys.stderr)

# ============================================================================
# FIX KERYKEION ≥5.7 — CASAS SIMBÓLICAS
# ============================================================================

HOUSE_MAP = {
    "First_House": 1,
    "Second_House": 2,
    "Third_House": 3,
    "Fourth_House": 4,
    "Fifth_House": 5,
    "Sixth_House": 6,
    "Seventh_House": 7,
    "Eighth_House": 8,
    "Ninth_House": 9,
    "Tenth_House": 10,
    "Eleventh_House": 11,
    "Twelfth_House": 12,
}

def normalizar_casa(raw_house) -> int:
    if isinstance(raw_house, str):
        return HOUSE_MAP.get(raw_house, 1)
    try:
        return int(raw_house)
    except Exception:
        return 1

# ============================================================================
# MODELOS
# ============================================================================

class NatalRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    lugar: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: str = "Europe/Madrid"

class LecturaRequest(BaseModel):
    analisis_savp: dict
    datos_natales: Optional[dict] = None
    fase: Optional[int] = None
    nombre: str = "Consultante"

class TransitoRequest(BaseModel):
    planeta_transitante: str
    grado_transito: float
    signo_transito: str
    planeta_natal: str
    grado_natal: float
    signo_natal: str
    retrogrado: bool = False
    analisis_natal: dict

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Final"])

# ============================================================================
# INFO
# ============================================================================

@router.get("/")
def info():
    return {
        "version": "SAVP v3.6 Final",
        "kerykeion": KERYKEION_DISPONIBLE,
        "core": CORE_DISPONIBLE,
        "motor_lectura": MOTOR_LECTURA_DISPONIBLE,
        "tikun": TIKUN_DISPONIBLE,
        "visualizaciones": VISUALIZACIONES_DISPONIBLE,
        "transitos": TRANSITOS_DISPONIBLE,
        "diagrama": DIAGRAMA_DISPONIBLE,
    }

# ============================================================================
# NATAL
# ============================================================================

@router.post("/natal")
def natal(request: NatalRequest):

    if not KERYKEION_DISPONIBLE or not CORE_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Módulos no disponibles")

    try:
        subject = AstrologicalSubject(
            name=request.nombre,
            year=int(request.fecha.split("/")[2]),
            month=int(request.fecha.split("/")[1]),
            day=int(request.fecha.split("/")[0]),
            hour=int(request.hora.split(":")[0]),
            minute=int(request.hora.split(":")[1]),
            city=request.lugar,
            lat=request.lat,
            lng=request.lon,
            tz_str=request.timezone,
        )

        planetas = {}
        planet_map = {
            "sol": "sun",
            "luna": "moon",
            "mercurio": "mercury",
            "venus": "venus",
            "marte": "mars",
            "jupiter": "jupiter",
            "saturno": "saturn",
            "urano": "uranus",
            "neptuno": "neptune",
            "pluton": "pluto",
        }

        for esp, eng in planet_map.items():
            if hasattr(subject, eng):
                p = getattr(subject, eng)
                planetas[esp] = {
                    "grado": round(float(getattr(p, "position", 0)), 2),
                    "signo": getattr(p, "sign", "Ari"),
                    "casa": normalizar_casa(getattr(p, "house", 1)),
                    "retrogrado": bool(getattr(p, "retrograde", False)),
                }

        if hasattr(subject, "lunar_node"):
            ln = subject.lunar_node
            casa_nn = normalizar_casa(getattr(ln, "house", 1))

            planetas["nodo_norte"] = {
                "grado": round(float(getattr(ln, "position", 0)), 2),
                "signo": getattr(ln, "sign", "Ari"),
                "casa": casa_nn,
                "retrogrado": bool(getattr(ln, "retrograde", False)),
            }

            planetas["nodo_sur"] = {
                "grado": (planetas["nodo_norte"]["grado"] + 180) % 30,
                "signo": planetas["nodo_norte"]["signo"],
                "casa": ((casa_nn + 6 - 1) % 12) + 1,
                "retrogrado": True,
            }

        analisis = procesar_carta_savp_v36_completa(subject, planetas)

        tikun = generar_tikun_completo(analisis) if TIKUN_DISPONIBLE else None
        visualizaciones = (
            exportar_visualizaciones_completas(analisis)
            if VISUALIZACIONES_DISPONIBLE
            else None
        )

        return {
            "datos_natales": request.dict(),
            "carta_astronomica": planetas,
            "analisis_savp": analisis,
            "tikun": tikun,
            "visualizaciones": visualizaciones,
        }

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
