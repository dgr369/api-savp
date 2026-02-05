# ============================================================================
# MOTOR DE LECTURA SAVP v3.6 — ROBUSTO Y COMPATIBLE
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
import traceback
import sys

router = APIRouter(prefix="/savp/v36", tags=["SAVP v3.6 Lectura"])

# ============================================================================
# MODELO DE REQUEST (CON ALIAS DEFENSIVOS)
# ============================================================================

class LecturaRequest(BaseModel):
    analisis_savp: Dict = Field(
        ...,
        alias="analisis",
        description="Análisis SAVP completo"
    )
    fase: Optional[int] = None
    nombre: str = "Consultante"

    class Config:
        allow_population_by_field_name = True

# ============================================================================
# MOTOR
# ============================================================================

def generar_fase_completa(
    analisis_savp: Dict,
    fase: Optional[int] = None,
    nombre: str = "Consultante"
) -> str:

    fases = analisis_savp.get("fases")

    if not fases:
        raise ValueError("analisis_savp no contiene el bloque 'fases'")

    if fase is None:
        return "\n\n".join(
            fases[str(f)] for f in sorted(map(int, fases.keys()))
        )

    fase_str = str(fase)
    if fase_str not in fases:
        raise ValueError(f"Fase {fase} no disponible")

    return fases[fase_str]

# ============================================================================
# ENDPOINT
# ============================================================================

@router.post("/lectura")
def lectura_endpoint(request: LecturaRequest):
    try:
        texto = generar_fase_completa(
            analisis_savp=request.analisis_savp,
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
