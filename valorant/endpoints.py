from flask import Blueprint, request, Response
import os
import requests
import logging
import urllib.parse

from .config import NOMBRE, TAG, REGION, API_KEY
from .rangos_es import Rangos_ES
from common.response import text_response
from common.http import get_session
from common.cache import SimpleTTLCache

# --- Valorant Module ---
valorant_bp = Blueprint('valorant', __name__)
_session = get_session()
_cache = SimpleTTLCache(default_ttl=int(os.environ.get("VALORANT_CACHE_TTL", "15")))

# --- Helpers ---
def _quoted(s: str) -> str:
    return urllib.parse.quote(s or "", safe='')

def _format_delta(delta, lang='es'):
    if not isinstance(delta, int): 
        return "sin cambios" if lang == 'es' else "no changes"
    
    if lang == 'en':
        if delta > 0: return f"gained {delta} points"
        if delta < 0: return f"lost {abs(delta)} points"
        return "points didn't change"
    else:
        if delta > 0: return f"gané {delta} puntos"
        if delta < 0: return f"perdí {abs(delta)} puntos"
        return "no cambiaron mis puntos"

# --- Routes ---
@valorant_bp.route('/rango')
def rango():
    lang = request.args.get("lang", "es").lower()
    if not (API_KEY or "").strip():
        return text_response("API_KEY vacía.", 500)

    cache_key = f"rango:{REGION}:{NOMBRE}:{TAG}:{lang}"
    cached = _cache.get(cache_key)
    if cached: return text_response(cached)

    try:
        # API request - Petitorio de datos
        url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{REGION}/{_quoted(NOMBRE)}/{_quoted(TAG)}?api_key={API_KEY}"
        res = _session.get(url, timeout=10)
        res.raise_for_status()
        data = res.json().get('data', {}).get('current_data', {})

        if not data: return text_response("Sin datos.")

        rango_en = data.get('currenttierpatched')
        rango_display = Rangos_ES.get(rango_en, rango_en) if lang == 'es' else rango_en
        puntos = data.get('ranking_in_tier')
        delta = _format_delta(data.get('mmr_change_to_last_game'), lang)
        agente = obtener_ultimo_agente()

        if lang == 'en':
            respuesta = f"Rank: {rango_display} with {puntos} points. Last match was with {agente or 'someone'} and I {delta}."
        else:
            respuesta = f"Actualmente estoy en {rango_display} con {puntos} puntos. Mi última partida fue con {agente or 'alguien'} y {delta}."
            
        _cache.set(cache_key, respuesta)
        return text_response(respuesta)
    except Exception as e:
        logging.error(f"Error in rank endpoint: {e}")
        return text_response("Servicio no disponible.", 502)

def obtener_ultimo_agente():
    try:
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/{REGION}/{_quoted(NOMBRE)}/{_quoted(TAG)}?api_key={API_KEY}"
        data = _session.get(url, timeout=10).json()
        if data.get('status') == 200 and data.get('data'):
            match = data['data'][0]
            for p in match.get('players', {}).get('all_players', []):
                if p.get('name', '').lower() == NOMBRE.lower():
                    return p.get('character')
    except: pass
    return None

@valorant_bp.route('/ultima-ranked')
def ultima_ranked():
    lang = request.args.get("lang", "es").lower()
    try:
        # Match history - Historial de partidas
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/{REGION}/{_quoted(NOMBRE)}/{_quoted(TAG)}?api_key={API_KEY}"
        data = _session.get(url, timeout=10).json()

        if data.get('status') != 200 or not data.get('data'):
            return text_response("Sin actividad." if lang == 'es' else "No activity.")

        for match in data['data']:
            if match.get('metadata', {}).get('mode', '').lower() == 'competitive':
                meta = match.get('metadata', {})
                mapa = meta.get('map')
                
                for p in match.get('players', {}).get('all_players', []):
                    if p.get('name', '').lower() == NOMBRE.lower():
                        stats = p.get('stats', {})
                        k, d, a = stats.get('kills'), stats.get('deaths'), stats.get('assists')
                        team = p.get('team')
                        personaje = p.get('character')
                        gano = match.get('teams', {}).get(team.lower(), {}).get('has_won')
                        break
                
                if lang == 'en':
                    res = "Win" if gano else "Loss"
                    return text_response(f"Match: {res} in {mapa} | Agent: {personaje} | KDA: {k}/{d}/{a}")
                else:
                    res = "Victoria" if gano else "Derrota"
                    # here you can change the text of the message - Aqui puedes cambiar el texto del mensaje 
                    return text_response(f"Mi última partida fue {res} en {mapa} con {personaje}. KDA: {k}/{d}/{a}.")
                    
        return text_response("Sin ranked." if lang == 'es' else "No ranked found.")
    except Exception as e:
        logging.error(f"Error checking last match: {e}")
        return text_response("Error.", 500)
