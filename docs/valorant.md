#  Documentación de Valorant

Guía detallada sobre el módulo de estadísticas de Valorant, integrando la API de HenrikDev.

## 1. Funcionamiento del Módulo

Este módulo consulta la [API de HenrikDev](https://api.henrikdev.xyz/) para obtener en tiempo real el rango, puntos de MMR (Movement MMR), y detalles de la última partida competitiva.

### Optimización y Caché
- **Caché**: Para evitar saturar la API externa y mejorar la velocidad de respuesta para los bots, las consultas se guardan en caché durante **15 minutos** (configurable en `.env`).
- **Rápida Respuesta**: Los endpoints devuelven texto plano (`text/plain`), lo cual es ideal para que los chatbots lo lean directamente sin problemas de formato.

## 2. Endpoints Disponibles

### [GET] `/valorant/rango`
Muestra el rango actual, el MMR y el último agente jugado.
- **Parámetros Opcionales**:
    - `name`: Nombre del usuario (por defecto usa `VALORANT_USER`).
    - `tag`: Etiqueta (por defecto usa `VALORANT_TAG`).
    - `region`: Región (por defecto usa `VALORANT_REGION`).
    - `lang`: Idioma de respuesta (`es` o `en`).
- **Respuesta**: Rango: Oro 3 (22 RR)

### [GET] `/valorant/ultima-ranked`
Detalle de la última partida competitiva jugada.
- **Parámetros Opcionales**: Los mismos que `/valorant/rango`.
- **Respuesta**: "Resultado: Victoria | Mapa: Ascent | KDA: 20/10/5"

### [GET] `/valorant/rango-imagen`
Obtiene la URL directa de la imagen del rango actual.
- **Uso**: Ideal para usarlo como fuente de navegador en OBS o para mostrarlo en un panel de streaming.
- **Respuesta**: La URL de la imagen del rango (ej: Bronze 1).

## 3. Configuración de Región

Si tu cuenta es de Latinoamérica, te recomendamos probar con la región `na` (Norteamérica) si la región `latam` no devuelve datos. Esto se debe a cómo la API de HenrikDev organiza los servidores.

## 4. Configuración de Comandos (Bots)

### Nightbot
- **Rango**: `$(urlfetch https://tu-api.vercel.app/valorant/rango?name=NOMBRE&tag=TAG&region=na)`
- **Última**: `$(urlfetch https://tu-api.vercel.app/valorant/ultima-ranked?name=NOMBRE&tag=TAG&region=na)`

### StreamElements
- **Rango**: `${readapi https://tu-api.vercel.app/valorant/rango?name=NOMBRE&tag=TAG&region=na}`
- **Última**: `${readapi https://tu-api.vercel.app/valorant/ultima-ranked?name=NOMBRE&tag=TAG&region=na}`

---
[Volver al README](../README.md)
