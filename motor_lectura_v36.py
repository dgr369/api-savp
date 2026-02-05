# ============================================================================
# MOTOR DE LECTURA SAVP v3.6 — CON PERSISTENCIA
# TODO EN ROOT
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
import sys
import traceback

# Importar análisis persistido
from savp_v36_router_completo import LAST_ANALISIS_SAVP

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Lectura"])

# ============================================================================
# MODELO REQUEST (CON ALIAS)
# ============================================================================

class LecturaRequest(BaseModel):
    analisis_savp: Optional[Dict] = Field(None, alias="analisis")
    fase: Optional[int] = None
    nombre: str = "Consultante"

    class Config:
        allow_population_by_field_name = True

# ============================================================================
# MOTOR DE LECTURA
# ============================================================================

def generar_fase_completa(
    analisis_savp: Dict,
    fase: Optional[int] = None,
    nombre: str = "Consultante"
) -> str:

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

@router.post("/lectura")
def lectura_endpoint(request: LecturaRequest):

    try:
        analisis = request.analisis_savp or LAST_ANALISIS_SAVP

        if analisis is None:
            raise ValueError("No hay analisis_savp disponible")

        texto = generar_fase_completa(
            analisis_savp=analisis,
            fase=request.fase,
            nombre=request.nombre
        )

        return {
            "nombre": request.nombre,
            "fase": request.fase,
            "texto": texto
        }

    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
