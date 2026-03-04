from flask import Blueprint, request, Response, url_for
from datetime import datetime, timezone
import urllib.parse
import requests
import os
import re
import logging
import time

from .config import CHANNEL_LOGIN, CLIENT_ID, CLIENT_SECRET, USER_ACCESS_TOKEN, ENDPOINT_PASSWORD
from .api import get_user_id, get_follow_info, validate_token, create_clip, get_clip_url, get_app_token
from common.response import text_response
from common.http import get_session
from common.cache import SimpleTTLCache

twitch_bp = Blueprint('twitch', __name__)
_session = get_session()
_cache = SimpleTTLCache(default_ttl=15)

def _humanize_duration(delta_seconds: float, lang='es') -> str:
    # Convierte segundos en un formato legible (años, meses, días, etc.)
    minutes = int(delta_seconds // 60)
    hours = minutes // 60
    days = hours // 24
    years = days // 365
    months = (days % 365) // 30
    days_rem = (days % 365) % 30

    parts: list[str] = []
    if years:
        p = f"{years} año" if years == 1 else f"{years} años"
        if lang == 'en': p = f"{years} year" if years == 1 else f"{years} years"
        parts.append(p)
    if months:
        p = f"{months} mes" if months == 1 else f"{months} meses"
        if lang == 'en': p = f"{months} month" if months == 1 else f"{months} months"
        parts.append(p)
    if days_rem:
        p = f"{days_rem} día" if days_rem == 1 else f"{days_rem} días"
        if lang == 'en': p = f"{days_rem} day" if days_rem == 1 else f"{days_rem} days"
        parts.append(p)

    if not parts:
        hours_rem = hours % 24
        minutes_rem = minutes % 60
        if hours_rem:
            p = f"{hours_rem} hora" if hours_rem == 1 else f"{hours_rem} horas"
            if lang == 'en': p = f"{hours_rem} hour" if hours_rem == 1 else f"{hours_rem} hours"
            parts.append(p)
        if minutes_rem:
            p = f"{minutes_rem} minuto" if minutes_rem == 1 else f"{minutes_rem} minutos"
            if lang == 'en': p = f"{minutes_rem} minute" if minutes_rem == 1 else f"{minutes_rem} minutes"
            parts.append(p)
        if not parts:
            parts.append("menos de un minuto" if lang == 'es' else "less than a minute")

    sep = ", " if lang == 'es' else ", "
    return sep.join(parts)

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
        lang = request.args.get("lang", "es").lower()
        follower_id = get_user_id(user_login)
        channel_id = get_user_id(channel_login)
        
        if not follower_id:
            msg = f"Usuario '{user_login}' no encontrado" if lang == 'es' else f"User '{user_login}' not found"
            return text_response(msg, 404)
        if not channel_id:
            msg = f"Canal '{channel_login}' no encontrado" if lang == 'es' else f"Channel '{channel_login}' not found"
            return text_response(msg, 404)

        info = get_follow_info(follower_id, channel_id)
        if not info:
            msg = f"{user_login} no sigue a {channel_login}" if lang == 'es' else f"{user_login} is not following {channel_login}"
            return text_response(msg)

        followed_at = datetime.fromisoformat(info.get("followed_at").replace("Z", "+00:00"))
        delta = (datetime.now(timezone.utc) - followed_at).total_seconds()
        
        duration = _humanize_duration(delta, lang)
        if lang == 'en':
            result = f"{user_login} has been following {channel_login} for {duration}."
        else:
            result = f"{user_login} sigue a {channel_login} desde hace {duration}."
            
        _cache.set(cache_key, result)
        return text_response(result)
    except Exception as e:
        logging.error(f"Error in followage: {e}")
        msg = "Error al conectar con Twitch." if lang == 'es' else "Error connecting to Twitch."
        return text_response(msg, 502)

@twitch_bp.route('/token')
def token():
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
    lines = ["Estado de LosPerris Twitch Api Public", "---"]
    
    if not CLIENT_ID: lines.append("❌ CLIENT_ID: No configurado")
    if not CLIENT_SECRET: lines.append("❌ CLIENT_SECRET: No configurado")
    if not CHANNEL_LOGIN: lines.append("⚠️ CHANNEL_LOGIN: No configurado (usará parámetros de URL)")
    
    try:
        tok = get_app_token()
        validate_token(tok)
        lines.append("✅ Conexión con Twitch (App): OK")
    except Exception as e:
        lines.append(f"❌ Conexión con Twitch (App): FALLO")
        lines.append(f"   Detalle: {str(e)[:50]}...")

    if USER_ACCESS_TOKEN:
        try:
            validate_token(USER_ACCESS_TOKEN)
            lines.append("✅ Vinculación de Usuario: OK")
        except Exception as e:
            lines.append("❌ Vinculación de Usuario: TOKEN EXPIRADO O INVÁLIDO")
            lines.append("   Acción: Ve al Dashboard y pulsa 'Actualizar Conexión'.")
    else:
        lines.append("⚠️ Vinculación de Usuario: No realizada")
        lines.append("   Nota: Los clips podrían no funcionar sin esto.")
        
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

@twitch_bp.route('/save-token', methods=['POST'])
def save_token():
    # Guarda el token de usuario en el .env local para persistencia (solo en local)
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    if not token:
        return text_response("Token vacío", 400)

    env_path = os.path.join(os.getcwd(), '.env')
    
    try:
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("USER_ACCESS_TOKEN="):
                new_lines.append(f"USER_ACCESS_TOKEN={token}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"USER_ACCESS_TOKEN={token}\n")
            
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        return text_response("Token guardado correctamente en .env")
    except Exception as e:
        logging.error(f"Error saving token to .env: {e}")
        return text_response(f"Error al guardar: {e}", 500)

@twitch_bp.route('/login')
def login():
    if not CLIENT_ID:
        return text_response("Error: CLIENT_ID no configurado en .env", 500)
    redirect_uri = url_for('twitch.oauth_callback', _external=True)
    
    scopes = "clips:edit+moderator:read:followers"
    twitch_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&response_type=token"
        f"&scope={scopes}"
    )
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Twitch Login</title></head>
    <body style="background:#0e0f12; color:#eaeaea; font-family:sans-serif; text-align:center; padding-top:50px;">
        <p>Redirigiendo a Twitch para autorizar...</p>
        <script>window.location.href = "{twitch_url}";</script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")

@twitch_bp.route('/callback', methods=['GET', 'POST'])
def oauth_callback():
    is_vercel = os.environ.get('VERCEL') == '1'
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Conectando... | LosPerris</title>
        <style>
            body {{ background: #0e0f12; color: #eaeaea; font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }}
            .card {{ background: #1c1f24; border: 1px solid #30343a; padding: 40px; border-radius: 20px; text-align: center; width: 100%; max-width: 450px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }}
            .spinner {{ width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.1); border-top: 4px solid #9146ff; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            h1 {{ font-size: 1.5rem; margin: 0 0 10px; color: #fff; }}
            p {{ color: #a8b0bd; line-height: 1.5; margin: 0 0 20px; }}
            .success-icon {{ font-size: 50px; color: #3fb950; margin-bottom: 20px; display: none; }}
            .token-box {{ background: #000; border: 1px dashed #444; padding: 15px; border-radius: 10px; margin: 20px 0; display: none; text-align: left; }}
            .token-box label {{ display: block; font-size: 0.8rem; color: #8b949e; margin-bottom: 5px; }}
            code {{ display: block; word-break: break-all; color: #f59e0b; font-size: 0.85rem; background: #111; padding: 10px; border-radius: 6px; border: 1px solid #222; }}
            .btn-action {{ display: inline-block; background: #9146ff; color: white; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: 700; border: none; cursor: pointer; transition: 0.2s; }}
            .btn-action:hover {{ filter: brightness(1.1); transform: translateY(-2px); }}
            .step-guide {{ text-align: left; font-size: 0.9rem; margin-top: 20px; display: none; border-top: 1px solid #30343a; padding-top: 20px; }}
            .step-guide ol {{ padding-left: 20px; color: #8b949e; }}
            .step-guide li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="spinner" id="loader"></div>
            <div class="success-icon" id="success">✓</div>
            <h1 id="title">Conectando...</h1>
            <p id="desc">Estamos procesando tu vinculación.</p>
            
            <div id="vercel-content" style="display:none;">
                <div class="token-box">
                    <label>Tu USER_ACCESS_TOKEN:</label>
                    <code id="tokenText"></code>
                </div>
                <button class="btn-action" onclick="copyToken()">Copiar Token</button>
                
                <div class="step-guide">
                    <p style="color:white; font-weight:600;">⚠️ Pasos para Vercel:</p>
                    <ol>
                        <li>Ve a tu proyecto en el panel de Vercel.</li>
                        <li>Entra en <b>Settings</b> -> <b>Environment Variables</b>.</li>
                        <li>Crea una variable llamada <code>USER_ACCESS_TOKEN</code>.</li>
                        <li>Pega el token que acabas de copiar y guarda.</li>
                    </ol>
                    <a href="/" style="color:#9146ff; text-decoration:none; font-size:0.8rem;">← Volver al Inicio</a>
                </div>
            </div>

            <div id="local-content" style="display:none;">
                <a href="/" class="btn-action">Volver al Inicio</a>
            </div>
        </div>

        <script>
            const isVercel = {"true" if is_vercel else "false"};
            const hashParams = new URLSearchParams(window.location.hash.slice(1));
            const token = hashParams.get('access_token');

            if(token) {{
                if(isVercel) {{
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('success').style.display = 'block';
                    document.getElementById('title').innerText = "¡Clave Obtenida!";
                    document.getElementById('desc').innerText = "Como estás en Vercel, debes configurar esta clave manualmente en su panel.";
                    document.getElementById('tokenText').innerText = token;
                    document.getElementById('vercel-content').style.display = 'block';
                    document.querySelector('.token-box').style.display = 'block';
                    document.querySelector('.step-guide').style.display = 'block';
                }} else {{
                    fetch('/twitch/save-token', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token: token }})
                    }}).then(r => {{
                        if(r.ok) {{
                            document.getElementById('loader').style.display = 'none';
                            document.getElementById('success').style.display = 'block';
                            document.getElementById('title').innerText = "¡Todo listo!";
                            document.getElementById('desc').innerText = "Tu cuenta se ha vinculado y guardado automáticamente.";
                            document.getElementById('local-content').style.display = 'block';
                        }} else {{
                            throw new Error();
                        }}
                    }}).catch(() => {{
                        document.getElementById('loader').style.display = 'none';
                        document.getElementById('title').innerText = "Error al guardar";
                        document.getElementById('desc').innerText = "No pudimos escribir en tu archivo .env. Intenta copiar el token manualmente.";
                        // Fallback to showing token if auto-save fails even in local
                        document.getElementById('tokenText').innerText = token;
                        document.getElementById('vercel-content').style.display = 'block';
                    }});
                }}
            }} else {{
                document.getElementById('loader').style.display = 'none';
                document.getElementById('title').innerText = "Error";
                document.getElementById('desc').innerText = "No se recibió el token de Twitch.";
            }}

            function copyToken() {{
                const text = document.getElementById('tokenText').innerText;
                navigator.clipboard.writeText(text).then(() => {{
                    const btn = event.target;
                    const original = btn.innerText;
                    btn.innerText = "¡Copiado!";
                    btn.style.background = "#238636";
                    setTimeout(() => {{ 
                        btn.innerText = original;
                        btn.style.background = "";
                    }}, 2000);
                }});
            }}
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")
