from flask import Blueprint, request, Response, url_for
from datetime import datetime, timezone
import urllib.parse
import requests
import re
import logging
import time

from .config import CHANNEL_LOGIN, CLIENT_ID, CLIENT_SECRET, USER_ACCESS_TOKEN, ENDPOINT_PASSWORD
from .api import get_user_id, get_follow_info, validate_token, create_clip, get_clip_url, get_app_token
from common.response import text_response
from common.http import get_session
from common.cache import SimpleTTLCache

# --- Twitch Module ---
twitch_bp = Blueprint('twitch', __name__)
_session = get_session()
_cache = SimpleTTLCache(default_ttl=15)

# --- Helpers ---
def _humanize_duration(delta_seconds: float) -> str:
    minutes = int(delta_seconds // 60)
    hours = minutes // 60
    days = hours // 24
    years = days // 365
    months = (days % 365) // 30
    days_rem = (days % 365) % 30

    parts: list[str] = []
    if years: parts.append(f"{years} años")
    if months: parts.append(f"{months} meses")
    if days_rem: parts.append(f"{days_rem} días")

    if not parts:
        hours_rem = hours % 24
        minutes_rem = minutes % 60
        if hours_rem: parts.append(f"{hours_rem} horas")
        if minutes_rem: parts.append(f"{minutes_rem} minutos")
        if not parts: parts.append("menos de un minuto")

    return ", ".join(parts)

# --- Routes ---
@twitch_bp.route('/followage')
def followage():
    user_login = request.args.get("user", "").strip().lower()
    channel_login = request.args.get("channel", "").strip().lower() or CHANNEL_LOGIN.lower()

    if not user_login:
        return text_response("Debes poner ?user=<nombre>", 400)
    
    cache_key = f"followage:{user_login}:{channel_login}"
    cached = _cache.get(cache_key)
    if cached: return text_response(cached)

    try:
        follower_id = get_user_id(user_login)
        channel_id = get_user_id(channel_login)
        
        if not follower_id: return text_response(f"Usuario '{user_login}' no encontrado", 404)
        if not channel_id: return text_response(f"Canal '{channel_login}' no encontrado", 404)

        info = get_follow_info(follower_id, channel_id)
        if not info: return text_response(f"{user_login} no sigue a {channel_login}")

        followed_at = datetime.fromisoformat(info.get("followed_at").replace("Z", "+00:00"))
        delta = (datetime.now(timezone.utc) - followed_at).total_seconds()
        
        result = f"{user_login} sigue a {channel_login} desde hace {_humanize_duration(delta)}."
        _cache.set(cache_key, result)
        return text_response(result)
    except Exception as e:
        logging.error(f"Error in followage: {e}")
        return text_response("Error al conectar con Twitch.", 500)

@twitch_bp.route('/token')
def token():
    # App access token generation (password required) - Generar token (requiere clave)
    pwd = request.args.get("password") or request.headers.get("X-Endpoint-Password")
    if ENDPOINT_PASSWORD and pwd != ENDPOINT_PASSWORD:
        return text_response("No autorizado.", 401)

    try:
        tok = get_app_token()
        return text_response(tok)
    except Exception:
        return text_response("Error al generar el token.", 500)

@twitch_bp.route('/status')
def status():
    # Health and token validation - Salud y validación de tokens
    lines = ["Estado de LosPerris Twitch Api Public", ""]
    lines.append(f"Canal principal: {CHANNEL_LOGIN or '(no configurado)'}")

    try:
        tok = get_app_token()
        validate_token(tok)
        lines.append("Token de App: OK")
    except:
        lines.append("Token de App: FALLO")

    if USER_ACCESS_TOKEN:
        try:
            validate_token(USER_ACCESS_TOKEN)
            lines.append("Token de Usuario: OK")
        except:
            lines.append("Token de Usuario: FALLO")
    return text_response("\n".join(lines))

@twitch_bp.route('/clip', methods=['GET', 'POST'])
def clip():
    channel = request.args.get("channel") or CHANNEL_LOGIN
    if not channel: return text_response("Falta el canal.", 400)

    try:
        clip_obj = create_clip(channel.lower())
        if not clip_obj: return text_response("No se pudo crear el clip.", 502)
        
        clip_id = clip_obj.get("id")
        time.sleep(0.5)
        url = get_clip_url(clip_id) or f"https://clips.twitch.tv/{clip_id}"
        return text_response(url)
    except Exception as e:
        logging.error(f"Error creating clip: {e}")
        return text_response("Error al crear el clip.", 500)

@twitch_bp.route('/callback', methods=['GET', 'POST'])
def oauth_callback():
    # Implicit OAuth fragment capture - Captura de fragmento de OAuth
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>LosPerris Twitch Api Public - Auth</h1>
        <p id="msg">Capturando token...</p>
        <script>
            const hash = new URLSearchParams(window.location.hash.slice(1));
            const token = hash.get('access_token');
            if(token) document.getElementById('msg').innerHTML = "Tu token es: <br><code>" + token + "</code>";
            else document.getElementById('msg').innerText = "No se encontró el token.";
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")
