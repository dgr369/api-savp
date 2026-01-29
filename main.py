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
    fecha_transito: Optional[str] = None
    hora_transito: Optional[str] = None
    house_system: Optional[str] = "P"
    use_natal_houses: Optional[bool] = True

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
    house_system: Optional[str] = "P"

# UTILIDADES
def parse_fecha_hora(fecha_str: str, hora_str: str):
    """Parsea fecha y hora en formatos flexibles"""
    try:
        # Formato esperado: YYYY-MM-DD o DD/MM/YYYY
        if "/" in fecha_str:
            # Convertir DD/MM/YYYY a YYYY-MM-DD
            parts = fecha_str.split("/")
            fecha_str = f"{parts[2]}-{parts[1]}-{parts[0]}"

        # Parsear
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        hora_parts = hora_str.split(":")
        hour = int(hora_parts[0])
        minute = int(hora_parts[1]) if len(hora_parts) > 1 else 0

        return fecha.year, fecha.month, fecha.day, hour, minute

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parseando fecha/hora: {str(e)}")

def geocode_ciudad(ciudad: str, pais: str):
    """Geocodifica ciudad usando geopy"""
    try:
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="savp_astrology_api")
        location = geolocator.geocode(f"{ciudad}, {pais}")

        if not location:
            raise HTTPException(status_code=404, detail=f"No se encontró la ciudad: {ciudad}, {pais}")

        return location.latitude, location.longitude

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en geocodificación: {str(e)}")

def get_planet_data(subject: AstrologicalSubject, planet_name: str):
    """Extrae datos de un planeta en Kerykeion 5.x"""
    try:
        if not hasattr(subject, planet_name):
            return None

        planet = getattr(subject, planet_name)
        # Kerykeion 5.x devuelve objetos con atributos
        if isinstance(planet, dict):
            # Formato dict
            casa = planet.get('house', 1)
            return {
                "grado": round(planet.get('position', 0), 2),
                "signo": planet.get('sign', ''),
                "casa": casa,
                "retrogrado": planet.get('retrograde', False)
            }
        else:
            # Formato objeto
            try:
                casa = getattr(planet, 'house', 1)
                return {
                    "grado": round(getattr(planet, 'position', 0), 2),
                    "signo": getattr(planet, 'sign', ''),
                    "casa": casa,
                    "retrogrado": getattr(planet, 'retrograde', False)
                }
            except:
                return None

    except Exception as e:
        print(f"Error get_planet_data {planet_name}: {e}")
        return None

def grado_absoluto_desde_signo(grado: float, signo: str) -> float:
    """Convierte grado dentro del signo a grado absoluto (0-360)"""
    signos = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
             'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']
    if signo not in signos:
        return grado

    signo_index = signos.index(signo)
    return signo_index * 30 + grado

def calcular_casa_en_carta_natal(grado_absoluto: float, subject_natal: AstrologicalSubject) -> int:
    """Calcula en qué casa natal cae un grado absoluto"""
    try:
        # Obtener cúspides de casas del subject natal
        casas = []
        for i in range(1, 13):
            house_attr = f'house{i}'
            if hasattr(subject_natal, house_attr):
                house_data = getattr(subject_natal, house_attr)
                if isinstance(house_data, dict):
                    grado = house_data.get('position', 0)
                    signo = house_data.get('sign', '')
                else:
                    grado = getattr(house_data, 'position', 0)
                    signo = getattr(house_data, 'sign', '')

                grado_abs = grado_absoluto_desde_signo(grado, signo)
                casas.append(grado_abs)

        if len(casas) != 12:
            print(f"DEBUG: Solo {len(casas)} casas encontradas")
            return 1

        # Encontrar casa correspondiente
        for i in range(12):
            casa_inicio = casas[i]
            casa_fin = casas[(i + 1) % 12]

            # Manejar wrap-around en 360°
            if casa_fin < casa_inicio:
                casa_fin += 360
                if grado_absoluto < casa_inicio:
                    grado_absoluto += 360

            if casa_inicio <= grado_absoluto < casa_fin:
                return i + 1

        return 1

    except Exception as e:
        print(f"Error calcular_casa_en_carta_natal: {e}")
        return 1

