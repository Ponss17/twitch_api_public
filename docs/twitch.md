#  Documentación de Twitch

Guía detallada sobre el funcionamiento, endpoints y configuración del módulo de Twitch.

## 1. Funcionamiento del Módulo

El módulo de Twitch utiliza la [API de Twitch (Helix)](https://dev.twitch.tv/docs/api/) para interactuar con tu canal. Para que el bot pueda realizar acciones (como crear clips), necesita un **User Access Token**.

### Flujo de Tokens
1. **App Token**: Se genera automáticamente para consultas públicas (followage).
2. **User Token**: Se genera cuando tú, como dueño del canal, te vinculas desde el Dashboard. Este token tiene "scopes" (permisos) para crear clips.

## 2. Endpoints Disponibles

### [GET] `/twitch/followage`
Calcula cuánto tiempo lleva un usuario siguiendo al canal.
- **Parámetros**:
    - `user` (Requerido): Nombre del usuario que quieres consultar.
    - `channel` (Opcional): Nombre del canal (por defecto usa `CHANNEL_LOGIN`).
- **Ejemplo**: `/twitch/followage?user=ponss17`

### [GET] `/twitch/clip`
Crea un clip del directo actual.
- **Parámetros**:
    - `channel` (Opcional): Canal donde crear el clip.
- **Requisito**: Debes estar en directo y haber vinculado tu cuenta en el Dashboard.
- **Respuesta**: La URL del clip generado o un error descriptivo.

### [GET] `/twitch/token`
Genera un App Access Token (solo para uso interno o depuración).
- **Seguridad**: Requiere `?password=TU_PASSWORD` o el header `X-Endpoint-Password`.
- **Respuesta**: El token generado en texto plano.

### [GET] `/twitch/status`
Verifica si la API está configurada correctamente.
- **Respuesta**: Un JSON detallado con el estado de los tokens y la conexión.

## 3. Configuración de Comandos (Bots)

Sustituye `tu-api.vercel.app` por tu dirección real.

### Nightbot
- **Followage**: `$(urlfetch https://tu-api.vercel.app/twitch/followage?user=$(touser)&channel=TU_CANAL)`
- **Clip**: `$(urlfetch https://tu-api.vercel.app/twitch/clip?channel=TU_CANAL)`

### StreamElements
- **Followage**: `${readapi https://tu-api.vercel.app/twitch/followage?user=${user.name}&channel=TU_CANAL}`
- **Clip**: `${readapi https://tu-api.vercel.app/twitch/clip?channel=TU_CANAL}`

## 4. Preguntas Frecuentes (FAQ)

- **¿Vence el token?** Sí, el token de usuario dura unos 60 días. El Dashboard te avisará cuando queden pocos días. Solo tienes que volver a pulsar "Vincular" para renovarlo.
- **El comando de clip falla**: Asegúrate de que el canal esté **en vivo** al momento de usarlo. Twitch no permite crear clips de canales offline.

---
[Volver al README](../README.md)
