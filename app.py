from flask import Flask, Response, url_for, request, Blueprint
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import logging
import importlib
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Initialization ---
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'img'), static_url_path='/img')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

logging.basicConfig(level=logging.INFO)

# Rate limiting
limiter = Limiter(
    get_remote_address, 
    app=app, 
    default_limits=["100 per minute"], 
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
)

# Security headers - Cabeceras de seguridad
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

# --- Twitch ---
from twitch.endpoints import twitch_bp
from twitch.index import twitch_index

app.register_blueprint(twitch_bp, url_prefix='/twitch')
app.add_url_rule('/twitch', 'twitch_index', view_func=twitch_index)

# --- Valorant (Optional) ---
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

# --- Dashboard ---
@app.route('/')
def index():
    valorant_card = ""
    v_status = "Deshabilitado"
    v_dot = ""
    if valorant_active:
        v_status = "Habilitado"
        v_dot = "active"
        valorant_url = url_for('static', filename='valorant/valorant_Icon_purple.webp')
        valorant_card = f"""
        <div class="card service-card">
            <div class="card-header">
                <img src="{valorant_url}" alt="Valorant" class="service-icon">
                <div class="header-text">
                    <h2>Valorant</h2>
                    <p>Estadísticas y rango actual</p>
                </div>
            </div>
            <div class="card-body">
                <div class="status-indicator">
                    <div class="dot {v_dot}"></div>
                    <span>{v_status}</span>
                </div>
                <div class="card-actions">
                    <a href="/valorant" class="btn btn-primary btn-valorant">Gestionar</a>
                </div>
            </div>
        </div>
        """

    # Better status check for Twitch - Mejor verificación de estado para Twitch
    t_status = "Vincular cuenta"
    t_dot = ""
    if os.environ.get("USER_ACCESS_TOKEN"):
        t_status = "Cuenta vinculada"
        t_dot = "active"

    # Generate URLs for images - Generar URLs para imágenes
    logo_url = url_for('static', filename='user/LosPerris-minimal.webp')
    twitch_icon_url = url_for('static', filename='twitch/twitch.webp')

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LosPerris | Dashboard</title>
    <link rel="icon" type="image/x-icon" href="{logo_url}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0c0e12; --surf: #161a21; --brd: #2d333b; --txt: #f0f6fc; --txt-sec: #8b949e;
            --acc: #8957e5; --val: #fa4454; --twt: #9146ff; --ok: #3fb950;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: var(--bg); color: var(--txt); font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }}
        .container {{ width: 100%; max-width: 800px; animation: fadeIn 0.5s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .logo {{ width: 80px; height: 80px; border-radius: 50%; border: 3px solid var(--acc); margin-bottom: 15px; }}
        h1 {{ font-size: 2rem; margin-bottom: 5px; }}
        .header p {{ color: var(--txt-sec); }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: var(--surf); border: 1px solid var(--brd); border-radius: 16px; transition: 0.2s; overflow: hidden; display: flex; flex-direction: column; }}
        .card:hover {{ border-color: var(--acc); transform: translateY(-3px); }}
        .card-header {{ padding: 25px; display: flex; align-items: center; gap: 15px; }}
        .service-icon {{ width: 45px; height: 45px; border-radius: 10px; }}
        .card-body {{ padding: 0 25px 25px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
        
        .status-indicator {{ display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--txt-sec); margin-bottom: 20px; }}
        .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--txt-sec); }}
        .dot.active {{ background: var(--ok); box-shadow: 0 0 10px var(--ok); }}
        
        .btn {{ display: block; width: 100%; padding: 14px; border-radius: 10px; text-decoration: none; text-align: center; font-weight: 700; font-size: 1rem; transition: 0.2s; color: white; border: none; cursor: pointer; }}
        .btn-twitch {{ background: var(--twt); }}
        .btn-valorant {{ background: var(--val); }}
        .btn:hover {{ filter: brightness(1.1); transform: translateY(-1px); }}
        
        .footer {{ margin-top: 50px; text-align: center; font-size: 0.85rem; color: var(--txt-sec); opacity: 0.6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{logo_url}" alt="Logo" class="logo">
            <h1>LosPerris</h1>
            <p>Panel de Control Simplificado</p>
        </div>
        
        <div class="grid">
            <!-- Twitch Card -->
            <div class="card">
                <div class="card-header">
                    <img src="{twitch_icon_url}" alt="Twitch" class="service-icon">
                    <div class="header-text">
                        <h2>Twitch</h2>
                        <p>Clips y seguidores</p>
                    </div>
                </div>
                <div class="card-body">
                    <div class="status-indicator">
                        <div class="dot {t_dot}"></div>
                        <span>{t_status}</span>
                    </div>
                    <div class="card-actions">
                        <a href="/twitch" class="btn btn-twitch">Gestionar</a>
                    </div>
                </div>
            </div>
            
            {valorant_card}
        </div>
        
        <div class="footer">
            <p>&copy; 2026 LosPerris • Simplicidad ante todo ✨</p>
        </div>
    </div>
</body>
</html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
