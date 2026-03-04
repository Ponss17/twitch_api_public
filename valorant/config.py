import os

# El nombre del jugador debe ser igual al que se usa en el juego.
# El TG no contiene el hashtag (#) solo el valor.
NOMBRE = os.environ.get("VALORANT_USER", "Nayecute Twitch")
TAG    = os.environ.get("VALORANT_TAG", "965")
REGION = os.environ.get("VALORANT_REGION", "na")
# Nota : Prueba usar "na" si no te deja con tu cuenta de latam.

# Aqui puedes definir tu api key de HenrikDev.
# Se recomienda setearla como variable de entorno o utilizar un archivo .env.
API_KEY = os.environ.get("API_KEY", "")
