"""
motor_lectura_v36.py
Motor de Lectura Interpretativa Completa SAVP v3.6

Integra:
- Protocolo 10 fases de v3.5
- Refinamientos técnicos de v3.6
- Tikún automático diferenciado
- Generación de visualizaciones

SAVP v3.6 - Sistema Árbol de la Vida Personal
Fecha: Febrero 2025
"""

from typing import Dict, List, Optional, Tuple
import json


# ============================================================================
# PROTOCOLO 10 FASES
# ============================================================================

FASES_LECTURA = {
    0: {
        'nombre': 'VERIFICACIÓN DE DATOS',
        'descripcion': 'Validar datos natales antes de proceder',
        'requerimientos': ['fecha', 'hora', 'lugar', 'coordenadas'],
        'validaciones': [
            'Fecha válida (1900-2100)',
            'Hora en formato 24h',
            'Coordenadas coherentes',
            'Timezone correcto'
        ]
    },
    
    1: {
        'nombre': 'PROYECCIÓN SEPHIRÓTICA',
        'descripcion': 'Planetas → Sephiroth + Pilares ponderados',
        'componentes': [
            'Tabla planetas con Sephirah',
            'Distribución por pilares (%)',
            'Diagnóstico pilar dominante',
            'Ponderación v3.6 (2 capas)'
        ]
    },
    
    2: {
        'nombre': 'GENIOS DE LOS 72',
        'descripcion': 'Calcular Genio para cada planeta/punto',
        'formula': '(índiceSigno × 6) + floor(grado/5) + 1',
        'incluir': ['10 planetas', 'ASC', 'MC', 'Nodos']
    },
    
    3: {
        'nombre': 'CADENA DE DISPOSITORES',
        'descripcion': 'ASC → dispositores → Motor primario',
        'analisis': [
            'Cadena completa como grafo',
            'Convergencias (hubs)',
            'Válvulas (retrógrados ℞)',
            'Motores (sin salida)',
            'Bucles detectados'
        ]
    },
    
    4: {
        'nombre': 'SENDEROS + TAROT',
        'descripcion': '3 tipos de senderos: ocupación, aspectos, críticos',
        'tipos': {
            'ocupacion': 'Senderos estructurales por Sephiroth ocupadas',
            'aspectos': 'Senderos dinámicos por aspectos planetarios',
            'criticos': 'Doble activación (ocupación + aspecto)'
        }
    },
    
    5: {
        'nombre': 'TRIPLE LECTURA I (Planetas 1-5)',
        'descripcion': 'Lectura profunda: Sol, Luna, Mercurio, Venus, Marte',
        'estructura': [
            'Proyección sephirótica (2-3 frases)',
            '¿CÓMO SE VIVE? (4-6 manifestaciones concretas)',
            'TIKÚN (3-4 prácticas específicas + Salmo)'
        ]
    },
    
    6: {
        'nombre': 'TRIPLE LECTURA II (Planetas 6-10)',
        'descripcion': 'Lectura profunda: Jupiter, Saturno, Urano, Neptuno, Plutón',
        'estructura': 'Igual que Fase 5'
    },
    
    7: {
        'nombre': 'EJE NODAL',
        'descripcion': 'Nodo Norte (destino) + Sur (karma)',
        'incluir': [
            'Genios de ambos Nodos',
            'Casas de los Nodos',
            'Tikún nodal (protocolo 4 fases: 1 año)',
            'Integración con Genios específicos'
        ]
    },
    
    8: {
        'nombre': 'ASPECTOS MAYORES',
        'descripcion': '5 aspectos más importantes como Senderos',
        'elementos': [
            'Letra hebrea del sendero',
            'Arcano del Tarot',
            'Interpretación pneumatológica',
            'Tikún si aspecto tenso'
        ]
    },
    
    9: {
        'nombre': 'VOCACIÓN + OPUS MAGNUM',
        'descripcion': 'Síntesis de 7 capas → Vocación → Gran Obra',
        'componentes': [
            'Síntesis de 7 capas',
            '3 vocaciones recomendadas',
            'Opus Magnum (protocolo 40 días: Nigredo/Albedo/Rubedo)'
        ]
    },
    
    10: {
        'nombre': 'CONCLUSIÓN INTEGRAL',
        'descripcion': 'Síntesis final + Misión + Próximos pasos',
        'incluir': [
            'Arquetipo definitivo',
            '7 fortalezas + 7 desafíos',
            'Sombra principal',
            'Misión (esotérica + práctica)',
            '10 signos de éxito',
            'Próximos pasos concretos'
        ]
    }
}


# ============================================================================
# GENERADOR DE FASE 0: VERIFICACIÓN
# ============================================================================

def generar_fase_0_verificacion(datos_natales: dict) -> dict:
    """
    Fase 0: Verificar datos antes de proceder.
    
    Returns:
        dict con validaciones y tabla de confirmación
    """
    nombre = datos_natales.get('nombre', 'Consultante')
    fecha = datos_natales.get('fecha', '')
    hora = datos_natales.get('hora', '')
    lugar = datos_natales.get('lugar', '')
    lat = datos_natales.get('lat')
    lon = datos_natales.get('lon')
    timezone = datos_natales.get('timezone', 'Europe/Madrid')
    
    # Validaciones
    validaciones = []
    errores = []
    
    # 1. Fecha
    if fecha:
        validaciones.append("✅ Fecha proporcionada")
    else:
        errores.append("❌ Falta fecha de nacimiento")
    
    # 2. Hora
    if hora:
        validaciones.append("✅ Hora proporcionada")
    else:
        errores.append("⚠️  Hora no proporcionada (requerida para casas)")
    
    # 3. Lugar
    if lugar:
        validaciones.append("✅ Lugar proporcionado")
    else:
        errores.append("❌ Falta lugar de nacimiento")
    
    # 4. Coordenadas
    if lat is not None and lon is not None:
        validaciones.append(f"✅ Coordenadas: {lat:.2f}°, {lon:.2f}°")
    else:
        errores.append("⚠️  Coordenadas no proporcionadas (se geocodificarán)")
    
    # Tabla de confirmación
    tabla = f"""
═══════════════════════════════════════════════════════════════════
FASE 0: VERIFICACIÓN DE DATOS NATALES
═══════════════════════════════════════════════════════════════════

📋 DATOS EXTRAÍDOS:

  • Nombre:    {nombre}
  • Fecha:     {fecha}
  • Hora:      {hora}
  • Lugar:     {lugar}
  • Coordenadas: {f'{lat:.4f}°, {lon:.4f}°' if lat and lon else 'Por determinar'}
  • Timezone:  {timezone}

───────────────────────────────────────────────────────────────────

✓ VALIDACIONES:

"""
    
    for v in validaciones:
        tabla += f"  {v}\n"
    
    if errores:
        tabla += "\n⚠️  ATENCIÓN:\n\n"
        for e in errores:
            tabla += f"  {e}\n"
    
    tabla += """
═══════════════════════════════════════════════════════════════════

⚠️  CONFIRMACIÓN REQUERIDA

Por favor, verifica que los datos son correctos antes de continuar.
Si hay algún error, corrígelo ahora.

¿Los datos son correctos? (Responde: SÍ / NO / CORREGIR)

═══════════════════════════════════════════════════════════════════
"""
    
    return {
        'fase': 0,
        'nombre': 'VERIFICACIÓN DE DATOS',
        'validaciones': validaciones,
        'errores': errores,
        'tabla_confirmacion': tabla,
        'datos_validados': len(errores) == 0,
        'requiere_confirmacion': True
    }


# ============================================================================
# GENERADOR DE FASE 1: PROYECCIÓN SEPHIRÓTICA
# ============================================================================

