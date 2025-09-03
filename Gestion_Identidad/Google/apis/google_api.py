import requests
from django.conf import settings
from debug.loggers import google_logger


API_KEY = getattr(settings, "GOOGLE_API_KEY", None)
CX = getattr(settings, "GOOGLE_CX", None)


def google_search(query, num_results=5):
    """
    Ejecuta una búsqueda en Google Custom Search y deja trazas completas.
    """
    google_logger.debug("── Google API: función google_search llamada ──")
    google_logger.debug(f"🔍 Query recibida: {query}")
    google_logger.debug(f"🔑 API_KEY={API_KEY[:6]}... len={len(API_KEY) if API_KEY else 0}")
    google_logger.debug(f"🔑 CX={CX} len={len(CX) if CX else 0}")

    if not API_KEY or not CX:
        google_logger.error("❌ API_KEY o CX no están configurados en settings.py")
        return None


    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": num_results
    }


    try:
        response = requests.get(url, params=params, timeout=10)
        google_logger.debug(f"📡 Status code: {response.status_code}")


        data = response.json()
        google_logger.debug(f"📦 Respuesta de Google: {data}")


        if response.status_code == 200:
            return data
        else:
            google_logger.error(f"❌ Error en la búsqueda. Código: {response.status_code}")
            return None


    except Exception as e:
        google_logger.error(f"❌ Excepción al llamar a Google API: {str(e)}")
        return None
