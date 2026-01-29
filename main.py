"""
API Astrológica para SAVP v3.5
Versión CORREGIDA - Compatible con Kerykeion 5.7.0+
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from kerykeion import AstrologicalSubject
from typing import Optional, Dict, Any, List, Tuple

import pytz

app = FastAPI(
    title="API Astrológica SAVP v3.5",
    description="Cálculos astrológicos para el Sistema Árbol de la Vida Personal",
    version="1.3.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELOS
# =========================
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


# =========================
# FUNCIONES AUXILIARES
# =========================

# Normalización robusta de signos (abreviaturas, inglés y español)
SIGN_INDEX = {
    # 3 letras (kerykeion típico)
    "ari": 0, "tau": 1, "gem": 2, "can": 3, "leo": 4, "vir": 5,
    "lib": 6, "sco": 7, "sag": 8, "cap": 9, "aqu": 10, "pis": 11,

    # inglés completo (por si acaso)
    "aries": 0, "taurus": 1, "gemini": 2, "cancer": 3, "leo": 4, "virgo": 5,
    "libra": 6, "scorpio": 7, "sagittarius": 8, "capricorn": 9, "aquarius": 10, "pisces": 11,

    # español (por si acaso)
    "tauro": 1,
    "géminis": 2, "geminis": 2,
    "cáncer": 3, "cancer": 3,
    "virgo": 5,
    "escorpio": 7,
    "sagitario": 8,
    "capricornio": 9,
    "acuario": 10,
    "piscis": 11,
}

def sign_to_index(sign: str) -> int:
    if not sign:
        return 0
    s = sign.strip().lower()
    if s in SIGN_INDEX:
        return SIGN_INDEX[s]
    s3 = s[:3]
    return SIGN_INDEX.get(s3, 0)

def grado_absoluto_desde_signo(grado: float, signo: str) -> float:
    """Convierte grado en signo a grado absoluto (0-360)"""
    return (sign_to_index(signo) * 30.0 + float(grado)) % 360.0


def geocode_ciudad(ciudad: str, pais: str) -> Tuple[float, float]:
    """
    Geocodifica ciudad usando Nominatim (OpenStreetMap - gratis, sin API key)
    Fallback a diccionario de ciudades españolas principales
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError

    # Intentar geocoding real primero
    try:
        geolocator = Nominatim(user_agent="api-savp-v1", timeout=10)
        location = geolocator.geocode(f"{ciudad}, {pais}", exactly_one=True, language="es")
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
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

    if ciudad_lower in ciudades_espana:
        return ciudades_espana[ciudad_lower]

    # Búsqueda parcial (por si escriben variantes)
    for key, coords in ciudades_espana.items():
        if ciudad_lower in key or key in ciudad_lower:
            return coords

    # Default final: Madrid
    return (40.4168, -3.7038)


def get_planet_data(subject: AstrologicalSubject, planet_name: str) -> Optional[Dict[str, Any]]:
    """Obtiene datos de un planeta de forma segura"""
    try:
        planet = getattr(subject, planet_name, None)
        if planet is None:
            return None

        if isinstance(planet, dict):
            return {
                "grado": round(float(planet.get("position", 0.0)), 2),
                "signo": planet.get("sign", ""),
                "casa": int(planet.get("house", 1)) if planet.get("house", 1) is not None else 1,
                "retrogrado": bool(planet.get("retrograde", False))
            }
        else:
            return {
                "grado": round(float(getattr(planet, "position", 0.0)), 2),
                "signo": getattr(planet, "sign", ""),
                "casa": int(getattr(planet, "house", 1)) if getattr(planet, "house", 1) is not None else 1,
                "retrogrado": bool(getattr(planet, "retrograde", False))
            }
    except Exception:
        return None