def get_mean_node(subject):
    """
    Calcula el Nodo Norte Medio usando fórmula astronómica
    (sin pyswisseph, que no compila en Render)

    Fórmula de Jean Meeus (Astronomical Algorithms):
    Nodo Medio = 125.04452° - 1934.136261° × T + 0.0020708° × T² + T³ / 450000
    donde T = (JD - 2451545.0) / 36525 (siglos julianos desde J2000)
    """
    try:
        from datetime import datetime
        import pytz

        # Fecha juliana J2000 (1 enero 2000 12:00 UTC)
        J2000 = 2451545.0

        # Crear datetime con timezone
        tz = pytz.timezone(subject.tz_str)
        dt_local = tz.localize(datetime(
            subject.year, subject.month, subject.day,
            subject.hour, subject.minute
        ))

        # Convertir a UTC
        dt_utc = dt_local.astimezone(pytz.UTC)

        # Calcular fecha juliana (algoritmo estándar)
        y = dt_utc.year
        m = dt_utc.month
        d = dt_utc.day
        h = dt_utc.hour + dt_utc.minute / 60.0

        if m <= 2:
            y -= 1
            m += 12

        A = int(y / 100)
        B = 2 - A + int(A / 4)

        jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5
        jd += h / 24.0

        # Siglos julianos desde J2000
        T = (jd - J2000) / 36525.0

        # Fórmula del Nodo Medio (Meeus)
        omega = 125.04452 - 1934.136261 * T + 0.0020708 * T**2 + T**3 / 450000.0

        # Normalizar a 0-360
        omega = omega % 360.0
        longitude = omega

        # Convertir a signo y grado
        sign_num = int(longitude / 30)
        degree = longitude % 30

        signos = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
                  'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis']

        # DEBUG
        print(f"DEBUG mean_node: JD={jd:.5f}, T={T:.8f}")
        print(f"DEBUG mean_node: longitude={longitude:.2f}°, {signos[sign_num]} {degree:.2f}°")

        return {
            "grado": round(degree, 2),
            "signo": signos[sign_num],
            "retrogrado": True
        }

    except Exception as e:
        print(f"ERROR calculando mean_node: {e}")
        import traceback
        traceback.print_exc()

        # Fallback: usar true_node
        print("FALLBACK: usando true_node")
        return get_planet_data(subject, 'true_node')

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

    # Nodos lunares - Usar MEDIO (mean_node) calculado manualmente
    nodo_norte_data = get_mean_node(subject)
    if nodo_norte_data:
        # Calcular casa SIEMPRE (en natal: con la propia carta; en tránsitos: con reference_subject)
        ref = reference_subject if reference_subject else subject
        grado_abs = grado_absoluto_desde_signo(nodo_norte_data['grado'], nodo_norte_data['signo'])
        casa_ref = calcular_casa_en_carta_natal(grado_abs, ref)
        nodo_norte_data['casa'] = casa_ref

        planetas["nodo_norte"] = nodo_norte_data

        # Nodo Sur (opuesto al Norte)
        nodo_sur_grado = nodo_norte_data['grado']
        nodo_sur_signo_idx = (['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
                               'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis'].index(nodo_norte_data['signo']) + 6) % 12
        nodo_sur_signo = ['Ari', 'Tau', 'Gem', 'Can', 'Leo', 'Vir',
                         'Lib', 'Sco', 'Sag', 'Cap', 'Aqu', 'Pis'][nodo_sur_signo_idx]

        nodo_sur_data = {
            "grado": nodo_sur_grado,
            "signo": nodo_sur_signo,
            "retrogrado": True
        }

        # Calcular casa SIEMPRE (en natal: con la propia carta; en tránsitos: con reference_subject)
        ref = reference_subject if reference_subject else subject
        grado_abs = grado_absoluto_desde_signo(nodo_sur_data['grado'], nodo_sur_data['signo'])
        casa_ref = calcular_casa_en_carta_natal(grado_abs, ref)
        nodo_sur_data['casa'] = casa_ref

        planetas["nodo_sur"] = nodo_sur_data

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

    return {"planetas": planetas, "puntos": puntos}