def generar_fase_1_proyeccion(analisis_savp: dict) -> str:
    """
    Fase 1: Proyección Sephirótica con pilares ponderados.
    """
    planetas = analisis_savp.get('planetas_savp', {})
    pilares = analisis_savp.get('pilares', {})
    porcentajes = analisis_savp.get('porcentajes', {})
    diagnostico = analisis_savp.get('diagnostico', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 1: PROYECCIÓN SEPHIRÓTICA
═══════════════════════════════════════════════════════════════════

🌳 ÁRBOL DE LA VIDA PERSONAL

"""
    
    # Tabla de planetas → Sephiroth
    texto += "📊 PLANETAS EN EL ÁRBOL:\n\n"
    texto += "  Planeta      Grado    Signo   Casa   Sephirah      Pilar        Peso\n"
    texto += "  ──────────────────────────────────────────────────────────────────\n"
    
    for nombre in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte', 
                   'Jupiter', 'Saturno', 'Urano', 'Neptuno', 'Pluton']:
        if nombre in planetas:
            p = planetas[nombre]
            astro = p.get('astronomico', {})
            seph = p.get('sephirah', 'N/A')
            pilar = p.get('pilar', 'N/A')
            pond = p.get('ponderacion', {})
            peso = pond.get('peso_final', 0)
            retro = " ℞" if astro.get('retrogrado') else ""
            
            texto += f"  {nombre:10s}  {astro.get('grado', 0):5.1f}°  {astro.get('signo', 'N/A'):5s}  "
            texto += f"{astro.get('casa', 0):2d}    {seph:12s}  {pilar.capitalize():10s}  {peso:.2f}{retro}\n"
    
    # Distribución por pilares
    texto += "\n" + "─" * 67 + "\n\n"
    texto += "⚖️  DISTRIBUCIÓN POR PILARES (Ponderación v3.6):\n\n"
    
    for pilar_nombre in ['izquierdo', 'central', 'derecho']:
        pct = porcentajes.get(pilar_nombre, 0)
        peso_total = pilares.get(pilar_nombre, {}).get('peso_total', 0)
        planetas_pilar = pilares.get(pilar_nombre, {}).get('planetas', [])
        
        barra = "█" * int(pct / 2)
        texto += f"  {pilar_nombre.upper():12s}  {barra:30s} {pct:5.1f}% ({peso_total:.2f} pts)\n"
        
        for p in planetas_pilar[:3]:  # Top 3
            texto += f"    • {p['nombre']:10s} {p['peso']:.2f}\n"
        
        texto += "\n"
    
    # Diagnóstico
    pilar_dom = diagnostico.get('pilar_dominante', 'N/A')
    tipo = diagnostico.get('tipo', 'N/A')
    pct_dom = porcentajes.get(pilar_dom, 0)
    
    texto += "─" * 67 + "\n\n"
    texto += "🎯 DIAGNÓSTICO:\n\n"
    texto += f"  • Pilar dominante: {pilar_dom.upper()} ({pct_dom:.1f}%)\n"
    texto += f"  • Tipo: {tipo.upper()}\n\n"
    
    # Interpretación del pilar
    if pilar_dom == 'derecho':
        texto += """  📖 INTERPRETACIÓN:
  
  El Pilar Derecho (Jupiterino-Venusino) domina tu Árbol.
  Énfasis en CONSTRUCCIÓN, EXPANSIÓN y RELACIONES.
  
  Chesed (Júpiter) y Netzach (Venus) son tus motores:
  → Crecimiento a través del vínculo
  → Abundancia mediante generosidad
  → Forma que emerge de la belleza
  
  Tikún: No dispersar, consolidar.
"""
    
    elif pilar_dom == 'izquierdo':
        texto += """  📖 INTERPRETACIÓN:
  
  El Pilar Izquierdo (Saturnino-Marciano) domina tu Árbol.
  Énfasis en LIMITACIÓN, DISCERNIMIENTO y FUERZA.
  
  Binah (Saturno) y Geburah (Marte) son tus motores:
  → Estructura a través de la disciplina
  → Purificación mediante el corte
  → Poder que emerge de la restricción
  
  Tikún: No endurecer, integrar compasión.
"""
    
    else:  # central
        texto += """  📖 INTERPRETACIÓN:
  
  El Pilar Central (Solar-Lunar) domina tu Árbol.
  Énfasis en EQUILIBRIO, MEDIACIÓN y CONCIENCIA.
  
  Tiphareth (Sol) y Yesod (Luna) son tus ejes:
  → Integración de opuestos
  → Transformación consciente
  → Puente entre lo alto y lo bajo
  
  Tikún: No quedar en el medio, elegir y actuar.
"""
    
    texto += """
═══════════════════════════════════════════════════════════════════

✓ Fase 1 completada

¿Continuar con Fase 2: GENIOS DE LOS 72?

O prefieres:
• Profundizar en esta proyección
• Hacer preguntas específicas
• Pausar aquí

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# GENERADOR DE FASE 2: GENIOS
# ============================================================================

def generar_fase_2_genios(analisis_savp: dict) -> str:
    """
    Fase 2: Genios de los 72.
    """
    planetas = analisis_savp.get('planetas_savp', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 2: GENIOS DE LOS 72
═══════════════════════════════════════════════════════════════════

🕯️  "NOMEN DEI SEPTUAGINTA DUARUM LITERARUM"
   (El Nombre de Dios de 72 Letras)

Los 72 Genios derivan de tres versículos del Éxodo (14:19-21).
Cada 5° del zodíaco corresponde a un Genio específico.

Fórmula: (índiceSigno × 6) + floor(grado/5) + 1

───────────────────────────────────────────────────────────────────

📋 GENIOS POR PLANETA:

"""
    
    for nombre in ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte',
                   'Jupiter', 'Saturno', 'Urano', 'Neptuno', 'Pluton']:
        if nombre in planetas:
            p = planetas[nombre]
            astro = p.get('astronomico', {})
            genio = p.get('genio', {})
            
            texto += f"  {nombre.upper()}\n"
            texto += f"    Posición: {astro.get('grado'):.2f}° {astro.get('signo')} (Casa {astro.get('casa')})\n"
            texto += f"    Genio: #{genio.get('numero')} {genio.get('nombre')}\n"
            texto += f"    Salmo: {genio.get('salmo', 'N/A')}\n"
            texto += f"    Quinario: {genio.get('quinario', 'N/A')}\n"
            texto += f"    Atributos: {genio.get('atributos', 'N/A')[:60]}...\n\n"
    
    texto += """═══════════════════════════════════════════════════════════════════

✓ Fase 2 completada

¿Continuar con Fase 3: CADENA DE DISPOSITORES?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FUNCIÓN PRINCIPAL: GENERAR FASE COMPLETA
# ============================================================================

def generar_fase_completa(numero_fase: int, analisis_savp: dict, datos_natales: dict = None) -> str:
    """
    Genera el texto completo de una fase específica (0-10).
    
    Args:
        numero_fase: 0-10
        analisis_savp: Resultado de procesar_carta_savp_v36_completa()
        datos_natales: Dict con datos natales (solo para Fase 0)
    
    Returns:
        str: Texto formateado de la fase
    """
    if numero_fase == 0:
        if not datos_natales:
            return "❌ Error: Se requieren datos_natales para Fase 0"
        resultado = generar_fase_0_verificacion(datos_natales)
        return resultado['tabla_confirmacion']
    
    elif numero_fase == 1:
        return generar_fase_1_proyeccion(analisis_savp)
    
    elif numero_fase == 2:
        return generar_fase_2_genios(analisis_savp)
    
    elif numero_fase == 3:
        return generar_fase_3_cadena(analisis_savp)
    
    elif numero_fase == 4:
        return generar_fase_4_senderos(analisis_savp)
    
    elif numero_fase == 5:
        return generar_fase_5_triple_lectura_1(analisis_savp)
    
    elif numero_fase == 6:
        return generar_fase_6_triple_lectura_2(analisis_savp)
    
    elif numero_fase == 7:
        return generar_fase_7_eje_nodal(analisis_savp)
    
    elif numero_fase == 8:
        return generar_fase_8_aspectos(analisis_savp)
    
    elif numero_fase == 9:
        return generar_fase_9_vocacion(analisis_savp)
    
    elif numero_fase == 10:
        return generar_fase_10_conclusion(analisis_savp)
    
    else:
        return f"❌ Fase {numero_fase} no válida (rango 0-10)"


if __name__ == "__main__":
    print("=" * 70)
    print("✅ MOTOR DE LECTURA INTERPRETATIVA v3.6 COMPLETO")
    print("=" * 70)
    print(f"\nProtocolo: {len(FASES_LECTURA)} fases implementadas\n")
    
    for num, fase in FASES_LECTURA.items():
        print(f"  Fase {num:2d}: {fase['nombre']}")
    
    print("\n" + "=" * 70)
    print("Sistema listo para generar lecturas completas SAVP v3.6")
    print("=" * 70)


# ============================================================================
# FASE 3: CADENA DE DISPOSITORES
# ============================================================================

def generar_fase_3_cadena(analisis_savp: dict) -> str:
    """Fase 3: Cadena de dispositores como grafo."""
    cadena = analisis_savp.get('cadena_dispositores', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 3: CADENA DE DISPOSITORES
═══════════════════════════════════════════════════════════════════

🔗 TOPOLOGÍA DEL GRAFO

La cadena muestra cómo fluye el poder desde el ASC hacia los dispositores.

"""
    
    nodos = cadena.get('nodos', {})
    convergencias = cadena.get('convergencias', [])
    valvulas = cadena.get('valvulas', [])
    motores = cadena.get('motores', [])
    bucles = cadena.get('bucles', [])
    
    # Convergencias
    if convergencias:
        texto += "🔴 CONVERGENCIAS (Hubs de poder):\n\n"
        for conv in convergencias:
            entradas = sum(1 for n, d in nodos.items() if d.get('dispositor') == conv)
            peso = nodos.get(conv, {}).get('peso', 0)
            presion = entradas / peso if peso > 0 else 999
            
            texto += f"  • {conv}: {entradas} entradas → peso {peso:.2f} pts\n"
            texto += f"    Presión: {presion:.2f} (entradas/peso)\n"
            
            if presion > 5:
                texto += f"    ⚠️  CRÍTICO: Sobrecarga severa\n"
            elif presion > 3:
                texto += f"    ⚠️  ALTO: Cuello de botella\n"
            texto += "\n"
    
    # Válvulas
    if valvulas:
        texto += "⚙️  VÁLVULAS (Retrógrados ℞):\n\n"
        for valv in valvulas:
            texto += f"  • {valv} ℞ : Retiene/filtra energía antes de liberar\n"
        texto += "\n"
    
    # Motores
    if motores:
        texto += "⚡ MOTORES (Sin salida):\n\n"
        for motor in motores:
            texto += f"  • {motor}: Autorregente, fuente primaria\n"
        texto += "\n"
    
    # Bucles
    if bucles:
        texto += f"🔄 BUCLES DETECTADOS: {len(bucles)}\n\n"
        for i, bucle in enumerate(bucles[:3], 1):
            texto += f"  {i}. {' → '.join(bucle)}\n"
        texto += "\n"
    
    texto += """═══════════════════════════════════════════════════════════════════

✓ Fase 3 completada

¿Continuar con Fase 4: SENDEROS + TAROT?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FASE 4: SENDEROS
# ============================================================================

def generar_fase_4_senderos(analisis_savp: dict) -> str:
    """Fase 4: Senderos (3 tipos)."""
    senderos_criticos = analisis_savp.get('senderos_criticos_resumen', [])
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 4: SENDEROS + TAROT
═══════════════════════════════════════════════════════════════════

🎴 LOS 22 SENDEROS DEL ÁRBOL

Hay 3 tipos de senderos:

1️⃣  ESTRUCTURALES (por ocupación): Sephiroth ocupadas
2️⃣  DINÁMICOS (por aspectos): Conexiones planetarias
3️⃣  CRÍTICOS (doble activación): Ocupación + aspecto simultáneo

───────────────────────────────────────────────────────────────────

🔥 SENDEROS CRÍTICOS (Máxima prioridad):

"""
    
    if senderos_criticos:
        for i, sc in enumerate(senderos_criticos[:5], 1):
            sendero = sc.get('sendero', {})
            num = sendero.get('numero')
            nombre = sendero.get('nombre')
            arcano = sendero.get('arcano')
            
            planetas_inv = ' ↔ '.join(sc.get('planetas', []))
            aspecto = sc.get('aspecto', {})
            tipo_asp = aspecto.get('tipo', 'N/A')
            peso = sc.get('peso_combinado', 0)
            urgencia = sc.get('urgencia', 'MEDIA')
            
            urgencia_emoji = "🔴" if urgencia == "ALTA" else "🟡"
            
            texto += f"  {i}. SENDERO #{num}: {nombre} (Arcano {arcano})\n"
            texto += f"     {urgencia_emoji} Urgencia: {urgencia}\n"
            texto += f"     Planetas: {planetas_inv}\n"
            texto += f"     Aspecto: {tipo_asp.capitalize()}\n"
            texto += f"     Peso combinado: {peso:.2f} pts\n\n"
    else:
        texto += "  ℹ️  No se detectaron senderos críticos\n\n"
    
    texto += """═══════════════════════════════════════════════════════════════════

✓ Fase 4 completada

¿Continuar con Fase 5: TRIPLE LECTURA I (Planetas 1-5)?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FASE 5: TRIPLE LECTURA I (Planetas 1-5)
# ============================================================================

def generar_fase_5_triple_lectura_1(analisis_savp: dict) -> str:
    """
    Fase 5: Lectura profunda de Sol, Luna, Mercurio, Venus, Marte.
    
    Estructura por planeta:
    - Proyección sephirótica (2-3 frases técnicas)
    - ¿CÓMO SE VIVE? (4-6 manifestaciones concretas)
    - TIKÚN (3-4 prácticas + Salmo)
    """
    planetas = analisis_savp.get('planetas_savp', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 5: TRIPLE LECTURA I (Planetas Personales)
═══════════════════════════════════════════════════════════════════

Lectura profunda de los 5 planetas personales.
Cada planeta analizado en 3 niveles: Esencia → Manifestación → Acción

"""
    
    planetas_fase_5 = ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte']
    
    for nombre in planetas_fase_5:
        if nombre not in planetas:
            continue
        
        p = planetas[nombre]
        astro = p.get('astronomico', {})
        seph = p.get('sephirah', 'N/A')
        pilar = p.get('pilar', 'N/A')
        genio = p.get('genio', {})
        pond = p.get('ponderacion', {})
        senderos = p.get('senderos', {})
        
        # Símbolo
        simbolos = {
            'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿',
            'Venus': '♀', 'Marte': '♂'
        }
        simbolo = simbolos.get(nombre, '')
        
        grado = astro.get('grado', 0)
        signo = astro.get('signo', 'N/A')
        casa = astro.get('casa', 0)
        retro = " ℞" if astro.get('retrogrado') else ""
        
        dignidad = pond.get('dignidad', 'peregrino')
        peso = pond.get('peso_final', 0)
        
        # Header
        texto += f"""
───────────────────────────────────────────────────────────────────
{simbolo} {nombre.upper()} — {grado:.1f}° {signo}, Casa {casa}{retro}
───────────────────────────────────────────────────────────────────

"""
        
        # PROYECCIÓN SEPHIRÓTICA
        texto += "🔮 PROYECCIÓN SEPHIRÓTICA\n\n"
        texto += f"{nombre} en {seph} ({pilar.capitalize()}). "
        texto += f"Genio #{genio.get('numero')} {genio.get('nombre')} ({genio.get('atributos', 'N/A')[:40]}...). "
        
        if dignidad == 'domicilio':
            texto += f"DOMICILIO: Máxima expresión de {nombre}, poder pleno. "
        elif dignidad == 'exaltacion':
            texto += f"EXALTACIÓN: {nombre} elevado, potencial máximo. "
        elif dignidad == 'exilio':
            texto += f"EXILIO: {nombre} en terreno hostil, esfuerzo requerido. "
        elif dignidad == 'caida':
            texto += f"CAÍDA: {nombre} debilitado, demanda compensación. "
        else:
            texto += f"PEREGRINO: {nombre} neutral, adaptable. "
        
        texto += f"Peso: {peso:.2f} pts.\n\n"
        
        # ¿CÓMO SE VIVE ESTO?
        texto += "💫 ¿CÓMO SE VIVE ESTO? (Manifestaciones)\n\n"
        
        # Manifestaciones específicas por planeta
        if nombre == 'Sol':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Cuesta brillar sin validación externa
  • Te preguntas "¿quién soy realmente?" con frecuencia
  • Necesitas demostrar tu valor más que otros
  • Cuando te reconocen, dudas si es genuino
  • Tu luz se enciende en servicio, no en protagonismo
"""
            else:
                texto += """  • Sabes quién eres sin necesitar confirmación
  • Tu presencia ilumina naturalmente los espacios
  • Lideras sin imponerte, otros te siguen
  • Tu propósito es claro, aunque el camino no
  • Irradia desde el centro, no desde la fachada
"""
        
        elif nombre == 'Luna':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Emociones bloqueadas o explosivas (poco término medio)
  • Cuesta conectar con lo que realmente sientes
  • El pasado pesa, cuesta soltar memorias
  • Relación compleja con figura materna/cuidado
  • Necesitas estructura para sentirte seguro
"""
            else:
                texto += """  • Emociones fluyen sin atascarse
  • Intuyes atmósferas antes de entrar
  • Cuidas sin absorber, nutres sin agotar
  • Tu hogar (interior/exterior) es tu ancla
  • Los ciclos emocionales no te desestabilizan
"""
        
        elif nombre == 'Mercurio':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Mente dispersa o bloqueada (ambos extremos)
  • Cuesta traducir lo que piensas en palabras
  • Aprendes diferente, sistema educativo no encajó
  • Comunicación genera malentendidos frecuentes
  • Cuando hablas, nadie escucha; cuando callas, te buscan
"""
            else:
                texto += """  • Mente rápida, conectas ideas al instante
  • Aprendes por ósmosis, sin esfuerzo aparente
  • Hablas varios "idiomas" (técnico, emocional, social)
  • Tu comunicación clarifica, no confunde
  • Escribir/hablar es pensar en voz alta
"""
        
        elif nombre == 'Venus':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Amor cuesta, relaciones demandan trabajo constante
  • Atraes lo que no te conviene (patrón repetido)
  • Das más de lo que recibes sin notarlo
  • Belleza y placer son "culpables" o "merecidos"
  • Valoras a otros más que a ti mismo
"""
            else:
                texto += """  • Amor fluye, relaciones son jardines (no batallas)
  • Atraes afinidad genuina sin esfuerzo
  • Das desde la abundancia, no desde la falta
  • Belleza es cotidiana, no excepcional
  • Te valoras sin arrogancia ni duda
"""
        
        elif nombre == 'Marte':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Ira reprimida o explosiva (poco control)
  • Cuesta defender límites sin culpa o agresión
  • Pasividad extrema o combatividad constante
  • Competencia genera malestar (ganar/perder duele)
  • Acción bloqueada: sabes qué hacer, no puedes moverte
"""
            else:
                texto += """  • Ira calibrada: cuando es necesario, proporcional
  • Defiendes sin atacar, cortas sin destruir
  • Acción decidida pero no impulsiva
  • Competencia sana: mejoras, no aniquilas
  • Tu espada está afilada pero envainada hasta que se necesita
"""
        
        texto += "\n"
        
        # TIKÚN
        texto += "🔥 TIKÚN (Acción correctiva)\n\n"
        
        if nombre == 'Sol':
            if dignidad in ['exilio', 'caida']:
                texto += f"""  → Ritual solar dominical: 10 minutos al amanecer, afirma "Soy" sin justificar
  → Lista semanal: 3 actos donde brillaste SIN aprobación externa
  → No busques roles de líder hasta que LO SEAS internamente
  → Salmo {genio.get('salmo', 'N/A')} cuando busques validación
"""
            else:
                texto += f"""  → Mantén centro aunque otros proyecten sobre ti
  → Lídera desde servicio, no desde ego
  → Ritual: Cada logro, agradece en silencio (no publicar)
  → Salmo {genio.get('salmo', 'N/A')} cuando sientas peso de expectativas
"""
        
        elif nombre == 'Luna':
            if dignidad in ['exilio', 'caida']:
                texto += f"""  → Diario emocional: 5 min antes de dormir, nombra 3 emociones del día
  → No racionalices sentimientos, obsérvalos sin arreglar
  → Crea ritual nocturno fijo (ancla tu Luna errante)
  → Salmo {genio.get('salmo', 'N/A')} cuando emociones desborden o congelen
"""
            else:
                texto += f"""  → Mantén límites emocionales (no absorber todo)
  → Ritual lunar: Luna nueva = soltar, Luna llena = agradecer
  → Tu intuición es oro, no la discutas con lógica
  → Salmo {genio.get('salmo', 'N/A')} para limpiar emociones ajenas absorbidas
"""
        
        elif nombre == 'Mercurio':
            if dignidad in ['exilio', 'caida']:
                texto += f"""  → Escritura diaria estructurada: 100 palabras, 3 ideas clave
  → Aprende por PRÁCTICA (no solo teoría)
  → No fuerces estilo comunicativo que no es tuyo
  → Salmo {genio.get('salmo', 'N/A')} cuando mente se bloquee o disperse
"""
            else:
                texto += f"""  → Filtra información: no todo merece tu análisis
  → Silencio estratégico (no todo requiere respuesta)
  → Enseña lo que sabes: tu don se multiplica compartiéndolo
  → Salmo {genio.get('salmo', 'N/A')} cuando mente acelere sin freno
"""
        
        elif nombre == 'Venus':
            if dignidad in ['exilio', 'caida']:
                texto += f"""  → Ritual venusino viernes: Acto de belleza/amor para TI (no para otros)
  → Lista mensual: "Di NO a..." (ejercita rechazo sin culpa)
  → Invierte en ti antes de dar (no es egoísmo)
  → Salmo {genio.get('salmo', 'N/A')} cuando amor se vuelva sacrificio tóxico
"""
            else:
                texto += f"""  → No te conformes: tu don es atraer calidad, úsalo
  → Belleza cotidiana: Crea algo bello 1x/semana (sin mostrar)
  → Comparte abundancia sin vaciar tu copa
  → Salmo {genio.get('salmo', 'N/A')} cuando relaciones se vuelvan transaccionales
"""
        
        elif nombre == 'Marte':
            if dignidad in ['exilio', 'caida']:
                texto += f"""  → Ejercicio físico intenso 3x/semana (canaliza Marte bloqueado)
  → Practica "No" firme sin justificar: 1 vez/día durante 21 días
  → No guardes ira: Expresa (sin atacar) o libera (físicamente)
  → Salmo {genio.get('salmo', 'N/A')} cuando pasividad o ira te paralicen
"""
            else:
                texto += f"""  → Mantén espada afilada: entrena aunque no haya batalla
  → Corta limpio, no desgastes con micro-agresiones
  → Canaliza fuerza en construcción, no solo en defensa
  → Salmo {genio.get('salmo', 'N/A')} cuando fuerza se vuelva crueldad
"""
        
        texto += "\n"
    
    texto += """═══════════════════════════════════════════════════════════════════

✓ Fase 5 completada

¿Continuar con Fase 6: TRIPLE LECTURA II (Planetas 6-10)?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FASE 6: TRIPLE LECTURA II (Planetas 6-10)
# ============================================================================

def generar_fase_6_triple_lectura_2(analisis_savp: dict) -> str:
    """
    Fase 6: Lectura profunda de Jupiter, Saturno, Urano, Neptuno, Plutón.
    """
    planetas = analisis_savp.get('planetas_savp', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 6: TRIPLE LECTURA II (Planetas Transpersonales)
═══════════════════════════════════════════════════════════════════

Lectura profunda de los 5 planetas transpersonales.
Representan fuerzas colectivas operando en lo personal.

"""
    
    planetas_fase_6 = ['Jupiter', 'Saturno', 'Urano', 'Neptuno', 'Pluton']
    simbolos = {'Jupiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Pluton': '♇'}
    
    for nombre in planetas_fase_6:
        if nombre not in planetas:
            continue
        
        p = planetas[nombre]
        astro = p.get('astronomico', {})
        seph = p.get('sephirah', 'N/A')
        genio = p.get('genio', {})
        pond = p.get('ponderacion', {})
        
        simbolo = simbolos.get(nombre, '')
        grado = astro.get('grado', 0)
        signo = astro.get('signo', 'N/A')
        casa = astro.get('casa', 0)
        retro = " ℞" if astro.get('retrogrado') else ""
        dignidad = pond.get('dignidad', 'peregrino')
        peso = pond.get('peso_final', 0)
        
        texto += f"""
───────────────────────────────────────────────────────────────────
{simbolo} {nombre.upper()} — {grado:.1f}° {signo}, Casa {casa}{retro}
───────────────────────────────────────────────────────────────────

🔮 PROYECCIÓN SEPHIRÓTICA

{nombre} en {seph}. Genio #{genio.get('numero')} {genio.get('nombre')}. 
{dignidad.capitalize()}, peso {peso:.2f} pts.

💫 ¿CÓMO SE VIVE ESTO?

"""
        
        # Manifestaciones específicas por planeta transpersonal
        if nombre == 'Jupiter':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Expansión bloqueada: proyectos mueren antes de crecer
  • Optimismo escaso o ingenuo (extremos)
  • Cuesta confiar en abundancia: "nunca hay suficiente"
  • Maestros/mentores decepcionan o están ausentes
  • Fe es concepto abstracto, no experiencia vivida
"""
            else:
                texto += """  • Expandirte es natural como respirar
  • Optimismo calibrado: confías pero verificas
  • Abundancia te encuentra sin buscarla
  • Mentores aparecen en momentos clave
  • Fe es experiencia, no creencia forzada
"""
        
        elif nombre == 'Saturno':
            if dignidad in ['exilio', 'caida']:
                texto += """  • Estructura ausente o rígida (ambos duelen)
  • Autoridad: Rechazo total o sumisión extrema
  • Tiempo es enemigo: "Siempre es tarde" o "Nunca es momento"
  • Disciplina cuesta, procrastinación crónica
  • Límites inexistentes o muros infranqueables
"""
            else:
                texto += """  • Estructura sin prisión: orden que libera
  • Autoridad ganada, no impuesta ni rechazada
  • Tiempo es aliado: Construyes para décadas
  • Disciplina sin esfuerzo visible: Es tu naturaleza
  • Límites claros sin crueldad
"""
        
        elif nombre == 'Urano':
            texto += """  • Cambios súbitos reconfiguran vida cada X años
  • Intuición eléctrica: "Sé que algo va a pasar"
  • Originalidad no buscada, eres diferente sin intentarlo
  • Sistemas establecidos te asfixian
  • Libertad sobre seguridad, siempre
"""
        
        elif nombre == 'Neptuno':
            texto += """  • Límites difusos entre tú y otros (empatía extrema)
  • Realidad + imaginación se mezclan fluidamente
  • Arte/música/mística te conectan con "algo más"
  • Escapismo tentador cuando realidad duele
  • Compasión infinita o desilusión total
"""
        
        elif nombre == 'Pluton':
            texto += """  • Transformación profunda cada ciclo vital
  • Poder te atrae y aterra simultáneamente
  • Muerte/renacimiento no son metáforas, son vivencias
  • Control vs Entrega: Tu dilema existencial
  • Lo oculto te llama: psicología, misterios, sombras
"""
        
        texto += f"""

🔥 TIKÚN

  → {obtener_tikun_transpersonal(nombre, dignidad, genio.get('salmo', 'N/A'))}

"""
    
    texto += """═══════════════════════════════════════════════════════════════════

✓ Fase 6 completada

¿Continuar con Fase 7: EJE NODAL?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def obtener_tikun_transpersonal(planeta: str, dignidad: str, salmo: int) -> str:
    """Helper para Tikún de transpersonales."""
    tikun_map = {
        'Jupiter': f"""Ritual jupiterino jueves: Agradecer 10 bendiciones sin pedir nada
   → Si bloqueado: Actúa "como si" abundancia existiera
   → Salmo {salmo} cuando fe se desmorone""",
        
        'Saturno': f"""Disciplina saturnina: Horario fijo para DESCANSO (no solo trabajo)
   → Si rígido: Rompe 1 regla propia cada semana
   → Salmo {salmo} cuando estructura esclavice o colapse""",
        
        'Urano': f"""No resistas cambios, surfea la ola
   → Innovación programada: Altera 1 rutina/mes intencionalmente
   → Salmo {salmo} cuando rebeldía sea destructiva (no liberadora)""",
        
        'Neptuno': f"""Canaliza neptunianamente: Arte, música, meditación (nunca drogas/alcohol)
   → Límites firmes con compasión ilimitada
   → Salmo {salmo} cuando pierdas contacto con realidad""",
        
        'Pluton': f"""Psicoterapia profunda o trabajo sombra (no opcional si Plutón fuerte)
   → Suelta control en áreas no-vitales conscientemente
   → Salmo {salmo} cuando poder se vuelva manipulación"""
    }
    
    return tikun_map.get(planeta, f"Salmo {salmo} cuando {planeta} se desequilibre")


# ============================================================================
# FASE 7: EJE NODAL
# ============================================================================

def generar_fase_7_eje_nodal(analisis_savp: dict) -> str:
    """
    Fase 7: Nodo Norte (destino) + Nodo Sur (karma).
    Incluye protocolo Tikún de 1 año (4 fases).
    """
    # Nota: Los nodos no están en el análisis actual, pero estructuramos la fase
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 7: EJE NODAL (Karma y Destino)
═══════════════════════════════════════════════════════════════════

🌑 NODO SUR (Karma - Lo que traes)
☊ NODO NORTE (Destino - Hacia donde vas)

El Eje Nodal marca la tensión evolutiva fundamental de tu vida.

───────────────────────────────────────────────────────────────────

⚠️  NOTA: Para análisis completo del Eje Nodal se requieren:
   • Posición exacta Nodo Norte (signo, grado, casa)
   • Posición exacta Nodo Sur (signo, grado, casa)
   • Genios de ambos Nodos

ESTRUCTURA DE INTERPRETACIÓN:

🌑 NODO SUR (Tu zona de confort kármica)
   • Casa: Campo donde opera automáticamente
   • Signo: Cualidad que dominas (pero desgasta)
   • Genio: Talento heredado que necesita evolucionar
   • RIESGO: Quedarte aquí = estancamiento

☊ NODO NORTE (Tu destino evolutivo)
   • Casa: Campo de expansión necesaria
   • Signo: Cualidad a desarrollar conscientemente
   • Genio: Guía para la nueva dirección
   • META: Moverte aquí = crecimiento

───────────────────────────────────────────────────────────────────

📿 TIKÚN NODAL (Protocolo 1 año - 4 fases)

Trabajo anual dividido en 4 trimestres alquímicos:

TRIMESTRE 1 (Meses 1-3): NIGREDO - Reconocer patrón Sur
   → Identifica 7 hábitos/creencias del Nodo Sur
   → Diario: ¿Cuándo caigo en zona confort?
   → Salmo del Nodo Sur: Diario durante 3 meses

TRIMESTRE 2 (Meses 4-6): ALBEDO - Purificar lo excesivo
   → Elimina 3 de los 7 hábitos identificados
   → Práctica semanal: Actúa desde Nodo Norte intencionalmente
   → Ayuno de comportamiento Sur: 1 día/semana

TRIMESTRE 3 (Meses 7-9): CITRINITAS - Cultivar nuevo patrón
   → Desarrolla 3 cualidades del Nodo Norte
   → Proyecto que REQUIERA energía Norte (obligatoriedad)
   → Salmo del Nodo Norte: Diario durante 3 meses

TRIMESTRE 4 (Meses 10-12): RUBEDO - Integrar ambos
   → No rechazar Sur, usarlo AL SERVICIO de Norte
   → Ritual mensual: Gratitud al pasado + compromiso con futuro
   → Balance: 70% Norte, 30% Sur (no 100%/0%)

═══════════════════════════════════════════════════════════════════

✓ Fase 7 completada

¿Continuar con Fase 8: ASPECTOS MAYORES?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FASE 8: ASPECTOS MAYORES
# ============================================================================

def generar_fase_8_aspectos(analisis_savp: dict) -> str:
    """
    Fase 8: 5 aspectos más importantes como Senderos del Tarot.
    """
    senderos_criticos = analisis_savp.get('senderos_criticos_resumen', [])
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 8: ASPECTOS MAYORES COMO SENDEROS
═══════════════════════════════════════════════════════════════════

Los aspectos son Senderos dinámicos: Conexiones activas entre Sephiroth.
Cada aspecto es un Arcano del Tarot operando en tu psique.

TOP 5 ASPECTOS (Por peso e importancia):

"""
    
    if senderos_criticos:
        for i, sc in enumerate(senderos_criticos[:5], 1):
            sendero = sc.get('sendero', {})
            num = sendero.get('numero')
            nombre = sendero.get('nombre')
            arcano = sendero.get('arcano')
            letra = sendero.get('letra', 'N/A')
            
            planetas_inv = sc.get('planetas', [])
            aspecto_data = sc.get('aspecto', {})
            tipo_asp = aspecto_data.get('tipo', 'N/A')
            orbe = aspecto_data.get('orbe', 0)
            exacto = aspecto_data.get('exacto', False)
            
            peso = sc.get('peso_combinado', 0)
            urgencia = sc.get('urgencia', 'MEDIA')
            
            urgencia_emoji = "🔴" if urgencia == "ALTA" else "🟡"
            exacto_txt = " ⚡ EXACTO" if exacto else ""
            
            texto += f"""
───────────────────────────────────────────────────────────────────
{i}. SENDERO #{num}: {nombre.upper()} (Arcano {arcano})
───────────────────────────────────────────────────────────────────

{urgencia_emoji} Urgencia: {urgencia}{exacto_txt}
Planetas: {' ↔ '.join(planetas_inv)}
Aspecto: {tipo_asp.capitalize()} (orbe {orbe:.2f}°)
Letra hebrea: {letra}
Peso: {peso:.2f} pts

🎴 INTERPRETACIÓN:

"""
            
            # Interpretación según Arcano
            interpretacion = obtener_interpretacion_arcano(arcano, planetas_inv, tipo_asp)
            texto += interpretacion + "\n"
            
            # Tikún si es aspecto tenso
            if tipo_asp in ['cuadratura', 'oposicion'] or urgencia == 'ALTA':
                texto += "\n🔥 TIKÚN:\n\n"
                tikun_aspecto = obtener_tikun_aspecto(arcano, planetas_inv)
                texto += tikun_aspecto + "\n"
    
    else:
        texto += "  ℹ️  No hay senderos críticos detectados en esta carta.\n"
    
    texto += """
═══════════════════════════════════════════════════════════════════

✓ Fase 8 completada

¿Continuar con Fase 9: VOCACIÓN + OPUS MAGNUM?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def obtener_interpretacion_arcano(arcano: int, planetas: list, tipo_asp: str) -> str:
    """Interpretación pneumatológica de Arcanos."""
    
    interpretaciones = {
        0: "EL LOCO: Libertad absoluta vs estructura. La locura sagrada del que abandona seguridad por verdad.",
        3: "LA EMPERATRIZ: Fertilidad creativa. Belleza que genera forma. Venus dando a luz lo tangible.",
        8: "LA FUERZA: Dominio sin violencia. Leo domesticado por amor, no por miedo.",
        9: "EL ERMITAÑO: Luz interior que guía en soledad. Sabiduría extraída del retiro.",
        10: "LA RUEDA: Ciclos inevitables. Lo que sube baja. Fortuna como maestra de desapego.",
        11: "LA JUSTICIA: Equilibrio kármico. Espada y balanza. Verdad sin piedad.",
        12: "EL COLGADO: Sacrificio consciente. Ver al revés para ver verdad. Suspensión necesaria.",
        15: "EL DIABLO: Apego material. Cadenas que creemos no poder romper. Prisión consentida.",
        16: "LA TORRE: Destrucción de lo falso. Rayo que derriba estructuras huecas."
    }
    
    base = interpretaciones.get(arcano, f"Arcano {arcano}: Misterio a descifrar")
    
    if tipo_asp in ['cuadratura', 'oposicion']:
        return base + f"\n\n  ⚠️  Aspecto TENSO entre {' y '.join(planetas)}: Este sendero demanda trabajo activo."
    else:
        return base + f"\n\n  ✓ Aspecto FLUIDO entre {' y '.join(planetas)}: Este sendero opera con menos fricción."


def obtener_tikun_aspecto(arcano: int, planetas: list) -> str:
    """Tikún específico por Arcano tenso."""
    
    tikun_map = {
        0: "  → Estructura mínima viable (libertad sin caos)\n  → No huir, elegir conscientemente\n  → Ritual: 1 decisión arriesgada/trimestre",
        11: "  → Acepta consecuencias sin victimismo\n  → Perdona pero no olvides lección\n  → Protocolo: Escribe qué debes a quién (sin culpa)",
        12: "  → No eternizar sacrificio: Tiene fecha límite\n  → Pregunta: ¿Sirve esto a algo mayor?\n  → Ritual: 40 días suspensión voluntaria de algo",
        15: "  → Identifica cadenas auto-impuestas\n  → Rompe 1 apego/mes durante 6 meses\n  → Ayuno de deseo: 1 semana sin X (eliges qué)",
        16: "  → No reconstruyas igual: Deja que caiga\n  → Acepta que algo debe morir\n  → Ritual: Quema simbólica de lo que se derrumbó"
    }
    
    return tikun_map.get(arcano, f"  → Trabaja conscientemente con energía de Arcano {arcano}")


# ============================================================================
# FASE 9: VOCACIÓN + OPUS MAGNUM
# ============================================================================

def generar_fase_9_vocacion(analisis_savp: dict) -> str:
    """
    Fase 9: Síntesis de 7 capas → 3 vocaciones → Opus Magnum.
    """
    diagnostico = analisis_savp.get('diagnostico', {})
    pilares = analisis_savp.get('pilares', {})
    porcentajes = analisis_savp.get('porcentajes', {})
    
    pilar_dom = diagnostico.get('pilar_dominante', 'central')
    
    texto = f"""
═══════════════════════════════════════════════════════════════════
FASE 9: VOCACIÓN Y OPUS MAGNUM
═══════════════════════════════════════════════════════════════════

SÍNTESIS DE 7 CAPAS (Tu configuración única):

1️⃣  PILAR DOMINANTE: {pilar_dom.upper()} ({porcentajes.get(pilar_dom, 0):.1f}%)
2️⃣  SEPHIROTH OCUPADAS: {len([p for p in analisis_savp.get('planetas_savp', {}).values()])} planetas proyectados
3️⃣  CADENA DISPOSITORES: {len(analisis_savp.get('cadena_dispositores', {}).get('nodos', {}))} nodos
4️⃣  CONVERGENCIAS: {len(analisis_savp.get('cadena_dispositores', {}).get('convergencias', []))}
5️⃣  SENDEROS CRÍTICOS: {len(analisis_savp.get('senderos_criticos_resumen', []))}
6️⃣  GENIOS PRINCIPALES: Revisar Fase 2
7️⃣  EJE NODAL: Revisar Fase 7

───────────────────────────────────────────────────────────────────

🎯 3 VOCACIONES RECOMENDADAS

Basadas en tu configuración sephirótica:

"""
    
    # Generar vocaciones según pilar dominante
    if pilar_dom == 'derecho':
        texto += """
1. VOCACIÓN JUPITERINA (Chesed)
   → Maestro/mentor, Coach, Terapeuta expansivo
   → Crear abundancia/oportunidad para otros
   → Roles: Educador, Filántropo, Visionario empresarial

2. VOCACIÓN VENUSINA (Netzach)
   → Arte, diseño, belleza, relaciones
   → Crear armonía tangible en el mundo
   → Roles: Artista, Diseñador, Mediador, Terapeuta relacional

3. VOCACIÓN INTEGRADORA
   → Combina expansión (Júpiter) + belleza (Venus)
   → Roles: Curator cultural, Event designer, Life coach estético
"""
    
    elif pilar_dom == 'izquierdo':
        texto += """
1. VOCACIÓN SATURNINA (Binah)
   → Arquitecto de sistemas, Estructurador
   → Crear orden donde hay caos
   → Roles: Consultor estratégico, Ingeniero, Planificador

2. VOCACIÓN MARCIANA (Geburah)
   → Cirujano (literal o metafórico), Juez, Purificador
   → Cortar lo que no sirve con precisión
   → Roles: Abogado, Militar ético, Sanador por corte

3. VOCACIÓN INTEGRADORA
   → Combina estructura (Saturno) + fuerza (Marte)
   → Roles: Project manager de crisis, Reformador social
"""
    
    else:  # central
        texto += """
1. VOCACIÓN SOLAR (Tiphareth)
   → Líder consciente, Integrador, Sanador
   → Iluminar desde el centro sin ego
   → Roles: CEO con propósito, Líder espiritual, Médico holístico

2. VOCACIÓN LUNAR (Yesod)
   → Cuidador, Terapeuta emocional, Guardián de memorias
   → Nutrir y reflejar lo que otros no ven
   → Roles: Psicólogo, Historiador, Archivista emocional

3. VOCACIÓN INTEGRADORA
   → Combina conciencia (Sol) + intuición (Luna)
   → Roles: Chamán moderno, Consultor psico-espiritual
"""
    
    texto += """
───────────────────────────────────────────────────────────────────

🔥 OPUS MAGNUM (Tu Gran Obra)

Protocolo alquímico de 40 días para manifestar vocación:

📅 FASE 1: NIGREDO (Días 1-10) — Muerte de lo viejo
   → Identifica qué debes soltar para tu vocación
   → Escribe tu "anti-vocación" (lo que NO eres)
   → Ritual: Quema simbólica de roles falsos (papel con fuego)
   → Ayuno de identidad: No digas "Soy X" durante 10 días

📅 FASE 2: ALBEDO (Días 11-20) — Purificación
   → Limpia distracciones: 1 hábito/relación/objeto por día
   → Silencio vocacional: No hables de tu vocación con nadie
   → Estudio: Lee 1 biografía de alguien en tu campo
   → Práctica: 30 min/día haciendo tu vocación (sin cobrar)

📅 FASE 3: CITRINITAS (Días 21-30) — Amanecer dorado
   → Declara vocación en voz alta (solo para ti)
   → Crea prototipo/demo/muestra de tu trabajo
   → Comparte con 1 persona de confianza (feedback)
   → Inversión: Gasta $ en algo que apoye tu vocación

📅 FASE 4: RUBEDO (Días 31-40) — Manifestación
   → Acción pública: Anuncia tu vocación al mundo
   → Primera transacción: Cobra por tu servicio (aunque sea $1)
   → Ritual de cierre: Agradece al proceso, compromete 1 año
   → Plan: Define 3 hitos para próximos 90 días

═══════════════════════════════════════════════════════════════════

✓ Fase 9 completada

¿Continuar con Fase 10: CONCLUSIÓN INTEGRAL?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


# ============================================================================
# FASE 10: CONCLUSIÓN INTEGRAL
# ============================================================================

def generar_fase_10_conclusion(analisis_savp: dict) -> str:
    """
    Fase 10: Síntesis final completa.
    """
    diagnostico = analisis_savp.get('diagnostico', {})
    planetas = analisis_savp.get('planetas_savp', {})
    senderos = analisis_savp.get('senderos_criticos_resumen', [])
    
    # Identificar planeta más fuerte
    planeta_fuerte = max(
        [(n, p.get('ponderacion', {}).get('peso_final', 0)) for n, p in planetas.items()],
        key=lambda x: x[1],
        default=('N/A', 0)
    )
    
    # Identificar planeta más débil
    planeta_debil = min(
        [(n, p.get('ponderacion', {}).get('peso_final', 999)) for n, p in planetas.items() if p.get('ponderacion', {}).get('peso_final', 999) < 1],
        key=lambda x: x[1],
        default=('N/A', 0)
    )
    
    texto = f"""
═══════════════════════════════════════════════════════════════════
FASE 10: CONCLUSIÓN INTEGRAL
═══════════════════════════════════════════════════════════════════

🎭 ARQUETIPO DEFINITIVO

Tu carta natal revela el arquetipo del:

**"{obtener_arquetipo(diagnostico, planeta_fuerte[0], senderos)}"**

───────────────────────────────────────────────────────────────────

✨ 7 FORTALEZAS FUNDAMENTALES

1. Planeta más fuerte: {planeta_fuerte[0]} ({planeta_fuerte[1]:.2f} pts)
   → Tu mayor recurso natural

2. Pilar dominante: {diagnostico.get('pilar_dominante', 'N/A').capitalize()}
   → Tu eje de operación preferido

3. Senderos activos: {len(senderos)}
   → Conexiones dinámicas disponibles

4. [PERSONALIZAR]: Dignidad en domicilio/exaltación
   
5. [PERSONALIZAR]: Genio principal que te guía

6. [PERSONALIZAR]: Casa angular fuerte

7. [PERSONALIZAR]: Aspecto armónico dominante

───────────────────────────────────────────────────────────────────

⚠️  7 DESAFÍOS PRINCIPALES

1. Planeta más débil: {planeta_debil[0]} ({planeta_debil[1]:.2f} pts)
   → Tu mayor área de trabajo

2. Convergencias: {len(analisis_savp.get('cadena_dispositores', {}).get('convergencias', []))}
   → Posibles cuellos de botella

3. Senderos críticos urgentes: {sum(1 for s in senderos if s.get('urgencia') == 'ALTA')}
   → Áreas que demandan atención inmediata

4. [PERSONALIZAR]: Planetas en exilio/caída

5. [PERSONALIZAR]: Aspecto tenso dominante

6. [PERSONALIZAR]: Casa vacía significativa

7. [PERSONALIZAR]: Retrógrados múltiples

───────────────────────────────────────────────────────────────────

🌑 LA SOMBRA

Tu sombra principal opera a través de: **{identificar_sombra(planeta_debil[0], diagnostico)}**

No la rechaces. Intégrala.
La sombra es oro sin pulir.

───────────────────────────────────────────────────────────────────

🎯 MISIÓN DUAL

MISIÓN ESOTÉRICA (Interna):
→ {obtener_mision_esoterica(diagnostico.get('pilar_dominante'))}

MISIÓN PRÁCTICA (Externa):
→ {obtener_mision_practica(diagnostico.get('pilar_dominante'))}

───────────────────────────────────────────────────────────────────

✅ 10 SIGNOS DE QUE ESTÁS EN CAMINO

Sabrás que avanzas cuando:

1. Tu fortaleza principal opera sin esfuerzo
2. Tu debilidad principal ya no te paraliza
3. Senderos críticos se activan conscientemente
4. Convergencias fluyen sin colapsar
5. Tu Genio principal se manifiesta regularmente
6. Vocación = Trabajo (no están separados)
7. Sombra emerge pero no domina
8. Relaciones reflejan tu crecimiento
9. Sincronicidades aumentan
10. Sientes que estás donde debes estar

───────────────────────────────────────────────────────────────────

🚀 PRÓXIMOS PASOS CONCRETOS

📅 PRÓXIMOS 7 DÍAS:
   1. Revisar toda esta lectura en 1 sentada
   2. Elegir 1 Tikún de Fase 5-6 para empezar HOY
   3. Invocar Genio principal (Salmo diario)

📅 PRÓXIMOS 30 DÍAS:
   1. Implementar Tikún de planeta más débil
   2. Trabajar 1 sendero crítico conscientemente
   3. Ritual lunar (Luna nueva + Luna llena)

📅 PRÓXIMOS 90 DÍAS:
   1. Opus Magnum (40 días + integración)
   2. Evaluar vocación vs realidad actual
   3. Ajustar según manifestaciones reales

📅 PRÓXIMO AÑO:
   1. Protocolo Tikún Nodal completo (si aplica)
   2. Revisión cada equinoccio/solsticio
   3. Nueva lectura completa en tu cumpleaños

═══════════════════════════════════════════════════════════════════

🕯️  CIERRE RITUAL

Has recibido tu mapa pneumatológico completo.
No es predicción, es potencial.
No es destino, es invitación.

Que los 72 Genios te guíen.
Que el Árbol florezca en ti.

✨ PAX PROFUNDA ✨

═══════════════════════════════════════════════════════════════════

FIN DEL ANÁLISIS SAVP v3.6

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def obtener_arquetipo(diagnostico: dict, planeta_fuerte: str, senderos: list) -> str:
    """Genera arquetipo definitivo."""
    pilar = diagnostico.get('pilar_dominante', 'central')
    
    arquetipos = {
        'derecho': f"Constructor de Abundancia (Pilar Derecho con {planeta_fuerte} dominante)",
        'izquierdo': f"Arquitecto de Límites (Pilar Izquierdo con {planeta_fuerte} dominante)",
        'central': f"Mediador Consciente (Pilar Central con {planeta_fuerte} dominante)"
    }
    
    return arquetipos.get(pilar, "Buscador del Equilibrio")


def identificar_sombra(planeta_debil: str, diagnostico: dict) -> str:
    """Identifica sombra principal."""
    sombras = {
        'Sol': "Falso brillo (ego sin sustancia)",
        'Luna': "Emocionalidad incontrolada o congelada",
        'Mercurio': "Charlatanería o mutismo",
        'Venus': "Apego tóxico o frialdad afectiva",
        'Marte': "Violencia o impotencia",
        'Jupiter': "Exceso sin límite o tacañería extrema",
        'Saturno': "Rigidez cruel o ausencia de estructura",
        'Urano': "Rebeldía caótica o conformismo extremo",
        'Neptuno': "Escapismo o materialismo ciego",
        'Pluton': "Control obsesivo o victimismo"
    }
    
    return sombras.get(planeta_debil, "La negación de tu poder")


def obtener_mision_esoterica(pilar: str) -> str:
    """Misión esotérica según pilar."""
    misiones = {
        'derecho': "Expandir el Bien sin perder límites (Chesed equilibrado por Geburah)",
        'izquierdo': "Purificar con Compasión (Geburah templado por Chesed)",
        'central': "Integrar Opuestos en Unidad Consciente (Tiphareth realizado)"
    }
    
    return misiones.get(pilar, "Conocerte a ti mismo")


def obtener_mision_practica(pilar: str) -> str:
    """Misión práctica según pilar."""
    misiones = {
        'derecho': "Crear abundancia tangible que otros puedan usar",
        'izquierdo': "Establecer orden justo donde hay caos",
        'central': "Ser puente: Conectar lo que está separado"
    }
    
    return misiones.get(pilar, "Manifestar tu esencia en el mundo")


# ============================================================================
# FASE 5: TRIPLE LECTURA I (Planetas 1-5)
# ============================================================================

def generar_fase_5_triple_lectura_i(analisis_savp: dict) -> str:
    """
    Fase 5: Lectura profunda de Sol, Luna, Mercurio, Venus, Marte.
    
    Estructura por planeta:
    - Proyección sephirótica (técnico-hermético)
    - ¿CÓMO SE VIVE? (manifestaciones concretas)
    - TIKÚN (prácticas específicas + Salmo)
    """
    planetas = analisis_savp.get('planetas_savp', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 5: TRIPLE LECTURA I (Planetas Personales)
═══════════════════════════════════════════════════════════════════

Lectura profunda de los 5 planetas personales:
☉ Sol, ☽ Luna, ☿ Mercurio, ♀ Venus, ♂ Marte

Estructura: PROYECCIÓN → ¿CÓMO SE VIVE? → TIKÚN

───────────────────────────────────────────────────────────────────

"""
    
    planetas_fase5 = ['Sol', 'Luna', 'Mercurio', 'Venus', 'Marte']
    simbolos = {'Sol': '☉', 'Luna': '☽', 'Mercurio': '☿', 'Venus': '♀', 'Marte': '♂'}
    
    for nombre in planetas_fase5:
        if nombre not in planetas:
            continue
        
        p_data = planetas[nombre]
        astro = p_data.get('astronomico', {})
        seph = p_data.get('sephirah', 'N/A')
        pilar = p_data.get('pilar', 'N/A')
        genio = p_data.get('genio', {})
        pond = p_data.get('ponderacion', {})
        senderos = p_data.get('senderos', {})
        
        grado = astro.get('grado', 0)
        signo = astro.get('signo', 'N/A')
        casa = astro.get('casa', 0)
        retro = " ℞" if astro.get('retrogrado') else ""
        dignidad = pond.get('dignidad', 'peregrino')
        peso = pond.get('peso_final', 0)
        
        # Emoji dignidad
        dign_emoji = {'domicilio': '👑', 'exaltacion': '✨', 'exilio': '🚫', 'caida': '⬇️', 'peregrino': '⚪'}
        emoji = dign_emoji.get(dignidad, '⚪')
        
        texto += f"""
{simbolos[nombre]} {nombre.upper()} — {grado:.1f}° {signo}, Casa {casa}{retro}

PROYECCIÓN SEPHIRÓTICA
{seph} ({pilar.capitalize()}). Genio #{genio.get('numero')} {genio.get('nombre')}.
{emoji} {dignidad.capitalize()} ({peso:.2f} pts). """
        
        # Añadir info de senderos críticos si existen
        criticos = senderos.get('criticos', [])
        if criticos:
            texto += f"Sendero crítico: {criticos[0].get('sendero', {}).get('nombre', 'N/A')}."
        
        texto += f"""

¿CÓMO SE VIVE ESTO? (Manifestaciones concretas)
"""
        
        # Generar manifestaciones según planeta y dignidad
        manifestaciones = generar_manifestaciones_planeta(nombre, dignidad, signo, casa)
        for manif in manifestaciones:
            texto += f"• {manif}\n"
        
        texto += f"""
TIKÚN (Acción espiritual)
"""
        
        # Generar tikún según planeta
        tikun_items = generar_tikun_planeta(nombre, dignidad, genio)
        for item in tikun_items:
            texto += f"→ {item}\n"
        
        texto += "\n" + "─" * 67 + "\n"
    
    texto += """
═══════════════════════════════════════════════════════════════════

✓ Fase 5 completada

¿Continuar con Fase 6: TRIPLE LECTURA II (Planetas 6-10)?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def generar_manifestaciones_planeta(nombre: str, dignidad: str, signo: str, casa: int) -> list:
    """Genera manifestaciones concretas según planeta."""
    
    manifestaciones_base = {
        'Sol': {
            'domicilio': [
                "Tu identidad brilla naturalmente, sin esfuerzo",
                "Lideras con autoridad que otros reconocen espontáneamente",
                "Sabes quién eres y lo expresas sin disculpas",
                "Tu presencia ilumina espacios y personas"
            ],
            'exilio': [
                "Te cuesta sentir que brillas por ti mismo",
                "Dependes de validación externa para sentirte valioso",
                "Dudas de tu autoridad incluso cuando la tienes",
                "Prefieres apoyar a otros antes que destacar tú"
            ],
            'default': [
                "Buscas reconocimiento pero no siempre de forma directa",
                "Tu identidad se define más por lo que haces que por lo que eres",
                "Alternas entre brillar y ocultarte según el contexto"
            ]
        },
        'Luna': {
            'domicilio': [
                "Tus emociones fluyen con naturalidad y coherencia",
                "Nutres a otros sin esfuerzo consciente",
                "Tu intuición es tu mejor brújula",
                "Necesitas hogar/refugio seguro para funcionar"
            ],
            'exilio': [
                "Te cuesta conectar con lo que sientes realmente",
                "Intelectualizas emociones en lugar de vivirlas",
                "La rigidez emocional te protege pero te aísla",
                "Evitas dependencia pero la necesitas"
            ],
            'default': [
                "Tus estados de ánimo varían según el ambiente",
                "Necesitas seguridad emocional pero no siempre la encuentras",
                "Cuidas a otros pero no siempre te cuidas a ti"
            ]
        },
        'Mercurio': {
            'exilio': [
                "Tu mente vaga dispersa, cuesta concentrar",
                "Hablas mucho pero comunicas poco esencial",
                "Ideas abstractas te fascinan pero no concluyes",
                "Piensas en grande pero pierdes los detalles"
            ],
            'default': [
                "Tu mente es tu herramienta principal",
                "Necesitas variedad intelectual para no aburrirte",
                "Comunicas mejor escribiendo que hablando (o viceversa)"
            ]
        },
        'Venus': {
            'exilio': [
                "Atraes pero no retienes (o viceversa)",
                "Relaciones intensas pero conflictivas",
                "Valoras lo que es difícil de conseguir",
                "El amor duele más de lo que debería"
            ],
            'caida': [
                "Perfeccionismo tóxico en relaciones",
                "Criticas lo que amas",
                "Servicio que agota en lugar de nutrir",
                "Dificultad para recibir afecto"
            ],
            'default': [
                "Buscas belleza y armonía a tu manera",
                "Tus vínculos son importantes pero complejos",
                "El dinero/placer tienen significado emocional profundo"
            ]
        },
        'Marte': {
            'exaltacion': [
                "Tu fuerza de voluntad es monumental",
                "Cuando decides algo, lo sostienes años",
                "Defiendes causas/personas con lealtad férrea",
                "Planificas batallas, no improvisas"
            ],
            'exilio': [
                "Te cuesta ser asertivo directamente",
                "Pasividad externa, resentimiento interno",
                "Evitas conflicto hasta que explotas",
                "Fuerza se expresa en aguante, no en ataque"
            ],
            'caida': [
                "Intensidad emocional que desborda",
                "Impulsos difíciles de controlar",
                "Defendes a los tuyos con ferocidad extrema",
                "Ira se enquista si no se canaliza"
            ],
            'default': [
                "Actúas cuando algo te importa de verdad",
                "Tu coraje emerge en crisis",
                "Necesitas sentir que luchas por algo justo"
            ]
        }
    }
    
    planeta_manif = manifestaciones_base.get(nombre, {})
    return planeta_manif.get(dignidad, planeta_manif.get('default', ["Tu " + nombre + " se expresa de forma particular"]))


def generar_tikun_planeta(nombre: str, dignidad: str, genio: dict) -> list:
    """Genera tikún específico por planeta."""
    
    genio_nombre = genio.get('nombre', 'N/A')
    salmo = genio.get('salmo', 0)
    
    tikun_base = {
        'Sol': {
            'exilio': [
                f"Ritual solar cada domingo: afirmar tu valor intrínseco",
                f"Escribe 3 logros semanales que solo tú reconozcas",
                f"Invoca a {genio_nombre} cuando dudes de ti",
                f"Salmo {salmo} al despertar durante 40 días"
            ],
            'default': [
                f"Identifica tu propósito central (Tiphareth)",
                f"Actúa desde el centro, no desde la periferia",
                f"Salmo {salmo} cuando necesites claridad de misión"
            ]
        },
        'Luna': {
            'exilio': [
                f"Diario emocional nocturno (sin análisis)",
                f"Ritual lunar en menguante: soltar rigidez",
                f"Contacto con agua como práctica semanal",
                f"Salmo {salmo} cuando el corazón se cierre"
            ],
            'default': [
                f"Honra tus ciclos emocionales",
                f"Crea espacio sagrado de refugio",
                f"Salmo {salmo} en luna nueva y llena"
            ]
        },
        'Mercurio': {
            'exilio': [
                f"Escritura estructurada diaria (100 palabras máximo)",
                f"Resumen de 3 ideas clave cada noche",
                f"Invoca a {genio_nombre} antes de comunicar algo importante",
                f"Salmo {salmo} cuando la mente se disperse"
            ],
            'default': [
                f"Usa el verbo con precisión quirúrgica",
                f"Mensajero de Hod: conecta verdad con forma",
                f"Salmo {salmo} antes de decisiones importantes"
            ]
        },
        'Venus': {
            'exilio': [
                f"Ritual venusino cada viernes: acto de belleza/amor",
                f"Regalo anónimo mensual (sin esperar retorno)",
                f"Invoca a {genio_nombre} (Amor Divino)",
                f"Salmo {salmo} cuando el corazón se endurezca"
            ],
            'caida': [
                f"Lista diaria: 3 cosas imperfectas que amas",
                f"Perdona un defecto ajeno cada semana",
                f"Salmo {salmo} contra perfeccionismo tóxico"
            ],
            'default': [
                f"Cultiva belleza sin apego al resultado",
                f"Ama desde Netzach (eternidad), no desde carencia",
                f"Salmo {salmo} en conflictos relacionales"
            ]
        },
        'Marte': {
            'exaltacion': [
                f"Canaliza fuerza en proyectos constructivos",
                f"No conviertas todo en batalla",
                f"Salmo {salmo} cuando la voluntad se endurezca"
            ],
            'exilio': [
                f"Di 'no' una vez al día durante 21 días",
                f"Practica asertividad en situaciones seguras",
                f"Recupera tu espada interior (Geburah)",
                f"Salmo {salmo} antes de confrontaciones necesarias"
            ],
            'caida': [
                f"Ejercicio físico intenso 3x/semana (canalización)",
                f"Pausa de 10 segundos antes de reaccionar",
                f"Salmo {salmo} cuando la ira emerja"
            ],
            'default': [
                f"Usa la fuerza solo cuando sea justo",
                f"Espada de Geburah: corta lo que no sirve",
                f"Salmo {salmo} antes de acciones importantes"
            ]
        }
    }
    
    planeta_tikun = tikun_base.get(nombre, {})
    return planeta_tikun.get(dignidad, planeta_tikun.get('default', [f"Trabaja conscientemente con {nombre}"]))


# ============================================================================
# FASE 6: TRIPLE LECTURA II (Planetas 6-10)
# ============================================================================

def generar_fase_6_triple_lectura_ii(analisis_savp: dict) -> str:
    """
    Fase 6: Lectura profunda de Jupiter, Saturno, Urano, Neptuno, Plutón.
    """
    planetas = analisis_savp.get('planetas_savp', {})
    
    texto = """
═══════════════════════════════════════════════════════════════════
FASE 6: TRIPLE LECTURA II (Planetas Transpersonales)
═══════════════════════════════════════════════════════════════════

Lectura profunda de los 5 planetas sociales y transpersonales:
♃ Júpiter, ♄ Saturno, ♅ Urano, ♆ Neptuno, ♇ Plutón

───────────────────────────────────────────────────────────────────

"""
    
    planetas_fase6 = ['Jupiter', 'Saturno', 'Urano', 'Neptuno', 'Pluton']
    simbolos = {'Jupiter': '♃', 'Saturno': '♄', 'Urano': '♅', 'Neptuno': '♆', 'Pluton': '♇'}
    
    for nombre in planetas_fase6:
        if nombre not in planetas:
            continue
        
        p_data = planetas[nombre]
        astro = p_data.get('astronomico', {})
        seph = p_data.get('sephirah', 'N/A')
        genio = p_data.get('genio', {})
        pond = p_data.get('ponderacion', {})
        
        grado = astro.get('grado', 0)
        signo = astro.get('signo', 'N/A')
        casa = astro.get('casa', 0)
        retro = " ℞" if astro.get('retrogrado') else ""
        dignidad = pond.get('dignidad', 'peregrino')
        peso = pond.get('peso_final', 0)
        
        dign_emoji = {'domicilio': '👑', 'exaltacion': '✨', 'exilio': '🚫', 'caida': '⬇️', 'peregrino': '⚪'}
        emoji = dign_emoji.get(dignidad, '⚪')
        
        texto += f"""
{simbolos[nombre]} {nombre.upper()} — {grado:.1f}° {signo}, Casa {casa}{retro}

PROYECCIÓN SEPHIRÓTICA
{seph}. Genio #{genio.get('numero')} {genio.get('nombre')}.
{emoji} {dignidad.capitalize()} ({peso:.2f} pts).

¿CÓMO SE VIVE?
"""
        
        # Manifestaciones transpersonales
        manifestaciones_trans = generar_manifestaciones_transpersonales(nombre, dignidad, casa)
        for manif in manifestaciones_trans:
            texto += f"• {manif}\n"
        
        texto += f"""
TIKÚN
"""
        
        tikun_trans = generar_tikun_transpersonal(nombre, dignidad, genio)
        for item in tikun_trans:
            texto += f"→ {item}\n"
        
        texto += "\n" + "─" * 67 + "\n"
    
    texto += """
═══════════════════════════════════════════════════════════════════

✓ Fase 6 completada

¿Continuar con Fase 7: EJE NODAL (Karma y Destino)?

═══════════════════════════════════════════════════════════════════
"""
    
    return texto


def generar_manifestaciones_transpersonales(nombre: str, dignidad: str, casa: int) -> list:
    """Manifestaciones para planetas transpersonales."""
    
    base = {
        'Jupiter': [
            "Expandes donde otros contraen",
            "Tu optimismo es contagioso (o ingenuo, según el contexto)",
            "Crees en posibilidades que otros no ven",
            "La abundancia llega cuando no la fuerzas"
        ],
        'Saturno': [
            "Estructura es tu lenguaje natural",
            "Ves límites donde otros ven libertad",
            "Tu disciplina es tu mayor fortaleza y tu prisión",
            "El tiempo es tu aliado, la prisa tu enemigo"
        ],
        'Urano': [
            "Rompes patrones sin pedir permiso",
            "Tu originalidad incomoda a sistemas rígidos",
            "Insights súbitos cambian tu dirección",
            "Libertad es no-negociable para ti"
        ],
        'Neptuno': [
            "Percibes lo sutil que otros no captan",
            "Límites se disuelven en tu presencia",
            "Sueñas realidades que luego manifiestas (o te pierdes en ellas)",
            "Compasión universal pero vulnerable a engaño"
        ],
        'Pluton': [
            "Transformas lo que tocas (incluido a ti)",
            "Ves lo oculto bajo las apariencias",
            "Poder te atrae pero también te asusta",
            "Muerte y renacimiento son tu ciclo natural"
        ]
    }
    
    return base.get(nombre, ["Este planeta opera en capas profundas de tu psique"])


def generar_tikun_transpersonal(nombre: str, dignidad: str, genio: dict) -> list:
    """Tikún para transpersonales."""
    
    salmo = genio.get('salmo', 0)
    
    base = {
        'Jupiter': [
            f"Expande con discernimiento (Chesed equilibrado)",
            f"Generosidad sin ingenuidad",
            f"Salmo {salmo} cuando dudes de la abundancia"
        ],
        'Saturno': [
            f"Construye sin rigidez (Binah flexible)",
            f"Disciplina que libera, no que encarcela",
            f"Salmo {salmo} cuando el peso sea excesivo"
        ],
        'Urano': [
            f"Innova sin destruir lo válido (Chokmah)",
            f"Libertad responsable",
            f"Salmo {salmo} cuando la rebeldía sea reactiva"
        ],
        'Neptuno': [
            f"Sueña con los pies en la tierra (Kether anclado)",
            f"Compasión con límites",
            f"Salmo {salmo} contra ilusiones/engaños"
        ],
        'Pluton': [
            f"Transforma sin destruir el núcleo (Daath)",
            f"Poder al servicio de la vida",
            f"Salmo {salmo} en crisis transformativas"
        ]
    }
    
    return base.get(nombre, [f"Integra conscientemente {nombre}"])


# ============================================================================
# ACTUALIZAR FUNCIÓN generar_fase_completa
# ============================================================================

def generar_fase_completa_UPDATED(numero_fase: int, analisis_savp: dict, datos_natales: dict = None) -> str:
    """
    Genera el texto completo de una fase específica (ACTUALIZADO con Fases 5-6).
    """
    if numero_fase == 0:
        if not datos_natales:
            return "❌ Error: Se requieren datos_natales para Fase 0"
        resultado = generar_fase_0_verificacion(datos_natales)
        return resultado['tabla_confirmacion']
    
    elif numero_fase == 1:
        return generar_fase_1_proyeccion(analisis_savp)
    
    elif numero_fase == 2:
        return generar_fase_2_genios(analisis_savp)
    
    elif numero_fase == 3:
        return generar_fase_3_cadena(analisis_savp)
    
    elif numero_fase == 4:
        return generar_fase_4_senderos(analisis_savp)
    
    elif numero_fase == 5:
        return generar_fase_5_triple_lectura_i(analisis_savp)
    
    elif numero_fase == 6:
        return generar_fase_6_triple_lectura_ii(analisis_savp)
    
    elif numero_fase == 7:
        return generar_fase_7_eje_nodal(analisis_savp)
    
    elif numero_fase == 8:
        return generar_fase_8_aspectos(analisis_savp)
    
    elif numero_fase == 9:
        return generar_fase_9_vocacion(analisis_savp)
    
    elif numero_fase == 10:
        return generar_fase_10_conclusion(analisis_savp)
    
    else:
        return f"❌ Fase {numero_fase} no válida (rango 0-10)"


# Reemplazar función original
generar_fase_completa = generar_fase_completa_UPDATED
