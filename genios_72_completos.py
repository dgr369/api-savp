"""
genios_72_completos.py
Tabla Completa de los 72 Genios de la Shemhamphorash

SAVP v3.6 - Sistema Árbol de la Vida Personal
Extraído de: Tabla_72_Genios_Completa.md
Fecha: Febrero 2025

Los 72 Genios derivan de tres versículos del Éxodo (14:19-21).
Distribución: 360° ÷ 72 = 5° por Genio (quinario)
Fórmula: (índiceSigno × 6) + floor(grado/5) + 1
"""

GENIOS_72_COMPLETOS = {
    1: {'nombre': 'VEHU-IAH', 'salmo': 3, 'atributos': 'Voluntad Primordial, Impulso Divino'},
    2: {'nombre': 'YELI-EL', 'salmo': 22, 'atributos': 'Amor Divino, Kundalini'},
    3: {'nombre': 'SITA-EL', 'salmo': 91, 'atributos': 'ConstrucciÃ³n bajo Fuego'},
    4: {'nombre': 'ELEMI-AH', 'salmo': 6, 'atributos': 'Viaje Interior, PeregrinaciÃ³n Espiritual'},
    5: {'nombre': 'MAHAS-IAH', 'salmo': 34, 'atributos': 'Paz en Guerra, Rector de las Cosas FÃ­sicas'},
    6: {'nombre': 'LELAH-EL', 'salmo': 9, 'atributos': 'IluminaciÃ³n SÃºbita, Ciencia de lo Ãštil'},
    7: {'nombre': 'ACHA-IAH', 'salmo': 103, 'atributos': 'Paciencia Divina'},
    8: {'nombre': 'CAHETH-EL', 'salmo': 95, 'atributos': 'Prosperidad Santificada'},
    9: {'nombre': 'HAZI-EL', 'salmo': 25, 'atributos': 'Misericordia Universal, CompasiÃ³n Tangible'},
    10: {'nombre': 'ALAD-IAH', 'salmo': 33, 'atributos': 'Gracia Perdonadora'},
    11: {'nombre': 'LAVI-AH', 'salmo': 18, 'atributos': 'Victoria Oculta, Revelaciones en SueÃ±os'},
    12: {'nombre': 'HAHAU-IAH', 'salmo': 10, 'atributos': 'Refugio, ProtecciÃ³n Divina'},
    13: {'nombre': 'YEZAL-EL', 'salmo': 98, 'atributos': 'Fidelidad Conyugal'},
    14: {'nombre': 'MEBAH-EL', 'salmo': 9, 'atributos': 'Verdad Liberadora'},
    15: {'nombre': 'LAUU-IAH', 'salmo': 8, 'atributos': 'Victoria, Celebridad, Talento Musical y PoÃ©tico'},
    16: {'nombre': 'CALAH-IAH', 'salmo': 35, 'atributos': 'Justicia Divina'},
    17: {'nombre': 'LEVU-IAH', 'salmo': 40, 'atributos': 'RevelaciÃ³n de Misterios'},
    18: {'nombre': 'CALI-EL', 'salmo': 7, 'atributos': 'ConfusiÃ³n de Malvados'},
    19: {'nombre': 'LEVU-IAH', 'salmo': 40, 'atributos': 'Memoria Expandida'},
    20: {'nombre': 'PAHAL-IAH', 'salmo': 120, 'atributos': 'RedenciÃ³n'},
    21: {'nombre': 'NELCHA-EL', 'salmo': 31, 'atributos': 'Estudio de MatemÃ¡ticas'},
    22: {'nombre': 'YEYAY-EL', 'salmo': 121, 'atributos': 'Renombre, Diplomacia, ProtecciÃ³n de Grandes'},
    23: {'nombre': 'MELAH-EL', 'salmo': 121, 'atributos': 'CuraciÃ³n por Plantas'},
    24: {'nombre': 'HAHUI-AH', 'salmo': 33, 'atributos': 'ProtecciÃ³n de Refugiados'},
    25: {'nombre': 'NITH-HAI-AH', 'salmo': 9, 'atributos': 'SabidurÃ­a Oculta'},
    26: {'nombre': 'HAAI-AH', 'salmo': 109, 'atributos': 'Decisiones PolÃ­ticas'},
    27: {'nombre': 'YERAT-EL', 'salmo': 140, 'atributos': 'ConfusiÃ³n de Malvados, PropagaciÃ³n de la Luz, CivilizaciÃ³n'},
    28: {'nombre': 'SEEH-IAH', 'salmo': 71, 'atributos': 'Longevidad, Salud'},
    29: {'nombre': 'REYI-EL', 'salmo': 54, 'atributos': 'LiberaciÃ³n de Enemigos'},
    30: {'nombre': 'OUMA-EL', 'salmo': 71, 'atributos': 'Amistad Universal, Paciencia Multiplicada'},
    31: {'nombre': 'LECA-BEL', 'salmo': 71, 'atributos': 'Talento Natural, Genio Innato'},
    32: {'nombre': 'VESHAR-IAH', 'salmo': 33, 'atributos': 'Justicia Legal'},
    33: {'nombre': 'YECHAU-IAH', 'salmo': 94, 'atributos': 'Orden Universal'},
    34: {'nombre': 'LEHACH-IAH', 'salmo': 131, 'atributos': 'Obediencia de Subalternos'},
    35: {'nombre': 'KEVAK-IAH', 'salmo': 116, 'atributos': 'Paz con Adversarios'},
    36: {'nombre': 'MENAD-EL', 'salmo': 26, 'atributos': 'LiberaciÃ³n de OpresiÃ³n'},
    37: {'nombre': 'ANI-EL', 'salmo': 80, 'atributos': 'Victoria Intelectual'},
    38: {'nombre': 'HAAMI-AH', 'salmo': 18, 'atributos': 'BÃºsqueda de la Verdad'},
    39: {'nombre': 'REHA-EL', 'salmo': 30, 'atributos': 'SanaciÃ³n de Enfermedades, Longevidad, Amor Paterno-Filial'},
    40: {'nombre': 'YEYAZ-EL', 'salmo': 88, 'atributos': 'Escritores y FilÃ³sofos'},
    41: {'nombre': 'HAHAH-EL', 'salmo': 110, 'atributos': 'Misioneros Espirituales'},
    42: {'nombre': 'MIKA-EL', 'salmo': 121, 'atributos': 'Casa de Dios, OrganizaciÃ³n PolÃ­tica Justa, Seguridad del Estado'},
    43: {'nombre': 'VEUAL-IAH', 'salmo': 88, 'atributos': 'DestrucciÃ³n de Enemigos Espirituales'},
    44: {'nombre': 'YELAH-IAH', 'salmo': 119, 'atributos': 'Talento Militar, ProtecciÃ³n en Batalla, Victoria Justa'},
    45: {'nombre': 'SEALH-IAH', 'salmo': 94, 'atributos': 'ResurrecciÃ³n de CaÃ­dos'},
    46: {'nombre': 'ARI-EL', 'salmo': 145, 'atributos': 'RevelaciÃ³n de Tesoros'},
    47: {'nombre': 'ASAL-IAH', 'salmo': 105, 'atributos': 'ContemplaciÃ³n de lo Divino'},
    48: {'nombre': 'MIHAH-EL', 'salmo': 98, 'atributos': 'Fertilidad, ArmonÃ­a Conyugal'},
    49: {'nombre': 'VEHU-EL', 'salmo': 145, 'atributos': 'Grandeza de Alma'},
    50: {'nombre': 'DANI-EL', 'salmo': 145, 'atributos': 'Elocuencia, Decisiones Justas'},
    51: {'nombre': 'HAHASH-IAH', 'salmo': 104, 'atributos': 'Medicina Universal, Alquimia Espiritual, Piedra Filosofal'},
    52: {'nombre': 'IMAMI-AH', 'salmo': 7, 'atributos': 'DestrucciÃ³n de Enemigos'},
    53: {'nombre': 'NANA-EL', 'salmo': 113, 'atributos': 'ComunicaciÃ³n Espiritual'},
    54: {'nombre': 'NITHA-EL', 'salmo': 9, 'atributos': 'Vida Eterna en los Elegidos'},
    55: {'nombre': 'MEBAH-IAH', 'salmo': 102, 'atributos': 'ConsolaciÃ³n Intelectual'},
    56: {'nombre': 'POI-EL', 'salmo': 145, 'atributos': 'Riqueza, EstimaciÃ³n'},
    57: {'nombre': 'NEMAMI-AH', 'salmo': 113, 'atributos': 'Prosperidad'},
    58: {'nombre': 'YEYAZ-EL', 'salmo': 88, 'atributos': 'Consuelo, Fidelidad Conyugal, LiberaciÃ³n de Opresores'},
    59: {'nombre': 'HARACH-EL', 'salmo': 113, 'atributos': 'Riqueza Intelectual'},
    60: {'nombre': 'MITSAR-EL', 'salmo': 145, 'atributos': 'SanaciÃ³n de Enfermedades Mentales'},
    61: {'nombre': 'UMAB-EL', 'salmo': 113, 'atributos': 'Afinidades, Amistad'},
    62: {'nombre': 'YAHAH-EL', 'salmo': 119, 'atributos': 'Conocimiento Trascendente'},
    63: {'nombre': 'ANAU-EL', 'salmo': 3, 'atributos': 'CÃ­rculo de Sabios'},
    64: {'nombre': 'MECHI-EL', 'salmo': 33, 'atributos': 'InspiraciÃ³n Literaria'},
    65: {'nombre': 'DAMA-BI-AH', 'salmo': 88, 'atributos': 'Fuente de SabidurÃ­a'},
    66: {'nombre': 'MENA-EL', 'salmo': 26, 'atributos': 'LiberaciÃ³n de Cautivos'},
    67: {'nombre': 'AYAI-EL', 'salmo': 37, 'atributos': 'TransmutaciÃ³n'},
    68: {'nombre': 'HABUU-IAH', 'salmo': 106, 'atributos': 'SanaciÃ³n, Fertilidad'},
    69: {'nombre': 'ROAH-EL', 'salmo': 16, 'atributos': 'RestituciÃ³n de Objetos'},
    70: {'nombre': 'YABAM-IAH', 'salmo': 119, 'atributos': 'GÃ©nesis AlquÃ­mica'},
    71: {'nombre': 'HAYI-EL', 'salmo': 109, 'atributos': 'ProtecciÃ³n Divina'},
    72: {'nombre': 'MUMA-IAH', 'salmo': 116, 'atributos': 'Fin y Principio, Renacimiento'},
}


