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
            casa = planet.get("house", 1)
            return {
                "grado": round(planet.get("position", 0), 2),
                "signo": planet.get("sign", ""),
                "casa": casa,
                "retrogrado": planet.get("retrograde", False)
            }
        else:
            # Formato objeto
            try:
                casa = getattr(planet, "house", 1)
                return {
                    "grado": round(getattr(planet, "position", 0), 2),
                    "signo": getattr(planet, "sign", ""),
                    "casa": casa,
                    "retrogrado": getattr(planet, "retrograde", False)
                }
            except Exception:
                return None

    except Exception as e:
        print(f"Error get_planet_data {planet_name}: {e}")
        return None


def grado_absoluto_desde_signo(grado: float, signo: str) -> float:
    """Convierte grado dentro del signo a grado absoluto (0-360)"""
    signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
              "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    if signo not in signos:
        return grado

    signo_index = signos.index(signo)
    return signo_index * 30 + grado


# ✅ CORREGIDO: lectura de cúspides compatible con Kerykeion 5.x
def calcular_casa_en_carta_natal(grado_absoluto: float, subject_natal: AstrologicalSubject) -> int:
    """
    Calcula en qué casa cae un grado absoluto (0-360) usando las cúspides del subject_natal.

    Compatible con Kerykeion 5.x (first_house..twelfth_house) y variantes.
    """
    try:
        # Orden de cúspides en Kerykeion 5.x
        house_attrs_v5 = [
            "first_house", "second_house", "third_house", "fourth_house",
            "fifth_house", "sixth_house", "seventh_house", "eighth_house",
            "ninth_house", "tenth_house", "eleventh_house", "twelfth_house"
        ]
        # Fallback por si existieran house1..house12
        house_attrs_num = [f"house{i}" for i in range(1, 13)]

        def _extract_pos_sign(house_obj):
            if house_obj is None:
                return None, None
            if isinstance(house_obj, dict):
                return house_obj.get("position", 0), house_obj.get("sign", "")
            return getattr(house_obj, "position", 0), getattr(house_obj, "sign", "")

        casas_abs = []

        # A) first_house..twelfth_house
        for attr in house_attrs_v5:
            if hasattr(subject_natal, attr):
                g, s = _extract_pos_sign(getattr(subject_natal, attr))
                if s:
                    casas_abs.append(grado_absoluto_desde_signo(g, s))

        # B) house1..house12
        if len(casas_abs) != 12:
            casas_abs = []
            for attr in house_attrs_num:
                if hasattr(subject_natal, attr):
                    g, s = _extract_pos_sign(getattr(subject_natal, attr))
                    if s:
                        casas_abs.append(grado_absoluto_desde_signo(g, s))

        # C) subject_natal.houses / houses_list (si existiera)
        if len(casas_abs) != 12:
            casas_abs = []
            if hasattr(subject_natal, "houses") and subject_natal.houses:
                hs = subject_natal.houses
                if isinstance(hs, dict):
                    try:
                        hs = [hs[k] for k in sorted(hs.keys())]
                    except Exception:
                        hs = list(hs.values())
                for h in hs[:12]:
                    g, s = _extract_pos_sign(h)
                    if s:
                        casas_abs.append(grado_absoluto_desde_signo(g, s))

            if len(casas_abs) != 12 and hasattr(subject_natal, "houses_list") and subject_natal.houses_list:
                for h in subject_natal.houses_list[:12]:
                    g, s = _extract_pos_sign(h)
                    if s:
                        casas_abs.append(grado_absoluto_desde_signo(g, s))

        if len(casas_abs) != 12:
            print(f"DEBUG: Solo {len(casas_abs)} casas encontradas (esperadas 12). Devuelvo casa 1.")
            return 1

        grado = grado_absoluto % 360.0

        for i in range(12):
            inicio = casas_abs[i]
            fin = casas_abs[(i + 1) % 12]

            g = grado
            if fin < inicio:
                fin += 360.0
                if g < inicio:
                    g += 360.0

            if inicio <= g < fin:
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

        signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                  "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

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
        return get_planet_data(subject, "true_node")


