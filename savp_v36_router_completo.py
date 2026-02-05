# ============================================================================
# SAVP v3.6 — ROUTER NATAL CON PERSISTENCIA MÍNIMA
# TODO EN ROOT
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import traceback

from kerykeion import AstrologicalSubject

from savp_v36_core_completo import procesar_carta_savp_v36_completa
from tikun_automatico import generar_tikun_completo
from visualizaciones import exportar_visualizaciones_completas

# ============================================================================
# PERSISTENCIA MÍNIMA (MEMORIA DE PROCESO)
# ============================================================================

LAST_ANALISIS_SAVP = None

# ============================================================================
# FIX CASAS KERYKEION
# ============================================================================

HOUSE_MAP = {
    "First_House": 1, "Second_House": 2, "Third_House": 3,
    "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
    "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
    "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12,
}

def normalizar_casa(raw):
    if isinstance(raw, str):
        return HOUSE_MAP.get(raw, 1)
    try:
        return int(raw)
    except Exception:
        return 1

# ============================================================================
# MODELO REQUEST
# ============================================================================

class NatalRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    lugar: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: str = "Europe/Madrid"

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Natal"])

# ============================================================================
# ENDPOINT NATAL
# ============================================================================

@router.post("/natal")
def calcular_natal(request: NatalRequest):

    global LAST_ANALISIS_SAVP

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
            "sol": "sun", "luna": "moon", "mercurio": "mercury",
            "venus": "venus", "marte": "mars", "jupiter": "jupiter",
            "saturno": "saturn", "urano": "uranus",
            "neptuno": "neptune", "pluton": "pluto",
        }

        for esp, eng in planet_map.items():
            p = getattr(subject, eng)
            planetas[esp] = {
                "grado": round(float(p.position), 2),
                "signo": p.sign,
                "casa": normalizar_casa(p.house),
                "retrogrado": bool(p.retrograde),
            }

        analisis = procesar_carta_savp_v36_completa(subject, planetas)

        # 🔒 Guardar análisis para futuras lecturas
        LAST_ANALISIS_SAVP = analisis

        tikun = generar_tikun_completo(analisis)
        visualizaciones = exportar_visualizaciones_completas(analisis)

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
