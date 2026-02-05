# ============================================================================
# SAVP v3.6 FINAL — ROUTER COMPLETO (ROOT + NODO MEDIO)
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
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
# IMPORTS SAVP (ROOT)
# ============================================================================

try:
    from savp_v36_core_completo import procesar_carta_savp_v36_completa
    CORE_DISPONIBLE = True
except ImportError:
    CORE_DISPONIBLE = False
    print("❌ savp_v36_core_completo no disponible", file=sys.stderr)

try:
    from tikun_automatico import generar_tikun_completo
    TIKUN_DISPONIBLE = True
except ImportError:
    TIKUN_DISPONIBLE = False

try:
    from visualizaciones import exportar_visualizaciones_completas
    VISUALIZACIONES_DISPONIBLE = True
except ImportError:
    VISUALIZACIONES_DISPONIBLE = False

# ============================================================================
# FIX CASAS KERYKEION ≥5.7
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

def normalizar_casa(raw):
    if isinstance(raw, str):
        return HOUSE_MAP.get(raw, 1)
    try:
        return int(raw)
    except Exception:
        return 1

# ============================================================================
# MODELOS
# ============================================================================

class NatalRequest(BaseModel):
    nombre: str
    fecha: str = Field(..., description="DD/MM/YYYY")
    hora: str = Field(..., description="HH:MM")
    lugar: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: str = "Europe/Madrid"

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Final"])

# ============================================================================
# ENDPOINT NATAL
# ============================================================================

@router.post("/natal")
def calcular_natal(request: NatalRequest):

    if not KERYKEION_DISPONIBLE or not CORE_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Módulos no disponibles")

    try:
        # ------------------------------------------------------------------
        # CREACIÓN DEL SUBJECT
        # ------------------------------------------------------------------

        subject_kwargs = dict(
            name=request.nombre,
            year=int(request.fecha.split("/")[2]),
            month=int(request.fecha.split("/")[1]),
            day=int(request.fecha.split("/")[0]),
            hour=int(request.hora.split(":")[0]),
            minute=int(request.hora.split(":")[1]),
            tz_str=request.timezone,
        )

        if request.lat is not None and request.lon is not None:
            subject_kwargs["lat"] = request.lat
            subject_kwargs["lng"] = request.lon
            subject_kwargs["city"] = request.lugar
        else:
            subject_kwargs["city"] = request.lugar

        subject = AstrologicalSubject(**subject_kwargs)

        # ------------------------------------------------------------------
        # PLANETAS
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # NODO NORTE MEDIO (FORZADO)
        # ------------------------------------------------------------------

        if not hasattr(subject, "mean_lunar_node"):
            raise ValueError("Nodo Norte Medio no disponible en Kerykeion")

        ln = subject.mean_lunar_node
        casa_nn = normalizar_casa(getattr(ln, "house", 1))

        planetas["nodo_norte"] = {
            "grado": round(float(getattr(ln, "position", 0)), 4),
            "signo": getattr(ln, "sign", "Ari"),
            "casa": casa_nn,
            "retrogrado": False,
            "tipo": "mean"
        }

        planetas["nodo_sur"] = {
            "grado": (planetas["nodo_norte"]["grado"] + 180) % 30,
            "signo": planetas["nodo_norte"]["signo"],
            "casa": ((casa_nn + 6 - 1) % 12) + 1,
            "retrogrado": True,
            "tipo": "mean"
        }

        # ------------------------------------------------------------------
        # ANÁLISIS SAVP
        # ------------------------------------------------------------------

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
        raise HTTPException(
            status_code=500,
            detail=f"Error en cálculo natal: {str(e)}"
        )
