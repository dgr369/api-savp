"""
visualizaciones.py
Exportación de visualizaciones para SAVP v3.6

Genera:
- Grafos Mermaid (cadena de dispositores)
- SVG del Árbol de la Vida
- Tablas HTML interactivas

SAVP v3.6 - Sistema Árbol de la Vida Personal
Fecha: Febrero 2025
"""

from typing import Dict, List


# ============================================================================
# GRAFO MERMAID - CADENA DE DISPOSITORES
# ============================================================================

def exportar_grafo_mermaid(cadena: dict, planetas: dict) -> str:
    """
    Genera código Mermaid para visualizar cadena de dispositores.
    
    Args:
        cadena: Dict con nodos, convergencias, válvulas, bucles
        planetas: Dict con datos de planetas
    
    Returns:
        str: Código Mermaid listo para renderizar
    """
    lines = [
        "```mermaid",
        "graph TD",
        "  %% Cadena de Dispositores SAVP v3.6",
        ""
    ]
    
    nodos_info = cadena.get('nodos', {})
    convergencias = cadena.get('convergencias', [])
    valvulas = cadena.get('valvulas', [])
    motores = cadena.get('motores', [])
    
    # Definir nodos con estilos
    for nombre, info in nodos_info.items():
        peso = info.get('peso', 1.0)
        retro = info.get('retrogrado', False)
        
        # Determinar forma del nodo
        if nombre in motores:
            forma_inicio, forma_fin = "([", "])"  # Stadium
            clase = "motor"
        elif nombre in convergencias:
            forma_inicio, forma_fin = "{", "}"  # Rombo
            clase = "convergencia"
        elif nombre in valvulas:
            forma_inicio, forma_fin = "((", "))"  # Círculo doble
            clase = "valvula"
        else:
            forma_inicio, forma_fin = "[", "]"  # Rectángulo
            clase = "nodo"
        
        simbolo = "℞" if retro else ""
        label = f"{nombre}{simbolo}<br/>{peso:.2f}"
        
        lines.append(f"  {nombre}{forma_inicio}\"{label}\"{forma_fin}")
    
    lines.append("")
    
    # Definir conexiones
    for nombre, info in nodos_info.items():
        dispositor = info.get('dispositor')
        if dispositor:
            # Estilo de flecha según tipo
            if nombre in valvulas:
                estilo = "-.->|℞|"  # Línea punteada para válvulas
            else:
                estilo = "-->"
            
            lines.append(f"  {nombre} {estilo} {dispositor}")
    
    lines.append("")
    
    # Estilos CSS
    lines.extend([
        "  %% Estilos",
        "  classDef motor fill:#ffd700,stroke:#ff6347,stroke-width:3px",
        "  classDef convergencia fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px",
        "  classDef valvula fill:#4ecdc4,stroke:#1a535c,stroke-width:2px,stroke-dasharray: 5 5",
        "  classDef nodo fill:#95e1d3,stroke:#38ada9,stroke-width:2px",
        ""
    ])
    
    # Aplicar estilos
    if motores:
        lines.append(f"  class {','.join(motores)} motor")
    if convergencias:
        lines.append(f"  class {','.join(convergencias)} convergencia")
    if valvulas:
        lines.append(f"  class {','.join(valvulas)} valvula")
    
    lines.append("```")
    
    return "\n".join(lines)


# ============================================================================
# SVG - ÁRBOL DE LA VIDA CON PLANETAS
# ============================================================================

