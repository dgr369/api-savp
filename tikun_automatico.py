"""
tikun_automatico.py
Generación automática de Tikún diferenciado por tipología

SAVP v3.6 - Sistema Árbol de la Vida Personal
Fecha: Febrero 2025

Genera recomendaciones específicas según:
- Tipología detectada (gobierno único, hábito múltiple, etc.)
- Debilidades planetarias
- Senderos críticos
- Convergencias en cadena
"""

from typing import Dict, List, Optional


# ============================================================================
# PLANTILLAS DE TIKÚN POR TIPOLOGÍA
# ============================================================================

TIKUN_TIPOLOGIAS = {
    'gobierno_unico': {
        'descripcion': 'Un solo planeta en domicilio concentra todo el poder',
        'riesgo': 'Despotismo interior, falta de flexibilidad',
        'tikun_base': 'Ética del poder - Reflexión sobre uso responsable',
        'practica': 'Diario de gobierno: ¿Cómo usé mi poder hoy?',
        'duracion': '7 semanas (49 días)',
        'ritual': 'Meditación semanal sobre virtud opuesta al planeta dominante'
    },
    
    'habito_multiple': {
        'descripcion': 'Múltiples planetas en exilio/caída = desgaste continuo',
        'riesgo': 'Autosabotaje por patrones destructivos arraigados',
        'tikun_base': 'Consistencia práctica - Romper cadenas de hábito',
        'practica': 'Ritual diario mínimo (5 min) durante 40 días consecutivos',
        'duracion': '40 días (ciclo alquímico)',
        'ritual': 'Práctica planetaria del planeta más débil'
    },
    
    'equilibrio': {
        'descripcion': 'Distribución balanceada, sin dominancias extremas',
        'riesgo': 'Falta de foco, dispersión energética',
        'tikun_base': 'Elección consciente - Priorizar sin desequilibrar',
        'practica': 'Proyecto de 3 meses enfocado en un pilar específico',
        'duracion': '90 días (ciclo trimestral)',
        'ritual': 'Revisión mensual de balance entre pilares'
    },
    
    'pilar_dominante': {
        'descripcion': 'Un pilar >45% del peso total',
        'riesgo': 'Unilateralidad, compensación reactiva',
        'tikun_base': 'Integración de opuesto - Fortalecer pilar débil',
        'practica': 'Ejercicio semanal del pilar opuesto',
        'duracion': '13 semanas (trimestre lunar)',
        'ritual': 'Invocación de Sephiroth del pilar débil'
    }
}


# ============================================================================
# TIKÚN POR PLANETA DÉBIL
# ============================================================================