# ENDPOINTS
@app.get("/test_nodos")
def test_nodos():
    """Endpoint de prueba para verificar que los nodos funcionan"""
    try:
        subject = AstrologicalSubject(
            name="Test",
            year=1977,
            month=6,
            day=4,
            hour=9,
            minute=15,
            city="Zaragoza",
            nation="España",
            lat=41.65,
            lng=-0.88,
            tz_str="Europe/Madrid"
        )

        # Intentar obtener nodos de varias formas
        result = {
            "mean_node_exists": hasattr(subject, 'mean_node'),
            "true_node_exists": hasattr(subject, 'true_node'),
        }

        if hasattr(subject, 'mean_node'):
            nodo = getattr(subject, 'mean_node')
            result["mean_node_type"] = str(type(nodo))
            result["mean_node_value"] = str(nodo)
            result["mean_node_data"] = get_planet_data(subject, 'mean_node')

        if hasattr(subject, 'true_node'):
            nodo = getattr(subject, 'true_node')
            result["true_node_type"] = str(type(nodo))
            result["true_node_value"] = str(nodo)
            result["true_node_data"] = get_planet_data(subject, 'true_node')

        # NUEVO: Probar get_mean_node directamente
        print("=" * 50)
        print("PROBANDO get_mean_node()...")
        mean_node_calc = get_mean_node(subject)
        result["mean_node_calculated"] = mean_node_calc
        print(f"Resultado: {mean_node_calc}")
        print("=" * 50)

        # También probar formatear_posiciones
        posiciones = formatear_posiciones(subject)
        result["posiciones_nodos"] = {
            "nodo_norte": posiciones["planetas"].get("nodo_norte"),
            "nodo_sur": posiciones["planetas"].get("nodo_sur")
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/natal")
def calcular_natal(request: NatalRequest):
    """Calcula carta natal completa"""
    try:
        # Parsear fecha/hora
        year, month, day, hour, minute = parse_fecha_hora(request.fecha, request.hora)

        # Obtener coordenadas
        if request.lat is not None and request.lon is not None:
            lat, lon = request.lat, request.lon
        else:
            lat, lon = geocode_ciudad(request.ciudad, request.pais)

        # Crear subject con Kerykeion
        subject = AstrologicalSubject(
            name=request.nombre,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=request.ciudad,
            nation=request.pais,
            lat=lat,
            lng=lon,
            tz_str=request.timezone,
            houses_system_identifier=request.house_system
        )

        # Formatear posiciones
        carta = formatear_posiciones(subject)

        return {
            "success": True,
            "datos": {
                "nombre": request.nombre,
                "fecha": request.fecha,
                "hora": request.hora,
                "ciudad": request.ciudad,
                "coordenadas": {"lat": lat, "lon": lon}
            },
            "carta": carta
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando natal: {str(e)}")

@app.post("/transits")
def calcular_transitos(request: TransitsRequest):
    """Calcula tránsitos actuales en casas natales"""
    try:
        # Parsear datos natales
        year_n, month_n, day_n, hour_n, minute_n = parse_fecha_hora(request.fecha_natal, request.hora_natal)

        # Coordenadas natales
        if request.lat_natal is not None and request.lon_natal is not None:
            lat_n, lon_n = request.lat_natal, request.lon_natal
        else:
            lat_n, lon_n = geocode_ciudad(request.ciudad_natal, request.pais_natal)

        # Crear subject natal
        natal_subject = AstrologicalSubject(
            name=request.nombre,
            year=year_n,
            month=month_n,
            day=day_n,
            hour=hour_n,
            minute=minute_n,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        # Fecha/hora de tránsito (default: ahora)
        if request.fecha_transito and request.hora_transito:
            year_t, month_t, day_t, hour_t, minute_t = parse_fecha_hora(request.fecha_transito, request.hora_transito)
        else:
            now = datetime.now()
            year_t, month_t, day_t, hour_t, minute_t = now.year, now.month, now.day, now.hour, now.minute

        # Subject de tránsito (misma ubicación natal por defecto)
        transit_subject = AstrologicalSubject(
            name=f"Transits_{request.nombre}",
            year=year_t,
            month=month_t,
            day=day_t,
            hour=hour_t,
            minute=minute_t,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        # Calcular posiciones de tránsito (en casas natales si se pide)
        if request.use_natal_houses:
            transits = formatear_posiciones(transit_subject, reference_subject=natal_subject)
        else:
            transits = formatear_posiciones(transit_subject)

        natal = formatear_posiciones(natal_subject)

        return {
            "success": True,
            "datos": {
                "nombre": request.nombre,
                "natal": {
                    "fecha": request.fecha_natal,
                    "hora": request.hora_natal,
                    "ciudad": request.ciudad_natal,
                    "coordenadas": {"lat": lat_n, "lon": lon_n}
                },
                "transito": {
                    "fecha": request.fecha_transito if request.fecha_transito else now.strftime("%Y-%m-%d"),
                    "hora": request.hora_transito if request.hora_transito else now.strftime("%H:%M"),
                }
            },
            "natal": natal,
            "transitos": transits
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando tránsitos: {str(e)}")

@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    """Calcula revolución solar"""
    try:
        # Parsear datos natales
        year_n, month_n, day_n, hour_n, minute_n = parse_fecha_hora(request.fecha_natal, request.hora_natal)

        # Coordenadas natales
        if request.lat_natal is not None and request.lon_natal is not None:
            lat_n, lon_n = request.lat_natal, request.lon_natal
        else:
            lat_n, lon_n = geocode_ciudad(request.ciudad_natal, request.pais_natal)

        # Crear subject natal
        natal_subject = AstrologicalSubject(
            name=request.nombre,
            year=year_n,
            month=month_n,
            day=day_n,
            hour=hour_n,
            minute=minute_n,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        # Para la revolución solar: aproximación (mismo día/mes, año solicitado, misma hora)
        # Nota: el cálculo exacto requeriría búsqueda del retorno solar preciso.
        year_sr = request.año_revolucion
        sr_subject = AstrologicalSubject(
            name=f"SolarReturn_{request.nombre}_{year_sr}",
            year=year_sr,
            month=month_n,
            day=day_n,
            hour=hour_n,
            minute=minute_n,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        natal = formatear_posiciones(natal_subject)
        solar = formatear_posiciones(sr_subject)

        return {
            "success": True,
            "datos": {
                "nombre": request.nombre,
                "año_revolucion": request.año_revolucion,
                "natal": {
                    "fecha": request.fecha_natal,
                    "hora": request.hora_natal,
                    "ciudad": request.ciudad_natal,
                    "coordenadas": {"lat": lat_n, "lon": lon_n}
                }
            },
            "natal": natal,
            "revolucion_solar": solar
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando revolución solar: {str(e)}")

@app.get("/")
def root():
    return {
        "message": "API SAVP v3.5 - OK",
        "endpoints": ["/natal", "/transits", "/solar_return", "/test_nodos"]
    }
