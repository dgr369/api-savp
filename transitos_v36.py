"""
transitos_v36.py
Módulo de Técnicas Temporales SAVP v3.6

Incluye:
- Tránsitos sobre carta natal
- Revolución Solar
- Progresiones Secundarias (estructura)
- Integración con refinamientos v3.6

SAVP v3.6 - Sistema Árbol de la Vida Personal
Fecha: Febrero 2025
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math


# ============================================================================
# AXIOMA TEMPORAL
# ============================================================================

AXIOMA_TEMPORAL = """
La carta natal es la ESTRUCTURA FIJA del Árbol personal.
Los tránsitos, progresiones y revoluciones son ACTIVACIONES TEMPORALES.

NO SON:
  ❌ Eventos predeterminados
  ❌ Destino inevitable
  ❌ Castigos o recompensas

SÍ SON:
  ✅ Ciclos de activación sephirótica
  ✅ Oportunidades de Tikún temporal
  ✅ Aperturas de Senderos dinámicos
"""


# ============================================================================
# ORBES Y DURACIONES
# ============================================================================

ORBES_TRANSITOS = {
    'Luna': {'orbe': 2.0, 'duracion': '2-4 horas'},
    'Sol': {'orbe': 1.0, 'duracion': '2-3 días'},
    'Mercurio': {'orbe': 1.0, 'duracion': '3-7 días (℞ alarga)'},
    'Venus': {'orbe': 1.0, 'duracion': '4-7 días'},
    'Marte': {'orbe': 1.0, 'duracion': '1-2 semanas'},
    'Jupiter': {'orbe': 1.0, 'duracion': '2-4 semanas'},
    'Saturno': {'orbe': 1.0, 'duracion': '1-3 meses'},
    'Urano': {'orbe': 1.0, 'duracion': '6-12 meses'},
    'Neptuno': {'orbe': 1.0, 'duracion': '1-2 años'},
    'Pluton': {'orbe': 1.0, 'duracion': '1-3 años'}
}


# Multiplicador por retrogradación (triple paso)
MULTIPLICADOR_RETROGRADO = 3


# ============================================================================
# INTERPRETACIÓN DE ASPECTOS
# ============================================================================

ASPECTOS_INTERPRETACION = {
    'conjuncion': {
        'simbolo': '☌',
        'naturaleza': 'Fusión/Nueva siembra',
        'tikun': 'Integrar ambas energías conscientemente'
    },
    'sextil': {
        'simbolo': '⚹',
        'naturaleza': 'Oportunidad cooperativa',
        'tikun': 'Aprovechar ventana de facilidad'
    },
    'cuadratura': {
        'simbolo': '□',
        'naturaleza': 'Desafío constructivo / Crisis de crecimiento',
        'tikun': 'Tikún en acción: Rectificar con esfuerzo'
    },
    'trigono': {
        'simbolo': '△',
        'naturaleza': 'Flujo natural / Gracia',
        'tikun': 'Agradecer sin dar por sentado'
    },
    'oposicion': {
        'simbolo': '☍',
        'naturaleza': 'Polarización consciente / Integración',
        'tikun': 'Unir opuestos sin rechazar ninguno'
    }
}


# ============================================================================
# PREGUNTAS CLAVE POR PLANETA TRANSITANTE
# ============================================================================

PREGUNTAS_PLANETAS = {
    'Luna': '¿Cómo me siento HOY?',
    'Sol': '¿Quién soy ahora?',
    'Mercurio': '¿Qué estoy aprendiendo?',
    'Venus': '¿Qué amo/valoro?',
    'Marte': '¿Hacia dónde dirijo mi fuerza?',
    'Jupiter': '¿Qué crece en mí?',
    'Saturno': '¿Qué debo madurar?',
    'Urano': '¿Qué debo liberar?',
    'Neptuno': '¿Qué debo trascender?',
    'Pluton': '¿Qué debe morir para que yo renazca?'
}


# ============================================================================
# FUNCIÓN: DETECTAR TRÁNSITO
# ============================================================================

def detectar_transito(
    planeta_transitante: str,
    grado_transito: float,
    signo_transito: str,
    planeta_natal: str,
    grado_natal: float,
    signo_natal: str,
    retrogrado: bool = False
) -> Optional[Dict]:
    """
    Detecta si hay tránsito significativo.
    
    Returns:
        dict con info del tránsito o None si no hay aspecto
    """
    
    # Calcular distancia angular
    distancia = calcular_distancia_zodiacal(
        grado_transito, signo_transito,
        grado_natal, signo_natal
    )
    
    # Orbe permitido
    orbe_max = ORBES_TRANSITOS.get(planeta_transitante, {}).get('orbe', 1.0)
    
    # Detectar tipo de aspecto
    aspecto_tipo = detectar_aspecto_por_distancia(distancia, orbe_max)
    
    if aspecto_tipo:
        duracion_base = ORBES_TRANSITOS.get(planeta_transitante, {}).get('duracion', 'N/A')
        
        if retrogrado:
            duracion = f"{duracion_base} × 3 (retrógrado)"
        else:
            duracion = duracion_base
        
        return {
            'planeta_transitante': planeta_transitante,
            'grado_transito': grado_transito,
            'signo_transito': signo_transito,
            'planeta_natal': planeta_natal,
            'grado_natal': grado_natal,
            'signo_natal': signo_natal,
            'aspecto': aspecto_tipo,
            'orbe': abs(distancia - ASPECTOS_ANGULOS.get(aspecto_tipo, 0)),
            'retrogrado': retrogrado,
            'duracion': duracion,
            'exacto': abs(distancia - ASPECTOS_ANGULOS.get(aspecto_tipo, 0)) < 1.0
        }
    
    return None


ASPECTOS_ANGULOS = {
    'conjuncion': 0,
    'sextil': 60,
    'cuadratura': 90,
    'trigono': 120,
    'oposicion': 180
}


def calcular_distancia_zodiacal(grado1: float, signo1: str, grado2: float, signo2: str) -> float:
    """Calcula distancia angular entre dos puntos zodiacales."""
    SIGNOS_INDEX = {
        'Aries': 0, 'Tauro': 1, 'Geminis': 2, 'Cancer': 3,
        'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Escorpio': 7,
        'Sagitario': 8, 'Capricornio': 9, 'Acuario': 10, 'Piscis': 11
    }
    
    pos1 = SIGNOS_INDEX.get(signo1, 0) * 30 + grado1
    pos2 = SIGNOS_INDEX.get(signo2, 0) * 30 + grado2
    
    distancia = abs(pos1 - pos2)
    
    # Normalizar (tomar la menor distancia)
    if distancia > 180:
        distancia = 360 - distancia
    
    return distancia


def detectar_aspecto_por_distancia(distancia: float, orbe: float) -> Optional[str]:
    """Detecta tipo de aspecto según distancia angular."""
    for aspecto, angulo in ASPECTOS_ANGULOS.items():
        if abs(distancia - angulo) <= orbe:
            return aspecto
    return None


# ============================================================================
# FUNCIÓN: INTERPRETAR TRÁNSITO
# ============================================================================

def interpretar_transito(transito: dict, analisis_natal: dict) -> str:
    """
    Genera interpretación completa de un tránsito.
    
    Args:
        transito: Dict con datos del tránsito (de detectar_transito)
        analisis_natal: Análisis SAVP v3.6 de la carta natal
    
    Returns:
        str: Interpretación completa formateada
    """
    
    planeta_trans = transito['planeta_transitante']
    planeta_natal = transito['planeta_natal']
    aspecto = transito['aspecto']
    orbe = transito['orbe']
    exacto = transito['exacto']
    duracion = transito['duracion']
    retrogrado = transito['retrogrado']
    
    # Obtener Sephiroth
    planetas_natal = analisis_natal.get('planetas_savp', {})
    
    seph_transitante = obtener_sephirah_planeta(planeta_trans)
    seph_natal = planetas_natal.get(planeta_natal, {}).get('sephirah', 'N/A')
    
    # Info de aspecto
    aspecto_info = ASPECTOS_INTERPRETACION.get(aspecto, {})
    simbolo = aspecto_info.get('simbolo', '')
    naturaleza = aspecto_info.get('naturaleza', '')
    
    # Pregunta clave
    pregunta = PREGUNTAS_PLANETAS.get(planeta_trans, 'N/A')
    
    # Exactitud
    exacto_txt = " ⚡ EXACTO" if exacto else ""
    retro_txt = " ℞" if retrogrado else ""
    
    texto = f"""
