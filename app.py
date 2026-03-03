from flask import Flask, Response, url_for, request
import os
import logging
import importlib
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Initialization ---
app = Flask(__name__, static_folder='img', static_url_path='/img')
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
        "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'"
    )
    return resp

# --- Twitch ---
from twitch.endpoints import twitch_bp
from twitch.index import twitch_index

app.register_blueprint(twitch_bp, url_prefix='/twitch')
app.add_url_rule('/oauth/callback', 'oauth_callback_legacy', view_func=twitch_bp.view_functions['oauth_callback'])
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
    if valorant_active:
        valorant_card = f"""
        <div class="card service-card">
            <div class="card-header">
                <img src="{url_for('static', filename='valorant/valorant_Icon_purple.webp')}" alt="Valorant" class="service-icon">
                <div class="header-text">
                    <h2>Valorant Stats</h2>
                    <p>Estado actual y MMR</p>
                </div>
            </div>
            <div class="card-body">
                <ul class="endpoint-list">
                    <li>
                        <div style="display: flex; align-items: center; width: 100%;">
                            <a href="/valorant/rango"><code>/valorant/rango</code></a>
                            <button class="copy-btn" onclick="copyCmd('/valorant/rango')" title="Copiar comando Nightbot">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            </button>
                            <span class="badge">GET</span>
                        </div>
                    </li>
                    <li>
                        <div style="display: flex; align-items: center; width: 100%;">
                            <a href="/valorant/ultima-ranked"><code>/valorant/ultima-ranked</code></a>
                            <button class="copy-btn" onclick="copyCmd('/valorant/ultima-ranked')" title="Copiar comando Nightbot">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            </button>
                            <span class="badge">GET</span>
                        </div>
                    </li>
                </ul>
                <div class="card-footer">
                    <a href="/valorant" class="btn btn-primary btn-valorant">Ver Detalle</a>
                </div>
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LosPerris Twitch Api Public | Dashboard</title>
    <link rel="icon" type="image/x-icon" href="{url_for('static', filename='user/LosPerris-minimal.webp')}">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0c0e12; --surf: #161a21; --brd: #2d333b; --txt: #f0f6fc; --txt-sec: #8b949e;
            --acc: #7c4dff; --val: #fa4454; --twt: #9146ff; --ok: #3fb950;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: var(--bg); color: var(--txt); font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }}
        .container {{ width: 100%; max-width: 900px; animation: fadeIn 0.5s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .header {{ display: flex; align-items: center; gap: 15px; margin-bottom: 30px; }}
        .logo {{ width: 60px; height: 60px; border-radius: 50%; border: 2px solid var(--acc); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }}
        .card {{ background: var(--surf); border: 1px solid var(--brd); border-radius: 12px; transition: 0.2s; overflow: hidden; }}
        .card:hover {{ border-color: var(--acc); transform: translateY(-3px); }}
        .card-header {{ padding: 20px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--brd); }}
        .service-icon {{ width: 35px; height: 35px; border-radius: 6px; }}
        .card-body {{ padding: 20px; }}
        .endpoint-list {{ list-style: none; }}
        .endpoint-list li {{ margin-bottom: 10px; display: flex; justify-content: space-between; }}
        .endpoint-list a {{ color: var(--txt); text-decoration: none; font-size: 0.9rem; }}
        .endpoint-list a:hover {{ color: var(--acc); }}
        code {{ background: rgba(255,255,255,0.05); padding: 2px 5px; border-radius: 4px; font-family: monospace; flex-grow: 1; }}
        .badge {{ font-size: 0.65rem; color: var(--ok); border: 1px solid var(--ok); padding: 1px 4px; border-radius: 4px; margin-left: 8px; flex-shrink: 0; }}
        .copy-btn {{ background: transparent; border: none; color: var(--txt-sec); cursor: pointer; padding: 4px; margin-left: 8px; transition: 0.2s; display: flex; align-items: center; border-radius: 4px; }}
        .copy-btn:hover {{ color: var(--acc); background: rgba(255,255,255,0.05); }}
        .copy-btn svg {{ width: 14px; height: 14px; }}
        .card-footer {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--brd); }}
        .btn {{ display: block; padding: 10px; border-radius: 8px; text-decoration: none; text-align: center; font-weight: 600; font-size: 0.9rem; transition: 0.2s; color: white; }}
        .btn-twitch {{ background: var(--twt); }}
        .btn-valorant {{ background: var(--val); }}
        .btn:hover {{ opacity: 0.8; }}
        .footer {{ margin-top: 30px; text-align: center; font-size: 0.8rem; color: var(--txt-sec); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{url_for('static', filename='user/LosPerris-minimal.webp')}" alt="Logo" class="logo">
            <h1>LosPerris Twitch Api Public</h1>
        </div>
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <img src="{url_for('static', filename='twitch/twitch.webp')}" alt="Twitch" class="service-icon">
                <div class="header-text">
                    <h2>Twitch API</h2>
                    <p>Uso público, gestión privada</p>
                </div>
                </div>
                <div class="card-body">
                    <ul class="endpoint-list">
                        <li>
                            <div style="display: flex; align-items: center; width: 100%;">
                                <a href="/twitch/status"><code>/twitch/status</code></a>
                                <button class="copy-btn" onclick="copyCmd('/twitch/status')" title="Copiar comando">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                </button>
                                <span class="badge">GET</span>
                            </div>
                        </li>
                        <li>
                            <div style="display: flex; align-items: center; width: 100%;">
                                <a href="/twitch/followage?user=ponss17"><code>/twitch/followage</code></a>
                                <button class="copy-btn" onclick="copyCmd('/twitch/followage?user=$(touser)')" title="Copiar comando Nightbot">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                </button>
                                <span class="badge">GET</span>
                            </div>
                        </li>
                        <li>
                            <div style="display: flex; align-items: center; width: 100%;">
                                <a href="/twitch/clip"><code>/twitch/clip</code></a>
                                <button class="copy-btn" onclick="copyCmd('/twitch/clip')" title="Copiar comando">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                </button>
                                <span class="badge">POST</span>
                            </div>
                        </li>
                    </ul>
                    <div class="card-footer">
                        <a href="/twitch" class="btn btn-twitch">Ver Endpoints</a>
                    </div>
                </div>
            </div>
            {valorant_card}
        </div>
        <div class="footer">
            <p>&copy; 2024 LosPerris • Desplegado en Vercel ✨</p>
        </div>
    </div>
    <script>
        function copyCmd(path) {{
            const url = window.location.origin + path;
            const fullCmd = path.includes('followage') || path.includes('rango') || path.includes('ranked') 
                ? `$(urlfetch ${{url}})` 
                : url;
            
            navigator.clipboard.writeText(fullCmd).then(() => {{
                const btn = event.currentTarget;
                const originalInner = btn.innerHTML;
                btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ok)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
                setTimeout(() => btn.innerHTML = originalInner, 2000);
            }});
        }}
    </script>
</body>
</html>
    """
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
