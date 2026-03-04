# 🚀 Despliegue en Vercel

Guía detallada para desplegar y configurar LosPerris API en Vercel.

## 1. Requisitos Previos

- Una cuenta en [GitHub](https://github.com).
- Una cuenta en [Vercel](https://vercel.com).
- El código de este repositorio subido a tu GitHub (puedes hacer un Fork).

## 2. Configuración en Vercel

1. **Importar Proyecto**: En el dashboard de Vercel, haz clic en "Add New" -> "Project" y selecciona tu repositorio.
2. **Framework Preset**: Vercel debería detectar automáticamente que es un proyecto de Python/Flask. Si no, selecciona "Other".
3. **Variables de Entorno**: Esta es la parte más importante. Debes añadir las siguientes variables en la sección "Environment Variables":

| Variable | Importancia | ¿Dónde conseguirla? |
| :--- | :--- | :--- |
| `CLIENT_ID` | **Requerido** | [Twitch Dev Console](https://dev.twitch.tv/console) |
| `CLIENT_SECRET` | **Requerido** | [Twitch Dev Console](https://dev.twitch.tv/console) |
| `CHANNEL_LOGIN` | **Requerido** | Tu nombre de usuario en Twitch |
| `API_KEY` | Opcional | [HenrikDev API](https://api.henrikdev.xyz/) |
| `ENABLE_VALORANT` | Opcional | Pon `true` para activar el módulo |
| `SECRET_KEY` | Recomendado | Cualquier frase larga y secreta |

## 3. Vinculación de Twitch (Paso Crítico)

Como Vercel no guarda archivos permanentemente, el archivo `.env` local no funcionará para el `USER_ACCESS_TOKEN`.

1. Despliega tu aplicación.
2. Entra a la URL de tu API (ej: `https://tu-api.vercel.app/`).
3. En el Dashboard, pulsa en **Vincular con Twitch**.
4. Tras autorizar, volverás a una página de éxito.
5. **Copia el token** que se muestra en pantalla.
6. Ve a la configuración de tu proyecto en Vercel -> Settings -> Environment Variables.
7. Añade o actualiza la variable `USER_ACCESS_TOKEN` con el token que copiaste.
8. **Redisplay**: Para que el cambio surta efecto, ve a la pestaña "Deployments", haz clic en los tres puntos del último despliegue y selecciona "Redeploy".

## 4. Solución de Problemas

- **Error de Redirect URI**: Asegúrate de que en la consola de Twitch has añadido `https://tu-api.vercel.app/twitch/callback` como una de las "OAuth Redirect URLs".
- **Bot no lee los comandos**: Verifica que las URLs en Nightbot/StreamElements no tengan `/` al final si no es necesario, y que el servidor esté activo.

---
[Volver al README](../README.md)
