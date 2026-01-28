"""
API Astrológica para SAVP v3.5
Versión CORREGIDA - Compatible con Kerykeion 5.7.0
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from kerykeion import AstrologicalSubject
from typing import Optional

app = FastAPI(
    title="API Astrológica SAVP v3.5",
    description="Cálculos astrológicos para el Sistema Árbol de la Vida Personal",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELOS
class NatalRequest(BaseModel):
    nombre: str
    fecha: str
    hora: str
    ciudad: str
    pais: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = "Europe/Madrid"

class TransitsRequest(BaseModel):
    nombre: str
    fecha_natal: str
    hora_natal: str
    ciudad_natal: str
    pais_natal: str
    lat_natal: Optional[float] = None
    lon_natal: Optional[float] = None
    timezone_natal: Optional[str] = "Europe/Madrid"
    fecha_transito: Optional[str] = None

class SolarReturnRequest(BaseModel):
    nombre: str
    fecha_natal: str
    hora_natal: str
    ciudad_natal: str
    pais_natal: str
    lat_natal: Optional[float] = None
    lon_natal: Optional[float] = None
    timezone_natal: Optional[str] = "Europe/Madrid"
    año_revolucion: int

# FUNCIONES
def geocode_ciudad(ciudad: str, pais: str):
    ciudades = {
        "madrid": (40.4168, -3.7038),
        "barcelona": (41.3851, 2.1734),
        "zaragoza": (41.6488, -0.8891),
        "valencia": (39.4699, -0.3763),
        "sevilla": (37.3886, -5.9823),
        "malaga": (36.7213, -4.4214),
        "bilbao": (43.2630, -2.9350),
    }
    return ciudades.get(ciudad.lower(), (40.4168, -3.7038))

def get_planet_data(subject, planet_name):
    """Obtiene datos de un planeta de forma segura"""
    try:
        planet = getattr(subject, planet_name, None)
        if planet is None:
            return None
        
        # Kerykeion devuelve dict
        if isinstance(planet, dict):
            return {
                "grado": round(planet.get('position', 0), 2),
                "signo": planet.get('sign', ''),
                "casa": planet.get('house', 1),
                "retrogrado": planet.get('retrograde', False)
            }
        # O objeto con atributos
        else:
            return {
                "grado": round(getattr(planet, 'position', 0), 2),
                "signo": getattr(planet, 'sign', ''),
                "casa": getattr(planet, 'house', 1),
                "retrogrado": getattr(planet, 'retrograde', False)
            }
    except:
        return None

def formatear_posiciones(subject: AstrologicalSubject):
    """Extrae posiciones planetarias - Compatible con Kerykeion 5.x"""
    planetas = {}
    
    # Mapeo de nombres
    planet_map = {
        "sol": "sun",
        "luna": "moon",
        "mercurio": "mercury",
        "venus": "venus",
        "marte": "mars",
        "jupiter": "jupiter",
        "saturno": "saturn",
        "urano": "uranus",
        "neptuno": "neptune",
        "pluton": "pluto"
    }
    
    for esp, eng in planet_map.items():
        data = get_planet_data(subject, eng)
        if data:
            planetas[esp] = data
    
    # Puntos especiales
    puntos = {}
    
    # ASC
    asc_data = get_planet_data(subject, 'first_house')
    if asc_data:
        puntos["asc"] = {
            "grado": asc_data["grado"],
            "signo": asc_data["signo"]
        }
    
    # MC
    mc_data = get_planet_data(subject, 'tenth_house')
    if mc_data:
        puntos["mc"] = {
            "grado": mc_data["grado"],
            "signo": mc_data["signo"]
        }
    
    # Nodo Norte
    nodo_data = get_planet_data(subject, 'mean_node')
    if nodo_data:
        puntos["nodo_norte"] = nodo_data
    
    return {"planetas": planetas, "puntos": puntos}

# ENDPOINTS
@app.get("/")
def root():
    return {
        "api": "API Astrológica SAVP v3.5",
        "version": "1.0.0",
        "endpoints": ["/natal", "/transits", "/solar_return", "/docs"]
    }

@app.post("/natal")
def calcular_natal(request: NatalRequest):
    try:
        lat, lon = (request.lat, request.lon) if request.lat and request.lon else geocode_ciudad(request.ciudad, request.pais)
        
        fecha_dt = datetime.strptime(request.fecha, "%Y-%m-%d")
        hora_parts = request.hora.split(":")
        
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/transits")
def calcular_transitos(request: TransitsRequest):
    try:
        lat_natal, lon_natal = (request.lat_natal, request.lon_natal) if request.lat_natal and request.lon_natal else geocode_ciudad(request.ciudad_natal, request.pais_natal)
        
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
        
        if request.fecha_transito:
            fecha_transito_dt = datetime.strptime(request.fecha_transito, "%Y-%m-%d")
        else:
            fecha_transito_dt = datetime.now()
        
        transitos = AstrologicalSubject(
            name="Tránsitos",
            year=fecha_transito_dt.year,
            month=fecha_transito_dt.month,
            day=fecha_transito_dt.day,
            hour=12,
            minute=0,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal
        )
        
        return {
            "success": True,
            "fecha_transito": fecha_transito_dt.strftime("%Y-%m-%d"),
            "natal": formatear_posiciones(natal),
            "transitos": formatear_posiciones(transitos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    try:
        lat, lon = (request.lat_natal, request.lon_natal) if request.lat_natal and request.lon_natal else geocode_ciudad(request.ciudad_natal, request.pais_natal)
        
        fecha_natal_dt = datetime.strptime(request.fecha_natal, "%Y-%m-%d")
        hora_natal_parts = request.hora_natal.split(":")
        
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
        
        return {
            "success": True,
            "año_revolucion": request.año_revolucion,
            "fecha_revolucion": f"{request.año_revolucion}-{fecha_natal_dt.month:02d}-{fecha_natal_dt.day:02d}",
            "carta_revolucion": formatear_posiciones(revolucion)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
