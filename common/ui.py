from flask import url_for

def get_badge_info():
    """Retorna el HTML y CSS necesario para el badge de LosPerris."""
    logo_url = url_for('static', filename='user/LosPerris-minimal.webp')
    
    css = """
    .badge { position: fixed; bottom: 20px; right: 20px; background: rgba(24, 24, 27, 0.8); backdrop-filter: blur(8px); border: 1px solid var(--brd); padding: 8px 16px; border-radius: 100px; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: var(--txt); text-decoration: none; transition: 0.2s; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.5); font-family: 'Outfit', sans-serif; }
    .badge:hover { transform: translateY(-2px); border-color: var(--acc); background: var(--card); }
    .badge img { width: 16px; height: 16px; border-radius: 50%; }
    """
    
    html = f'''
    <a href="https://losperris.site" target="_blank" class="badge">
        <img src="{logo_url}" alt="Logo">
        <span>LosPerris</span>
    </a>
    '''
    return {"css": css, "html": html}

def get_page_layout(title: str, content: str, extra_css: str = "", extra_js: str = ""):
    """Envoltura común para todas las páginas del proyecto."""
    logo_url = url_for('static', filename='user/LosPerris-minimal.webp')
    badge = get_badge_info()
    
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | LosPerris</title>
    <link rel="icon" type="image/webp" href="{logo_url}">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ 
            --bg: #09090b; 
            --card: #18181b; 
            --brd: #27272a; 
            --txt: #f4f4f5; 
            --txt-sec: #a1a1aa; 
            --acc: #8b5cf6; 
            --acc-v: #fb7185;
            --acc-t: #a855f7;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: var(--bg); 
            color: var(--txt); 
            font-family: 'Outfit', sans-serif; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            padding: 20px;
        }}
        {badge['css']}
        {extra_css}
    </style>
</head>
<body>
    {content}
    {badge['html']}
    {extra_js}
</body>
</html>
"""
