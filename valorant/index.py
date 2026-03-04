from flask import Response, url_for
from .config import NOMBRE, TAG, REGION


def valorant_index():
    # Pre-build Nightbot commands with explicit parameters - Construir comandos con parámetros explícitos
    rango_url = url_for('valorant.rango', _external=True)
    ultima_url = url_for('valorant.ultima_ranked', _external=True)
    
    # Add explicit params to the URL for confidence - Añadir parámetros explícitos para seguridad
    player_params = f"name={NOMBRE}&tag={TAG}&region={REGION}"
    cmd_rango = f"$(urlfetch {rango_url}?{player_params})"
    cmd_ultima = f"$(urlfetch {ultima_url}?{player_params})"

    html = f"""
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Valorant | LosPerris</title>
    <style>
      :root {{ --bg: #0e1117; --card: #161b22; --brd: #30363d; --txt: #c9d1d9; --acc: #fa4454; --ok: #238636; }}
      body {{ margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); color: var(--txt); font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; padding: 10px; }}
      .app-container {{ width: 100%; max-width: 440px; text-align: center; }}
      .card {{ background: var(--card); border: 1px solid var(--brd); border-radius: 16px; padding: 25px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
      .logo-icon {{ width: 50px; height: 50px; background: #fa4454; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; }}
      .logo-icon svg {{ width: 30px; height: 30px; fill: white; }}
      h1 {{ margin: 0 0 5px; font-size: 20px; color: white; }}
      p {{ color: #8b949e; line-height: 1.4; margin-bottom: 20px; font-size: 0.9rem; }}
      .commands-list {{ margin-top: 20px; text-align: left; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px; border: 1px solid var(--brd); }}
      .commands-list h3 {{ font-size: 0.95rem; margin: 0 0 12px; color: white; }}
      .cmd-item {{ margin-bottom: 12px; }}
      .cmd-item:last-child {{ margin-bottom: 0; }}
      .cmd-item span {{ display: block; color: #8b949e; margin-bottom: 5px; font-weight: 600; font-size: 0.75rem; }}
      .copy-row {{ display: flex; gap: 6px; }}
      code {{ flex-grow: 1; background: #000; color: #fa4454; padding: 8px; border-radius: 6px; font-size: 0.75rem; word-break: break-all; border: 1px solid #333; }}
      .btn-copy {{ background: #30363d; border: 1px solid var(--brd); color: white; padding: 0 10px; border-radius: 6px; cursor: pointer; font-size: 0.75rem; }}
      .status-box {{ margin-top: 20px; padding: 8px; border-radius: 8px; background: rgba(0,0,0,0.1); font-size: 0.8rem; display: flex; align-items: center; justify-content: center; gap: 8px; }}
      .dot {{ width: 6px; height: 6px; border-radius: 50%; background: #238636; box-shadow: 0 0 8px #238636; }}
      .nota-v {{ margin-top: 15px; background: rgba(250, 68, 84, 0.1); border: 1px solid rgba(250, 68, 84, 0.2); padding: 10px; border-radius: 8px; font-size: 0.8rem; text-align: left; color: #ff808b; }}
      .links {{ margin-top: 15px; font-size: 0.8rem; }}
      .links a {{ color: var(--acc); text-decoration: none; opacity: 0.8; }}
    </style>
  </head>
  <body>
    <div class="app-container">
      <div class="card">
        <div class="logo-icon">
          <svg viewBox="0 0 100 100"><path d="M99.15 24c-5.05-5.05-14.54-5.05-19.59 0L49.99 53.58 20.44 24c-5.05-5.05-14.54-5.05-19.59 0-5.05 5.05-5.05 14.54 0 19.59L49.99 93.18l49.16-49.59c5.05-5.05 5.05-14.54 0-19.59z"/></svg>
        </div>
        <h1>Valorant</h1>
        <p>Comandos configurados para {NOMBRE}#{TAG}.</p>
        
        <div class="commands-list">
          <div class="cmd-item">
            <span>Rango Actual:</span>
            <div class="copy-row">
              <code id="cmdRango">{cmd_rango}</code>
              <button class="btn-copy" onclick="copy('cmdRango')">Copiar</button>
            </div>
          </div>
          <div class="cmd-item">
            <span>Última Ranked:</span>
            <div class="copy-row">
              <code id="cmdUltima">{cmd_ultima}</code>
              <button class="btn-copy" onclick="copy('cmdUltima')">Copiar</button>
            </div>
          </div>
        </div>
        
        <div class="nota-v">
            <b>Nota:</b> Prueba usar "na" si no te deja con tu cuenta de latam.
        </div>

        <div class="status-box">
          <div class="dot"></div>
          <span>Región: {REGION.upper()} | Jugador: {NOMBRE}</span>
        </div>
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
