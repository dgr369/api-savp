# ============================================================================
# MAIN FASTAPI — SAVP v3.6 UNIFICADO
# TODO EN UN SOLO ARCHIVO
# ============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import traceback
import sys

# ============================================================================
# DEPENDENCIAS SAVP
# ============================================================================

from kerykeion import AstrologicalSubject

from savp_v36_core_completo import procesar_carta_savp_v36_completa
from tikun_automatico import generar_tikun_completo
from visualizaciones import exportar_visualizaciones_completas

# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title="SAVP v3.6",
    description="Systema Arbor Vitae Personalis",
    version="3.6"
)

# ============================================================================
# ESTADO GLOBAL (PERSISTENCIA LIMPIA)
# ============================================================================

LAST_ANALISIS_SAVP: Optional[Dict] = None

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
# MODELOS
# ============================================================================

class NatalRequest(BaseModel):
    nombre: str
    fecha: str          # DD/MM/YYYY
    hora: str           # HH:MM
    lugar: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: str = "Europe/Madrid"

class LecturaRequest(BaseModel):
    analisis_savp: Optional[Dict] = None
    fase: Optional[int] = None
    nombre: str = "Consultante"

# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "system": "SAVP v3.6",
        "endpoints": [
            "/savp/v36/natal",
            "/savp/v36/lectura"
        ]
    }

# ============================================================================
# ENDPOINT /natal
# ============================================================================
@app.post("/savp/v36/natal")
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

        # Persistencia limpia
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

# ============================================================================
# MOTOR DE LECTURA
# ============================================================================

def generar_fase_completa(analisis_savp: Dict, fase: Optional[int]) -> str:
    fases = analisis_savp.get("fases")
    if not fases:
        raise ValueError("El análisis no contiene fases")

    if fase is None:
        return "\n\n".join(
            fases[str(f)] for f in sorted(map(int, fases.keys()))
        )

    fase_str = str(fase)
    if fase_str not in fases:
        raise ValueError(f"Fase {fase} no disponible")

    return fases[fase_str]

# ============================================================================
# ENDPOINT /lectura
# ============================================================================
@app.post("/savp/v36/lectura")
def lectura(request: LecturaRequest):

    try:
        analisis = request.analisis_savp or LAST_ANALISIS_SAVP

        if analisis is None:
            raise ValueError("No hay analisis_savp disponible. Ejecuta /natal primero.")

        texto = generar_fase_completa(
            analisis_savp=analisis,
            fase=request.fase
        )

        return {
            "nombre": request.nombre,
            "fase": request.fase,
            "texto": texto
        }

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
