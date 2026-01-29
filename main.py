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
    house_system: Optional[str] = "P"  # P=Placidus, W=Whole Sign, E=Equal

class TransitsRequest(BaseModel):
    nombre: str
    fecha_natal: str
    hora_natal: str
    ciudad_natal: str
    pais_natal: str
    lat_natal: Optional[float] = None
    lon_natal: Optional[float] = None
    timezone_natal: Optional[str] = "Europe/Madrid"
    fecha_transito: Optional[str] = None  # YYYY-MM-DD
    hora_transito: Optional[str] = None   # HH:MM
    house_system: Optional[str] = "P"  # P=Placidus, W=Whole Sign, E=Equal
    use_natal_houses: Optional[bool] = True  # SAVP v3.5 requiere True por defecto

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
    house_system: Optional[str] = "P"  # P=Placidus, W=Whole Sign, E=Equal

# FUNCIONES
def geocode_ciudad(ciudad: str, pais: str):
    """
    Geocodifica ciudad usando Nominatim (OpenStreetMap - gratis, sin API key)
    Fallback a diccionario de ciudades españolas principales
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    
    # Intentar geocoding real primero
    try:
        geolocator = Nominatim(user_agent="api-savp-v1", timeout=10)
        # Formato: "Ciudad, País" para mejor precisión
        location = geolocator.geocode(f"{ciudad}, {pais}", exactly_one=True, language="es")
        
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
        # Si falla el servicio, continuar con fallback
        print(f"Geocoding fallback: {e}")
        pass
    
    # Fallback: Diccionario de ciudades españolas principales
    ciudades_espana = {
        "madrid": (40.4168, -3.7038),
        "barcelona": (41.3851, 2.1734),
        "zaragoza": (41.6488, -0.8891),
        "valencia": (39.4699, -0.3763),
        "sevilla": (37.3886, -5.9823),
        "málaga": (36.7213, -4.4214),
        "malaga": (36.7213, -4.4214),
        "bilbao": (43.2630, -2.9350),
        "alicante": (38.3452, -0.4810),
        "córdoba": (37.8882, -4.7794),
        "cordoba": (37.8882, -4.7794),
        "valladolid": (41.6528, -4.7245),
        "murcia": (37.9922, -1.1307),
        "palma": (39.5696, 2.6502),
        "las palmas": (28.1248, -15.4300),
        "bilbao": (43.2630, -2.9350),
        "vitoria": (42.8467, -2.6716),
        "salamanca": (40.9701, -5.6635),
        "santander": (43.4623, -3.8100),
        "pamplona": (42.8125, -1.6458),
        "toledo": (39.8628, -4.0273),
        "badajoz": (38.8794, -6.9706),
        "logroño": (42.4627, -2.4450),
        "fuentes de ebro": (41.5167, -0.6333),
        "alcobendas": (40.5479, -3.6411),
    }
    
    ciudad_lower = ciudad.lower().strip()
    
    # Buscar en diccionario
    if ciudad_lower in ciudades_espana:
        return ciudades_espana[ciudad_lower]
    
    # Búsqueda parcial (por si escriben "Fuentes Ebro" en vez de "Fuentes de Ebro")
    for key, coords in ciudades_espana.items():
        if ciudad_lower in key or key in ciudad_lower:
            return coords
    
    # Default final: Madrid (capital)
    return (40.4168, -3.7038)

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

def calcular_casa_en_carta_natal(planeta_grado_abs, natal_subject):
    """
    Calcula en qué casa NATAL cae un planeta dado su grado absoluto
    
    Args:
        planeta_grado_abs: Grado absoluto del planeta (0-360)
        natal_subject: AstrologicalSubject de la carta natal
    
    Returns:
        Número de casa natal (1-12)
    """
    try:
        # Kerykeion 5.x usa houses_list
        if not hasattr(natal_subject, 'houses_list'):
            print("ERROR: natal_subject no tiene houses_list")
            return 1
        
        houses_list = natal_subject.houses_list
        print(f"DEBUG houses_list type: {type(houses_list)}")
        print(f"DEBUG houses_list length: {len(houses_list) if houses_list else 0}")
        
        if not houses_list or len(houses_list) < 12:
            print("ERROR: houses_list vacía o incompleta")
            return 1
        
        # Mapeo de signos a índice
        signos_map = {
            'Ari': 0, 'Tau': 1, 'Gem': 2, 'Can': 3, 'Leo': 4, 'Vir': 5,
            'Lib': 6, 'Sco': 7, 'Sag': 8, 'Cap': 9, 'Aqu': 10, 'Pis': 11
        }
        
        houses_abs = []
        
        # Convertir cada casa a grado absoluto
        for i, house in enumerate(houses_list, 1):
            print(f"DEBUG Casa {i}: type={type(house)}, value={house}")
            
            # Obtener position y sign
            if isinstance(house, dict):
                pos = house.get('position', 0)
                sign = house.get('sign', 'Ari')
            else:
                pos = getattr(house, 'position', 0)
                sign = getattr(house, 'sign', 'Ari')
            
            # Convertir a grado absoluto
            sign_short = sign[:3] if len(sign) > 3 else sign
            sign_idx = signos_map.get(sign_short, 0)
            abs_pos = (sign_idx * 30 + pos) % 360
            houses_abs.append(abs_pos)
            
            print(f"DEBUG Casa {i}: {pos:.2f}° {sign} = {abs_pos:.2f}° absoluto")
        
        # Normalizar grado del planeta
        grado_norm = planeta_grado_abs % 360
        print(f"DEBUG Planeta: {grado_norm:.2f}° absoluto")
        
        # Buscar en qué casa cae
        for casa in range(12):
            cusp_actual = houses_abs[casa]
            cusp_siguiente = houses_abs[(casa + 1) % 12] if casa < 11 else houses_abs[0]
            
            # Manejar cruce de 0°
            if cusp_siguiente < cusp_actual:
                # Casa cruza 0° Aries
                if grado_norm >= cusp_actual or grado_norm < cusp_siguiente:
                    print(f"DEBUG → Casa {casa+1} (cruce 0°): {cusp_actual:.2f}° <= {grado_norm:.2f}° o < {cusp_siguiente:.2f}°")
                    return casa + 1
            else:
                # Casa normal
                if cusp_actual <= grado_norm < cusp_siguiente:
                    print(f"DEBUG → Casa {casa+1} (normal): {cusp_actual:.2f}° <= {grado_norm:.2f}° < {cusp_siguiente:.2f}°")
                    return casa + 1
        
        print("DEBUG → Fallback Casa 1")
        return 1
        
    except Exception as e:
        print(f"ERROR calculando casa: {e}")
        import traceback
        traceback.print_exc()
        return 1

def grado_absoluto_desde_signo(grado, signo):
    """Convierte grado en signo a grado absoluto (0-360)"""
    signos_map = {
        'Ari': 0, 'Tau': 1, 'Gem': 2, 'Can': 3, 'Leo': 4, 'Vir': 5,
        'Lib': 6, 'Sco': 7, 'Sag': 8, 'Cap': 9, 'Aqu': 10, 'Pis': 11
    }
    signo_corto = signo[:3] if len(signo) > 3 else signo
    signo_idx = signos_map.get(signo_corto, 0)
    return (signo_idx * 30 + grado) % 360

def formatear_posiciones(subject: AstrologicalSubject, reference_subject: Optional[AstrologicalSubject] = None):
    """
    Extrae posiciones planetarias - Compatible con Kerykeion 5.x
    
    Args:
        subject: Carta a formatear
        reference_subject: Si se proporciona, las casas se calculan con respecto a esta carta
                          (útil para tránsitos en casas natales)
    """
    planetas = {}
    
    # DEBUG
    if reference_subject:
        print(f"DEBUG formatear_posiciones: reference_subject presente")
        print(f"DEBUG reference_subject.name = {reference_subject.name}")
        # Verificar que tiene atributos de casas
        print(f"DEBUG hasattr house1? {hasattr(reference_subject, 'house1')}")
        if hasattr(reference_subject, 'house1'):
            h1 = getattr(reference_subject, 'house1')
            print(f"DEBUG house1 = {h1}")
    
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
            # Si usamos casas de referencia (casas natales), recalcular
            if reference_subject:
                grado_abs = grado_absoluto_desde_signo(data['grado'], data['signo'])
                print(f"DEBUG {esp}: {data['grado']}° {data['signo']} = {grado_abs}° absoluto")
                casa_natal = calcular_casa_en_carta_natal(grado_abs, reference_subject)
                data['casa'] = casa_natal
            
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
        "version": "1.2.0",
        "endpoints": ["/natal", "/transits", "/solar_return", "/geocode", "/docs"]
    }

@app.get("/geocode")
def test_geocode(ciudad: str, pais: str = "España"):
    """
    Endpoint de prueba para verificar geocoding
    Útil para que el GPT verifique coordenadas antes de calcular
    """
    try:
        lat, lon = geocode_ciudad(ciudad, pais)
        return {
            "success": True,
            "ciudad": ciudad,
            "pais": pais,
            "coordenadas": {
                "lat": lat,
                "lon": lon
            },
            "mensaje": "Coordenadas obtenidas correctamente"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "mensaje": "Error al geocodificar"
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
            tz_str=request.timezone,
            houses_system_identifier=request.house_system
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
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )
        
        if request.fecha_transito:
            fecha_transito_dt = datetime.strptime(request.fecha_transito, "%Y-%m-%d")
            # Si se proporciona hora_transito, usarla; sino 12:00
            if request.hora_transito:
                hora_parts = request.hora_transito.split(":")
                hora_t = int(hora_parts[0])
                minuto_t = int(hora_parts[1])
            else:
                hora_t = 12
                minuto_t = 0
        else:
            fecha_transito_dt = datetime.now()
            hora_t = fecha_transito_dt.hour
            minuto_t = fecha_transito_dt.minute
        
        transitos = AstrologicalSubject(
            name="Tránsitos",
            year=fecha_transito_dt.year,
            month=fecha_transito_dt.month,
            day=fecha_transito_dt.day,
            hour=hora_t,
            minute=minuto_t,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )
        
        # Formatear posiciones
        natal_pos = formatear_posiciones(natal)
        
        # Si use_natal_houses=True, calcular tránsitos en casas natales
        if request.use_natal_houses:
            transitos_pos = formatear_posiciones(transitos, reference_subject=natal)
        else:
            transitos_pos = formatear_posiciones(transitos)
        
        return {
            "success": True,
            "fecha_transito": fecha_transito_dt.strftime("%Y-%m-%d"),
            "hora_transito": f"{hora_t:02d}:{minuto_t:02d}",
            "use_natal_houses": request.use_natal_houses,
            "natal": natal_pos,
            "transitos": transitos_pos
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
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )
        
        return {
            "success": True,
            "año_revolucion": request.año_revolucion,
            "fecha_revolucion": f"{request.año_revolucion}-{fecha_natal_dt.month:02d}-{fecha_natal_dt.day:02d}",
            "carta_revolucion": formatear_posiciones(revolucion)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
