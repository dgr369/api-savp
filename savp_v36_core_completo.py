"""
savp_v36_core.py COMPLETO
Módulo central SAVP v3.6 - Fase 2 Completa

Incluye:
- Dignidades esenciales
- Genios de los 72 (TABLA COMPLETA - 72 Genios con salmos y atributos)
- Ponderación 2 capas
- Cadena de dispositores como grafo
- Senderos 3 tipos (ocupación, aspectos, críticos)
- Cálculo automático de aspectos
- Ontología unificada

Requiere:
- genios_72_completos.py (tabla completa, fallback incluido)

Autor: Sistema SAVP
Fecha: Febrero 2025
Versión: 3.6 Completa
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import json

# Kerykeion es opcional para tests
try:
    from kerykeion import AstrologicalSubject
    KERYKEION_AVAILABLE = True
except ImportError:
    KERYKEION_AVAILABLE = False
    AstrologicalSubject = None


# ============================================================================
# TABLAS DE CORRESPONDENCIAS SAVP
# ============================================================================

# Planetas → Sephiroth
PLANETA_SEPHIRAH = {
    'Sol': 'Tiphareth',
    'Luna': 'Yesod',
    'Mercurio': 'Hod',
    'Venus': 'Netzach',
    'Marte': 'Geburah',
    'Jupiter': 'Chesed',
    'Saturno': 'Binah',
    'Urano': 'Chokmah',
    'Neptuno': 'Kether',
    'Pluton': 'Daath'
}

# Sephiroth → Pilares
SEPHIRAH_PILAR = {
    'Kether': 'central',
    'Chokmah': 'derecho',
    'Binah': 'izquierdo',
    'Chesed': 'derecho',
    'Geburah': 'izquierdo',
    'Tiphareth': 'central',
    'Netzach': 'derecho',
    'Hod': 'izquierdo',
    'Yesod': 'central',
    'Malkuth': 'central',
    'Daath': 'central'
}

# Dignidades esenciales
DIGNIDADES_CANONICAS = {
    'Sol': {'domicilio': ['Leo'], 'exaltacion': ['Aries'], 'exilio': ['Acuario'], 'caida': ['Libra']},
    'Luna': {'domicilio': ['Cancer'], 'exaltacion': ['Tauro'], 'exilio': ['Capricornio'], 'caida': ['Escorpio']},
    'Mercurio': {'domicilio': ['Geminis', 'Virgo'], 'exaltacion': ['Virgo'], 'exilio': ['Sagitario', 'Piscis'], 'caida': ['Piscis']},
    'Venus': {'domicilio': ['Tauro', 'Libra'], 'exaltacion': ['Piscis'], 'exilio': ['Aries', 'Escorpio'], 'caida': ['Virgo']},
    'Marte': {'domicilio': ['Aries', 'Escorpio'], 'exaltacion': ['Capricornio'], 'exilio': ['Libra', 'Tauro'], 'caida': ['Cancer']},
    'Jupiter': {'domicilio': ['Sagitario', 'Piscis'], 'exaltacion': ['Cancer'], 'exilio': ['Geminis', 'Virgo'], 'caida': ['Capricornio']},
    'Saturno': {'domicilio': ['Capricornio', 'Acuario'], 'exaltacion': ['Libra'], 'exilio': ['Cancer', 'Leo'], 'caida': ['Aries']},
    'Urano': {'domicilio': ['Acuario'], 'exaltacion': ['Escorpio'], 'exilio': ['Leo'], 'caida': ['Tauro']},
    'Neptuno': {'domicilio': ['Piscis'], 'exaltacion': ['Cancer'], 'exilio': ['Virgo'], 'caida': ['Capricornio']},
    'Pluton': {'domicilio': ['Escorpio'], 'exaltacion': ['Leo'], 'exilio': ['Tauro'], 'caida': ['Acuario']}
}

PESO_ESENCIAL = {
    'domicilio': 3.0,
    'exaltacion': 2.0,
    'peregrino': 1.0,
    'exilio': 0.5,
    'caida': 0.25
}

# Mapeo de nombres Kerykeion → SAVP (signos abreviados)
SIGNOS_KERYKEION_SAVP = {
    'Ari': 'Aries', 'Tau': 'Tauro', 'Gem': 'Geminis', 'Can': 'Cancer',
    'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Escorpio',
    'Sag': 'Sagitario', 'Cap': 'Capricornio', 'Aqu': 'Acuario', 'Pis': 'Piscis'
}

# Índices de signos para cálculos
SIGNOS_INDEX = {
    'Aries': 0, 'Tauro': 1, 'Geminis': 2, 'Cancer': 3,
    'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Escorpio': 7,
    'Sagitario': 8, 'Capricornio': 9, 'Acuario': 10, 'Piscis': 11
}

# 72 Genios - Tabla completa embebida
GENIOS_72 = {
    1: {'nombre': 'VEHU-IAH', 'salmo': 3, 'atributos': 'Voluntad Primordial, Impulso Divino'},
    2: {'nombre': 'YELI-EL', 'salmo': 22, 'atributos': 'Amor Divino, Kundalini'},
    3: {'nombre': 'SITA-EL', 'salmo': 91, 'atributos': 'Construcción bajo Fuego'},
    4: {'nombre': 'ELEMI-AH', 'salmo': 6, 'atributos': 'Viaje Interior, Peregrinación Espiritual'},
    5: {'nombre': 'MAHAS-IAH', 'salmo': 34, 'atributos': 'Paz en Guerra, Rector de las Cosas Físicas'},
    6: {'nombre': 'LELAH-EL', 'salmo': 9, 'atributos': 'Iluminación Súbita, Ciencia de lo Útil'},
    7: {'nombre': 'ACHA-IAH', 'salmo': 103, 'atributos': 'Paciencia Divina'},
    8: {'nombre': 'CAHETH-EL', 'salmo': 95, 'atributos': 'Prosperidad Santificada'},
    9: {'nombre': 'HAZI-EL', 'salmo': 25, 'atributos': 'Misericordia Universal, Compasión Tangible'},
    10: {'nombre': 'ALAD-IAH', 'salmo': 33, 'atributos': 'Gracia Perdonadora'},
    11: {'nombre': 'LAVI-AH', 'salmo': 18, 'atributos': 'Victoria Oculta, Revelaciones en Sueños'},
    12: {'nombre': 'HAHAU-IAH', 'salmo': 10, 'atributos': 'Refugio, Protección Divina'},
    13: {'nombre': 'YEZAL-EL', 'salmo': 98, 'atributos': 'Fidelidad Conyugal'},
    14: {'nombre': 'MEBAH-EL', 'salmo': 9, 'atributos': 'Verdad Liberadora'},
    15: {'nombre': 'LAUU-IAH', 'salmo': 8, 'atributos': 'Victoria, Celebridad, Talento Musical y Poético'},
    16: {'nombre': 'CALAH-IAH', 'salmo': 35, 'atributos': 'Justicia Expeditiva'},
    17: {'nombre': 'LEVU-IAH', 'salmo': 40, 'atributos': 'Expansión de la Inteligencia'},
    18: {'nombre': 'CALI-EL', 'salmo': 7, 'atributos': 'Socorro Inmediato'},
    19: {'nombre': 'LEVU-IAH', 'salmo': 40, 'atributos': 'Memoria Prodigiosa'},
    20: {'nombre': 'PAHAL-IAH', 'salmo': 120, 'atributos': 'Vocación, Redención'},
    21: {'nombre': 'NELA-IAH', 'salmo': 145, 'atributos': 'Estudio, Meditación Profunda'},
    22: {'nombre': 'YEYA-EL', 'salmo': 121, 'atributos': 'Fama, Diplomacia'},
    23: {'nombre': 'MELAH-EL', 'salmo': 121, 'atributos': 'Curación de Enfermos'},
    24: {'nombre': 'CHAHU-IAH', 'salmo': 33, 'atributos': 'Exilio Voluntario, Protección'},
    25: {'nombre': 'NETAH-IAH', 'salmo': 145, 'atributos': 'Elevación Espiritual'},
    26: {'nombre': 'HAAI-AH', 'salmo': 119, 'atributos': 'Victoria sobre Enemigos Ocultos'},
    27: {'nombre': 'YERAT-EL', 'salmo': 140, 'atributos': 'Difusión de Luces, Propagación del Conocimiento'},
    28: {'nombre': 'SEEHH-IAH', 'salmo': 71, 'atributos': 'Longevidad, Salud'},
    29: {'nombre': 'REYI-EL', 'salmo': 54, 'atributos': 'Liberación de Enemigos'},
    30: {'nombre': 'AUMA-EL', 'salmo': 113, 'atributos': 'Paciencia, Conversión'},
    31: {'nombre': 'LECA-EL', 'salmo': 131, 'atributos': 'Clarividencia, Ciencia'},
    32: {'nombre': 'VESHAR-IAH', 'salmo': 33, 'atributos': 'Clemencia, Justicia'},
    33: {'nombre': 'YEHU-IAH', 'salmo': 94, 'atributos': 'Conocimiento, Subordinación'},
    34: {'nombre': 'LEHAH-IAH', 'salmo': 131, 'atributos': 'Obediencia, Contención'},
    35: {'nombre': 'CAVAQ-IAH', 'salmo': 88, 'atributos': 'Testamentos, Reconciliación Familiar'},
    36: {'nombre': 'MENAD-EL', 'salmo': 26, 'atributos': 'Trabajo, Liberación de Opresión'},
    37: {'nombre': 'ANIE-EL', 'salmo': 80, 'atributos': 'Victoria, Rompimiento de Círculos Viciosos'},
    38: {'nombre': 'HAAMI-AH', 'salmo': 131, 'atributos': 'Ritos, Ceremonias Religiosas'},
    39: {'nombre': 'REHA-EL', 'salmo': 30, 'atributos': 'Salud, Longevidad Familiar'},
    40: {'nombre': 'YEYAZ-EL', 'salmo': 88, 'atributos': 'Gozo, Alegría, Consuelo'},
    41: {'nombre': 'HAHAH-EL', 'salmo': 120, 'atributos': 'Refugio, Protección'},
    42: {'nombre': 'MIKA-EL', 'salmo': 121, 'atributos': 'Casa de Dios, Arcángel Miguel'},
    43: {'nombre': 'VEVAL-IAH', 'salmo': 88, 'atributos': 'Destrucción de Enemigos, Liberación'},
    44: {'nombre': 'YELAH-IAH', 'salmo': 119, 'atributos': 'Talento Militar, Protección en Batalla'},
    45: {'nombre': 'SEALH-IAH', 'salmo': 94, 'atributos': 'Resurrección de Caídos'},
    46: {'nombre': 'ARI-EL', 'salmo': 145, 'atributos': 'Revelación de Tesoros'},
    47: {'nombre': 'ASAL-IAH', 'salmo': 105, 'atributos': 'Contemplación de lo Divino'},
    48: {'nombre': 'MIHAH-EL', 'salmo': 98, 'atributos': 'Fertilidad, Armonía Conyugal'},
    49: {'nombre': 'VEHU-EL', 'salmo': 145, 'atributos': 'Grandeza de Alma'},
    50: {'nombre': 'DANI-EL', 'salmo': 145, 'atributos': 'Elocuencia, Decisiones Justas'},
    51: {'nombre': 'HAHASH-IAH', 'salmo': 104, 'atributos': 'Medicina Universal, Alquimia Espiritual'},
    52: {'nombre': 'IMAMI-AH', 'salmo': 7, 'atributos': 'Destrucción de Enemigos'},
    53: {'nombre': 'NANA-EL', 'salmo': 113, 'atributos': 'Comunicación Espiritual'},
    54: {'nombre': 'NITHA-EL', 'salmo': 9, 'atributos': 'Vida Eterna en los Elegidos'},
    55: {'nombre': 'MEBAH-IAH', 'salmo': 102, 'atributos': 'Consolación Intelectual'},
    56: {'nombre': 'POI-EL', 'salmo': 145, 'atributos': 'Riqueza, Estimación'},
    57: {'nombre': 'NEMAMI-AH', 'salmo': 113, 'atributos': 'Prosperidad'},
    58: {'nombre': 'YEYAZ-EL', 'salmo': 88, 'atributos': 'Consuelo, Fidelidad Conyugal'},
    59: {'nombre': 'HARACH-EL', 'salmo': 113, 'atributos': 'Riqueza Intelectual'},
    60: {'nombre': 'MITSAR-EL', 'salmo': 145, 'atributos': 'Sanación de Enfermedades Mentales'},
    61: {'nombre': 'UMAB-EL', 'salmo': 113, 'atributos': 'Afinidades, Amistad'},
    62: {'nombre': 'YAHAH-EL', 'salmo': 119, 'atributos': 'Conocimiento Trascendente'},
    63: {'nombre': 'ANAU-EL', 'salmo': 3, 'atributos': 'Círculo de Sabios'},
    64: {'nombre': 'MECHI-EL', 'salmo': 33, 'atributos': 'Inspiración Literaria'},
    65: {'nombre': 'DAMA-IAH', 'salmo': 88, 'atributos': 'Fuente de Sabiduría'},
    66: {'nombre': 'MENA-EL', 'salmo': 26, 'atributos': 'Liberación de Cautivos'},
    67: {'nombre': 'AYAI-EL', 'salmo': 37, 'atributos': 'Transmutación'},
    68: {'nombre': 'HABUU-IAH', 'salmo': 106, 'atributos': 'Sanación, Fertilidad'},
    69: {'nombre': 'ROAH-EL', 'salmo': 16, 'atributos': 'Restitución de Objetos'},
    70: {'nombre': 'YABAM-IAH', 'salmo': 119, 'atributos': 'Génesis Alquímica'},
    71: {'nombre': 'HAYI-EL', 'salmo': 109, 'atributos': 'Protección Divina'},
    72: {'nombre': 'MUMA-IAH', 'salmo': 116, 'atributos': 'Fin y Principio, Renacimiento'}
}

# 22 Senderos del Árbol de la Vida
SENDEROS_ARBOL = {
    11: {'nombre': 'El Loco', 'arcano': 0, 'sephiroth': ('Kether', 'Chokmah'), 'elemento': 'Aire'},
    12: {'nombre': 'El Mago', 'arcano': 1, 'sephiroth': ('Kether', 'Binah'), 'elemento': 'Mercurio'},
    13: {'nombre': 'La Sacerdotisa', 'arcano': 2, 'sephiroth': ('Kether', 'Tiphareth'), 'elemento': 'Luna'},
    14: {'nombre': 'La Emperatriz', 'arcano': 3, 'sephiroth': ('Chokmah', 'Binah'), 'elemento': 'Venus'},
    15: {'nombre': 'El Emperador', 'arcano': 4, 'sephiroth': ('Chokmah', 'Tiphareth'), 'elemento': 'Aries'},
    16: {'nombre': 'El Hierofante', 'arcano': 5, 'sephiroth': ('Chokmah', 'Chesed'), 'elemento': 'Tauro'},
    17: {'nombre': 'Los Enamorados', 'arcano': 6, 'sephiroth': ('Binah', 'Tiphareth'), 'elemento': 'Géminis'},
    18: {'nombre': 'El Carro', 'arcano': 7, 'sephiroth': ('Binah', 'Geburah'), 'elemento': 'Cáncer'},
    19: {'nombre': 'La Fuerza', 'arcano': 8, 'sephiroth': ('Chesed', 'Geburah'), 'elemento': 'Leo'},
    20: {'nombre': 'El Ermitaño', 'arcano': 9, 'sephiroth': ('Chesed', 'Tiphareth'), 'elemento': 'Virgo'},
    21: {'nombre': 'La Rueda', 'arcano': 10, 'sephiroth': ('Chesed', 'Netzach'), 'elemento': 'Júpiter'},
    22: {'nombre': 'La Justicia', 'arcano': 11, 'sephiroth': ('Geburah', 'Tiphareth'), 'elemento': 'Libra'},
    23: {'nombre': 'El Colgado', 'arcano': 12, 'sephiroth': ('Geburah', 'Hod'), 'elemento': 'Agua'},
    24: {'nombre': 'La Muerte', 'arcano': 13, 'sephiroth': ('Tiphareth', 'Netzach'), 'elemento': 'Escorpio'},
    25: {'nombre': 'Templanza', 'arcano': 14, 'sephiroth': ('Tiphareth', 'Yesod'), 'elemento': 'Sagitario'},
    26: {'nombre': 'El Diablo', 'arcano': 15, 'sephiroth': ('Tiphareth', 'Hod'), 'elemento': 'Capricornio'},
    27: {'nombre': 'La Torre', 'arcano': 16, 'sephiroth': ('Netzach', 'Hod'), 'elemento': 'Marte'},
    28: {'nombre': 'La Estrella', 'arcano': 17, 'sephiroth': ('Netzach', 'Yesod'), 'elemento': 'Acuario'},
    29: {'nombre': 'La Luna', 'arcano': 18, 'sephiroth': ('Netzach', 'Malkuth'), 'elemento': 'Piscis'},
    30: {'nombre': 'El Sol', 'arcano': 19, 'sephiroth': ('Hod', 'Yesod'), 'elemento': 'Sol'},
    31: {'nombre': 'El Juicio', 'arcano': 20, 'sephiroth': ('Hod', 'Malkuth'), 'elemento': 'Fuego'},
    32: {'nombre': 'El Mundo', 'arcano': 21, 'sephiroth': ('Yesod', 'Malkuth'), 'elemento': 'Saturno'}
}

# Regencias (para dispositores)
REGENCIAS = {
    'Aries': 'Marte', 'Tauro': 'Venus', 'Geminis': 'Mercurio', 'Cancer': 'Luna',
    'Leo': 'Sol', 'Virgo': 'Mercurio', 'Libra': 'Venus', 'Escorpio': 'Pluton',
    'Sagitario': 'Jupiter', 'Capricornio': 'Saturno', 'Acuario': 'Urano', 'Piscis': 'Neptuno'
}


# ============================================================================
# ONTOLOGÍA v3.6
# ============================================================================

@dataclass
class PlanetaSAVP:
    """Planeta con todos los datos SAVP v3.6."""
    nombre: str
    simbolo: str
    
    # Astronómico
    grado: float
    signo: str
    casa: int
    retrogrado: bool
    
    # Proyección
    sephirah: str
    pilar: str
    
    # Dignidad y peso
    dignidad: str
    peso_esencial: float
    M_casa: float
    M_retro: float
    M_aspectos: float
    peso_final: float
    
    # Genio
    genio_numero: int
    genio_nombre: str
    genio_atributos: str = ""
    
    # Cadena
    dispositor: Optional[str] = None
    
    # Aspectos
    aspectos: List[Dict] = field(default_factory=list)
    
    # Senderos
    senderos_ocupacion: List[Dict] = field(default_factory=list)
    senderos_aspectos: List[Dict] = field(default_factory=list)
    senderos_criticos: List[Dict] = field(default_factory=list)


@dataclass
class NodoCadena:
    """Nodo en el grafo de dispositores."""
    planeta: str
    sephirah: str
    peso: float
    retrogrado: bool
    dispositores: List[str]
    dispone_a: List[str]
    tipo: str  # 'motor', 'convergencia', 'valvula', 'nodo_simple'


# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def normalizar_signo(signo_corto: str) -> str:
    """Convierte signo abreviado a nombre completo."""
    return SIGNOS_KERYKEION_SAVP.get(signo_corto, signo_corto)


def calcular_dignidad(planeta: str, signo: str) -> Tuple[str, float]:
    """Calcula dignidad esencial."""
    signo = normalizar_signo(signo)
    digs = DIGNIDADES_CANONICAS.get(planeta)
    
    if not digs:
        return ('peregrino', 1.0)
    
    if signo in digs.get('domicilio', []):
        return ('domicilio', PESO_ESENCIAL['domicilio'])
    elif signo in digs.get('exaltacion', []):
        return ('exaltacion', PESO_ESENCIAL['exaltacion'])
    elif signo in digs.get('exilio', []):
        return ('exilio', PESO_ESENCIAL['exilio'])
    elif signo in digs.get('caida', []):
        return ('caida', PESO_ESENCIAL['caida'])
    else:
        return ('peregrino', PESO_ESENCIAL['peregrino'])


def calcular_genio(grado: float, signo: str) -> dict:
    """Calcula Genio de los 72 con tabla completa."""
    signo = normalizar_signo(signo)
    signo_idx = SIGNOS_INDEX.get(signo, 0)
    quinario = int(grado // 5)
    genio_num = 1 + (signo_idx * 6) + quinario
    
    # Usar tabla completa de 72 Genios
    genio_data = GENIOS_72.get(genio_num, {
        'nombre': f'GENIO_{genio_num}',
        'salmo': 0,
        'atributos': 'No catalogado'
    })
    
    return {
        'numero': genio_num,
        'nombre': genio_data.get('nombre', f'GENIO_{genio_num}'),
        'salmo': genio_data.get('salmo', 0),
        'atributos': genio_data.get('atributos', ''),
        'quinario': f"{quinario*5}-{(quinario+1)*5}°"
    }


def calcular_peso_final_v36(planeta_data: dict, aspectos_count: int = 0) -> dict:
    """Calcula peso final con sistema 2 capas."""
    dignidad, peso_base = calcular_dignidad(planeta_data['nombre'], planeta_data['signo'])
    
    casa = planeta_data['casa']
    if casa in [1, 4, 7, 10]:
        M_casa = 1.20
    elif casa in [2, 5, 8, 11]:
        M_casa = 1.00
    else:
        M_casa = 0.85
    
    M_retro = 0.90 if planeta_data.get('retrogrado', False) else 1.00
    M_aspectos = 1.00 + min(aspectos_count * 0.07, 0.35)
    
    peso_final = peso_base * M_casa * M_retro * M_aspectos
    
    return {
        'peso_final': round(peso_final, 2),
        'dignidad': dignidad,
        'peso_esencial': peso_base,
        'M_casa': M_casa,
        'M_retro': M_retro,
        'M_aspectos': M_aspectos
    }


def posicion_absoluta(signo: str, grado: float) -> float:
    """Convierte signo + grado a posición absoluta 0-360°."""
    signo = normalizar_signo(signo)
    idx = SIGNOS_INDEX.get(signo, 0)
    return (idx * 30) + grado


def calcular_distancia_angular(pos1: float, pos2: float) -> float:
    """Calcula distancia angular más corta."""
    distancia = abs(pos1 - pos2)
    if distancia > 180:
        distancia = 360 - distancia
    return distancia


def detectar_aspecto(distancia: float) -> Optional[Tuple[str, float]]:
    """Detecta tipo de aspecto según distancia angular."""
    aspectos = {
        'conjuncion': (0, 8),
        'sextil': (60, 6),
        'cuadratura': (90, 8),
        'trigono': (120, 8),
        'oposicion': (180, 8)
    }
    
    for tipo, (angulo, orbe_max) in aspectos.items():
        orbe = abs(distancia - angulo)
        if orbe <= orbe_max:
            return (tipo, orbe)
    
    return None


def calcular_aspectos_carta(planetas: List[Dict]) -> Dict[str, List[Dict]]:
    """Calcula todos los aspectos entre planetas."""
    aspectos_por_planeta = {p['nombre']: [] for p in planetas}
    procesados = set()
    
    for i, p1 in enumerate(planetas):
        pos1 = posicion_absoluta(p1['signo'], p1['grado'])
        
        for p2 in planetas[i+1:]:
            par = tuple(sorted([p1['nombre'], p2['nombre']]))
            if par in procesados:
                continue
            procesados.add(par)
            
            pos2 = posicion_absoluta(p2['signo'], p2['grado'])
            distancia = calcular_distancia_angular(pos1, pos2)
            
            aspecto_data = detectar_aspecto(distancia)
            if aspecto_data:
                tipo, orbe = aspecto_data
                exacto = orbe <= 3.0
                
                # Agregar a ambos planetas
                aspectos_por_planeta[p1['nombre']].append({
                    'tipo': tipo,
                    'con': p2['nombre'],
                    'orbe': round(orbe, 2),
                    'exacto': exacto
                })
                
                aspectos_por_planeta[p2['nombre']].append({
                    'tipo': tipo,
                    'con': p1['nombre'],
                    'orbe': round(orbe, 2),
                    'exacto': exacto
                })
    
    return aspectos_por_planeta


def senderos_de_sephirah(sephirah: str) -> List[Dict]:
    """Retorna senderos estructurales de una Sephirah."""
    if sephirah == 'Daath':
        return []
    
    senderos = []
    for num, datos in SENDEROS_ARBOL.items():
        if sephirah in datos['sephiroth']:
            conecta_con = [s for s in datos['sephiroth'] if s != sephirah]
            senderos.append({
                'numero': num,
                'nombre': datos['nombre'],
                'arcano': datos['arcano'],
                'conecta_con': conecta_con[0] if conecta_con else 'N/A',
                'elemento': datos['elemento']
            })
    
    return senderos


def buscar_sendero_entre_sephiroth(seph1: str, seph2: str) -> Optional[Dict]:
    """Busca sendero que conecta dos Sephiroth."""
    if seph1 == 'Daath' or seph2 == 'Daath':
        return None
    
    for num, datos in SENDEROS_ARBOL.items():
        if set([seph1, seph2]) == set(datos['sephiroth']):
            return {
                'numero': num,
                'nombre': datos['nombre'],
                'arcano': datos['arcano'],
                'sephiroth': datos['sephiroth'],
                'elemento': datos['elemento']
            }
    
    return None


def detectar_senderos_criticos(planetas_savp: List[PlanetaSAVP]) -> List[Dict]:
    """Detecta senderos con doble activación (ocupación + aspecto)."""
    criticos = []
    procesados = set()
    
    for p1 in planetas_savp:
        for aspecto in p1.aspectos:
            p2 = next((p for p in planetas_savp if p.nombre == aspecto['con']), None)
            if not p2:
                continue
            
            par = tuple(sorted([p1.nombre, p2.nombre]))
            if par in procesados:
                continue
            procesados.add(par)
            
            sendero = buscar_sendero_entre_sephiroth(p1.sephirah, p2.sephirah)
            if sendero:
                urgencia = 'ALTA' if aspecto['tipo'] in ['oposicion', 'cuadratura'] else 'MEDIA'
                
                criticos.append({
                    'sendero': sendero,
                    'planetas': [p1.nombre, p2.nombre],
                    'aspecto': aspecto,
                    'peso_combinado': round(p1.peso_final + p2.peso_final, 2),
                    'urgencia': urgencia
                })
    
    criticos.sort(key=lambda x: x['peso_combinado'], reverse=True)
    return criticos


def construir_grafo_dispositores(planetas: List[Dict]) -> Dict:
    """Construye grafo de cadena de dispositores."""
    nodos = {}
    
    for p in planetas:
        nombre = p['nombre']
        signo = normalizar_signo(p['signo'])
        dispositor = REGENCIAS.get(signo)
        
        if dispositor == nombre:
            dispositor = None  # Motor
        
        nodos[nombre] = {
            'dispositor': dispositor,
            'retrogrado': p.get('retrogrado', False),
            'sephirah': PLANETA_SEPHIRAH.get(nombre),
            'peso': p.get('peso_final', 1.0)
        }
    
    # Detectar convergencias
    dispositores_count = {}
    for nombre, data in nodos.items():
        disp = data['dispositor']
        if disp:
            dispositores_count[disp] = dispositores_count.get(disp, 0) + 1
    
    convergencias = [k for k, v in dispositores_count.items() if v > 1]
    valvulas = [k for k, v in nodos.items() if v['retrogrado']]
    motores = [k for k, v in nodos.items() if v['dispositor'] is None]
    
    # Detectar bucles
    bucles = []
    for inicio in nodos.keys():
        visitados = set()
        actual = inicio
        camino = []
        
        while actual and actual not in visitados:
            visitados.add(actual)
            camino.append(actual)
            actual = nodos[actual]['dispositor']
            
            if actual == inicio and len(camino) > 1:
                bucles.append(camino + [inicio])
                break
    
    return {
        'nodos': nodos,
        'convergencias': convergencias,
        'valvulas': valvulas,
        'motores': motores,
        'bucles': bucles
    }


# ============================================================================
# FUNCIÓN PRINCIPAL: ANÁLISIS COMPLETO
# ============================================================================

def procesar_carta_savp_v36_completa(subject, planetas_raw: dict) -> dict:
    """
    Análisis SAVP v3.6 COMPLETO con Fase 2.
    
    Incluye:
    - Dignidades y ponderación
    - Genios
    - Aspectos automáticos
    - Senderos 3 tipos
    - Cadena como grafo
    - Pilares
    """
    
    # 1. Preparar lista de planetas
    planetas_lista = []
    nombre_map = {
        'sol': 'Sol', 'luna': 'Luna', 'mercurio': 'Mercurio',
        'venus': 'Venus', 'marte': 'Marte', 'jupiter': 'Jupiter',
        'saturno': 'Saturno', 'urano': 'Urano', 'neptuno': 'Neptuno',
        'pluton': 'Pluton'
    }
    
    for nombre_esp, data in planetas_raw.items():
        nombre = nombre_map.get(nombre_esp)
        if not nombre:
            continue
        
        planetas_lista.append({
            'nombre': nombre,
            'grado': data['grado'],
            'signo': data['signo'],
            'casa': data['casa'],
            'retrogrado': data.get('retrogrado', False)
        })
    
    # 2. Calcular aspectos
    aspectos_por_planeta = calcular_aspectos_carta(planetas_lista)
    
    # 3. Construir planetas SAVP completos
    planetas_savp = []
    
    for planeta_data in planetas_lista:
        nombre = planeta_data['nombre']
        sephirah = PLANETA_SEPHIRAH.get(nombre)
        pilar = SEPHIRAH_PILAR.get(sephirah, 'central')
        
        genio = calcular_genio(planeta_data['grado'], planeta_data['signo'])
        
        aspectos = aspectos_por_planeta.get(nombre, [])
        aspectos_exactos = sum(1 for a in aspectos if a['exacto'])
        
        ponderacion = calcular_peso_final_v36(planeta_data, aspectos_exactos)
        
        # Senderos por ocupación
        senderos_ocup = senderos_de_sephirah(sephirah)
        
        planeta_savp = PlanetaSAVP(
            nombre=nombre,
            simbolo='☉☽☿♀♂♃♄♅♆♇'['Sol Luna Mercurio Venus Marte Jupiter Saturno Urano Neptuno Pluton'.split().index(nombre)] if nombre != 'ASC' else 'ASC',
            grado=planeta_data['grado'],
            signo=normalizar_signo(planeta_data['signo']),
            casa=planeta_data['casa'],
            retrogrado=planeta_data['retrogrado'],
            sephirah=sephirah,
            pilar=pilar,
            dignidad=ponderacion['dignidad'],
            peso_esencial=ponderacion['peso_esencial'],
            M_casa=ponderacion['M_casa'],
            M_retro=ponderacion['M_retro'],
            M_aspectos=ponderacion['M_aspectos'],
            peso_final=ponderacion['peso_final'],
            genio_numero=genio['numero'],
            genio_nombre=genio['nombre'],
            genio_atributos=genio['atributos'],
            aspectos=aspectos,
            senderos_ocupacion=senderos_ocup
        )
        
        planetas_savp.append(planeta_savp)
    
    # 4. Senderos por aspectos y críticos
    for p in planetas_savp:
        senderos_asp = []
        for aspecto in p.aspectos:
            p2 = next((pl for pl in planetas_savp if pl.nombre == aspecto['con']), None)
            if p2:
                sendero = buscar_sendero_entre_sephiroth(p.sephirah, p2.sephirah)
                if sendero:
                    senderos_asp.append({
                        'sendero': sendero,
                        'aspecto': aspecto
                    })
        p.senderos_aspectos = senderos_asp
    
    senderos_criticos = detectar_senderos_criticos(planetas_savp)
    
    for p in planetas_savp:
        p.senderos_criticos = [c for c in senderos_criticos if p.nombre in c['planetas']]
    
    # 5. Cadena de dispositores
    planetas_dict = [{
        'nombre': p.nombre,
        'signo': p.signo,
        'retrogrado': p.retrogrado,
        'peso_final': p.peso_final
    } for p in planetas_savp]
    
    grafo = construir_grafo_dispositores(planetas_dict)
    
    # 6. Distribución por pilares
    pilares = {
        'izquierdo': {'peso_total': 0.0, 'planetas': []},
        'central': {'peso_total': 0.0, 'planetas': []},
        'derecho': {'peso_total': 0.0, 'planetas': []}
    }
    
    for p in planetas_savp:
        pilares[p.pilar]['peso_total'] += p.peso_final
        pilares[p.pilar]['planetas'].append({
            'nombre': p.nombre,
            'peso': p.peso_final
        })
    
    total = sum(p['peso_total'] for p in pilares.values())
    porcentajes = {
        k: round((v['peso_total'] / total) * 100, 1)
        for k, v in pilares.items()
    }
    
    pilar_max = max(porcentajes.items(), key=lambda x: x[1])
    
    # 7. Serializar planetas
    planetas_serializados = {}
    for p in planetas_savp:
        planetas_serializados[p.nombre] = {
            'astronomico': {
                'grado': p.grado,
                'signo': p.signo,
                'casa': p.casa,
                'retrogrado': p.retrogrado
            },
            'sephirah': p.sephirah,
            'pilar': p.pilar,
            'genio': {
                'numero': p.genio_numero,
                'nombre': p.genio_nombre,
                'atributos': p.genio_atributos
            },
            'ponderacion': {
                'dignidad': p.dignidad,
                'peso_esencial': p.peso_esencial,
                'peso_final': p.peso_final,
                'M_casa': p.M_casa,
                'M_retro': p.M_retro,
                'M_aspectos': p.M_aspectos
            },
            'aspectos': p.aspectos,
            'senderos': {
                'ocupacion': p.senderos_ocupacion,
                'aspectos': p.senderos_aspectos,
                'criticos': p.senderos_criticos
            }
        }
    
    return {
        'planetas_savp': planetas_serializados,
        'pilares': pilares,
        'porcentajes': porcentajes,
        'cadena_dispositores': grafo,
        'senderos_criticos_resumen': senderos_criticos,
        'diagnostico': {
            'pilar_dominante': pilar_max[0],
            'porcentaje_dominante': pilar_max[1],
            'tipo': 'equilibrio' if pilar_max[1] < 40 else 'dominante'
        },
        'version': 'SAVP v3.6 Completa - Fase 2'
    }


if __name__ == "__main__":
    print("✅ savp_v36_core COMPLETO (Fase 2) cargado")