TIKUN_PLANETAS_DEBILES = {
    'Sol': {
        'exilio': {
            'problema': 'Identidad difusa, falta de brillo personal',
            'tikun': 'Ritual solar dominical - Afirmación de identidad',
            'practica': 'Escribir 3 logros semanales cada domingo',
            'genio_recomendado': 'Cualquier genio solar del signo opuesto (Leo)',
            'duracion': '40 días'
        },
        'caida': {
            'problema': 'Autoestima condicionada por aprobación externa',
            'tikun': 'Desapego de validación - Centramiento interior',
            'practica': 'Meditación diaria: "Soy completo sin validación"',
            'duracion': '28 días (ciclo lunar)'
        }
    },
    
    'Luna': {
        'exilio': {
            'problema': 'Desconexión emocional, rigidez afectiva',
            'tikun': 'Ritual lunar - Reconexión con ciclos emocionales',
            'practica': 'Diario de emociones diario durante luna menguante',
            'genio_recomendado': 'MIKA-EL (Casa de Dios)',
            'duracion': '1 ciclo lunar completo (29 días)'
        },
        'caida': {
            'problema': 'Emociones tóxicas, resentimiento profundo',
            'tikun': 'Limpieza emocional - Perdón activo',
            'practica': 'Carta de perdón (sin enviar) cada semana',
            'duracion': '7 semanas'
        }
    },
    
    'Mercurio': {
        'exilio': {
            'problema': 'Pensamiento confuso, comunicación ineficaz',
            'tikun': 'Claridad mental - Escritura estructurada',
            'practica': 'Resumen diario de 3 ideas clave (100 palabras)',
            'genio_recomendado': 'MECHI-EL (Inspiración literaria)',
            'duracion': '40 días'
        }
    },
    
    'Venus': {
        'exilio': {
            'problema': 'Dificultad para amar y ser amado, aridez afectiva',
            'tikun': 'Ritual venusino viernes - Cultivo de belleza',
            'practica': 'Acto de belleza/amor semanal (arte, regalo, servicio)',
            'genio_recomendado': 'YELI-EL (Amor Divino)',
            'duracion': '7 viernes consecutivos'
        },
        'caida': {
            'problema': 'Perfeccionismo tóxico en relaciones',
            'tikun': 'Aceptación de imperfección - Amor incondicional',
            'practica': 'Lista diaria: 3 cosas imperfectas que amo',
            'duracion': '30 días'
        }
    },
    
    'Marte': {
        'exilio': {
            'problema': 'Pasividad, falta de asertividad',
            'tikun': 'Recuperación de espada - Asertividad justa',
            'practica': 'Decir "no" una vez al día durante una semana',
            'genio_recomendado': 'MITSAR-EL (Sanación mental)',
            'duracion': '21 días'
        },
        'caida': {
            'problema': 'Agresividad reactiva, ira descontrolada',
            'tikun': 'Canalización marciana - Fuerza constructiva',
            'practica': 'Ejercicio físico intenso 3x/semana',
            'duracion': '40 días'
        }
    },
    
    'Jupiter': {
        'exilio': {
            'problema': 'Pesimismo, falta de fe en expansión',
            'tikun': 'Ritual jupiterino jueves - Cultivo de abundancia',
            'practica': 'Lista semanal: 10 bendiciones recibidas',
            'genio_recomendado': 'LAVI-AH (Victoria oculta)',
            'duracion': '12 jueves (trimestre)'
        }
    },
    
    'Saturno': {
        'exilio': {
            'problema': 'Falta de estructura, procrastinación crónica',
            'tikun': 'Disciplina saturnina - Construcción de hábitos',
            'practica': 'Horario fijo diario (despertar, comidas, dormir)',
            'genio_recomendado': 'YERA-EL (Difusión de luces)',
            'duracion': '90 días (consolidación de hábito)'
        }
    }
}


# ============================================================================
# TIKÚN POR SENDERO CRÍTICO
# ============================================================================

TIKUN_SENDEROS_CRITICOS = {
    16: {  # La Torre
        'nombre': 'La Torre',
        'problema': 'Destrucción sin discernimiento',
        'tikun': 'Usar mente-espada con compasión',
        'practica': 'Antes de criticar: ¿Es verdad? ¿Es necesario? ¿Es amable?',
        'genio': 'MITSAR-EL (Sanación mental)',
        'duracion': '40 días'
    },
    
    14: {  # Templanza
        'nombre': 'Templanza',
        'problema': 'Alquimia sin dirección',
        'tikun': 'Uso consciente del don natural',
        'practica': 'Meditación activa diaria + escritura automática semanal',
        'genio': 'Genio del ASC (punto de manifestación)',
        'duracion': '28 días (ciclo lunar)'
    },
    
    6: {  # Los Enamorados
        'nombre': 'Los Enamorados',
        'problema': 'Elección forzada, dualidad dolorosa',
        'tikun': 'Integrar, no elegir - Síntesis de opuestos',
        'practica': 'Proyecto que requiera ambas energías (ej: creatividad + disciplina)',
        'genio': 'Genios de ambos planetas involucrados',
        'duracion': '40 días'
    },
    
    27: {  # La Torre (Netzach-Hod)
        'nombre': 'La Torre',
        'problema': 'Conflicto mente-deseo',
        'tikun': 'Integración razón-emoción',
        'practica': 'Decisiones importantes: consultar cabeza Y corazón',
        'genio': 'MITSAR-EL',
        'duracion': '21 días'
    },
    
    15: {  # El Diablo
        'nombre': 'El Diablo',
        'problema': 'Apego material, esclavitud al deseo',
        'tikun': 'Desapego consciente - Uso correcto de lo material',
        'practica': 'Ayuno semanal (comida/tecnología/placeres)',
        'genio': 'VEHU-IAH (Voluntad primordial)',
        'duracion': '40 días'
    }
}