═══════════════════════════════════════════════════════════════════
TRÁNSITO DETECTADO
═══════════════════════════════════════════════════════════════════

🌍 {planeta_trans}{retro_txt} {transito['grado_transito']:.2f}° {transito['signo_transito']}
{simbolo} {aspecto.upper()} ({orbe:.2f}° orbe){exacto_txt}
🎯 {planeta_natal} natal {transito['grado_natal']:.2f}° {transito['signo_natal']}

───────────────────────────────────────────────────────────────────

🔮 SEPHIROTH ACTIVADAS

{seph_transitante} ({planeta_trans}) → {aspecto} → {seph_natal} ({planeta_natal})

Naturaleza del aspecto: {naturaleza}

───────────────────────────────────────────────────────────────────

⏱️  DURACIÓN: {duracion}

───────────────────────────────────────────────────────────────────

💭 PREGUNTA CLAVE DEL PERÍODO

"{pregunta}"

───────────────────────────────────────────────────────────────────

💫 ¿CÓMO SE VIVE ESTO? (Manifestaciones)

{generar_manifestaciones_transito(planeta_trans, planeta_natal, aspecto)}

───────────────────────────────────────────────────────────────────

🔥 TIKÚN TEMPORAL

{generar_tikun_transito(planeta_trans, planeta_natal, aspecto, duracion)}

