# ============================================================================
# MOTOR DE LECTURA SAVP v3.6
# Expuesto como FUNCIÓN INTERNA + ENDPOINT FASTAPI
# TODO EN ROOT
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import sys
import traceback

# ============================================================================
# ROUTER FASTAPI
# ============================================================================

router = APIRouter(
    prefix="/savp/v36",
    tags=["SAVP v3.6 Lecturas"]
)

# ============================================================================
# MODELO REQUEST
# ============================================================================

class LecturaRequest(BaseModel):
    analisis_savp: Dict
    datos_natales: Optional[Dict] = None
    fase: Optional[int] = None
    nombre: str = "Consultante"

# ============================================================================
# FUNCIÓN CENTRAL DE LECTURA (NO TOCAR)
# ============================================================================

def generar_fase_completa(
    analisis_savp: Dict,
    fase: Optional[int] = None,
    nombre: str = "Consultante"
) -> str:
    """
    Genera el texto completo de una fase SAVP v3.6.
    Si fase es None, genera todas.
    """

    try:
        fases = analisis_savp.get("fases", {})

        if not fases:
            raise ValueError("analisis_savp no contiene fases")

        if fase is None:
            return "\n\n".join(
                fases[str(f)] for f in sorted(map(int, fases.keys()))
            )

        fase_str = str(fase)
        if fase_str not in fases:
            raise ValueError(f"Fase {fase} no disponible en analisis_savp")

        return fases[fase_str]

    except Exception as e:
        raise RuntimeError(f"Error en motor de lectura: {str(e)}")

# ============================================================================
# ENDPOINT FASTAPI (ENVOLTORIO ESTABLE)
# ============================================================================

@router.post("/lectura")
def lectura_endpoint(request: LecturaRequest):
    """
    Endpoint oficial para generar lecturas por fase.
    RUTA: POST /savp/v36/lectura
    """

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
