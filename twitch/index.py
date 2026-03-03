from flask import Response, request, url_for
from .config import USER_ACCESS_TOKEN


def twitch_index():
    # Pre-build Nightbot commands - Construir comandos de Nightbot
    base_url = url_for('twitch.status', _external=True).replace('/status', '')
    redirect_uri = url_for('twitch.oauth_callback', _external=True)
    
    cmd_follow = f"$(urlfetch {base_url}/followage?user=$(touser))"
    cmd_clip = f"$(urlfetch {base_url}/clip)"

    is_connected = bool(USER_ACCESS_TOKEN)

    html = f"""
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Twitch | LosPerris</title>
    <style>
      :root {{ --bg: #0e1117; --card: #161b22; --brd: #30363d; --txt: #c9d1d9; --acc: #9146ff; --ok: #238636; }}
      body {{ margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); color: var(--txt); font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; padding: 10px; }}
      .app-container {{ width: 100%; max-width: 440px; text-align: center; }}
      .card {{ background: var(--card); border: 1px solid var(--brd); border-radius: 16px; padding: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
      .logo-icon {{ width: 50px; height: 50px; background: #9146ff; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; }}
      .logo-icon svg {{ width: 30px; height: 30px; fill: white; }}
      h1 {{ margin: 0 0 5px; font-size: 20px; color: white; }}
      p {{ color: #8b949e; line-height: 1.4; margin-bottom: 20px; font-size: 0.9rem; }}
      .btn-main {{ display: block; width: 100%; background: var(--acc); color: white; text-decoration: none; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 1rem; transition: 0.2s; border: none; cursor: pointer; }}
      .btn-main:hover {{ filter: brightness(1.2); }}
      .commands-list {{ margin-top: 20px; text-align: left; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; border: 1px solid var(--brd); }}
      .commands-list h3 {{ font-size: 0.95rem; margin: 0 0 12px; color: white; }}
      .cmd-item {{ margin-bottom: 12px; }}
      .cmd-item:last-child {{ margin-bottom: 0; }}
      .cmd-item span {{ display: block; color: #8b949e; margin-bottom: 5px; font-weight: 600; font-size: 0.75rem; }}
      .copy-row {{ display: flex; gap: 6px; }}
      code {{ flex-grow: 1; background: #000; color: #f59e0b; padding: 8px; border-radius: 6px; font-size: 0.75rem; word-break: break-all; border: 1px solid #333; }}
      .btn-copy {{ background: #30363d; border: 1px solid var(--brd); color: white; padding: 0 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; }}
      .setup-guide {{ margin-top: 20px; text-align: left; border-top: 1px solid var(--brd); padding-top: 15px; }}
      .setup-guide h4 {{ font-size: 0.85rem; color: #fff; margin: 0 0 8px; }}
      .status-box {{ margin-top: 15px; padding: 8px; border-radius: 8px; background: rgba(0,0,0,0.1); font-size: 0.8rem; display: flex; align-items: center; justify-content: center; gap: 8px; }}
      .dot {{ width: 6px; height: 6px; border-radius: 50%; background: #8b949e; }}
      .dot.active {{ background: var(--ok); box-shadow: 0 0 8px var(--ok); }}
      .links {{ margin-top: 15px; font-size: 0.8rem; }}
      .links a {{ color: var(--acc); text-decoration: none; opacity: 0.8; }}
    </style>
  </head>
  <body>
    <div class="app-container">
      <div class="card">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24"><path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z"/></svg>
        </div>
        <h1>Twitch</h1>
        <p>Copia los comandos para tu bot de chat.</p>
        
        <div class="commands-list">
          <div class="cmd-item">
            <span>Followage:</span>
            <div class="copy-row">
              <code id="cmdFollow">{cmd_follow}</code>
              <button class="btn-copy" onclick="copy('cmdFollow')">Copiar</button>
            </div>
          </div>
          <div class="cmd-item">
            <span>Clip:</span>
            <div class="copy-row">
              <code id="cmdClip">{cmd_clip}</code>
              <button class="btn-copy" onclick="copy('cmdClip')">Copiar</button>
            </div>
          </div>
        </div>

        <div class="setup-guide">
          <h4>Vercel/Twitch Dev URI:</h4>
          <div class="copy-row">
            <code id="redirUri">{redirect_uri}</code>
            <button class="btn-copy" onclick="copy('redirUri')">Copiar</button>
          </div>
        </div>

        <div class="status-box">
          <div class="dot {'active' if is_connected else ''}"></div>
          <span>{ "Conectado" if is_connected else "Sin vincular" }</span>
        </div>
        
        <a href="{url_for('twitch.login')}" class="btn-main" style="margin-top:15px; background: transparent; border: 1px solid var(--acc); color: var(--acc); font-size: 0.85rem; padding: 8px;">
           { "Actualizar Conexión" if is_connected else "Vincular Cuenta" }
        </a>
      </div>
      
      <div class="links">
        <a href="/">← Volver al Dashboard</a>
      </div>
    </div>
    <script>
      function copy(id) {{
        const text = document.getElementById(id).innerText;
        navigator.clipboard.writeText(text).then(() => {{
          const btn = event.target;
          const original = btn.innerText;
          btn.innerText = "¡OK!";
          btn.style.background = "#238636";
          setTimeout(() => {{ btn.innerText = original; btn.style.background = ""; }}, 1500);
        }});
      }}
    </script>
  </body>
</html>
    """
    return Response(html, mimetype="text/html")