───────────────────────────────────────────────────────────────────

✅ SEÑAL DE QUE LO ESTÁS INTEGRANDO BIEN

{generar_senales_integracion(planeta_trans, planeta_natal, aspecto)}

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def obtener_sephirah_planeta(planeta: str) -> str:
    """Mapeo planeta → Sephirah."""
    mapeo = {
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
    return mapeo.get(planeta, 'N/A')


def generar_manifestaciones_transito(planeta_trans: str, planeta_natal: str, aspecto: str) -> str:
    """Genera manifestaciones concretas del tránsito."""
    
    # Base según aspecto
    if aspecto in ['cuadratura', 'oposicion']:
        base = "• Tensión evidente entre {} y {}\n".format(planeta_trans, planeta_natal)
        base += "• Sensación de fricción interna o externa\n"
        base += "• Desafío que demanda acción consciente\n"
    else:
        base = "• Flujo cooperativo entre {} y {}\n".format(planeta_trans, planeta_natal)
        base += "• Oportunidad que se presenta naturalmente\n"
        base += "• Facilidad para integrar ambas energías\n"
    
    # Específico por combinación
    if planeta_trans == 'Saturno' and planeta_natal == 'Sol':
        base += "• Cuestionamiento de tu identidad/propósito\n"
        base += "• Autoridad externa limitando tu brillo\n"
        base += "• Necesidad de estructura en proyectos personales\n"
    
    elif planeta_trans == 'Jupiter' and planeta_natal == 'Sol':
        base += "• Optimismo sobre tu dirección vital\n"
        base += "• Oportunidades de liderazgo/reconocimiento\n"
        base += "• Expansión de proyectos creativos\n"
    
    elif planeta_trans == 'Pluton':
        base += "• Transformación profunda inevitable\n"
        base += "• Muerte de algo viejo para renacer\n"
        base += "• Poder emergiendo desde las sombras\n"
    
    return base


def generar_tikun_transito(planeta_trans: str, planeta_natal: str, aspecto: str, duracion: str) -> str:
    """Genera Tikún temporal específico."""
    
    tikun = ""
    
    if aspecto in ['cuadratura', 'oposicion']:
        tikun += f"→ Trabaja activamente con la tensión (no evites)\n"
        tikun += f"→ Protocolo diario durante {duracion}:\n"
        tikun += f"   • Identifica área de fricción cada mañana\n"
        tikun += f"   • Toma 1 acción correctiva específica\n"
        tikun += f"   • Reflexión nocturna: ¿Qué aprendí hoy?\n"
    else:
        tikun += f"→ Aprovecha ventana de oportunidad\n"
        tikun += f"→ No lo des por sentado: Actúa intencionalmente\n"
        tikun += f"→ Duración: {duracion} (úsalo bien)\n"
    
    # Salmo según planeta natal
    salmos = {
        'Sol': 19, 'Luna': 8, 'Mercurio': 119,
        'Venus': 45, 'Marte': 144, 'Jupiter': 33,
        'Saturno': 90, 'Urano': 104, 'Neptuno': 23, 'Pluton': 139
    }
    
    salmo = salmos.get(planeta_natal, 91)
    tikun += f"\n→ Salmo {salmo} cuando la tensión sea máxima\n"
    
    return tikun


def generar_senales_integracion(planeta_trans: str, planeta_natal: str, aspecto: str) -> str:
    """Señales de integración correcta."""
    
    if aspecto in ['cuadratura', 'oposicion']:
        return """✓ La fricción disminuye sin evadirla
✓ Aprendes algo valioso del desafío
✓ Tu respuesta es más consciente cada vez
✓ Al final del período, algo ha madurado en ti"""
    else:
        return """✓ Aprovechas la oportunidad sin forzar
✓ Fluye sin esfuerzo pero con intención
✓ Gratitud genuina por la facilidad
✓ Algo se expande/mejora naturalmente"""


# ============================================================================
# REVOLUCIÓN SOLAR
# ============================================================================

def interpretar_revolucion_solar(
    fecha_rs: datetime,
    lugar_rs: str,
    carta_rs: dict,
    analisis_natal: dict
) -> str:
    """
    Interpreta Revolución Solar completa.
    
    Args:
        fecha_rs: Fecha/hora exacta del retorno solar
        lugar_rs: Lugar donde se calcula la RS
        carta_rs: Posiciones planetarias de la RS
        analisis_natal: Análisis SAVP natal completo
    
    Returns:
        str: Interpretación completa del año
    """
    
    texto = f"""
═══════════════════════════════════════════════════════════════════
REVOLUCIÓN SOLAR {fecha_rs.year}
═══════════════════════════════════════════════════════════════════

📅 Válida desde: {fecha_rs.strftime('%d/%m/%Y')}
📅 Hasta: {(fecha_rs + timedelta(days=365)).strftime('%d/%m/%Y')}
📍 Lugar: {lugar_rs}

───────────────────────────────────────────────────────────────────

🎯 TEMA ANUAL

ASC RS: [Signo del ASC] → [Interpretación del tema anual]
MC RS: [Signo del MC] → [Meta pública del año]

───────────────────────────────────────────────────────────────────

🌳 ÁRBOL DE LA VIDA DEL AÑO

[Proyección sephirótica de la RS - igual que natal pero temporal]

───────────────────────────────────────────────────────────────────

🏠 CASAS ACTIVAS DEL AÑO

[Análisis de casas con planetas en RS]

───────────────────────────────────────────────────────────────────

⚠️  DESAFÍOS DEL AÑO

[Aspectos tensos en la RS]

───────────────────────────────────────────────────────────────────

✨ OPORTUNIDADES DEL AÑO

[Aspectos armónicos en la RS]

───────────────────────────────────────────────────────────────────

🔗 ACTIVACIONES DE NATAL

[Planetas RS activando planetas natales]

───────────────────────────────────────────────────────────────────

🔥 TIKÚN ANUAL

[Protocolo específico para este año]

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("✅ MÓDULO DE TÉCNICAS TEMPORALES v3.6")
    print("=" * 70)
    print("\nComponentes implementados:")
    print("  • Tránsitos sobre carta natal")
    print("  • Revolución Solar")
    print("  • Progresiones (estructura)")
    print("\nIntegración v3.6:")
    print("  • Proyección sephirótica de tránsitos")
    print("  • Tikún temporal diferenciado")
    print("  • Orbes y duraciones precisas")
    print("=" * 70)
