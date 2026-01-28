"""
API Astrológica para SAVP v3.5
Cálculos de carta natal, tránsitos y revolución solar
Usando Kerykeion (Swiss Ephemeris)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from kerykeion import AstrologicalSubject
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
    Compatible con Kerykeion v5+
    """
    planetas = {}
    
    # En Kerykeion v5+, los planetas están en subject.planets_list
    # y cada uno tiene attributes: name, sign, position, house, retrograde
    
    try:
        # Sol
        sol = next((p for p in subject.planets_list if p['name'] == 'Sun'), None)
        if sol:
            planetas["sol"] = {
                "grado": round(sol['position'], 2),
                "signo": sol['sign'],
                "casa": sol['house'],
                "retrogrado": sol.get('retrograde', False)
            }
        
        # Luna
        luna = next((p for p in subject.planets_list if p['name'] == 'Moon'), None)
        if luna:
            planetas["luna"] = {
                "grado": round(luna['position'], 2),
                "signo": luna['sign'],
                "casa": luna['house'],
                "retrogrado": luna.get('retrograde', False)
            }
        
        # Mercurio
        mercurio = next((p for p in subject.planets_list if p['name'] == 'Mercury'), None)
        if mercurio:
            planetas["mercurio"] = {
                "grado": round(mercurio['position'], 2),
                "signo": mercurio['sign'],
                "casa": mercurio['house'],
                "retrogrado": mercurio.get('retrograde', False)
            }
        
        # Venus
        venus = next((p for p in subject.planets_list if p['name'] == 'Venus'), None)
        if venus:
            planetas["venus"] = {
                "grado": round(venus['position'], 2),
                "signo": venus['sign'],
                "casa": venus['house'],
                "retrogrado": venus.get('retrograde', False)
            }
        
        # Marte
        marte = next((p for p in subject.planets_list if p['name'] == 'Mars'), None)
        if marte:
            planetas["marte"] = {
                "grado": round(marte['position'], 2),
                "signo": marte['sign'],
                "casa": marte['house'],
                "retrogrado": marte.get('retrograde', False)
            }
        
        # Júpiter
        jupiter = next((p for p in subject.planets_list if p['name'] == 'Jupiter'), None)
        if jupiter:
            planetas["jupiter"] = {
                "grado": round(jupiter['position'], 2),
                "signo": jupiter['sign'],
                "casa": jupiter['house'],
                "retrogrado": jupiter.get('retrograde', False)
            }
        
        # Saturno
        saturno = next((p for p in subject.planets_list if p['name'] == 'Saturn'), None)
        if saturno:
            planetas["saturno"] = {
                "grado": round(saturno['position'], 2),
                "signo": saturno['sign'],
                "casa": saturno['house'],
                "retrogrado": saturno.get('retrograde', False)
            }
        
        # Urano
        urano = next((p for p in subject.planets_list if p['name'] == 'Uranus'), None)
        if urano:
            planetas["urano"] = {
                "grado": round(urano['position'], 2),
                "signo": urano['sign'],
                "casa": urano['house'],
                "retrogrado": urano.get('retrograde', False)
            }
        
        # Neptuno
        neptuno = next((p for p in subject.planets_list if p['name'] == 'Neptune'), None)
        if neptuno:
            planetas["neptuno"] = {
                "grado": round(neptuno['position'], 2),
                "signo": neptuno['sign'],
                "casa": neptuno['house'],
                "retrogrado": neptuno.get('retrograde', False)
            }
        
        # Plutón
        pluton = next((p for p in subject.planets_list if p['name'] == 'Pluto'), None)
        if pluton:
            planetas["pluton"] = {
                "grado": round(pluton['position'], 2),
                "signo": pluton['sign'],
                "casa": pluton['house'],
                "retrogrado": pluton.get('retrograde', False)
            }
        
        # Puntos especiales (houses_list y nodes)
        puntos = {}
        
        # ASC (First House)
        if hasattr(subject, 'houses_list') and len(subject.houses_list) > 0:
            asc = subject.houses_list[0]
            puntos["asc"] = {
                "grado": round(asc['position'], 2),
                "signo": asc['sign']
            }
        
        # MC (Tenth House)
        if hasattr(subject, 'houses_list') and len(subject.houses_list) > 9:
            mc = subject.houses_list[9]
            puntos["mc"] = {
                "grado": round(mc['position'], 2),
                "signo": mc['sign']
            }
        
        # Nodo Norte
        nodo = next((p for p in subject.planets_list if p['name'] == 'Mean_Node'), None)
        if nodo:
            puntos["nodo_norte"] = {
                "grado": round(nodo['position'], 2),
                "signo": nodo['sign'],
                "casa": nodo['house']
            }
        
        return {
            "planetas": planetas,
            "puntos": puntos
        }
        
    except Exception as e:
        # Si falla, devolver estructura mínima con el error
        return {
            "planetas": {},
            "puntos": {},
            "error": f"Error al formatear posiciones: {str(e)}"
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