# ============================================================================
# TIKÚN POR CONVERGENCIA
# ============================================================================

def generar_tikun_convergencia(planeta_hub: str, num_entradas: int, peso_hub: float) -> dict:
    """
    Genera Tikún para planeta convergencia (múltiples dispositores).
    
    Args:
        planeta_hub: Nombre del planeta convergencia
        num_entradas: Número de planetas que desembocan
        peso_hub: Peso del planeta hub
    
    Returns:
        dict con Tikún específico
    """
    presion = num_entradas / peso_hub if peso_hub > 0 else 999
    
    if presion > 5:  # Presión crítica
        urgencia = 'CRÍTICA'
        problema = f'Sobrecarga extrema: {num_entradas} entradas, peso {peso_hub:.2f}'
        tikun = f'Desbloqueo urgente de {planeta_hub} - Ritual intensivo'
        practica = f'Ritual diario de {planeta_hub.lower()} durante 40 días SIN EXCEPCIÓN'
    elif presion > 3:  # Presión alta
        urgencia = 'ALTA'
        problema = f'Cuello de botella: {num_entradas} entradas, peso {peso_hub:.2f}'
        tikun = f'Fortalecer {planeta_hub} - Práctica semanal'
        practica = f'Ritual de {planeta_hub.lower()} cada semana (día planetario)'
    else:
        urgencia = 'MEDIA'
        problema = f'Convergencia moderada: {num_entradas} entradas'
        tikun = f'Atender {planeta_hub} conscientemente'
        practica = f'Revisión mensual de {planeta_hub.lower()}'
    
    return {
        'tipo': 'convergencia',
        'planeta': planeta_hub,
        'urgencia': urgencia,
        'problema': problema,
        'tikun': tikun,
        'practica': practica,
        'duracion': '40 días' if urgencia == 'CRÍTICA' else '90 días',
        'metrica': f'Presión hidráulica: {presion:.2f} (entradas/peso)'
    }


# ============================================================================
# GENERADOR PRINCIPAL
# ============================================================================

