# ============================================================================
# MOTOR DE LECTURA SAVP v3.6
# Endpoint STATELESS conforme al contrato oficial SAVP
# TODO EN ROOT
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import traceback
import sys

# ============================================================================
# ROUTER FASTAPI
# ============================================================================

router = APIRouter(
    prefix="/savp/v36",
    tags=["SAVP v3.6 Lectura"]
)

# ============================================================================
# MODELO DE REQUEST (CONTRATO SAVP v3.6)
# ============================================================================

class LecturaRequest(BaseModel):
    analisis_savp: Dict
    fase: Optional[int] = None
    nombre: str = "Consultante"

# ============================================================================
# FUNCIÓN CENTRAL DE LECTURA
# NO usa estado, NO usa cache, NO asume nada previo
# ============================================================================

def generar_fase_completa(
    analisis_savp: Dict,
    fase: Optional[int] = None,
    nombre: str = "Consultante"
) -> str:
    """
    Genera el texto completo de una fase SAVP v3.6.
    """

    fases = analisis_savp.get("fases")

    if not fases:
        raise ValueError("analisis_savp no contiene el bloque 'fases'")

    # Todas las fases
    if fase is None:
        return "\n\n".join(
            fases[str(f)] for f in sorted(map(int, fases.keys()))
        )

    fase_str = str(fase)

    if fase_str not in fases:
        raise ValueError(f"Fase {fase} no disponible en analisis_savp")

    return fases[fase_str]

# ============================================================================
# ENDPOINT OFICIAL /savp/v36/lectura
# CUMPLE EL CONTRATO DEFINIDO EN TUS INSTRUCCIONES
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
        raise HTTPException(
            status_code=500,
            detail=f"Error en lectura SAVP: {str(e)}"
        )
