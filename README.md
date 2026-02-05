# SAVP v3.6 - Sistema Árbol de la Vida Personal

**Systema Arbor Vitae Personalis v3.6 Final**

API completa para análisis astrológico cabalístico con interpretación pneumatológica.

---

## 🌟 Características v3.6

### Análisis Completo
- ✅ Cálculo astronómico preciso (Kerykeion + Swiss Ephemeris)
- ✅ Proyección sobre Árbol de la Vida (10 Sephiroth)
- ✅ 72 Genios completos con salmos y atributos
- ✅ Dignidades esenciales y accidentales
- ✅ Ponderación de 2 capas (v3.6)
- ✅ Distribución por pilares (Izquierdo, Central, Derecho)
- ✅ Nodos Lunares (Norte y Sur)

### Análisis Avanzado
- ✅ Cadena de dispositores como grafo
- ✅ Convergencias, válvulas, motores, bucles
- ✅ Senderos 3 tipos (ocupación, aspectos, críticos)
- ✅ Aspectos planetarios con orbes
- ✅ Diagnóstico cualitativo automático

### Interpretación
- ✅ Motor de lectura 10 fases completas
- ✅ Tikún automático diferenciado
- ✅ Manifestaciones concretas por planeta
- ✅ Prácticas espirituales específicas
- ✅ Vocación y Opus Magnum (40 días)

### Técnicas Temporales
- ✅ Tránsitos sobre carta natal
- ✅ Revolución Solar
- ✅ Interpretación pneumatológica
- ✅ Tikún temporal

### Visualizaciones
- ✅ Diagrama del Árbol (PNG 300 dpi)
- ✅ Grafo Mermaid (cadena dispositores)
- ✅ Árbol SVG completo
- ✅ Tabla HTML interactiva (senderos)

---

## 📦 Instalación Local

### Requisitos
- Python 3.11+
- pip

### Setup

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/savp-v36.git
cd savp-v36

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

API disponible en: `http://localhost:8000`

---

## 🚀 Endpoints

### GET `/`
Información general de la API

### GET `/health`
Health check

### GET `/savp/v36/`
Información del sistema SAVP v3.6

### POST `/savp/v36/natal`
**Análisis natal completo**

Request:
```json
{
  "nombre": "Consultante",
  "fecha": "10/12/1990",
  "hora": "02:25",
  "lugar": "Zaragoza, España",
  "timezone": "Europe/Madrid"
}
```

Response:
```json
{
  "success": true,
  "datos_natales": {...},
  "carta_astronomica": {
    "sol": {...},
    "luna": {...},
    ...
    "nodo_norte": {...},
    "nodo_sur": {...}
  },
  "analisis_savp": {
    "planetas_savp": {...},
    "pilares": {...},
    "cadena_dispositores": {...},
    "senderos_criticos_resumen": [...]
  },
  "tikun": {...},
  "visualizaciones": {...}
}
```

### POST `/savp/v36/lectura`
**Lectura interpretativa (1 fase o 10 completas)**

Request:
```json
{
  "analisis_savp": {...},
  "datos_natales": {...},
  "fase": null,
  "nombre": "Consultante"
}
```

`fase: null` → Todas las fases  
`fase: 0-10` → Fase específica

### POST `/savp/v36/transito`
**Detectar e interpretar tránsito**

Request:
```json
{
  "planeta_transitante": "Saturno",
  "grado_transito": 18.5,
  "signo_transito": "Piscis",
  "planeta_natal": "Sol",
  "grado_natal": 20.01,
  "signo_natal": "Acuario",
  "retrogrado": false,
  "analisis_natal": {...}
}
```

### GET `/savp/v36/test`
Test con Frater D. pre-cargado

---

## 📖 Las 10 Fases de Lectura

1. **Fase 0:** Verificación de datos
2. **Fase 1:** Proyección Sephirótica
3. **Fase 2:** Genios de los 72
4. **Fase 3:** Cadena de Dispositores
5. **Fase 4:** Senderos + Tarot
6. **Fase 5:** Triple Lectura I (Planetas personales)
7. **Fase 6:** Triple Lectura II (Planetas transpersonales)
8. **Fase 7:** Eje Nodal (Karma y Destino)
9. **Fase 8:** Aspectos Mayores
10. **Fase 9:** Vocación + Opus Magnum
11. **Fase 10:** Conclusión Integral

---

## 🔧 Módulos

### Core
- `main.py` - Aplicación FastAPI
- `savp_v36_router.py` - Router de endpoints
- `savp_v36_core.py` - Motor de análisis

### Interpretación
- `motor_lectura_v36.py` - Generador de lecturas
- `tikun_automatico.py` - Tikún diferenciado

### Visualización
- `visualizaciones.py` - Export Mermaid/SVG/HTML
- `generar_arbol_v36.py` - Diagrama PNG

### Temporal
- `transitos_v36.py` - Tránsitos y Revolución Solar

### Datos
- `genios_72_completos.py` - Tabla 72 Genios

---

## 📚 Documentación

- `DEPLOYMENT_GUIDE.md` - Guía de deployment en Render
- `INVENTARIO_ARCHIVOS.md` - Inventario completo
- Manual Técnico (en preparación)

---

## 🧪 Tests

```bash
# Test endpoint básico
curl http://localhost:8000/

# Test SAVP info
curl http://localhost:8000/savp/v36/

# Test con caso pre-cargado
curl http://localhost:8000/savp/v36/test
```

---

## 🌐 Deployment (Render)

Ver `DEPLOYMENT_GUIDE.md` para instrucciones completas.

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 📊 Rendimiento

- Cálculo astronómico: <1s
- Análisis SAVP completo: ~2s
- Lectura 10 fases: ~1s
- Tikún automático: <0.5s
- Visualizaciones: <0.5s
- **Total end-to-end:** ~4s

---

## 🔐 Licencia

Privado - Uso exclusivo SAVP

---

## 👤 Autor

Sistema SAVP  
Versión 3.6 Final  
Febrero 2025

---

## 📝 Changelog

### v3.6 Final (Febrero 2025)
- ✅ Cadena de dispositores como grafo
- ✅ Senderos 3 tipos diferenciados
- ✅ Aspectos automáticos con orbes
- ✅ Ponderación 2 capas (esencial + accidental)
- ✅ Tabla 72 Genios completa embebida
- ✅ Tikún automático diferenciado
- ✅ Motor de lectura 10 fases
- ✅ Visualizaciones mejoradas
- ✅ Diagrama visual con tamaños por peso
- ✅ Tránsitos + Revolución Solar
- ✅ Nodos Lunares integrados
- ✅ API completamente integrada

### v3.5 (Enero 2025)
- Versión base con análisis natal
- Proyección sephirótica
- Genios básicos
- Lectura manual

---

## 🤝 Soporte

Para consultas técnicas o issues, contactar directamente.

---

**🎯 SAVP v3.6 - Sistema Completo Operacional**