def formatear_posiciones(subject: AstrologicalSubject, reference_subject: Optional[AstrologicalSubject] = None):
    """
    Extrae posiciones planetarias - Compatible con Kerykeion 5.x

    Args:
        subject: Carta a formatear
        reference_subject: Si se proporciona, las casas se calculan con respecto a esta carta
                          (útil para tránsitos en casas natales)
    """
    planetas = {}

    # Si reference_subject está presente, recalculamos casas en casas natales (para tránsitos)

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
                grado_abs = grado_absoluto_desde_signo(data["grado"], data["signo"])
                casa_natal = calcular_casa_en_carta_natal(grado_abs, reference_subject)
                data["casa"] = casa_natal

            planetas[esp] = data

    # ✅ CORREGIDO: Nodos lunares - calcular casa SIEMPRE
    nodo_norte_data = get_mean_node(subject)
    if nodo_norte_data:
        # Calcular casa SIEMPRE: en natal con la propia carta; en tránsitos con reference_subject
        ref = reference_subject if reference_subject else subject
        grado_abs = grado_absoluto_desde_signo(nodo_norte_data["grado"], nodo_norte_data["signo"])
        nodo_norte_data["casa"] = calcular_casa_en_carta_natal(grado_abs, ref)

        planetas["nodo_norte"] = nodo_norte_data

        # Nodo Sur (opuesto al Norte)
        nodo_sur_grado = nodo_norte_data["grado"]
        nodo_sur_signo_idx = (["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                               "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"].index(nodo_norte_data["signo"]) + 6) % 12
        nodo_sur_signo = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                          "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"][nodo_sur_signo_idx]

        nodo_sur_data = {
            "grado": nodo_sur_grado,
            "signo": nodo_sur_signo,
            "retrogrado": True
        }

        # Calcular casa SIEMPRE: en natal con la propia carta; en tránsitos con reference_subject
        ref = reference_subject if reference_subject else subject
        grado_abs = grado_absoluto_desde_signo(nodo_sur_data["grado"], nodo_sur_data["signo"])
        nodo_sur_data["casa"] = calcular_casa_en_carta_natal(grado_abs, ref)

        planetas["nodo_sur"] = nodo_sur_data

    # Puntos especiales
    puntos = {}

    # ASC
    asc_data = get_planet_data(subject, "first_house")
    if asc_data:
        puntos["asc"] = {
            "grado": asc_data["grado"],
            "signo": asc_data["signo"]
        }

    # MC
    mc_data = get_planet_data(subject, "tenth_house")
    if mc_data:
        puntos["mc"] = {
            "grado": mc_data["grado"],
            "signo": mc_data["signo"]
        }

    return {"planetas": planetas, "puntos": puntos}


# ENDPOINTS
@app.get("/")
def root():
    return {"ok": True, "message": "SAVP v3.5 API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


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


def calcular_momento_retorno_solar(fecha_natal_dt, hora_natal, año_revolucion, lat, lon, timezone):
    """
    Calcula el momento exacto cuando el Sol vuelve a su posición natal

    Returns:
        tuple: (año, mes, dia, hora, minuto) del retorno exacto
    """
    from datetime import timedelta

    # Obtener posición natal del Sol
    hora_parts = hora_natal.split(":")
    natal_subject = AstrologicalSubject(
        name="Natal",
        year=fecha_natal_dt.year,
        month=fecha_natal_dt.month,
        day=fecha_natal_dt.day,
        hour=int(hora_parts[0]),
        minute=int(hora_parts[1]),
        lat=lat,
        lng=lon,
        tz_str=timezone,
        city="",
        nation=""
    )

    sol_natal_pos = get_planet_data(natal_subject, "sun")
    if not sol_natal_pos:
        raise ValueError("No se pudo obtener la posición natal del Sol")

    sol_natal_grado = grado_absoluto_desde_signo(sol_natal_pos["grado"], sol_natal_pos["signo"])

    # Comenzar búsqueda alrededor del cumpleaños (aproximación)
    fecha_inicio = datetime(año_revolucion, fecha_natal_dt.month, fecha_natal_dt.day, 0, 0)
    mejor_dt = None
    mejor_diff = 999999

    # Buscar minuto a minuto en un rango de +/- 24h (2880 minutos)
    for offset_min in range(-1440, 1441):
        dt = fecha_inicio + timedelta(minutes=offset_min)

        subject_temp = AstrologicalSubject(
            name="Temp",
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            lat=lat,
            lng=lon,
            tz_str=timezone,
            city="",
            nation=""
        )

        sol_temp = get_planet_data(subject_temp, "sun")
        if not sol_temp:
            continue

        sol_temp_grado = grado_absoluto_desde_signo(sol_temp["grado"], sol_temp["signo"])

        # Diferencia circular
        diff = abs(sol_temp_grado - sol_natal_grado)
        diff = min(diff, 360 - diff)

        if diff < mejor_diff:
            mejor_diff = diff
            mejor_dt = dt

    if not mejor_dt:
        raise ValueError("No se pudo calcular el retorno solar")

    return mejor_dt.year, mejor_dt.month, mejor_dt.day, mejor_dt.hour, mejor_dt.minute


@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    try:
        lat_natal, lon_natal = (request.lat_natal, request.lon_natal) if request.lat_natal and request.lon_natal else geocode_ciudad(request.ciudad_natal, request.pais_natal)

        fecha_natal_dt = datetime.strptime(request.fecha_natal, "%Y-%m-%d")

        # Calcular momento exacto del retorno solar
        y, m, d, h, mi = calcular_momento_retorno_solar(
            fecha_natal_dt=fecha_natal_dt,
            hora_natal=request.hora_natal,
            año_revolucion=request.año_revolucion,
            lat=lat_natal,
            lon=lon_natal,
            timezone=request.timezone_natal
        )

        # Construir carta de revolución solar
        sr = AstrologicalSubject(
            name=f"RS {request.año_revolucion}",
            year=y, month=m, day=d, hour=h, minute=mi,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        # Carta natal (para devolver también)
        hora_parts = request.hora_natal.split(":")
        natal = AstrologicalSubject(
            name=request.nombre,
            year=fecha_natal_dt.year,
            month=fecha_natal_dt.month,
            day=fecha_natal_dt.day,
            hour=int(hora_parts[0]),
            minute=int(hora_parts[1]),
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_natal,
            lng=lon_natal,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system
        )

        return {
            "success": True,
            "momento_retorno": f"{y:04d}-{m:02d}-{d:02d} {h:02d}:{mi:02d}",
            "natal": formatear_posiciones(natal),
            "revolucion_solar": formatear_posiciones(sr)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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

        mean_node_calc = get_mean_node(subject)

        posiciones = formatear_posiciones(subject)

        return {
            "mean_node_calculated": mean_node_calc,
            "posiciones_nodos": {
                "nodo_norte": posiciones["planetas"].get("nodo_norte"),
                "nodo_sur": posiciones["planetas"].get("nodo_sur")
            },
            "puntos": posiciones.get("puntos")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
