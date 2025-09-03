import requests
import json
from django.conf import settings
from debug.loggers import linkedin_logger

# 🔑 Clave API desde settings.py
LINKEDIN_API_KEY = getattr(settings, "LINKEDIN_API_KEY", None)

# 🌍 Base URL de la API en RapidAPI
BASE_URL = "https://linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"

# Encabezados comunes
HEADERS = {
    "x-rapidapi-key": LINKEDIN_API_KEY,
    "x-rapidapi-host": "linkedin-scraper-api-real-time-fast-affordable.p.rapidapi.com"
}


def make_request(endpoint, params=None):
    """Hace una petición genérica a la API de LinkedIn"""
    url = f"{BASE_URL}{endpoint}"
    linkedin_logger.debug(f"🌐 GET {url} con params={params}")

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            linkedin_logger.error("❌ Error decodificando JSON en la respuesta")
            return None
    else:
        linkedin_logger.error(f"❌ Error {response.status_code}: {response.text}")
        return None


def get_profile(username: str):
    """
    Obtener datos de perfil de LinkedIn por username (parte final de la URL).
    Ejemplo: "neal-mohan" → https://www.linkedin.com/in/neal-mohan/
    """
    endpoint = "/profile/detail"
    params = {"username": username}
    data = make_request(endpoint, params)

    if data:
        linkedin_logger.debug(
            f"✅ Perfil encontrado para {username}:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        )
    else:
        linkedin_logger.error(f"❌ No se pudo obtener perfil para {username}")

    return data


def get_profile_from_url(profile_url: str):
    """
    Obtener datos de perfil de LinkedIn a partir de la URL completa.
    Ejemplo: "https://www.linkedin.com/in/john-doe-123456/"
    """
    # Extraer el "username" de la URL (último segmento no vacío)
    parts = [p for p in profile_url.strip().split("/") if p]
    username = parts[-1] if parts else None

    if not username:
        linkedin_logger.error(f"❌ No se pudo extraer username de la URL: {profile_url}")
        return None

    return get_profile(username)
