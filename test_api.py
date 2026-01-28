"""
Script de testing para la API Astrológica
Prueba los 3 endpoints principales
"""

import requests
import json

# URL de la API (cambiar si está deployada)
BASE_URL = "http://localhost:8000"

def test_natal():
    """Test endpoint /natal"""
    print("\n=== TEST 1: CARTA NATAL ===")
    
    payload = {
        "nombre": "Frater D.",
        "fecha": "1977-02-08",
        "hora": "22:40",
        "ciudad": "Zaragoza",
        "pais": "España",
        "timezone": "Europe/Madrid"
    }
    
    response = requests.post(f"{BASE_URL}/natal", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Carta natal calculada correctamente")
        print(f"Sol: {data['carta']['planetas']['sol']['grado']}° {data['carta']['planetas']['sol']['signo']}")
        print(f"Luna: {data['carta']['planetas']['luna']['grado']}° {data['carta']['planetas']['luna']['signo']}")
        print(f"ASC: {data['carta']['puntos']['asc']['grado']}° {data['carta']['puntos']['asc']['signo']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_transits():
    """Test endpoint /transits"""
    print("\n=== TEST 2: TRÁNSITOS ===")
    
    payload = {
        "nombre": "Frater D.",
        "fecha_natal": "1977-02-08",
        "hora_natal": "22:40",
        "ciudad_natal": "Zaragoza",
        "pais_natal": "España",
        "timezone_natal": "Europe/Madrid",
        "fecha_transito": "2026-01-28"
    }
    
    response = requests.post(f"{BASE_URL}/transits", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Tránsitos calculados correctamente")
        print(f"Fecha tránsito: {data['fecha_transito']}")
        print(f"Sol transitando: {data['transitos']['planetas']['sol']['grado']}° {data['transitos']['planetas']['sol']['signo']}")
        print(f"Júpiter transitando: {data['transitos']['planetas']['jupiter']['grado']}° {data['transitos']['planetas']['jupiter']['signo']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_solar_return():
    """Test endpoint /solar_return"""
    print("\n=== TEST 3: REVOLUCIÓN SOLAR ===")
    
    payload = {
        "nombre": "Frater D.",
        "fecha_natal": "1977-02-08",
        "hora_natal": "22:40",
        "ciudad_natal": "Zaragoza",
        "pais_natal": "España",
        "timezone_natal": "Europe/Madrid",
        "año_revolucion": 2026
    }
    
    response = requests.post(f"{BASE_URL}/solar_return", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Revolución solar calculada correctamente")
        print(f"Año revolución: {data['año_revolucion']}")
        print(f"ASC RS: {data['carta_revolucion']['puntos']['asc']['grado']}° {data['carta_revolucion']['puntos']['asc']['signo']}")
        print(f"Sol RS: {data['carta_revolucion']['planetas']['sol']['grado']}° {data['carta_revolucion']['planetas']['sol']['signo']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("🔮 TESTING API ASTROLÓGICA SAVP v3.5")
    print(f"URL: {BASE_URL}")
    print("="*50)
    
    # Test 1: Carta Natal
    test_natal()
    
    # Test 2: Tránsitos
    test_transits()
    
    # Test 3: Revolución Solar
    test_solar_return()
    
    print("\n" + "="*50)
    print("✅ TESTS COMPLETADOS")
