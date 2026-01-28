"""
API Astrológica para SAVP v3.5
Cálculos de carta natal, tránsitos y revolución solar
Usando Kerykeion (Swiss Ephemeris)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from kerykeion import AstrologicalSubject, Report
from typing import Optional
import pytz

app = FastAPI(
    title="API Astrológica SAVP v3.5",
    description="Cálculos astrológicos para el Sistema Árbol de la Vida Personal",
    version="1.0.0"
)

# CORS para permitir llamadas desde GPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MODELOS DE DATOS

class NatalRequest(BaseModel):
    nombre: str
    fecha: str  # Formato: "YYYY-MM-DD"
    hora: str   # Formato: "HH:MM"
    ciudad: str
    pais: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = "Europe/Madrid"


class TransitsRequest(BaseModel):
    # Datos natales
    nombre: str
    fecha_natal: str
    hora_natal: str
    ciudad_natal: str
    pais_natal: str
    lat_natal: Optional[float] = None
    lon_natal: Optional[float] = None
    timezone_natal: Optional[str] = "Europe/Madrid"
    # Fecha de tránsitos
    fecha_transito: Optional[str] = None  # Si no se pasa, usa hoy


class SolarReturnRequest(BaseModel):
    nombre: str
    fecha_natal: str
    hora_natal: str
    ciudad_natal: str
    pais_natal: str
    lat_natal: Optional[float] = None
    lon_natal: Optional[float] = None
    timezone_natal: Optional[str] = "Europe/Madrid"
    año_revolucion: int  # Año para la revolución solar


# FUNCIONES AUXILIARES

def geocode_ciudad(ciudad: str, pais: str):
    """
    Geocodifica ciudad. Si no se pasa lat/lon, usa coordenadas aproximadas.
    Para producción, integrar con API de geocoding (Google, OpenCage, etc.)
    """
    # Diccionario básico de ciudades españolas
    ciudades = {
        "madrid": (40.4168, -3.7038),
        "barcelona": (41.3851, 2.1734),
        "zaragoza": (41.6488, -0.8891),
        "valencia": (39.4699, -0.3763),
        "sevilla": (37.3886, -5.9823),
        "malaga": (36.7213, -4.4214),
        "bilbao": (43.2630, -2.9350),
    }
    
    ciudad_lower = ciudad.lower()
    if ciudad_lower in ciudades:
        return ciudades[ciudad_lower]
    
    # Default: Madrid
    return (40.4168, -3.7038)


def formatear_posiciones(subject: AstrologicalSubject):
    """
    Extrae y formatea posiciones planetarias
    """
    planetas = {}
    
    # Sol
    planetas["sol"] = {
        "grado": round(subject.sun.position, 2),
        "signo": subject.sun.sign,
        "casa": subject.sun.house,
        "retrogrado": subject.sun.retrograde
    }
    
    # Luna
    planetas["luna"] = {
        "grado": round(subject.moon.position, 2),
        "signo": subject.moon.sign,
        "casa": subject.moon.house,
        "retrogrado": subject.moon.retrograde
    }
    
    # Mercurio
    planetas["mercurio"] = {
        "grado": round(subject.mercury.position, 2),
        "signo": subject.mercury.sign,
        "casa": subject.mercury.house,
        "retrogrado": subject.mercury.retrograde
    }
    
    # Venus
    planetas["venus"] = {
        "grado": round(subject.venus.position, 2),
        "signo": subject.venus.sign,
        "casa": subject.venus.house,
        "retrogrado": subject.venus.retrograde
    }
    
    # Marte
    planetas["marte"] = {
        "grado": round(subject.mars.position, 2),
        "signo": subject.mars.sign,
        "casa": subject.mars.house,
        "retrogrado": subject.mars.retrograde
    }
    
    # Júpiter
    planetas["jupiter"] = {
        "grado": round(subject.jupiter.position, 2),
        "signo": subject.jupiter.sign,
        "casa": subject.jupiter.house,
        "retrogrado": subject.jupiter.retrograde
    }
    
    # Saturno
    planetas["saturno"] = {
        "grado": round(subject.saturn.position, 2),
        "signo": subject.saturn.sign,
        "casa": subject.saturn.house,
        "retrogrado": subject.saturn.retrograde
    }
    
    # Urano
    planetas["urano"] = {
        "grado": round(subject.uranus.position, 2),
        "signo": subject.uranus.sign,
        "casa": subject.uranus.house,
        "retrogrado": subject.uranus.retrograde
    }
    
    # Neptuno
    planetas["neptuno"] = {
        "grado": round(subject.neptune.position, 2),
        "signo": subject.neptune.sign,
        "casa": subject.neptune.house,
        "retrogrado": subject.neptune.retrograde
    }
    
    # Plutón
    planetas["pluton"] = {
        "grado": round(subject.pluto.position, 2),
        "signo": subject.pluto.sign,
        "casa": subject.pluto.house,
        "retrogrado": subject.pluto.retrograde
    }
    
    # Puntos especiales
    puntos = {
        "asc": {
            "grado": round(subject.first_house.position, 2),
            "signo": subject.first_house.sign
        },
        "mc": {
            "grado": round(subject.tenth_house.position, 2),
            "signo": subject.tenth_house.sign
        },
        "nodo_norte": {
            "grado": round(subject.mean_node.position, 2),
            "signo": subject.mean_node.sign,
            "casa": subject.mean_node.house
        }
    }
    
    return {
        "planetas": planetas,
        "puntos": puntos
    }


# ENDPOINTS

@app.get("/")
def root():
    """Endpoint de prueba"""
    return {
        "api": "API Astrológica SAVP v3.5",
        "version": "1.0.0",
        "endpoints": [
            "/natal - Carta natal completa",
            "/transits - Tránsitos actuales sobre natal",
            "/solar_return - Revolución solar",
            "/docs - Documentación Swagger"
        ]
    }


@app.post("/natal")
def calcular_natal(request: NatalRequest):
    """
    Calcula carta natal completa
    """
    try:
        # Geocodificar si no hay coordenadas
        if request.lat is None or request.lon is None:
            lat, lon = geocode_ciudad(request.ciudad, request.pais)
        else:
            lat, lon = request.lat, request.lon
        
        # Parsear fecha y hora
        fecha_dt = datetime.strptime(request.fecha, "%Y-%m-%d")
        hora_parts = request.hora.split(":")
        
        # Crear sujeto astrológico
        subject = AstrologicalSubject(
            name=request.nombre,
            year=fecha_dt.year,
            month=fecha_dt.month,
            day=fecha_dt.day,
            hour=int(hora_parts[0]),
            minute=int(hora_parts[1]),
            city=request.ciudad,
            nation=request.pais,
            lat=lat,
            lng=lon,
            tz_str=request.timezone
        )
        
        # Formatear respuesta
        posiciones = formatear_posiciones(subject)
        
        return {
            "success": True,
            "datos": {
                "nombre": request.nombre,
                "fecha": request.fecha,
                "hora": request.hora,
                "ciudad": request.ciudad,
                "coordenadas": {"lat": lat, "lon": lon}
            },
            "carta": posiciones
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular natal: {str(e)}")


@app.post("/transits")
def calcular_transitos(request: TransitsRequest):
    """
    Calcula tránsitos actuales sobre carta natal
    """
    try:
        # Carta natal
        if request.lat_natal is None or request.lon_natal is None:
            lat_natal, lon_natal = geocode_ciudad(request.ciudad_natal, request.pais_natal)
        else:
            lat_natal, lon_natal = request.lat_natal, request.lon_natal
        
        fecha_natal_dt = datetime.strptime(request.fecha_natal, "%Y-%m-%d")
        hora_natal_parts = request.hora_natal.split(":")
        
        natal = AstrologicalSubject(
            name=request.nombre,
            year=fecha_natal_dt.year,
            month=fecha_natal_dt.month,
            day=fecha_natal_dt.day,
            hour=int(hora_natal_parts[0]),
            minute=int(hora_natal_parts[1]),
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal
        )
        
        # Tránsitos (fecha actual si no se especifica)
        if request.fecha_transito:
            fecha_transito_dt = datetime.strptime(request.fecha_transito, "%Y-%m-%d")
        else:
            fecha_transito_dt = datetime.now()
        
        transitos = AstrologicalSubject(
            name="Tránsitos",
            year=fecha_transito_dt.year,
            month=fecha_transito_dt.month,
            day=fecha_transito_dt.day,
            hour=12,  # Mediodía por defecto
            minute=0,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal
        )
        
        # Formatear respuestas
        posiciones_natal = formatear_posiciones(natal)
        posiciones_transitos = formatear_posiciones(transitos)
        
        return {
            "success": True,
            "fecha_transito": fecha_transito_dt.strftime("%Y-%m-%d"),
            "natal": posiciones_natal,
            "transitos": posiciones_transitos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular tránsitos: {str(e)}")


@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    """
    Calcula revolución solar para un año específico
    """
    try:
        # Geocodificar
        if request.lat_natal is None or request.lon_natal is None:
            lat, lon = geocode_ciudad(request.ciudad_natal, request.pais_natal)
        else:
            lat, lon = request.lat_natal, request.lon_natal
        
        # Fecha natal
        fecha_natal_dt = datetime.strptime(request.fecha_natal, "%Y-%m-%d")
        hora_natal_parts = request.hora_natal.split(":")
        
        # Revolución solar: mismo día/mes del año de revolución
        revolucion = AstrologicalSubject(
            name=f"{request.nombre} - RS {request.año_revolucion}",
            year=request.año_revolucion,
            month=fecha_natal_dt.month,
            day=fecha_natal_dt.day,
            hour=int(hora_natal_parts[0]),
            minute=int(hora_natal_parts[1]),
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat,
            lng=lon,
            tz_str=request.timezone_natal
        )
        
        posiciones_revolucion = formatear_posiciones(revolucion)
        
        return {
            "success": True,
            "año_revolucion": request.año_revolucion,
            "fecha_revolucion": f"{request.año_revolucion}-{fecha_natal_dt.month:02d}-{fecha_natal_dt.day:02d}",
            "carta_revolucion": posiciones_revolucion
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular revolución solar: {str(e)}")


# Para ejecutar localmente:
# uvicorn main:app --reload