def exportar_arbol_svg(planetas: dict, ancho: int = 600, alto: int = 800) -> str:
    """
    Genera SVG del Árbol de la Vida con planetas posicionados.
    
    Args:
        planetas: Dict con planetas_savp
        ancho, alto: Dimensiones del SVG
    
    Returns:
        str: Código SVG completo
    """
    # Posiciones de las Sephiroth en el Árbol (coordenadas normalizadas 0-1)
    POSICIONES_SEPHIROTH = {
        'Kether': (0.5, 0.1),
        'Chokmah': (0.75, 0.25),
        'Binah': (0.25, 0.25),
        'Chesed': (0.75, 0.45),
        'Geburah': (0.25, 0.45),
        'Tiphareth': (0.5, 0.50),
        'Netzach': (0.75, 0.70),
        'Hod': (0.25, 0.70),
        'Yesod': (0.5, 0.85),
        'Malkuth': (0.5, 0.95),
        'Daath': (0.5, 0.35)  # Sephirah oculta
    }
    
    # Senderos (conexiones)
    SENDEROS = [
        ('Kether', 'Chokmah'), ('Kether', 'Binah'), ('Kether', 'Tiphareth'),
        ('Chokmah', 'Binah'), ('Chokmah', 'Tiphareth'), ('Chokmah', 'Chesed'),
        ('Binah', 'Tiphareth'), ('Binah', 'Geburah'),
        ('Chesed', 'Geburah'), ('Chesed', 'Tiphareth'), ('Chesed', 'Netzach'),
        ('Geburah', 'Tiphareth'), ('Geburah', 'Hod'),
        ('Tiphareth', 'Netzach'), ('Tiphareth', 'Yesod'), ('Tiphareth', 'Hod'),
        ('Netzach', 'Hod'), ('Netzach', 'Yesod'), ('Netzach', 'Malkuth'),
        ('Hod', 'Yesod'), ('Hod', 'Malkuth'),
        ('Yesod', 'Malkuth')
    ]
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}">',
        '  <defs>',
        '    <style>',
        '      .sendero { stroke: #bbb; stroke-width: 2; fill: none; }',
        '      .sephirah { fill: #fff; stroke: #333; stroke-width: 2; }',
        '      .sephirah-text { font-family: Arial; font-size: 12px; text-anchor: middle; }',
        '      .planeta { fill: #4a90e2; stroke: #2c5aa0; stroke-width: 2; }',
        '      .planeta-text { font-family: Arial; font-size: 14px; font-weight: bold; fill: #fff; text-anchor: middle; }',
        '      .peso-text { font-family: Arial; font-size: 10px; fill: #666; text-anchor: middle; }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Título -->',
        f'  <text x="{ancho/2}" y="30" style="font-size: 20px; font-weight: bold; text-anchor: middle;">',
        '    Árbol de la Vida Personal',
        '  </text>',
        '',
        '  <!-- Senderos -->',
        '  <g id="senderos">'
    ]
    
    # Dibujar senderos
    for s1, s2 in SENDEROS:
        x1, y1 = POSICIONES_SEPHIROTH[s1]
        x2, y2 = POSICIONES_SEPHIROTH[s2]
        svg_lines.append(
            f'    <line class="sendero" x1="{x1*ancho}" y1="{y1*alto}" x2="{x2*ancho}" y2="{y2*alto}" />'
        )
    
    svg_lines.extend([
        '  </g>',
        '',
        '  <!-- Sephiroth -->',
        '  <g id="sephiroth">'
    ])
    
    # Dibujar Sephiroth
    for seph, (x, y) in POSICIONES_SEPHIROTH.items():
        if seph == 'Daath':
            continue  # Opcional: no dibujar Daath
        
        cx, cy = x * ancho, y * alto
        svg_lines.extend([
            f'    <circle class="sephirah" cx="{cx}" cy="{cy}" r="30" />',
            f'    <text class="sephirah-text" x="{cx}" y="{cy + 5}">{seph}</text>'
        ])
    
    svg_lines.extend([
        '  </g>',
        '',
        '  <!-- Planetas -->',
        '  <g id="planetas">'
    ])
    
    # Contar planetas por Sephirah para posicionarlos sin solapamiento
    planetas_por_seph = {}
    for nombre, data in planetas.items():
        if nombre in ['ASC', 'MC']:
            continue
        seph = data.get('sephirah')
        if seph not in planetas_por_seph:
            planetas_por_seph[seph] = []
        planetas_por_seph[seph].append((nombre, data))
    
    # Dibujar planetas
    for seph, planetas_list in planetas_por_seph.items():
        if seph not in POSICIONES_SEPHIROTH:
            continue
        
        x_seph, y_seph = POSICIONES_SEPHIROTH[seph]
        cx_base, cy_base = x_seph * ancho, y_seph * alto
        
        num_planetas = len(planetas_list)
        offset = 50  # Distancia desde Sephirah
        
        for i, (nombre, data) in enumerate(planetas_list):
            # Posicionar en círculo alrededor de Sephirah
            angulo = (360 / num_planetas) * i
            import math
            rad = math.radians(angulo)
            cx = cx_base + offset * math.cos(rad)
            cy = cy_base + offset * math.sin(rad)
            
            peso = data.get('ponderacion', {}).get('peso_final', 1.0)
            retro = data.get('astronomico', {}).get('retrogrado', False)
            simbolo = "℞" if retro else ""
            
            svg_lines.extend([
                f'    <circle class="planeta" cx="{cx}" cy="{cy}" r="20" />',
                f'    <text class="planeta-text" x="{cx}" y="{cy + 5}">{nombre[0]}{simbolo}</text>',
                f'    <text class="peso-text" x="{cx}" y="{cy + 35}">{peso:.1f}</text>'
            ])
    
    svg_lines.extend([
        '  </g>',
        '</svg>'
    ])
    
    return "\n".join(svg_lines)


