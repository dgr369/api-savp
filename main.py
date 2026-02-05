"""
API AstrolÃ³gica para SAVP v3.6
VersiÃ³n ACTUALIZADA - Compatible con Kerykeion 5.7.0

âœ… Nodos: mean node (Meeus) + casas calculadas correctamente
âœ… Casas: normalizadas SIEMPRE a enteros 1..12 (aunque Kerykeion devuelva "Third_House")
âœ… Geocoding: timeout mayor + cache simple para evitar timeouts en Render
âœ… RevoluciÃ³n Solar: AHORA calcula el instante exacto del retorno solar (aprox. a segundos)
âœ… SAVP v3.6: AnÃ¡lisis completo con dignidades, genios, ponderaciÃ³n 2 capas, dispositores y pilares
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from kerykeion import AstrologicalSubject
from typing import Optional, Any, Tuple

import pytz

# Swiss Ephemeris (viene por dependencia de kerykeion: pyswisseph)
# Si por cualquier motivo no estÃ¡, la RS harÃ¡ fallback a aproximaciÃ³n.
try:
    import swisseph as swe
except Exception:  # pragma: no cover
    swe = None

# ============================================================================
# SAVP v3.6 Integration
# ============================================================================
try:
    from savp_v36_router import router as savp_v36_router
    SAVP_V36_ENABLED = True
    print("âœ… SAVP v3.6 router cargado correctamente")
except ImportError as e:
    SAVP_V36_ENABLED = False
    print(f"âš ï¸  SAVP v3.6 no disponible: {e}")
    print("    La API seguirÃ¡ funcionando en modo v3.5 (solo astronomÃ­a)")
# ============================================================================


app = FastAPI(
    title=f"API AstrolÃ³gica SAVP {'v3.6' if SAVP_V36_ENABLED else 'v3.5'}",
    description="CÃ¡lculos astrolÃ³gicos para el Sistema Ãrbol de la Vida Personal",
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
# Incluir router SAVP v3.6 si estÃ¡ disponible
# ============================================================================
if SAVP_V36_ENABLED:
    app.include_router(savp_v36_router)
    print("âœ… Router SAVP v3.6 integrado en /savp/v36/*")
# ============================================================================

# Cache simple en memoria para geocode (reduce llamadas a Nominatim)
GEOCODE_CACHE: dict[Tuple[str, str], Tuple[float, float]] = {}

# NormalizaciÃ³n de casas (Kerykeion a veces devuelve "Third_House", etc.)
HOUSE_NAME_TO_NUM = {
    "FIRST_HOUSE": 1,
    "SECOND_HOUSE": 2,
    "THIRD_HOUSE": 3,
    "FOURTH_HOUSE": 4,
    "FIFTH_HOUSE": 5,
    "SIXTH_HOUSE": 6,
    "SEVENTH_HOUSE": 7,
    "EIGHTH_HOUSE": 8,
    "NINTH_HOUSE": 9,
    "TENTH_HOUSE": 10,
    "ELEVENTH_HOUSE": 11,
    "TWELFTH_HOUSE": 12,
}


def normalize_house(house_value: Any) -> int:
    """
    Convierte el valor 'house' a int 1..12 (VERSIÓN ROBUSTA v3.6.1).
    
    Compatible con TODAS las formas en que Kerykeion 5.x puede devolver casas:
      - int directo: 5
      - float: 5.0
      - string: "5", "Fifth_House", "FIFTH_HOUSE", "fifth_house"
      - objeto Kerykeion con .name o .__str__()
      - None → 1
    """
    import re
    
    # Caso 1: None
    if house_value is None:
        return 1
    
    # Caso 2: Ya es int
    if isinstance(house_value, int):
        return house_value if 1 <= house_value <= 12 else 1
    
    # Caso 3: Es float
    if isinstance(house_value, float):
        iv = int(house_value)
        return iv if 1 <= iv <= 12 else 1
    
    # Caso 4: Es objeto (Kerykeion puede devolver objetos)
    if not isinstance(house_value, str):
        # Intentar .name
        if hasattr(house_value, 'name'):
            house_value = str(getattr(house_value, 'name', ''))
        # Intentar .value
        elif hasattr(house_value, 'value'):
            val = getattr(house_value, 'value', None)
            if isinstance(val, int):
                return val if 1 <= val <= 12 else 1
            house_value = str(val)
        else:
            house_value = str(house_value)
    
    # Caso 5: Es string
    if isinstance(house_value, str):
        house_str = house_value.strip()
        
        # Extraer número si existe
        match = re.search(r'\b(\d{1,2})\b', house_str)
        if match:
            num = int(match.group(1))
            if 1 <= num <= 12:
                return num
        
        # Buscar en diccionario
        key = house_str.upper().replace(' ', '_').replace('-', '_')
        
        HOUSE_MAP = {
            "FIRST_HOUSE": 1, "SECOND_HOUSE": 2, "THIRD_HOUSE": 3,
            "FOURTH_HOUSE": 4, "FIFTH_HOUSE": 5, "SIXTH_HOUSE": 6,
            "SEVENTH_HOUSE": 7, "EIGHTH_HOUSE": 8, "NINTH_HOUSE": 9,
            "TENTH_HOUSE": 10, "ELEVENTH_HOUSE": 11, "TWELFTH_HOUSE": 12,
            "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
            "FIFTH": 5, "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8,
            "NINTH": 9, "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12,
            "1ST_HOUSE": 1, "2ND_HOUSE": 2, "3RD_HOUSE": 3,
            "4TH_HOUSE": 4, "5TH_HOUSE": 5, "6TH_HOUSE": 6,
            "7TH_HOUSE": 7, "8TH_HOUSE": 8, "9TH_HOUSE": 9,
            "10TH_HOUSE": 10, "11TH_HOUSE": 11, "12TH_HOUSE": 12,
            "HOUSE_1": 1, "HOUSE_2": 2, "HOUSE_3": 3,
            "HOUSE_4": 4, "HOUSE_5": 5, "HOUSE_6": 6,
            "HOUSE_7": 7, "HOUSE_8": 8, "HOUSE_9": 9,
            "HOUSE_10": 10, "HOUSE_11": 11, "HOUSE_12": 12,
            "HOUSE1": 1, "HOUSE2": 2, "HOUSE3": 3,
            "HOUSE4": 4, "HOUSE5": 5, "HOUSE6": 6,
            "HOUSE7": 7, "HOUSE8": 8, "HOUSE9": 9,
            "HOUSE10": 10, "HOUSE11": 11, "HOUSE12": 12,
        }
        
        result = HOUSE_MAP.get(key)
        if result:
            return result
        
        # Búsqueda parcial
        for house_name, num in HOUSE_MAP.items():
            if house_name in key:
                return num
    
    # Default
    print(f"⚠️  normalize_house: '{house_value}' → casa 1")
    return 1


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
    aÃ±o_revolucion: int
    house_system: Optional[str] = "P"


# =========================
# UTILIDADES
# =========================
def parse_fecha_hora(fecha_str: str, hora_str: str) -> Tuple[int, int, int, int, int, int]:
    """Parsea fecha y hora en formatos flexibles. Soporta HH:MM o HH:MM:SS."""
    try:
        # Formato esperado: YYYY-MM-DD o DD/MM/YYYY
        if "/" in fecha_str:
            parts = fecha_str.split("/")
            fecha_str = f"{parts[2]}-{parts[1]}-{parts[0]}"

        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")

        hora_parts = hora_str.split(":")
        hour = int(hora_parts[0])
        minute = int(hora_parts[1]) if len(hora_parts) > 1 else 0
        second = int(hora_parts[2]) if len(hora_parts) > 2 else 0

        return fecha.year, fecha.month, fecha.day, hour, minute, second

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parseando fecha/hora: {str(e)}")


def geocode_ciudad(ciudad: str, pais: str) -> Tuple[float, float]:
    """Geocodifica ciudad usando geopy (con cache y timeout apto para Render)."""
    try:
        key = (ciudad.strip().lower(), pais.strip().lower())
        if key in GEOCODE_CACHE:
            return GEOCODE_CACHE[key]

        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="savp_astrology_api", timeout=10)
        location = geolocator.geocode(f"{ciudad}, {pais}", exactly_one=True)

        if not location:
            raise HTTPException(status_code=404, detail=f"No se encontrÃ³ la ciudad: {ciudad}, {pais}")

        lat, lon = location.latitude, location.longitude
        GEOCODE_CACHE[key] = (lat, lon)
        return lat, lon

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en geocodificaciÃ³n: {str(e)}")


def get_planet_data(subject: AstrologicalSubject, planet_name: str):
    """
    Extrae datos de un planeta/punto en Kerykeion 5.x y normaliza 'casa' a int.
    VERSIÓN ROBUSTA v3.6.1 con manejo defensivo de .house
    """
    try:
        if not hasattr(subject, planet_name):
            return None

        planet = getattr(subject, planet_name)

        if isinstance(planet, dict):
            casa_raw = planet.get("house", 1)
            return {
                "grado": round(float(planet.get("position", 0)), 2),
                "signo": planet.get("sign", ""),
                "casa": normalize_house(casa_raw),
                "retrogrado": bool(planet.get("retrograde", False)),
            }

        # Extraer casa de forma defensiva
        casa_raw = None
        if hasattr(planet, "house"):
            casa_raw = getattr(planet, "house", None)
        
        if casa_raw is None:
            casa_raw = 1
        
        return {
            "grado": round(float(getattr(planet, "position", 0)), 2),
            "signo": getattr(planet, "sign", ""),
            "casa": normalize_house(casa_raw),
            "retrogrado": bool(getattr(planet, "retrograde", False)),
        }

    except Exception as e:
        print(f"❌ Error get_planet_data({planet_name}): {e}")
        return None


def grado_absoluto_desde_signo(grado: float, signo: str) -> float:
    """Convierte grado dentro del signo a grado absoluto (0-360)."""
    signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
    if signo not in signos:
        return float(grado)
    signo_index = signos.index(signo)
    return signo_index * 30 + float(grado)


def calcular_casa_en_carta_natal(grado_absoluto: float, subject_natal: AstrologicalSubject) -> int:
    """
    Calcula en quÃ© casa cae un grado absoluto (0-360) usando las cÃºspides del subject_natal.
    Compatible con Kerykeion 5.x (first_house..twelfth_house) y variantes.
    """
    try:
        house_attrs_v5 = [
            "first_house", "second_house", "third_house", "fourth_house",
            "fifth_house", "sixth_house", "seventh_house", "eighth_house",
            "ninth_house", "tenth_house", "eleventh_house", "twelfth_house",
        ]
        house_attrs_num = [f"house{i}" for i in range(1, 13)]

        def _extract_pos_sign(house_obj):
            if house_obj is None:
                return None, None
            if isinstance(house_obj, dict):
                return house_obj.get("position", 0), house_obj.get("sign", "")
            return getattr(house_obj, "position", 0), getattr(house_obj, "sign", "")

        casas_abs: list[float] = []

        # A) Kerykeion 5.x
        for attr in house_attrs_v5:
            if hasattr(subject_natal, attr):
                g, s = _extract_pos_sign(getattr(subject_natal, attr))
                if s:
                    casas_abs.append(grado_absoluto_desde_signo(g, s))

        # B) Fallback house1..house12
        if len(casas_abs) != 12:
            casas_abs = []
            for attr in house_attrs_num:
                if hasattr(subject_natal, attr):
                    g, s = _extract_pos_sign(getattr(subject_natal, attr))
                    if s:
                        casas_abs.append(grado_absoluto_desde_signo(g, s))

        # C) Fallback houses/houses_list
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

            # Manejo cruce 360Â°
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


def get_mean_node(subject: AstrologicalSubject):
    """
    Calcula el Nodo Norte Medio usando fÃ³rmula astronÃ³mica (Meeus).
    """
    try:
        from datetime import datetime as dt

        J2000 = 2451545.0

        tz = pytz.timezone(subject.tz_str)
        dt_local = tz.localize(dt(subject.year, subject.month, subject.day, subject.hour, subject.minute))
        dt_utc = dt_local.astimezone(pytz.UTC)

        y = dt_utc.year
        m = dt_utc.month
        d = dt_utc.day
        h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0

        if m <= 2:
            y -= 1
            m += 12

        A = int(y / 100)
        B = 2 - A + int(A / 4)

        jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5
        jd += h / 24.0

        T = (jd - J2000) / 36525.0

        omega = 125.04452 - 1934.136261 * T + 0.0020708 * T**2 + T**3 / 450000.0
        longitude = omega % 360.0

        sign_num = int(longitude / 30)
        degree = longitude % 30

        signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        return {"grado": round(degree, 2), "signo": signos[sign_num], "retrogrado": True}

    except Exception as e:
        print(f"ERROR calculando mean_node: {e}")
        print("FALLBACK: usando true_node")
        return get_planet_data(subject, "true_node")


def formatear_posiciones(subject: AstrologicalSubject, reference_subject: Optional[AstrologicalSubject] = None):
    """Extrae posiciones planetarias y puntos, con nodos y casas consistentes."""
    planetas: dict[str, Any] = {}

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
        "pluton": "pluto",
    }

    for esp, eng in planet_map.items():
        data = get_planet_data(subject, eng)
        if data:
            # Si estamos calculando trÃ¡nsitos en casas natales:
            if reference_subject:
                grado_abs = grado_absoluto_desde_signo(data["grado"], data["signo"])
                data["casa"] = calcular_casa_en_carta_natal(grado_abs, reference_subject)

            data["casa"] = normalize_house(data.get("casa"))
            planetas[esp] = data

    # Nodos: mean node + casa SIEMPRE calculada
    nodo_norte_data = get_mean_node(subject)
    if nodo_norte_data:
        ref = reference_subject if reference_subject else subject
        grado_abs = grado_absoluto_desde_signo(nodo_norte_data["grado"], nodo_norte_data["signo"])
        nodo_norte_data["casa"] = calcular_casa_en_carta_natal(grado_abs, ref)
        planetas["nodo_norte"] = nodo_norte_data

        # Nodo Sur (opuesto)
        signos = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
        nodo_sur_signo_idx = (signos.index(nodo_norte_data["signo"]) + 6) % 12
        nodo_sur_data = {"grado": nodo_norte_data["grado"], "signo": signos[nodo_sur_signo_idx], "retrogrado": True}
        grado_abs = grado_absoluto_desde_signo(nodo_sur_data["grado"], nodo_sur_data["signo"])
        nodo_sur_data["casa"] = calcular_casa_en_carta_natal(grado_abs, ref)
        planetas["nodo_sur"] = nodo_sur_data

    puntos: dict[str, Any] = {}

    # En Kerykeion, la cÃºspide de Casa 1 equivale al ASC y la Casa 10 al MC.
    asc_data = get_planet_data(subject, "first_house")
    if asc_data:
        puntos["asc"] = {"grado": asc_data["grado"], "signo": asc_data["signo"]}

    mc_data = get_planet_data(subject, "tenth_house")
    if mc_data:
        puntos["mc"] = {"grado": mc_data["grado"], "signo": mc_data["signo"]}

    return {"planetas": planetas, "puntos": puntos}


# =========================
# REVOLUCIÃ“N SOLAR EXACTA (Swiss Ephemeris)
# =========================
def _to_jd_ut(dt_utc: datetime) -> float:
    """UTC aware datetime -> Julian Day UT"""
    if swe is None:
        raise RuntimeError("Swiss Ephemeris (swisseph) no disponible")
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return float(swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour))


def _sun_lon_ut(jd_ut: float) -> float:
    """Longitud eclÃ­ptica geocÃ©ntrica tropical del Sol en JD UT"""
    if swe is None:
        raise RuntimeError("Swiss Ephemeris (swisseph) no disponible")
    lon = float(swe.calc_ut(jd_ut, swe.SUN)[0][0])
    return lon % 360.0


def _wrap_diff_deg(lon: float, target: float) -> float:
    """Diferencia angular lon-target en rango [-180, 180]"""
    return (lon - target + 540.0) % 360.0 - 180.0


def _jd_to_datetime_utc(jd_ut: float) -> datetime:
    """JD UT -> datetime UTC aware"""
    if swe is None:
        raise RuntimeError("Swiss Ephemeris (swisseph) no disponible")
    y, m, d, hour_decimal = swe.revjul(jd_ut, swe.GREG_CAL)
    hh = int(hour_decimal)
    mm = int((hour_decimal - hh) * 60)
    ss = int(round((((hour_decimal - hh) * 60) - mm) * 60))
    # normalizar
    if ss == 60:
        ss = 0
        mm += 1
    if mm == 60:
        mm = 0
        hh += 1
    return datetime(int(y), int(m), int(d), int(hh), int(mm), int(ss), tzinfo=pytz.UTC)


def find_solar_return_dt_utc(
    natal_dt_local_naive: datetime,
    tz_str: str,
    year: int,
) -> datetime:
    """
    Encuentra el instante UTC del retorno solar exacto:
    lon_sol(t) == lon_sol(natal)

    Nota: tolerancia muy fina (bisecciÃ³n 60 iteraciones).
    """
    if swe is None:
        raise RuntimeError("Swiss Ephemeris (swisseph) no disponible")

    tz = pytz.timezone(tz_str)
    natal_local = tz.localize(natal_dt_local_naive)
    natal_utc = natal_local.astimezone(pytz.UTC)

    # Longitud exacta del Sol natal
    jd_natal = _to_jd_ut(natal_utc)
    target_lon = _sun_lon_ut(jd_natal)

    # Ventana de bÃºsqueda: +/- 5 dÃ­as alrededor del "cumple" del aÃ±o objetivo
    approx_local = tz.localize(datetime(year, natal_local.month, natal_local.day, 12, 0, 0))
    approx_utc = approx_local.astimezone(pytz.UTC)
    jd_center = _to_jd_ut(approx_utc)

    jd0 = jd_center - 5.0
    jd1 = jd_center + 5.0

    def diff(jd: float) -> float:
        return _wrap_diff_deg(_sun_lon_ut(jd), target_lon)

    a, b = jd0, jd1
    fa, fb = diff(a), diff(b)

    # Asegurar acotaciÃ³n: buscamos un cambio de signo
    # (si no, recorremos por pasos para encontrar bracket)
    if fa * fb > 0:
        step = 0.25  # 6 horas
        prev_jd = a
        prev_f = fa
        found = False
        cur = a + step
        while cur <= b:
            cur_f = diff(cur)
            if prev_f * cur_f <= 0:
                a, b = prev_jd, cur
                fa, fb = prev_f, cur_f
                found = True
                break
            prev_jd, prev_f = cur, cur_f
            cur += step
        if not found:
            raise RuntimeError("No se pudo acotar el retorno solar (ventana insuficiente).")

    # BisecciÃ³n
    for _ in range(60):
        mid = (a + b) / 2.0
        fm = diff(mid)
        if fa * fm <= 0:
            b, fb = mid, fm
        else:
            a, fa = mid, fm

    jd_return = (a + b) / 2.0
    return _jd_to_datetime_utc(jd_return)


# =========================
# ENDPOINTS
# =========================
@app.get("/")
def root():
    """Endpoint raÃ­z con informaciÃ³n de la API."""
    endpoints = [
        "/natal",
        "/transits",
        "/solar_return",
        "/test_nodos",
        "/health"
    ]
    
    if SAVP_V36_ENABLED:
        endpoints.extend([
            "/savp/v36 (info SAVP v3.6)",
            "/savp/v36/natal (anÃ¡lisis completo)",
            "/savp/v36/test (Frater D.)",
            "/savp/v36/health"
        ])
    
    return {
        "ok": True,
        "message": f"SAVP API {'v3.6' if SAVP_V36_ENABLED else 'v3.5'} running",
        "version": "3.6.0" if SAVP_V36_ENABLED else "3.5.0",
        "savp_v36_enabled": SAVP_V36_ENABLED,
        "endpoints": endpoints,
        "docs": "/docs (Swagger UI automÃ¡tico)"
    }


@app.get("/health")
def health():
    """Health check bÃ¡sico."""
    return {
        "status": "ok",
        "version": "3.6.0" if SAVP_V36_ENABLED else "3.5.0",
        "savp_v36": SAVP_V36_ENABLED
    }


@app.post("/natal")
def calcular_natal(request: NatalRequest):
    """Calcula carta natal (solo astronomÃ­a, sin anÃ¡lisis SAVP)."""
    try:
        # Coordenadas
        if request.lat is not None and request.lon is not None:
            lat, lon = request.lat, request.lon
        else:
            lat, lon = geocode_ciudad(request.ciudad, request.pais)

        # Fecha/hora
        year, month, day, hour, minute, _second = parse_fecha_hora(request.fecha, request.hora)

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
            houses_system_identifier=request.house_system,
        )

        carta = formatear_posiciones(subject)

        return {
            "success": True,
            "datos": {
                "nombre": request.nombre,
                "fecha": request.fecha,
                "hora": request.hora,
                "ciudad": request.ciudad,
                "coordenadas": {"lat": lat, "lon": lon},
            },
            "carta": carta,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/transits")
def calcular_transitos(request: TransitsRequest):
    """Calcula trÃ¡nsitos sobre carta natal."""
    try:
        # Natal: coords
        if request.lat_natal is not None and request.lon_natal is not None:
            lat_n, lon_n = request.lat_natal, request.lon_natal
        else:
            lat_n, lon_n = geocode_ciudad(request.ciudad_natal, request.pais_natal)

        # Natal: fecha/hora
        y_n, m_n, d_n, h_n, mi_n, _s_n = parse_fecha_hora(request.fecha_natal, request.hora_natal)

        natal_subject = AstrologicalSubject(
            name=request.nombre,
            year=y_n,
            month=m_n,
            day=d_n,
            hour=h_n,
            minute=mi_n,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system,
        )

        # TrÃ¡nsito: fecha/hora (default "ahora" en timezone_natal)
        if request.fecha_transito and request.hora_transito:
            y_t, m_t, d_t, h_t, mi_t, _s_t = parse_fecha_hora(request.fecha_transito, request.hora_transito)
        else:
            tz = pytz.timezone(request.timezone_natal or "Europe/Madrid")
            now = datetime.now(tz)
            y_t, m_t, d_t, h_t, mi_t = now.year, now.month, now.day, now.hour, now.minute

        transit_subject = AstrologicalSubject(
            name="Transitos",
            year=y_t,
            month=m_t,
            day=d_t,
            hour=h_t,
            minute=mi_t,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system,
        )

        natal = formatear_posiciones(natal_subject)
        if request.use_natal_houses:
            transitos = formatear_posiciones(transit_subject, reference_subject=natal_subject)
        else:
            transitos = formatear_posiciones(transit_subject)

        return {"success": True, "natal": natal, "transitos": transitos}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/solar_return")
def calcular_revolucion_solar(request: SolarReturnRequest):
    """
    RevoluciÃ³n Solar REAL (retorno exacto del Sol) si swisseph estÃ¡ disponible.
    Devuelve ademÃ¡s debug con momento exacto del retorno.

    Si swisseph no estÃ¡ disponible, hace fallback a la aproximaciÃ³n (mismo mes/dÃ­a/hora natal).
    """
    try:
        # Coordenadas
        if request.lat_natal is not None and request.lon_natal is not None:
            lat_n, lon_n = request.lat_natal, request.lon_natal
        else:
            lat_n, lon_n = geocode_ciudad(request.ciudad_natal, request.pais_natal)

        # Natal: fecha/hora
        y_n, m_n, d_n, h_n, mi_n, s_n = parse_fecha_hora(request.fecha_natal, request.hora_natal)

        natal_subject = AstrologicalSubject(
            name=request.nombre,
            year=y_n,
            month=m_n,
            day=d_n,
            hour=h_n,
            minute=mi_n,
            city=request.ciudad_natal,
            nation=request.pais_natal,
            lat=lat_n,
            lng=lon_n,
            tz_str=request.timezone_natal,
            houses_system_identifier=request.house_system,
        )

        debug = {"modo": "exacto" if swe is not None else "aproximacion"}

        if swe is not None:
            # Hallar instante exacto del retorno solar (UTC)
            natal_dt_local_naive = datetime(y_n, m_n, d_n, h_n, mi_n, s_n)
            dt_return_utc = find_solar_return_dt_utc(natal_dt_local_naive, request.timezone_natal, request.aÃ±o_revolucion)

            tz = pytz.timezone(request.timezone_natal or "Europe/Madrid")
            dt_return_local = dt_return_utc.astimezone(tz)

            debug["momento_retorno_utc"] = dt_return_utc.isoformat()
            debug["momento_retorno_local"] = dt_return_local.isoformat()

            # Construir subject RS con minuto (Kerykeion no admite segundos)
            sr_subject = AstrologicalSubject(
                name=f"RS_{request.nombre}_{request.aÃ±o_revolucion}",
                year=dt_return_local.year,
                month=dt_return_local.month,
                day=dt_return_local.day,
                hour=dt_return_local.hour,
                minute=dt_return_local.minute,
                city=request.ciudad_natal,
                nation=request.pais_natal,
                lat=lat_n,
                lng=lon_n,
                tz_str=request.timezone_natal,
                houses_system_identifier=request.house_system,
            )

        else:
            # Fallback: aproximaciÃ³n (como antes)
            sr_subject = AstrologicalSubject(
                name=f"RS_{request.nombre}_{request.aÃ±o_revolucion}",
                year=request.aÃ±o_revolucion,
                month=m_n,
                day=d_n,
                hour=h_n,
                minute=mi_n,
                city=request.ciudad_natal,
                nation=request.pais_natal,
                lat=lat_n,
                lng=lon_n,
                tz_str=request.timezone_natal,
                houses_system_identifier=request.house_system,
            )

        return {
            "success": True,
            "natal": formatear_posiciones(natal_subject),
            "revolucion_solar": formatear_posiciones(sr_subject),
            "debug": debug,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/test_nodos")
def test_nodos():
    """Prueba rÃ¡pida para verificar nodos y casas."""
    try:
        subject = AstrologicalSubject(
            name="Test",
            year=1977,
            month=6,
            day=4,
            hour=9,
            minute=15,
            city="Zaragoza",
            nation="EspaÃ±a",
            lat=41.65,
            lng=-0.88,
            tz_str="Europe/Madrid",
        )
        posiciones = formatear_posiciones(subject)
        return {
            "mean_node_calculated": get_mean_node(subject),
            "nodo_norte": posiciones["planetas"].get("nodo_norte"),
            "nodo_sur": posiciones["planetas"].get("nodo_sur"),
            "puntos": posiciones.get("puntos"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
