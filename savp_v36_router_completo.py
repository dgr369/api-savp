# ============================================================================
# SAVP v3.6 FINAL — ROUTER COMPLETO (ROOT)
# Nodo Norte y Sur MEDIOS calculados internamente (Meeus)
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import sys
import traceback
from datetime import datetime, timezone

# ============================================================================
# KERYKEION (solo planetas)
# ============================================================================

from kerykeion import AstrologicalSubject

# ============================================================================
# IMPORTS SAVP (ROOT)
# ============================================================================

from savp_v36_core_completo import procesar_carta_savp_v36_completa
from tikun_automatico import generar_tikun_completo
from visualizaciones import exportar_visualizaciones_completas

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
# CÁLCULO NODO NORTE MEDIO (Meeus)
# ============================================================================

SIGNOS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
          "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]

def calcular_nodos_medios(dt_utc: datetime):
    # Julian Day
    a = (14 - dt_utc.month) // 12
    y = dt_utc.year + 4800 - a
    m = dt_utc.month + 12 * a - 3

    jd = (
        dt_utc.day
        + ((153 * m + 2) // 5)
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )

    jd += (dt_utc.hour + dt_utc.minute / 60) / 24
    T = (jd - 2451545.0) / 36525.0

    # Longitud Nodo Norte Medio
    omega = (
        125.04452
        - 1934.136261 * T
        + 0.0020708 * T**2
        + (T**3) / 450000
    ) % 360

    # Nodo Sur = oposición exacta
    omega_sur = (omega + 180) % 360

    def descomponer(longitud):
        signo_index = int(longitud // 30)
        grado = longitud % 30
        return SIGNOS[signo_index], round(grado, 4)

    signo_n, grado_n = descomponer(omega)
    signo_s, grado_s = descomponer(omega_sur)

    return {
        "norte": {"signo": signo_n, "grado": grado_n},
        "sur": {"signo": signo_s, "grado": grado_s},
    }

# ============================================================================
# MODELO REQUEST
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

        # ------------------ PLANETAS ------------------

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

        # ------------------ NODOS MEDIOS ------------------

        dt_utc = datetime(
            year=int(request.fecha.split("/")[2]),
            month=int(request.fecha.split("/")[1]),
            day=int(request.fecha.split("/")[0]),
            hour=int(request.hora.split(":")[0]),
            minute=int(request.hora.split(":")[1]),
            tzinfo=timezone.utc,
        )

        nodos = calcular_nodos_medios(dt_utc)

        planetas["nodo_norte"] = {
            "signo": nodos["norte"]["signo"],
            "grado": nodos["norte"]["grado"],
            "casa": 1,
            "retrogrado": False,
            "tipo": "mean",
        }

        planetas["nodo_sur"] = {
            "signo": nodos["sur"]["signo"],
            "grado": nodos["sur"]["grado"],
            "casa": 7,
            "retrogrado": True,
            "tipo": "mean",
        }

        # ------------------ SAVP ------------------

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