# ============================================================================
# TABLA HTML - SENDEROS
# ============================================================================

def exportar_tabla_senderos_html(senderos_criticos: list) -> str:
    """
    Genera tabla HTML interactiva con senderos críticos.
    
    Args:
        senderos_criticos: Lista de senderos con doble activación
    
    Returns:
        str: Código HTML completo
    """
    html = [
        '<!DOCTYPE html>',
        '<html lang="es">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Senderos Críticos - SAVP v3.6</title>',
        '  <style>',
        '    body { font-family: Arial, sans-serif; max-width: 1200px; margin: 40px auto; padding: 20px; }',
        '    h1 { color: #2c3e50; text-align: center; }',
        '    table { width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }',
        '    th { background: #3498db; color: white; padding: 12px; text-align: left; }',
        '    td { padding: 10px; border-bottom: 1px solid #ddd; }',
        '    tr:hover { background: #f5f5f5; }',
        '    .urgencia-ALTA { color: #e74c3c; font-weight: bold; }',
        '    .urgencia-MEDIA { color: #f39c12; }',
        '    .peso { font-size: 18px; font-weight: bold; color: #2c3e50; }',
        '    .arcano { font-style: italic; color: #7f8c8d; }',
        '  </style>',
        '</head>',
        '<body>',
        '  <h1>🜛 Senderos Críticos (Doble Activación)</h1>',
        '  <p style="text-align: center; color: #7f8c8d;">',
        f'    Total detectados: {len(senderos_criticos)} senderos con ocupación + aspecto',
        '  </p>',
        '',
        '  <table>',
        '    <thead>',
        '      <tr>',
        '        <th>#</th>',
        '        <th>Sendero</th>',
        '        <th>Planetas</th>',
        '        <th>Aspecto</th>',
        '        <th>Peso</th>',
        '        <th>Urgencia</th>',
        '      </tr>',
        '    </thead>',
        '    <tbody>'
    ]
    
    for i, sc in enumerate(senderos_criticos, 1):
        sendero = sc.get('sendero', {})
        num = sendero.get('numero', 0)
        nombre = sendero.get('nombre', 'N/A')
        arcano = sendero.get('arcano', 0)
        
        planetas = ' ↔ '.join(sc.get('planetas', []))
        aspecto = sc.get('aspecto', {})
        tipo_asp = aspecto.get('tipo', 'N/A')
        orbe = aspecto.get('orbe', 0)
        
        peso = sc.get('peso_combinado', 0)
        urgencia = sc.get('urgencia', 'MEDIA')
        
        html.extend([
            '      <tr>',
            f'        <td>{i}</td>',
            f'        <td><strong>#{num} {nombre}</strong><br/><span class="arcano">Arcano {arcano}</span></td>',
            f'        <td>{planetas}</td>',
            f'        <td>{tipo_asp} ({orbe:.2f}°)</td>',
            f'        <td class="peso">{peso:.2f}</td>',
            f'        <td class="urgencia-{urgencia}">{urgencia}</td>',
            '      </tr>'
        ])
    
    html.extend([
        '    </tbody>',
        '  </table>',
        '',
        '  <footer style="margin-top: 40px; text-align: center; color: #95a5a6; font-size: 12px;">',
        '    SAVP v3.6 - Sistema Árbol de la Vida Personal',
        '  </footer>',
        '</body>',
        '</html>'
    ])
    
    return "\n".join(html)


# ============================================================================
# FUNCIÓN PRINCIPAL: EXPORTAR TODO
# ============================================================================

def exportar_visualizaciones_completas(analisis_savp: dict) -> dict:
    """
    Genera todas las visualizaciones de una carta.
    
    Args:
        analisis_savp: Resultado de procesar_carta_savp_v36_completa()
    
    Returns:
        dict con código de cada visualización
    """
    cadena = analisis_savp.get('cadena_dispositores', {})
    planetas = analisis_savp.get('planetas_savp', {})
    senderos_criticos = analisis_savp.get('senderos_criticos_resumen', [])
    
    return {
        'grafo_mermaid': exportar_grafo_mermaid(cadena, planetas),
        'arbol_svg': exportar_arbol_svg(planetas),
        'tabla_senderos_html': exportar_tabla_senderos_html(senderos_criticos),
        'formatos_disponibles': ['mermaid', 'svg', 'html']
    }


if __name__ == "__main__":
    print("✅ Módulo visualizaciones.py cargado correctamente")
    print("\nFunciones disponibles:")
    print("  - exportar_grafo_mermaid()")
    print("  - exportar_arbol_svg()")
    print("  - exportar_tabla_senderos_html()")
    print("  - exportar_visualizaciones_completas()")