def house_cusps_abs_from_subject(subject: AstrologicalSubject) -> List[float]:
    """
    Devuelve lista de 12 cúspides absolutas (0..360), Casa 1..12.
    Compatible con Kerykeion 5.x:
      - first_house..twelfth_house
      - fallback seguro a subject.houses si existe
    """
    house_keys = [
        "first_house", "second_house", "third_house", "fourth_house", "fifth_house", "sixth_house",
        "seventh_house", "eighth_house", "ninth_house", "tenth_house", "eleventh_house", "twelfth_house",
    ]

    # Intento 1: atributos directos (lo más fiable)
    cusps: List[float] = []
    ok = True
    for key in house_keys:
        h = getattr(subject, key, None)
        if h is None:
            ok = False
            break

        if isinstance(h, dict):
            pos = float(h.get("position", 0.0))
            sign = h.get("sign", "Ari")
        else:
            pos = float(getattr(h, "position", 0.0))
            sign = getattr(h, "sign", "Ari")

        cusps.append((sign_to_index(sign) * 30.0 + pos) % 360.0)

    if ok and len(cusps) == 12:
        return cusps

    # Intento 2: subject.houses (si existiese)
    houses = getattr(subject, "houses", None)
    if houses:
        tmp: List[float] = []
        # puede venir dict {1:{...},2:{...}} o lista
        if isinstance(houses, dict):
            for i in range(1, 13):
                h = houses.get(i) or houses.get(str(i))
                if not h:
                    raise ValueError("Missing cusp in subject.houses")
                pos = float(h.get("position", 0.0))
                sign = h.get("sign", "Ari")
                tmp.append((sign_to_index(sign) * 30.0 + pos) % 360.0)
        elif isinstance(houses, list) and len(houses) >= 12:
            for i in range(12):
                h = houses[i]
                if isinstance(h, dict):
                    pos = float(h.get("position", 0.0))
                    sign = h.get("sign", "Ari")
                else:
                    pos = float(getattr(h, "position", 0.0))
                    sign = getattr(h, "sign", "Ari")
                tmp.append((sign_to_index(sign) * 30.0 + pos) % 360.0)
        else:
            raise ValueError("Unsupported subject.houses structure")

        if len(tmp) == 12:
            return tmp

    raise ValueError("No se pudieron obtener cúspides (first_house..twelfth_house ni subject.houses).")


def asignar_casa_por_cusps(planeta_grado_abs: float, cusps_abs: List[float]) -> int:
    """
    Asigna casa (1..12) usando cúspides absolutas (0..360).
    Maneja cruce por 0° correctamente.
    """
    lon = float(planeta_grado_abs) % 360.0
    if len(cusps_abs) != 12:
        raise ValueError("cusps_abs debe tener 12 elementos")

    for i in range(12):
        start = cusps_abs[i]
        end = cusps_abs[(i + 1) % 12]

        lon2 = lon
        end2 = end

        # cruce 0°
        if end2 < start:
            end2 += 360.0
        if lon2 < start:
            lon2 += 360.0

        if start <= lon2 < end2:
            return i + 1

    raise ValueError("No se pudo asignar casa con las cúspides dadas.")


def formatear_posiciones(subject: AstrologicalSubject, reference_subject: Optional[AstrologicalSubject] = None) -> Dict[str, Any]:
    """
    Extrae posiciones planetarias - Compatible con Kerykeion 5.x

    Args:
        subject: Carta a formatear
        reference_subject: si se proporciona, las casas se asignan usando cúspides de reference_subject
                          (tránsitos en casas natales).
    """
    planetas: Dict[str, Any] = {}

    # Precalcular cúspides natales si se piden casas natales
    cusps_abs: Optional[List[float]] = None
    if reference_subject is not None:
        cusps_abs = house_cusps_abs_from_subject(reference_subject)

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
        if not data:
            continue

        if cusps_abs is not None:
            # recalcular casa por cúspides natales reales
            grado_abs = grado_absoluto_desde_signo(data["grado"], data["signo"])
            data["casa"] = asignar_casa_por_cusps(grado_abs, cusps_abs)

        planetas[esp] = data

    # Puntos especiales
    puntos: Dict[str, Any] = {}

    # ASC (cúspide 1 del subject actual)
    asc_data = get_planet_data(subject, "first_house")
    if asc_data:
        puntos["asc"] = {
            "grado": asc_data["grado"],
            "signo": asc_data["signo"]
        }

    # MC (cúspide 10 del subject actual)
    mc_data = get_planet_data(subject, "tenth_house")
    if mc_data:
        puntos["mc"] = {
            "grado": mc_data["grado"],
            "signo": mc_data["signo"]
        }

    # Nodo Norte
    nodo_data = get_planet_data(subject, "mean_node")
    if nodo_data:
        puntos["nodo_norte"] = nodo_data

    return {"planetas": planetas, "puntos": puntos}


