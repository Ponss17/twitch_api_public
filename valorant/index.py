from flask import Response, url_for
from .config import NOMBRE, TAG, REGION
from common.ui import get_page_layout

def valorant_index():
    rango_url = url_for('valorant.rango', _external=True)
    ultima_url = url_for('valorant.ultima_ranked', _external=True)

    logo_valorant = url_for('static', filename='valorant/valorant_logo.webp')

    extra_css = """
        .card { background: var(--card); border: 1px solid var(--brd); border-radius: 20px; padding: 32px; width: 100%; max-width: 440px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
        .header { text-align: center; margin-bottom: 24px; }
        .logo-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; border: 1px solid var(--brd); background: rgba(251, 113, 133, 0.1); overflow: hidden; }
        .logo-box img { width: 28px; height: 28px; object-fit: contain; }
        .section-title { font-size: 0.8rem; font-weight: 700; color: var(--txt-sec); text-transform: uppercase; letter-spacing: 0.5px; margin: 24px 0 12px; }
        .input-row { display: flex; gap: 10px; margin-bottom: 12px; }
        input, select { width: 100%; padding: 12px; background: #09090b; border: 1px solid var(--brd); border-radius: 10px; color: white; font-size: 0.95rem; font-family: inherit; }
        input:focus, select:focus { border-color: var(--acc); outline: none; }
        .bot-tabs { display: flex; gap: 8px; margin-bottom: 16px; margin-top: 12px; }
        .tab { flex: 1; padding: 10px; text-align: center; background: rgba(255,255,255,0.05); border: 1px solid var(--brd); border-radius: 10px; cursor: pointer; font-size: 0.85rem; transition: 0.2s; }
        .tab.active { background: var(--acc-v); color: white; border-color: var(--acc-v); }
        .cmd-box { background: #000; border: 1px solid var(--brd); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
        .cmd-label { font-size: 0.7rem; font-weight: 700; color: var(--acc-v); margin-bottom: 8px; }
        .cmd-row { display: flex; align-items: center; gap: 10px; }
        code { flex: 1; font-family: monospace; font-size: 0.8rem; color: #facc15; overflow-wrap: anywhere; }
        .copy-btn { background: var(--brd); border: none; color: white; padding: 6px 10px; border-radius: 6px; font-size: 0.7rem; cursor: pointer; font-weight: 600; min-width: 60px; }
        .btn-s { display: block; width: 100%; padding: 12px; border-radius: 12px; text-decoration: none; text-align: center; font-weight: 600; font-size: 0.9rem; margin-top: 24px; border: 1px solid var(--brd); color: var(--txt-sec); transition: 0.2s; }
        .btn-s:hover { background: var(--acc-v); color: white; border-color: var(--acc-v); }
    """

    content = f"""
    <div class="card">
        <div class="header">
            <div class="logo-box">
                <img src="{logo_valorant}" alt="Valorant Logo">
            </div>
            <h1 style="font-size: 1.5rem;">Valorant</h1>
            <p style="font-size: 0.9rem; color: var(--txt-sec); margin-top: 4px;">Configura tus comandos</p>
        </div>

        <div class="section-title">Jugador</div>
        <div class="input-row">
            <input type="text" id="name" value="{NOMBRE}" placeholder="Nombre" style="flex: 2;">
            <input type="text" id="tag" value="{TAG}" placeholder="Tag" style="flex: 1;">
        </div>
        <select id="reg">
            <option value="na" {"selected" if REGION == "na" else ""}>NA (Norteamérica)</option>
            <option value="eu" {"selected" if REGION == "eu" else ""}>EU (Europa)</option>
            <option value="latam" {"selected" if REGION == "latam" else ""}>LATAM</option>
            <option value="br" {"selected" if REGION == "br" else ""}>BR (Brasil)</option>
            <option value="ap" {"selected" if REGION == "ap" else ""}>AP (Asia-Pacífico)</option>
            <option value="kr" {"selected" if REGION == "kr" else ""}>KR (Corea)</option>
        </select>

        <div class="section-title">Bot</div>
        <div class="bot-tabs">
            <div class="tab active" data-bot="nb">Nightbot</div>
            <div class="tab" data-bot="se">StreamElements</div>
        </div>

        <div class="cmd-box">
            <div class="cmd-label">Rango Actual</div>
            <div class="cmd-row">
                <code id="c1"></code>
                <button class="copy-btn" onclick="cp('c1')">Copiar</button>
            </div>
        </div>
        <div class="cmd-box">
            <div class="cmd-label">Última Ranked</div>
            <div class="cmd-row">
                <code id="c2"></code>
                <button class="copy-btn" onclick="cp('c2')">Copiar</button>
            </div>
        </div>

        <a href="/" class="btn-s">Volver al inicio</a>
    </div>
    """

    extra_js = f"""
    <script>
        const rU = "{rango_url}";
        const uU = "{ultima_url}";
        const iN = document.getElementById('name');
        const iT = document.getElementById('tag');
        const iR = document.getElementById('reg');
        const tabs = document.querySelectorAll('.tab');
        let bot = 'nb';

        function update() {{
            const n = encodeURIComponent(iN.value.trim() || 'JUGADOR');
            const t = encodeURIComponent(iT.value.trim() || 'TAG');
            const r = iR.value;
            const p = "name=" + n + "&tag=" + t + "&region=" + r;
            
            let q1, q2;
            if (bot === 'nb') {{
                q1 = "$(urlfetch " + rU + "?" + p + ")";
                q2 = "$(urlfetch " + uU + "?" + p + ")";
            }} else {{
                q1 = "${{readapi " + rU + "?" + p + "}}";
                q2 = "${{readapi " + uU + "?" + p + "}}";
            }}
            document.getElementById('c1').innerText = q1;
            document.getElementById('c2').innerText = q2;
        }}

        [iN, iT, iR].forEach(el => el.addEventListener('input', update));
        tabs.forEach(t => t.addEventListener('click', () => {{
            tabs.forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            bot = t.dataset.bot;
            update();
        }}));

        function cp(id) {{
            const txt = document.getElementById(id).innerText;
            navigator.clipboard.writeText(txt).then(() => {{
                const b = event.target;
                const old = b.innerText;
                b.innerText = "¡OK!";
                b.style.background = "#22c55e";
                setTimeout(() => {{ b.innerText = old; b.style.background = ""; }}, 1000);
            }});
        }}
        update();
    </script>
    """

    return Response(get_page_layout("Valorant", content, extra_css, extra_js), mimetype="text/html")
