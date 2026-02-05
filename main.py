# ============================================================================
# MAIN FASTAPI — SAVP v3.6 DEFINITIVO
# TODO EN ROOT — SIN AMBIGÜEDADES
# ============================================================================

from fastapi import FastAPI

# ------------------ IMPORTS ROUTERS ------------------

from savp_v36_router_completo import router as savp_router
from motor_lectura_v36 import router as lectura_router

# ------------------ APP ------------------

app = FastAPI(
    title="SAVP v3.6",
    description="Systema Arbor Vitae Personalis",
    version="3.6"
)

# ------------------ ROUTERS ------------------

# Carta natal + cálculo
app.include_router(savp_router)

# Lecturas por fases (FASE 1–10)
app.include_router(lectura_router)

# ------------------ ROOT CHECK ------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "system": "SAVP v3.6",
        "routers": [
            "/savp/v36/natal",
            "/savp/v36/lectura"
        ]
    }