def now_in_tz(tz_str: str) -> datetime:
    """Datetime 'ahora' consciente de zona horaria."""
    tz = pytz.timezone(tz_str)
    return datetime.now(tz)


# =========================
# ENDPOINTS
# =========================
@app.get("/")
def root():
    return {
        "api": "API Astrológica SAVP v3.5",
        "version": "1.3.0",
        "endpoints": ["/natal", "/transits", "/solar_return", "/geocode", "/docs"]
    }


@app.get("/geocode")
def test_geocode(ciudad: str, pais: str = "España"):
    """Endpoint de prueba para verificar geocoding"""
    try:
        lat, lon = geocode_ciudad(ciudad, pais)
        return {
            "success": True,
            "ciudad": ciudad,
            "pais": pais,
            "coordenadas": {"lat": lat, "lon": lon},
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
        lat, lon = (request.lat, request.lon) if (request.lat is not None and request.lon is not None) else geocode_ciudad(request.ciudad, request.pais)

        fecha_dt = datetime.strptime(request.fecha, "%Y-%m-%d")
        hora_parts = request.hora.split(":")
        hour = int(hora_parts[0])
        minute = int(hora_parts[1])

        subject = AstrologicalSubject(
            name=request.nombre,
            year=fecha_dt.year,
            month=fecha_dt.month,
            day=fecha_dt.day,
            hour=hour,
            minute=minute,
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
                "coordenadas": {"lat": lat, "lon": lon},
                "timezone": request.timezone,
                "house_system": request.house_system
            },
            "carta": posiciones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/transits")
def calcular_transitos(request: TransitsRequest):
    try:
        lat_natal, lon_natal = (request.lat_natal, request.lon_natal) if (request.lat_natal is not None and request.lon_natal is not None) else geocode_ciudad(request.ciudad_natal, request.pais_natal)

        # Carta natal
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

        # Momento de tránsito (fecha/hora)
        if request.fecha_transito:
            fecha_transito_dt = datetime.strptime(request.fecha_transito, "%Y-%m-%d")
            if request.hora_transito:
                hora_parts = request.hora_transito.split(":")
                hora_t = int(hora_parts[0])
                minuto_t = int(hora_parts[1])
            else:
                # Importante: si no viene hora, usar 12:00 local (no UTC)
                hora_t = 12
                minuto_t = 0
        else:
            now_dt = now_in_tz(request.timezone_natal)
            fecha_transito_dt = now_dt
            hora_t = now_dt.hour
            minuto_t = now_dt.minute

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

        natal_pos = formatear_posiciones(natal)

        if request.use_natal_houses:
            # Tránsitos en casas natales reales
            transitos_pos = formatear_posiciones(transitos, reference_subject=natal)
            houses_mode = "natal"
        else:
            # Tránsitos en casas del propio tránsito
            transitos_pos = formatear_posiciones(transitos)
            houses_mode = "transit"

        return {
            "success": True,
            "fecha_transito": fecha_transito_dt.strftime("%Y-%m-%d") if isinstance(fecha_transito_dt, datetime) else str(fecha_transito_dt),
            "hora_transito": f"{hora_t:02d}:{minuto_t:02d}",
            "timezone": request.timezone_natal,
            "house_system": request.house_system,
            "houses_mode": houses_mode,
            "use_natal_houses": request.use_natal_houses,
            "coordenadas": {"lat": lat_natal, "lon": lon_natal},
            "natal": natal_pos,
            "transitos": transitos_pos
        }

    except ValueError as e:
        # Errores de cúspides / casas
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    try:
        lat, lon = (request.lat_natal, request.lon_natal) if (request.lat_natal is not None and request.lon_natal is not None) else geocode_ciudad(request.ciudad_natal, request.pais_natal)

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
            "timezone": request.timezone_natal,
            "house_system": request.house_system,
            "coordenadas": {"lat": lat, "lon": lon},
            "carta_revolucion": formatear_posiciones(revolucion)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