def generar_tikun_completo(analisis_savp: dict) -> dict:
    """
    Genera Tikún completo y diferenciado para una carta.
    
    Args:
        analisis_savp: Resultado completo de procesar_carta_savp_v36_completa()
    
    Returns:
        dict con Tikún jerarquizado y priorizado
    """
    tikun_completo = {
        'resumen': '',
        'urgencia_maxima': 'BAJA',
        'tikun_primario': None,
        'tikun_secundario': [],
        'practicas_diarias': [],
        'practicas_semanales': [],
        'rituales_mensuales': [],
        'duracion_total': '90 días (mínimo)'
    }
    
    # 1. TIKÚN POR TIPOLOGÍA
    diagnostico = analisis_savp.get('diagnostico', {})
    tipo = diagnostico.get('tipo', 'equilibrio')
    
    if tipo in TIKUN_TIPOLOGIAS:
        tikun_tipo = TIKUN_TIPOLOGIAS[tipo].copy()
        tikun_completo['tikun_primario'] = {
            'tipo': 'tipologia',
            'nombre': tipo,
            **tikun_tipo
        }
    
    # 2. TIKÚN POR CONVERGENCIAS
    cadena = analisis_savp.get('cadena_dispositores', {})
    convergencias = cadena.get('convergencias', [])
    
    if convergencias:
        planetas = analisis_savp.get('planetas_savp', {})
        
        for conv in convergencias:
            # Contar entradas
            num_entradas = sum(
                1 for p_data in planetas.values()
                if p_data.get('ponderacion', {}).get('dispositor') == conv
            )
            
            peso_conv = planetas.get(conv, {}).get('ponderacion', {}).get('peso_final', 1.0)
            
            tikun_conv = generar_tikun_convergencia(conv, num_entradas, peso_conv)
            
            if tikun_conv['urgencia'] in ['CRÍTICA', 'ALTA']:
                tikun_completo['tikun_secundario'].insert(0, tikun_conv)
                tikun_completo['urgencia_maxima'] = 'ALTA'
            else:
                tikun_completo['tikun_secundario'].append(tikun_conv)
    
    # 3. TIKÚN POR SENDEROS CRÍTICOS
    senderos_criticos = analisis_savp.get('senderos_criticos_resumen', [])
    
    for sc in senderos_criticos[:3]:  # Top 3
        sendero = sc.get('sendero', {})
        arcano = sendero.get('arcano')
        
        if arcano in TIKUN_SENDEROS_CRITICOS:
            tikun_send = TIKUN_SENDEROS_CRITICOS[arcano].copy()
            tikun_send.update({
                'tipo': 'sendero_critico',
                'planetas_involucrados': sc.get('planetas', []),
                'peso_combinado': sc.get('peso_combinado', 0),
                'urgencia': sc.get('urgencia', 'MEDIA')
            })
            
            tikun_completo['tikun_secundario'].append(tikun_send)
    
    # 4. TIKÚN POR PLANETAS DÉBILES
    planetas = analisis_savp.get('planetas_savp', {})
    
    for nombre, data in planetas.items():
        if nombre in ['ASC', 'MC']:
            continue
        
        ponderacion = data.get('ponderacion', {})
        dignidad = ponderacion.get('dignidad')
        peso = ponderacion.get('peso_final', 1.0)
        
        if dignidad in ['exilio', 'caida'] and peso < 0.6:
            if nombre in TIKUN_PLANETAS_DEBILES:
                tikun_plan = TIKUN_PLANETAS_DEBILES[nombre].get(dignidad, {}).copy()
                if tikun_plan:
                    tikun_plan.update({
                        'tipo': 'planeta_debil',
                        'planeta': nombre,
                        'dignidad': dignidad,
                        'peso': peso,
                        'urgencia': 'ALTA' if peso < 0.4 else 'MEDIA'
                    })
                    tikun_completo['tikun_secundario'].append(tikun_plan)
    
    # 5. PRIORIZAR Y ORGANIZAR
    tikun_completo['tikun_secundario'].sort(
        key=lambda x: (
            {'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(x.get('urgencia', 'BAJA'), 3),
            -x.get('peso_combinado', x.get('peso', 0))
        )
    )
    
    # 6. GENERAR RESUMEN
    if tikun_completo['urgencia_maxima'] == 'ALTA':
        tikun_completo['resumen'] = 'Tikún de urgencia ALTA detectado. Acción inmediata requerida.'
    else:
        tikun_completo['resumen'] = 'Tikún de desarrollo gradual. Enfoque sostenido recomendado.'
    
    # 7. EXTRAER PRÁCTICAS
    for tikun in [tikun_completo['tikun_primario']] + tikun_completo['tikun_secundario']:
        if not tikun:
            continue
        
        practica = tikun.get('practica', '')
        if 'diario' in practica.lower() or 'cada día' in practica.lower():
            tikun_completo['practicas_diarias'].append({
                'practica': practica,
                'origen': tikun.get('tipo')
            })
        elif 'semanal' in practica.lower() or 'semana' in practica.lower():
            tikun_completo['practicas_semanales'].append({
                'practica': practica,
                'origen': tikun.get('tipo')
            })
        else:
            tikun_completo['rituales_mensuales'].append({
                'practica': practica,
                'origen': tikun.get('tipo')
            })
    
    return tikun_completo


if __name__ == "__main__":
    print("✅ Módulo tikun_automatico.py cargado correctamente")
    print(f"\nTipologías disponibles: {len(TIKUN_TIPOLOGIAS)}")
    print(f"Planetas con Tikún: {len(TIKUN_PLANETAS_DEBILES)}")
    print(f"Senderos con Tikún: {len(TIKUN_SENDEROS_CRITICOS)}")
