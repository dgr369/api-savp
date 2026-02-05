# API Astrológica SAVP v3.5

API REST para cálculos astrológicos del **Sistema Árbol de la Vida Personal (SAVP v3.5)** con Cábala Hermética y Astrología Cabalística.

🔗 **URL**: https://api-savp.onrender.com  
📚 **Documentación**: https://api-savp.onrender.com/docs

---

## 🌟 Características

✅ **Carta Natal** completa con Placidus/Whole Sign  
✅ **Tránsitos** en casas natales (SAVP v3.5)  
✅ **Revolución Solar** con cálculo del momento exacto del retorno  
✅ **Nodos Lunares** (Norte y Sur)  
✅ **Geocoding automático** (cualquier ciudad del mundo vía OpenStreetMap)  
✅ **Compatible** con Kerykeion 5.7.0  

---

## 📡 Endpoints

### 1. Carta Natal
```http
POST /natal
```

**Request**:
```json
{
  "nombre": "Ejemplo",
  "fecha": "1977-02-08",
  "hora": "22:40",
  "ciudad": "Fuentes de Ebro",
  "pais": "España",
  "timezone": "Europe/Madrid",
  "house_system": "P"
}
```

**Response**:
```json
{
  "success": true,
  "datos": {
    "nombre": "Ejemplo",
    "coordenadas": {"lat": 41.5167, "lon": -0.6333}
  },
  "carta": {
    "planetas": {
      "sol": {"grado": 20.13, "signo": "Aqu", "casa": 5, "retrogrado": false},
      "nodo_norte": {"grado": 23.1, "signo": "Lib", "casa": 4, "retrogrado": true},
      ...
    },
    "puntos": {
      "asc": {"grado": 10.42, "signo": "Lib"},
      "mc": {"grado": 12.18, "signo": "Can"}
    }
  }
}
```

---

### 2. Tránsitos
```http
POST /transits
```

**Request**:
```json
{
  "nombre": "Ejemplo",
  "fecha_natal": "1977-02-08",
  "hora_natal": "22:40",
  "ciudad_natal": "Fuentes de Ebro",
  "pais_natal": "España",
  "fecha_transito": "2026-01-29",
  "hora_transito": "09:17",
  "use_natal_houses": true
}
```

**Parámetros importantes**:
- `use_natal_houses: true` → Planetas de tránsito en **casas natales** (SAVP v3.5)
- `use_natal_houses: false` → Planetas de tránsito en casas del momento

**Response**: Similar a `/natal` pero con dos cartas: `natal` y `transitos`

---

### 3. Revolución Solar
```http
POST /solar_return
```

**Request**:
```json
{
  "nombre": "Ejemplo",
  "fecha_natal": "1990-12-10",
  "hora_natal": "02:25",
  "ciudad_natal": "Zaragoza",
  "pais_natal": "España",
  "año_revolucion": 2026
}
```

**Response**:
```json
{
  "success": true,
  "año_revolucion": 2026,
  "fecha_revolucion": "2026-12-09",
  "hora_revolucion": "20:02",
  "momento_exacto_retorno": "2026-12-09 20:02 Europe/Madrid",
  "carta_revolucion": {...}
}
```

⚡ **Nota**: La API calcula el **momento aproximado** (±2 horas) cuando el Sol vuelve a su posición natal.

---

### 4. Geocoding (Test)
```http
GET /geocode?ciudad=Zaragoza&pais=España
```

Verifica coordenadas antes de calcular.

---

### 5. Test Nodos (Debug)
```http
GET /test_nodos
```

Verifica que los nodos lunares funcionan correctamente.

---

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/dgr369/api-savp.git
cd api-savp

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn main:app --reload --port 8000
```

Abre: http://localhost:8000/docs

---

## 📦 Dependencias

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
kerykeion>=5.7.0
pytz>=2024.1
pydantic>=2.6.0
geopy>=2.4.1
```

---

## 🌍 Geocoding

La API usa **Nominatim (OpenStreetMap)** para geocodificar automáticamente cualquier ciudad del mundo:

- **Gratis** (sin API key)
- **Sin límites** para uso razonable
- **Fallback** a diccionario de 25+ ciudades españolas

**Ejemplos**:
- ✅ "Zaragoza, España"
- ✅ "Dartford, UK"
- ✅ "Příbor, República Checa"
- ✅ "New York, USA"

---

## 🏠 Sistemas de Casas

Soportados vía parámetro `house_system`:

- `"P"` → **Placidus** (default, recomendado para SAVP)
- `"W"` → Whole Sign
- `"E"` → Equal
- `"K"` → Koch
- `"R"` → Regiomontanus

---

## 🔧 Configuración Avanzada

### Coordenadas Manuales
Si el geocoding falla o quieres precisión máxima:

```json
{
  "lat_natal": 41.5167,
  "lon_natal": -0.6333
}
```

### Zona Horaria Personalizada
```json
{
  "timezone_natal": "America/New_York"
}
```

Ver: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

---

## 🎯 Uso con GPT (Actions)

1. **GPT Builder** → Configure → Actions
2. **Import from URL**: `https://api-savp.onrender.com/openapi.json`
3. O copiar schema de `Schema_OpenAPI_v1.3_FINAL.md`

**Instrucciones del GPT**: Ver `Instrucciones_Core_GPT.md`

---

## ⚠️ Limitaciones Conocidas

1. **Revolución Solar**: Momento exacto aproximado (±2 horas)
2. **Render Free Tier**: Cold start 30-60s tras inactividad
3. **Efemérides**: Rango 1900-2100 (limitación de Kerykeion)

---

## 📝 Changelog

### v1.3 (Actual)
- ✅ Casas natales para tránsitos (`use_natal_houses`)
- ✅ Nodos lunares (true_node)
- ✅ Revolución Solar con momento del retorno
- ✅ Geocoding internacional (Nominatim)
- ✅ Compatible Kerykeion 5.7.0

### v1.2
- Soporte `houses_system_identifier`
- Hora de tránsito opcional

### v1.0
- Release inicial

---

## 🐛 Troubleshooting

**"Error: No matching distribution found for kerykeion"**  
→ Usar `kerykeion>=5.7.0` (no versiones 4.x)

**"Casas incorrectas en tránsitos"**  
→ Verificar `use_natal_houses: true`

**"Nodos no aparecen"**  
→ Están en `planetas.nodo_norte` y `planetas.nodo_sur`

**"Geocoding falla"**  
→ Pasar `lat` y `lon` manualmente

---

## 📄 Licencia

Proyecto privado - Uso exclusivo para SAVP v3.5

---

## 👤 Autor

David García Ramos  
Sistema Árbol de la Vida Personal v3.5

---

## 🔗 Enlaces

- **API**: https://api-savp.onrender.com
- **Docs**: https://api-savp.onrender.com/docs
- **Kerykeion**: https://github.com/g-battaglia/kerykeion
