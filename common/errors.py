from flask import request, Response

def handle_bot_errors(e):
    """
    Controlador de errores centralizado para bots (Nightbot, StreamElements).
    Si la ruta pertenece a un módulo de API, devuelve texto plano en lugar de HTML.
    """
    path = request.path
    if path.startswith('/twitch') or path.startswith('/valorant'):
        code = getattr(e, 'code', 500)
        msg = "Error: Recurso no encontrado" if code == 404 else f"Error interno del servidor ({code})"
        return Response(msg, status=code, mimetype="text/plain")
    return e
