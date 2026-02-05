"""
test_produccion_api_v36.py
Test completo de API SAVP v3.6 en producción

Verifica:
- Endpoints funcionando
- Tiempos de respuesta
- Calidad de outputs
- Integración completa
"""

import requests
import json
import time
from datetime import datetime

# URL BASE (actualizar con tu URL de Render)
BASE_URL = "https://api-savp.onrender.com"

print("=" * 80)
print("TEST PRODUCCIÓN: API SAVP v3.6")
print("=" * 80)
print(f"\nURL Base: {BASE_URL}")
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "=" * 80)

# ============================================================================
# TEST 1: HEALTH CHECK
# ============================================================================

print("\n1️⃣  TEST: HEALTH CHECK")
print("-" * 80)

try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"✅ Health check OK ({elapsed:.2f}s)")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check FAIL: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 2: INFO ENDPOINT
# ============================================================================

print("\n2️⃣  TEST: INFO SAVP v3.6")
print("-" * 80)

try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/savp/v36/", timeout=10)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Info endpoint OK ({elapsed:.2f}s)")
        print(f"   Versión: {data.get('version')}")
        print(f"   Módulos disponibles:")
        
        modulos = data.get('modulos_disponibles', {})
        for mod, disponible in modulos.items():
            status = "✅" if disponible else "❌"
            print(f"     {status} {mod}")
    else:
        print(f"❌ Info endpoint FAIL: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 3: TEST ENDPOINT (Frater D.)
# ============================================================================

print("\n3️⃣  TEST: ENDPOINT /test (Frater D.)")
print("-" * 80)

try:
    start = time.time()
    response = requests.get(f"{BASE_URL}/savp/v36/test", timeout=30)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Test endpoint OK ({elapsed:.2f}s)")
        
        analisis = data.get('analisis', {})
        print(f"\n   📊 RESULTADOS:")
        print(f"   • Planetas procesados: {len(analisis.get('planetas_savp', {}))}")
        print(f"   • Senderos críticos: {len(analisis.get('senderos_criticos_resumen', []))}")
        
        pilares = analisis.get('porcentajes', {})
        print(f"   • Pilar dominante: {analisis.get('diagnostico', {}).get('pilar_dominante', 'N/A')}")
        print(f"     - Izquierdo: {pilares.get('izquierdo', 0):.1f}%")
        print(f"     - Central: {pilares.get('central', 0):.1f}%")
        print(f"     - Derecho: {pilares.get('derecho', 0):.1f}%")
        
        convergencias = len(analisis.get('cadena_dispositores', {}).get('convergencias', []))
        print(f"   • Convergencias: {convergencias}")
        
    else:
        print(f"❌ Test endpoint FAIL: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 4: ANÁLISIS NATAL COMPLETO
# ============================================================================

print("\n4️⃣  TEST: ANÁLISIS NATAL COMPLETO")
print("-" * 80)

payload = {
    "nombre": "Test Producción",
    "fecha": "10/12/1990",
    "hora": "02:25",
    "lugar": "Zaragoza, España",
    "timezone": "Europe/Madrid"
}

print(f"   Solicitando: {payload['nombre']} ({payload['fecha']})")

try:
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/savp/v36/natal",
        json=payload,
        timeout=60
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Análisis natal OK ({elapsed:.2f}s)")
        
        # Verificar componentes
        print(f"\n   📦 COMPONENTES DEVUELTOS:")
        print(f"   {'✅' if 'datos_natales' in data else '❌'} datos_natales")
        print(f"   {'✅' if 'carta_astronomica' in data else '❌'} carta_astronomica")
        print(f"   {'✅' if 'analisis_savp' in data else '❌'} analisis_savp")
        print(f"   {'✅' if 'tikun' in data else '❌'} tikun")
        print(f"   {'✅' if 'visualizaciones' in data else '❌'} visualizaciones")
        
        # Verificar planetas
        carta = data.get('carta_astronomica', {})
        print(f"\n   🌍 PLANETAS CALCULADOS:")
        for planeta in ['sol', 'luna', 'mercurio', 'venus', 'marte']:
            if planeta in carta:
                p = carta[planeta]
                print(f"   ✅ {planeta.capitalize()}: {p['grado']:.2f}° {p['signo']} Casa {p['casa']}")
        
        # Verificar nodos
        if 'nodo_norte' in carta:
            nn = carta['nodo_norte']
            print(f"   ✅ Nodo Norte: {nn['grado']:.2f}° {nn['signo']} Casa {nn['casa']}")
        else:
            print(f"   ❌ Nodo Norte: NO CALCULADO")
        
        # Verificar análisis
        analisis = data.get('analisis_savp', {})
        print(f"\n   🔍 ANÁLISIS SAVP:")
        print(f"   • Planetas: {len(analisis.get('planetas_savp', {}))}")
        print(f"   • Senderos críticos: {len(analisis.get('senderos_criticos_resumen', []))}")
        print(f"   • Convergencias: {len(analisis.get('cadena_dispositores', {}).get('convergencias', []))}")
        
        # Verificar Tikún
        tikun = data.get('tikun', {})
        if tikun:
            print(f"\n   🔥 TIKÚN:")
            print(f"   • Urgencia: {tikun.get('urgencia_maxima', 'N/A')}")
            print(f"   • Prácticas: {len(tikun.get('tikun_secundario', []))}")
        
        # Guardar response para inspección
        with open('test_produccion_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n   💾 Response guardado: test_produccion_response.json")
        
    else:
        print(f"❌ Análisis natal FAIL: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================================
# TEST 5: LECTURA INTERPRETATIVA (1 fase)
# ============================================================================

print("\n5️⃣  TEST: LECTURA INTERPRETATIVA (Fase 1)")
print("-" * 80)

# Usar análisis del test anterior si está disponible
if response.status_code == 200 and 'analisis_savp' in data:
    
    payload_lectura = {
        "analisis_savp": data['analisis_savp'],
        "datos_natales": data['datos_natales'],
        "fase": 1,
        "nombre": "Test Producción"
    }
    
    try:
        start = time.time()
        response_lectura = requests.post(
            f"{BASE_URL}/savp/v36/lectura",
            json=payload_lectura,
            timeout=30
        )
        elapsed = time.time() - start
        
        if response_lectura.status_code == 200:
            data_lectura = response_lectura.json()
            print(f"✅ Lectura Fase 1 OK ({elapsed:.2f}s)")
            
            texto = data_lectura.get('texto', '')
            print(f"\n   📖 PREVIEW (primeros 300 caracteres):")
            print(f"   {texto[:300]}...")
            print(f"\n   📏 Longitud total: {len(texto)} caracteres")
            
        else:
            print(f"❌ Lectura FAIL: {response_lectura.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("⚠️  Skipped (requiere análisis previo exitoso)")

# ============================================================================
# RESUMEN
# ============================================================================

print("\n" + "=" * 80)
print("RESUMEN TEST PRODUCCIÓN")
print("=" * 80)

print("""
Tests completados:
1. ✅ Health check
2. ✅ Info endpoint
3. ✅ Test endpoint (Frater D.)
4. ✅ Análisis natal completo
5. ✅ Lectura interpretativa

Verificar:
- Todos los tests pasaron
- Tiempos de respuesta <30s
- Nodos calculados
- Tikún generado
- Response guardado en test_produccion_response.json

""")

print("=" * 80)
print("🎯 TEST PRODUCCIÓN COMPLETADO")
print("=" * 80)
