# API ASTROLÓGICA SAVP v3.5

API REST para cálculos astrológicos usando Kerykeion (Swiss Ephemeris).

Soporta:
- ✅ Carta Natal completa
- ✅ Tránsitos actuales
- ✅ Revolución Solar

---

## INSTALACIÓN LOCAL

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar servidor

```bash
uvicorn main:app --reload
```

Servidor corriendo en: `http://localhost:8000`

Documentación Swagger: `http://localhost:8000/docs`

---

## DEPLOY EN RENDER (GRATIS)

### 1. Crear cuenta en Render

- Ir a https://render.com
- Registrarse (gratis)

### 2. Crear nuevo Web Service

- Dashboard → "New" → "Web Service"
- Conectar con GitHub o subir repositorio

### 3. Configuración

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment:**
- Python 3.11+

### 4. Deploy

- Click "Create Web Service"
- Esperar 2-3 minutos
- Obtendrás una URL: `https://tu-api.onrender.com`

---

## USO DE LA API

### ENDPOINT 1: Carta Natal

**POST** `/natal`

**Body (JSON):**
```json
{
  "nombre": "Frater D.",
  "fecha": "1977-02-08",
  "hora": "22:40",
  "ciudad": "Zaragoza",
  "pais": "España",
  "timezone": "Europe/Madrid"
}
```

**Respuesta:**
```json
{
  "success": true,
  "datos": {
    "nombre": "Frater D.",
    "fecha": "1977-02-08",
    "hora": "22:40",
    "ciudad": "Zaragoza",
    "coordenadas": {"lat": 41.6488, "lon": -0.8891}
  },
  "carta": {
    "planetas": {
      "sol": {
        "grado": 20.01,
        "signo": "Acuario",
        "casa": 5,
        "retrogrado": false
      },
      "luna": {
        "grado": 20.24,
        "signo": "Libra",
        "casa": 1,
        "retrogrado": false
      }
      // ... resto de planetas
    },
    "puntos": {
      "asc": {"grado": 10.12, "signo": "Libra"},
      "mc": {"grado": 11.57, "signo": "Cáncer"},
      "nodo_norte": {"grado": 27.49, "signo": "Libra", "casa": 1}
    }
  }
}
```

---

### ENDPOINT 2: Tránsitos

**POST** `/transits`

**Body (JSON):**
```json
{
  "nombre": "Frater D.",
  "fecha_natal": "1977-02-08",
  "hora_natal": "22:40",
  "ciudad_natal": "Zaragoza",
  "pais_natal": "España",
  "timezone_natal": "Europe/Madrid",
  "fecha_transito": "2026-01-28"
}
```

**Respuesta:**
```json
{
  "success": true,
  "fecha_transito": "2026-01-28",
  "natal": {
    // Posiciones natales
  },
  "transitos": {
    // Posiciones planetarias actuales
  }
}
```

---

### ENDPOINT 3: Revolución Solar

**POST** `/solar_return`

**Body (JSON):**
```json
{
  "nombre": "Frater D.",
  "fecha_natal": "1977-02-08",
  "hora_natal": "22:40",
  "ciudad_natal": "Zaragoza",
  "pais_natal": "España",
  "timezone_natal": "Europe/Madrid",
  "año_revolucion": 2026
}
```

**Respuesta:**
```json
{
  "success": true,
  "año_revolucion": 2026,
  "fecha_revolucion": "2026-02-08",
  "carta_revolucion": {
    // Posiciones para la revolución solar 2026
  }
}
```

---

## CONECTAR AL GPT

### 1. En GPT Builder → Configure → Actions

### 2. Añadir Schema OpenAPI

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "API Astrológica SAVP",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://tu-api.onrender.com"
    }
  ],
  "paths": {
    "/natal": {
      "post": {
        "summary": "Calcular carta natal",
        "operationId": "calcularNatal",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "nombre": {"type": "string"},
                  "fecha": {"type": "string", "format": "date"},
                  "hora": {"type": "string"},
                  "ciudad": {"type": "string"},
                  "pais": {"type": "string"},
                  "timezone": {"type": "string"}
                },
                "required": ["nombre", "fecha", "hora", "ciudad", "pais"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Carta natal calculada"
          }
        }
      }
    },
    "/transits": {
      "post": {
        "summary": "Calcular tránsitos",
        "operationId": "calcularTransitos",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "nombre": {"type": "string"},
                  "fecha_natal": {"type": "string"},
                  "hora_natal": {"type": "string"},
                  "ciudad_natal": {"type": "string"},
                  "pais_natal": {"type": "string"},
                  "timezone_natal": {"type": "string"},
                  "fecha_transito": {"type": "string"}
                }
              }
            }
          }
        }
      }
    },
    "/solar_return": {
      "post": {
        "summary": "Calcular revolución solar",
        "operationId": "calcularRevolucionSolar",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "nombre": {"type": "string"},
                  "fecha_natal": {"type": "string"},
                  "hora_natal": {"type": "string"},
                  "ciudad_natal": {"type": "string"},
                  "pais_natal": {"type": "string"},
                  "año_revolucion": {"type": "integer"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### 3. Guardar y probar

El GPT ahora puede calcular cartas natales, tránsitos y revoluciones solares automáticamente.

---

## TESTING

### Ejemplo con cURL

```bash
curl -X POST "http://localhost:8000/natal" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test",
    "fecha": "1990-01-01",
    "hora": "12:00",
    "ciudad": "Madrid",
    "pais": "España"
  }'
```

---

## MEJORAS FUTURAS

- [ ] Geocoding automático con API (Google Maps, OpenCage)
- [ ] Cálculo de aspectos
- [ ] Progresiones secundarias
- [ ] Direcciones primarias
- [ ] Cache de resultados (Redis)
- [ ] Autenticación (API keys)

---

## SOPORTE

**Kerykeion Documentation**: https://github.com/g-battaglia/kerykeion
**FastAPI Documentation**: https://fastapi.tiangolo.com/

---

## LICENCIA

Uso libre para SAVP v3.5