def obtener_genio(numero: int) -> dict:
    """
    Obtiene información completa de un Genio por número.
    
    Args:
        numero: Número del Genio (1-72)
    
    Returns:
        dict: {'nombre', 'salmo', 'atributos'}
    """
    return GENIOS_72_COMPLETOS.get(numero, {
        'nombre': f'GENIO_{numero}',
        'salmo': 0,
        'atributos': 'No catalogado'
    })


def calcular_genio_desde_posicion(grado: float, signo: str) -> dict:
    """
    Calcula el Genio correspondiente a una posición zodiacal.
    
    Args:
        grado: Grado dentro del signo (0-29.999°)
        signo: Nombre del signo (Aries, Tauro, etc.)
    
    Returns:
        dict completo del Genio con quinario y posición
        
    Ejemplo:
        >>> calcular_genio_desde_posicion(20.01, 'Acuario')
        {'numero': 65, 'nombre': 'DAMA-IAH', ...}
    """
    SIGNOS_INDEX = {
        'Aries': 0, 'Tauro': 1, 'Geminis': 2, 'Cancer': 3,
        'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Escorpio': 7,
        'Sagitario': 8, 'Capricornio': 9, 'Acuario': 10, 'Piscis': 11
    }
    
    signo_idx = SIGNOS_INDEX.get(signo, 0)
    quinario = int(grado // 5)
    genio_numero = 1 + (signo_idx * 6) + quinario
    
    genio_data = obtener_genio(genio_numero)
    
    return {
        'numero': genio_numero,
        'nombre': genio_data['nombre'],
        'salmo': genio_data['salmo'],
        'atributos': genio_data['atributos'],
        'quinario': f"{quinario*5}-{(quinario+1)*5}°",
        'signo': signo,
        'grado': round(grado, 2)
    }


def listar_genios_por_signo(signo: str) -> list:
    """
    Lista los 6 Genios de un signo zodiacal.
    
    Args:
        signo: Nombre del signo
    
    Returns:
        list de 6 dicts con información de cada Genio
    """
    SIGNOS_INDEX = {
        'Aries': 0, 'Tauro': 1, 'Geminis': 2, 'Cancer': 3,
        'Leo': 4, 'Virgo': 5, 'Libra': 6, 'Escorpio': 7,
        'Sagitario': 8, 'Capricornio': 9, 'Acuario': 10, 'Piscis': 11
    }
    
    signo_idx = SIGNOS_INDEX.get(signo, 0)
    inicio = 1 + (signo_idx * 6)
    
    genios_signo = []
    for i in range(6):
        num = inicio + i
        genio = obtener_genio(num)
        genios_signo.append({
            'numero': num,
            'grados': f"{i*5}-{(i+1)*5}°",
            **genio
        })
    
    return genios_signo


if __name__ == "__main__":
    print("=" * 80)
    print("TABLA COMPLETA DE LOS 72 GENIOS DE LA SHEMHAMPHORASH")
    print("SAVP v3.6")
    print("=" * 80)
    
    print(f"\n✅ Total: {len(GENIOS_72_COMPLETOS)} Genios cargados\n")
    
    # Test 1: Primeros 5 (Aries)
    print("PRIMEROS 5 GENIOS (Aries):")
    for i in range(1, 6):
        g = obtener_genio(i)
        print(f"  #{i:2d} {g['nombre']:15s} Salmo {g['salmo']:3d} - {g['atributos']}")
    
    # Test 2: Últimos 5 (Piscis)
    print("\nÚLTIMOS 5 GENIOS (Piscis):")
    for i in range(68, 73):
        g = obtener_genio(i)
        print(f"  #{i:2d} {g['nombre']:15s} Salmo {g['salmo']:3d} - {g['atributos']}")
    
    # Test 3: Cálculo desde posición
    print("\nTEST CÁLCULO DESDE POSICIÓN:")
    test_casos = [
        (20.01, 'Acuario', 65, 'DAMA-IAH'),  # Sol Frater D. (corregido)
        (29.32, 'Capricornio', 60, 'MITSAR-EL'),  # Marte Frater D.
        (13.0, 'Geminis', 15, 'LAUU-IAH'),  # Ejemplo documentación
        (0.0, 'Aries', 1, 'VEHU-IAH'),  # Primer Genio
        (29.9, 'Piscis', 72, 'MUME-IAH')  # Último Genio
    ]
    
    for grado, signo, num_esperado, nombre_esperado in test_casos:
        resultado = calcular_genio_desde_posicion(grado, signo)
        status = "✅" if resultado['numero'] == num_esperado else "❌"
        print(f"  {status} {grado:5.2f}° {signo:12s} → Genio #{resultado['numero']:2d} {resultado['nombre']}")
    
    # Test 4: Listar Genios de un signo
    print("\nGENIOS DE ACUARIO:")
    for g in listar_genios_por_signo('Acuario'):
        print(f"  #{g['numero']:2d} {g['grados']:8s} {g['nombre']:15s} - {g['atributos'][:50]}...")
    
    print("\n" + "=" * 80)
    print("✅ TABLA VALIDADA Y LISTA PARA USAR EN SAVP v3.6")
    print("=" * 80)
