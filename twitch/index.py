from flask import Response, request, url_for
from .config import CHANNEL_LOGIN, USER_ACCESS_TOKEN
from common.ui import get_page_layout

def twitch_index():
    base_url = url_for('twitch.status', _external=True).replace('/status', '')
    current_channel = CHANNEL_LOGIN or "TU_CANAL"
    is_connected = bool(USER_ACCESS_TOKEN)

    extra_css = """
        .card { background: var(--card); border: 1px solid var(--brd); border-radius: 20px; padding: 32px; width: 100%; max-width: 440px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
        .header { text-align: center; margin-bottom: 24px; }
        .status { display: inline-flex; align-items: center; gap: 8px; font-size: 0.8rem; background: rgba(255,255,255,0.05); padding: 4px 12px; border-radius: 100px; margin-top: 10px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: #ef4444; }
        .dot.active { background: #22c55e; box-shadow: 0 0 10px #22c55e; }
        .section-title { font-size: 0.8rem; font-weight: 700; color: var(--txt-sec); text-transform: uppercase; letter-spacing: 0.5px; margin: 24px 0 12px; }
        .input-group { margin-bottom: 16px; }
        input { width: 100%; padding: 12px; background: #09090b; border: 1px solid var(--brd); border-radius: 10px; color: white; font-size: 0.95rem; font-family: inherit; }
        input:focus { border-color: var(--acc); outline: none; }
        .bot-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
        .tab { flex: 1; padding: 10px; text-align: center; background: rgba(255,255,255,0.05); border: 1px solid var(--brd); border-radius: 10px; cursor: pointer; font-size: 0.85rem; transition: 0.2s; }
        .tab.active { background: var(--acc-t); color: white; border-color: var(--acc-t); }
        .cmd-box { background: #000; border: 1px solid var(--brd); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
        .cmd-label { font-size: 0.7rem; font-weight: 700; color: var(--acc-t); margin-bottom: 8px; }
        .cmd-row { display: flex; align-items: center; gap: 10px; }
        code { flex: 1; font-family: monospace; font-size: 0.8rem; color: #facc15; overflow-wrap: anywhere; }
        .copy-btn { background: var(--brd); border: none; color: white; padding: 6px 10px; border-radius: 6px; font-size: 0.7rem; cursor: pointer; font-weight: 600; min-width: 60px; }
        .btn-link { display: block; width: 100%; padding: 12px; border-radius: 12px; text-decoration: none; text-align: center; font-weight: 600; font-size: 0.9rem; margin-top: 24px; transition: 0.2s; }
        .btn-p { background: var(--acc-t); color: white; }
        .btn-s { border: 1px solid var(--brd); color: var(--txt-sec); }
        .btn-link:hover { filter: brightness(1.1); transform: translateY(-1px); }
    """

    content = f"""
    <div class="card">
        <div class="header">
            <div style="background: rgba(168, 85, 247, 0.1); width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; border: 1px solid var(--brd);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#a855f7"><path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714Z"/></svg>
            </div>
            <h1 style="font-size: 1.5rem;">Twitch</h1>
            <div class="status">
                <div class="dot {'active' if is_connected else ''}"></div>
                <span>{ "Conectado" if is_connected else "Sin vincular" }</span>
            </div>
        </div>

        <div class="section-title">Canal</div>
        <div class="input-group">
            <input type="text" id="chan" value="{current_channel}" placeholder="Tu canal">
        </div>

        <div class="section-title">Comandos para:</div>
        <div class="bot-tabs">
            <div class="tab active" data-bot="nb">Nightbot</div>
            <div class="tab" data-bot="se">StreamElements</div>
        </div>

        <div class="cmd-box">
            <div class="cmd-label">Followage</div>
            <div class="cmd-row">
                <code id="c1"></code>
                <button class="copy-btn" onclick="cp('c1')">Copiar</button>
            </div>
        </div>
        <div class="cmd-box">
            <div class="cmd-label">Clip</div>
            <div class="cmd-row">
                <code id="c2"></code>
                <button class="copy-btn" onclick="cp('c2')">Copiar</button>
            </div>
        </div>

        <a href="{url_for('twitch.login')}" class="btn-link btn-p">
            { "Reconectar" if is_connected else "Vincular con Twitch" }
        </a>
        <a href="/" class="btn-link btn-s">Volver al inicio</a>
    </div>
    """

    extra_js = f"""
    <script>
        const base = "{base_url}";
        const inp = document.getElementById('chan');
        const tabs = document.querySelectorAll('.tab');
        let bot = 'nb';

        function update() {{
            const c = inp.value.trim() || 'CANAL';
            let q1, q2;
            if (bot === 'nb') {{
                q1 = "$(urlfetch " + base + "/followage?user=$(touser)&channel=" + c + ")";
                q2 = "$(urlfetch " + base + "/clip?channel=" + c + ")";
            }} else {{
                q1 = "${{readapi " + base + "/followage?user=${{user.name}}&channel=" + c + "}}";
                q2 = "${{readapi " + base + "/clip?channel=" + c + "}}";
            }}
            document.getElementById('c1').innerText = q1;
            document.getElementById('c2').innerText = q2;
        }}

        inp.addEventListener('input', update);
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

    return Response(get_page_layout("Twitch", content, extra_css, extra_js), mimetype="text/html")
