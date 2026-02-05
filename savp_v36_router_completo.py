# ============================================================================
# SAVP v3.6 FINAL — ROUTER COMPLETO (ROOT + NODO NORTE MEDIO INTERNO)
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import math
import sys
import traceback
from datetime import datetime, timezone

# ============================================================================
# KERYKEION (solo planetas)
# ============================================================================

try:
    from kerykeion import AstrologicalSubject
    KERYKEION_DISPONIBLE = True
except ImportError:
    KERYKEION_DISPONIBLE = False
    print("⚠️ Kerykeion no disponible", file=sys.stderr)

# ============================================================================
# IMPORTS SAVP (ROOT)
# ============================================================================

from savp_v36_core_completo import procesar_carta_savp_v36_completa
from tikun_automatico import generar_tikun_completo
from visualizaciones import exportar_visualizaciones_completas

# ============================================================================
# FIX CASAS KERYKEION ≥5.7
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
# CÁLCULO NODO NORTE MEDIO (INDEPENDIENTE)
# Meeus simplificado – suficiente para astrología natal
# ============================================================================

def calcular_nodo_norte_medio(dt_utc: datetime):
    # Julian Day
    a = (14 - dt_utc.month) // 12
    y = dt_utc.year + 4800 - a
    m = dt_utc.month + 12 * a - 3
    jd = dt_utc.day + ((153 * m + 2) // 5) + 365 * y
    jd += y // 4 - y // 100 + y // 400 - 32045
    jd += (dt_utc.hour - 12) / 24 + dt_utc.minute / 1440

    T = (jd - 2451545.0) / 36525.0

    # Longitud media del Nodo Norte (Meeus)
    omega = (
        125.04452
        - 1934.136261 * T
        + 0.0020708 * T**2
        + T**3 / 450000
    )

    omega = omega % 360
    signo_index = int(omega // 30)
    grado = omega % 30

    signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
              "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

    return {
        "grado": round(grado, 4),
        "signo": signos[signo_index],
        "longitud": round(omega, 6)
    }

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

    if not KERYKEION_DISPONIBLE:
        raise HTTPException(status_code=503, detail="Kerykeion no disponible")

    try:
        # ------------------------------------------------------------------
        # SUBJECT
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # PLANETAS
        # ------------------------------------------------------------------

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

        # ------------------------------------------------------------------
        # NODO NORTE MEDIO (INTERNO)
        # ------------------------------------------------------------------

        dt_local = datetime(
            year=int(request.fecha.split("/")[2]),
            month=int(request.fecha.split("/")[1]),
            day=int(request.fecha.split("/")[0]),
            hour=int(request.hora.split(":")[0]),
            minute=int(request.hora.split(":")[1]),
            tzinfo=timezone.utc
        )

        nodo = calcular_nodo_norte_medio(dt_local)

        planetas["nodo_norte"] = {
            "grado": nodo["grado"],
            "signo": nodo["signo"],
            "casa": 1,   # casa se proyecta después si quieres refinar
            "retrogrado": False,
            "tipo": "mean"
        }

        planetas["nodo_sur"] = {
            "grado": (nodo["grado"] + 180) % 30,
            "signo": nodo["signo"],
            "casa": 7,
            "retrogrado": True,
            "tipo": "mean"
        }

        # ------------------------------------------------------------------
        # SAVP
        # ------------------------------------------------------------------

        analisis = procesar_carta_savp_v36_completa(subject, planetas)
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
