#  Documentación: Twitch

Módulo para interactuar con la API de Twitch (Helix) para followage, clips y gestión de tokens.

## Endpoints

### 📍 `/twitch/followage`
Calcula cuánto tiempo lleva un usuario siguiendo al canal.
- **Uso:** `/twitch/followage?user=nombre_usuario`
- **Ejemplo:** `https://api.tu-app.com/twitch/followage?user=ponss17`
- **Respuesta:** `ponss17 sigue a LosPerris desde hace 1 año, 2 meses.`

### 📍 `/twitch/clip`
Crea un clip en vivo del canal configurado.
- **Uso:** `/twitch/clip` (Soporta GET o POST)
- **Respuesta:** `¡Clip creado con éxito! -> https://clips.twitch.tv/UnicoIdentificador`

### 📍 `/twitch/status`
Verifica si el `USER_ACCESS_TOKEN` y el `CLIENT_ID` siguen siendo válidos.
- **Uso:** `/twitch/status`

### 📍 `/twitch/token`
Genera un App Access Token (útil para herramientas externas). Requiere la contraseña configurada.
- **Uso:** `/twitch/token?password=TU_PASSWORD`

## 🔑 Cómo obtener las credenciales

Para que los endpoints de Twitch funcionen, necesitas registrar una aplicación y obtener tokens. Sigue estos pasos:

### 1. Registrar Aplicación en Twitch
1. Ve a la [Consola de Desarrolladores de Twitch](https://dev.twitch.tv/console).
2. Haz clic en **Register Your Application**.
3. **Nombre:** Pon un nombre a tu app (ej: "Mi Bot de Stats").
4. **OAuth Redirect URLs:** Añade `https://tu-api.vercel.app/twitch/callback`. (Si pruebas en local, usa `http://localhost:5000/twitch/callback`).
5. **Categoría:** Elige "Application Integration".
6. Haz clic en **Create**.

### 2. Obtener Client ID y Secret
1. Selecciona tu app en la consola.
2. Copia el **Client ID**.
3. Haz clic en **New Secret** y copia el **Client Secret** (guárdalo bien).

### 3. Obtener User Access Token (OAuth Flow)
Esta API necesita permisos específicos para crear clips y ver seguidores:
1. Configura `CLIENT_ID` y `CLIENT_SECRET` en Vercel.
2. Abre esta URL en tu navegador reemplazando tus datos:
   `https://id.twitch.tv/oauth2/authorize?client_id=TU_CLIENT_ID&redirect_uri=TU_REDIRECT_URI&response_type=token&scope=clips:edit+moderator:read:followers`
3. Dale a **Autorizar**. Serás redirigido a tu API.
4. Verás el **USER_ACCESS_TOKEN** en pantalla. Cópialo y ponlo en tu variable de entorno `USER_ACCESS_TOKEN`.

> [!IMPORTANT]
> Para que el `followage` funcione, el token debe ser de la cuenta del **streamer** (o de un moderador del canal).

## ⚙️ Configuración (`twitch/config.py`)

Variables que debes configurar en Vercel:
- `CLIENT_ID`: De la consola de desarrolladores.
- `CLIENT_SECRET`: De la consola de desarrolladores.
- `CHANNEL_LOGIN`: El nombre de tu canal de Twitch.
- `USER_ACCESS_TOKEN`: El token obtenido en el paso 3.
- `ENDPOINT_PASSWORD`: Contraseña para generar tokens de App.

---
## 📝 Notas Importantes
> [!IMPORTANT]
> **Vercel / Despliegue:** Una vez vinculado Twitch, recuerda copiar el token que aparece en pantalla y pegalo en tus variables de entorno de Vercel como `USER_ACCESS_TOKEN`. Sin esto, los comandos no funcionarán en la nube.

Parte de **LosPerris Twitch Api Public**
