"""
main.py
API Astrológica SAVP v3.6 Final

Integración completa de todos los módulos v3.6

Fecha: Febrero 2025
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================================
# IMPORTAR ROUTER SAVP v3.6 FINAL
# ============================================================================

try:
    from savp_v36_router_completo import router as savp_v36_router
    SAVP_V36_ENABLED = True
    print("✅ SAVP v3.6 Final router cargado")
except ImportError as e:
    SAVP_V36_ENABLED = False
    print(f"⚠️  SAVP v3.6 no disponible: {e}")

# ============================================================================
# APP
# ============================================================================

app = FastAPI(
    title=f"API SAVP {'v3.6 Final' if SAVP_V36_ENABLED else 'v3.5'}",
    description="Sistema Árbol de la Vida Personal - API Completa",
    version="3.6.0" if SAVP_V36_ENABLED else "3.5.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INCLUIR ROUTERS
# ============================================================================

if SAVP_V36_ENABLED:
    app.include_router(savp_v36_router)

# ============================================================================
# ENDPOINTS PRINCIPALES
# ============================================================================

@app.get("/")
def root():
    """Información de la API."""
    return {
        "api": "SAVP API",
        "version": "3.6 Final" if SAVP_V36_ENABLED else "3.5",
        "status": "operational",
        "endpoints": {
            "savp_info": "/savp/v36/",
            "natal": "/savp/v36/natal",
            "lectura": "/savp/v36/lectura",
            "transito": "/savp/v36/transito",
            "test": "/savp/v36/test"
        } if SAVP_V36_ENABLED else {}
    }

@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy", "version": "3.6"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
