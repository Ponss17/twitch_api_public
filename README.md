# <img src="./img/user/LosPerris-minimal.webp" width="40" height="40" style="vertical-align: middle;"> LosPerris Twitch Api Public ✨

API en Flask con endpoints para Valorant y Twitch. Diseñada con caché TTL, sesiones HTTP optimizadas, seguridad global y despliegue sencillo en Vercel.

## 🚀 Despliegue en Vercel

Este proyecto está optimizado para **Vercel**. 

1. **GitHub:** Sube este código a tu repositorio.
2. **Vercel:** Conecta tu repositorio.
3. **Variables de Entorno:** Configura las variables necesarias (ver sección abajo).
4. **Listo!** Tu API estará volando en segundos.

## 🔸 Endpoints Principales

- `/` → Dashboard con acceso rápido a todos los servicios.
- `/twitch` → Panel de control de Twitch.
- `/valorant` → Panel de estadísticas de Valorant.

### 🎮 Valorant
- `/valorant/rango` → Rango actual, MMR y último agente jugado. Soporta `?lang=en` para inglés.
- `/valorant/ultima-ranked` → Detalle de la última partida competitiva. Soporta `?lang=en`.

### 📺 Twitch
- `/twitch/status` → Verifica el estado de tus tokens y configuración.
- `/twitch/followage?user=<nombre>` → Tiempo de seguimiento de un usuario.
- `/twitch/clip` → Crea un clip del canal configurado al instante.
- `/twitch/token` → Genera un token de App (protegido por contraseña).

## ⚙️ Configuración

### Variables de Entorno (Environment Variables)

| Variable | Descripción |
|----------|-------------|
| `API_KEY` | Tu API Key de HenrikDev (Valorant). |
| `ENABLE_VALORANT` | `true`/`false` para habilitar el módulo. |
| `ENDPOINT_PASSWORD` | Contraseña para endpoints protegidos. |
| `CLIENT_ID` | Twitch Client ID. |
| `CLIENT_SECRET` | Twitch Client Secret. |
| `CHANNEL_LOGIN` | Nombre de tu canal de Twitch. |
| `USER_ACCESS_TOKEN` | Token de usuario de Twitch. |

### Personalización de Jugador
Edita `valorant/config.py` para cambiar el perfil de Valorant:
```python
NOMBRE = "TuNombre"
TAG    = "TuTag"
REGION = "na" # na, eu, latam, etc.
```

## 🛠️ Desarrollo Local
1. Instala dependencias: `pip install -r requirements.txt`
2. Ejecuta: `python app.py`
3. Abre: `http://localhost:5000`

## 🛡️ Licencia y Créditos
Proyecto creado por **LosPerris**. 
Puedes usar este código libremente para tus proyectos siempre que mantengas los créditos. 

Consulta el archivo [LICENSE](./LICENSE) para más detalles.

---
Hecho con ❤️ por [LosPerris](https://www.twitch.tv/ponss17)
