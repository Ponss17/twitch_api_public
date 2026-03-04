from flask import Flask, Response, url_for, request, Blueprint
import os
from dotenv import load_dotenv

load_dotenv()

import logging
import importlib
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from common.ui import get_page_layout
from common.errors import handle_bot_errors

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), static_url_path='/static')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

logging.basicConfig(level=logging.INFO)

# Rate limiting
limiter = Limiter(
    get_remote_address, 
    app=app, 
    default_limits=["100 per minute"], 
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
)

@app.after_request
def add_security_headers(resp: Response):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('Referrer-Policy', 'no-referrer')
    resp.headers.setdefault(
        'Content-Security-Policy',
        "default-src 'self' https:; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'"
    )
    return resp

@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(502)
def bot_error_handler(e):
    return handle_bot_errors(e)

from twitch.endpoints import twitch_bp
from twitch.index import twitch_index

app.register_blueprint(twitch_bp, url_prefix='/twitch')
app.add_url_rule('/twitch', 'twitch_index', view_func=twitch_index)

ENABLE_VALORANT = os.environ.get("ENABLE_VALORANT", "true").lower() == "true"
valorant_active = False

if ENABLE_VALORANT and os.path.isdir(os.path.join(os.path.dirname(__file__), 'valorant')):
    try:
        v_module = importlib.import_module('valorant.endpoints')
        v_index = importlib.import_module('valorant.index').valorant_index
        
        app.register_blueprint(v_module.valorant_bp, url_prefix='/valorant')
        app.add_url_rule('/valorant', 'valorant_index_page', view_func=v_index)
        valorant_active = True
    except Exception as e:
        logging.error(f"Error loading Valorant module: {e}")

@app.route('/favicon.ico')
@app.route('/favicon.png')
def favicon():
    return app.send_static_file('user/LosPerris-minimal.webp')

@app.route('/')
def index():
    t_status = "Sin vincular"
    t_dot = ""
    t_note = ""
    if os.environ.get("USER_ACCESS_TOKEN"):
        try:
            # Validamos el token y calculamos los días restantes para mostrar el aviso de renovación
            from twitch.api import validate_token
            info = validate_token(os.environ.get("USER_ACCESS_TOKEN"))
            expires_in = info.get("expires_in", 0)
            days = expires_in // 86400
            t_status = "Conectado"
            t_dot = "active"
            if days > 0:
                t_note = f'<div class="token-note">Vence en {days} días</div>'
            else:
                t_note = '<div class="token-note" style="color:#fb7185">Vence hoy</div>'
        except:
            t_status = "Token expirado"
            t_dot = ""
            t_note = '<div class="token-note" style="color:#fb7185">Renueva la conexión</div>'

    v_status = "Deshabilitado"
    v_dot = ""
    if valorant_active:
        from valorant.config import API_KEY as V_API_KEY
        if V_API_KEY:
            v_status = "Habilitado"
            v_dot = "active"
        else:
            v_status = "Falta API Key"
            v_dot = ""
    
    logo_url = url_for('static', filename='user/LosPerris-minimal.webp')
    
    valorant_card_html = ""
    if valorant_active:
        valorant_icon_url = url_for('static', filename='valorant/valorant_logo.webp')
        valorant_card_html = f"""
            <a href="/valorant" class="card card-v">
                <div class="card-header">
                    <div class="card-icon" style="background: rgba(251, 113, 133, 0.1);">
                        <img src="{valorant_icon_url}" width="28" height="28" alt="Valorant">
                    </div>
                    <div class="card-title">
                        <h2>Valorant</h2>
                        <p>Rango y última partida</p>
                    </div>
                </div>
                <div class="status">
                    <span class="dot {v_dot}"></span>
                    {v_status}
                </div>
                <div class="btn">Gestionar</div>
            </a>
        """

    extra_css = """
        .container { width: 100%; max-width: 600px; padding: 40px 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .profile-img { width: 80px; height: 80px; border-radius: 50%; border: 2px solid var(--acc); margin-bottom: 16px; opacity: 0.9; }
        h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 4px; }
        .subtitle { color: var(--txt-sec); font-size: 0.9rem; }
        .grid { display: grid; gap: 16px; margin-top: 32px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
        .card { background: var(--card); border: 1px solid var(--brd); border-radius: 16px; padding: 24px; text-decoration: none; color: inherit; display: flex; flex-direction: column; transition: 0.2s; }
        .card:hover { border-color: var(--acc); transform: translateY(-2px); }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .card-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); border: 1px solid var(--brd); }
        .card-title h2 { font-size: 1.1rem; }
        .card-title p { font-size: 0.75rem; color: var(--txt-sec); }
        .status { display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: var(--txt-sec); margin-top: auto; padding-top: 16px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; }
        .active { background: #22c55e !important; box-shadow: 0 0 10px rgba(34, 197, 94, 0.4); }
        .token-note { font-size: 0.7rem; color: var(--txt-sec); margin-top: 4px; font-weight: 600; }
        .btn { display: block; text-align: center; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid var(--brd); border-radius: 8px; font-size: 0.85rem; font-weight: 600; margin-top: 16px; transition: 0.2s; }
        .card:hover .btn { background: var(--acc); color: white; border-color: var(--acc); }

        .card-v:hover { border-color: #fb7185 !important; }
        .card-v:hover .btn { background: #fb7185 !important; border-color: #fb7185 !important; color: white !important; }
        .footer { text-align: center; margin-top: 40px; color: var(--txt-sec); font-size: 0.8rem; opacity: 0.6; }
    """

    content = f"""
    <div class="container">
        <div class="header">
            <img src="{logo_url}" alt="Logo" class="profile-img">
            <h1>LosPerris API</h1>
            <p class="subtitle">Panel de control de comandos</p>
        </div>

        <div class="grid">
            <a href="/twitch" class="card">
                <div class="card-header">
                    <div class="card-icon" style="background: rgba(168, 85, 247, 0.1);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#a855f7"><path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z"/></svg>
                    </div>
                    <div class="card-title">
                        <h2>Twitch</h2>
                        <p>Clips y seguimiento</p>
                    </div>
                </div>
                <div class="status" style="flex-direction: column; align-items: flex-start; gap: 2px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span class="dot {t_dot}"></span>
                        {t_status}
                    </div>
                    {t_note}
                </div>
                <div class="btn">Gestionar</div>
            </a>

            {valorant_card_html}
        </div>

        <div class="footer">
            &copy; 2026 LosPerris • v1.5.0
        </div>
    </div>
    """
    return Response(get_page_layout("Dashboard", content, extra_css), mimetype="text/html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
