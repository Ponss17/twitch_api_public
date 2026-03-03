#  Documentación: Valorant

Módulo opcional para obtener estadísticas en tiempo real de Valorant mediante la API de HenrikDev.

## Endpoints

### 📍 `/valorant/rango`
Obtiene el rango actual, puntos de MMR y el último agente jugado.

- **Parámetros:** `?lang=es` (defecto) o `?lang=en`.
- **Respuesta ES:** `Actualmente estoy en Platino 2 con 45 puntos. Mi última partida fue con Jett y gané 18 puntos.`
- **Respuesta EN:** `Rank: Platinum 2 with 45 points. Last match was with Jett and I gained 18 points.`

### 📍 `/valorant/ultima-ranked`
Detalles de la última partida competitiva detectada en el historial.

- **Parámetros:** `?lang=es` (defecto) o `?lang=en`.
- **Respuesta ES:** `Mi última partida fue Victoria en Ascent con Jett. KDA: 15/7/3.`
- **Respuesta EN:** `Match: Win in Ascent | Agent: Jett | KDA: 15/7/3`

## 🔑 Cómo obtener la API Key (HenrikDev)

Para que el módulo de Valorant funcione, necesitas una clave de la API de HenrikDev.

1. Ve al [Dashboard de HenrikDev](https://dashboard.henrikdev.xyz/).
2. Inicia sesión con Discord.
3. Crea una nueva **API Key**.
4. Añádela a tus variables de entorno como `API_KEY`.

> [!NOTE]
> La versión gratuita tiene límites. Esta API usa caché para optimizar las peticiones.

## ⚙️ Configuración (`valorant/config.py`)

Configura los datos del jugador aquí:
```python
NOMBRE = "Nombre"
TAG    = "TAG"
REGION = "na" # na, eu, latam, kr, ap
API_KEY = os.environ.get("API_KEY", "")
```

## 🧠 Características Técnicas
- **Caché:** TTL configurable (`VALORANT_CACHE_TTL`, defecto 15s).
- **Traducciones:** Rango traducido automáticamente al español.
- **Robustez:** Reintentos automáticos mediante `common/http.py`.

---
Parte de **LosPerris Twitch Api Public**
