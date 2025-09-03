import os
import json
import requests
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from debug.loggers import linkedin_logger
from Gestion_Identidad.Google.views.google_search_view import find_sensitive, dict_to_list

# Clave API desde settings.py
LINKEDIN_API_KEY = getattr(settings, "LINKEDIN_API_KEY", None)

# Endpoint de RapidAPI (puedes cambiarlo si usas otra API de LinkedIn)
BASE_URL = "https://real-time-linkedin-data.p.rapidapi.com/search"

# 📂 Carpeta donde guardaremos las búsquedas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSQUEDAS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "busquedas"))
os.makedirs(BUSQUEDAS_DIR, exist_ok=True)


def make_request(username):
    """Lanza una petición a la API de LinkedIn (RapidAPI)"""
    headers = {
        "x-rapidapi-host": "real-time-linkedin-data.p.rapidapi.com",
        "x-rapidapi-key": LINKEDIN_API_KEY,
    }
    params = {"query": username, "geo": "es", "limit": 1}  # 🔹 Buscamos un usuario en España, máximo 1
    linkedin_logger.debug(f"🌐 GET {BASE_URL} con params={params}")

    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        linkedin_logger.error(f"❌ Error {response.status_code}: {response.text}")
        return None


@api_view(["POST"])
def linkedin_search_view(request):
    """Endpoint para buscar usuarios en LinkedIn"""
    username = request.data.get("username")
    if not username:
        return Response({"status": "error", "message": "Debe indicar un nombre o username."})

    linkedin_logger.debug(f"💼 Buscando en LinkedIn: {username}")

    # 📂 Ruta del archivo JSON
    file_path = os.path.join(BUSQUEDAS_DIR, f"{username}_linkedin.json")

    # 1️⃣ Si ya existe el archivo → lo cargamos
    if os.path.exists(file_path):
        linkedin_logger.debug(f"📂 Archivo ya existe, cargando desde: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        return Response({"status": "success", **result_data})

    # 2️⃣ Llamada a la API si no existe JSON
    data = make_request(username)
    if not data or "data" not in data:
        return Response({"status": "error", "message": f"No se encontró información de {username}"})

    profile = data["data"][0]  # Tomamos el primer resultado

    # 🔍 Datos principales
    user_info = {
        "name": profile.get("fullName"),
        "headline": profile.get("title"),
        "location": profile.get("location"),
        "profile_url": profile.get("profileUrl"),
    }

    # 🔍 Experiencia y educación (depende de la API exacta)
    experiences = profile.get("experiences", [])
    educations = profile.get("education", [])

    # 🔍 Analizamos datos sensibles en los textos
    sensitive_data = {
        "dnis": dict_to_list({}),
        "ibans": dict_to_list({}),
        "cccs": dict_to_list({}),
        "phones": dict_to_list({}),
    }

    # Revisar nombre, headline y experiencias
    find_sensitive(user_info.get("headline", ""), sensitive_data, user_info.get("profile_url", ""))
    for exp in experiences:
        find_sensitive(exp.get("title", ""), sensitive_data, user_info.get("profile_url", ""))
    for edu in educations:
        find_sensitive(edu.get("school", ""), sensitive_data, user_info.get("profile_url", ""))

    result_data = {
        "platform": "LinkedIn",
        "username": username,
        "user": user_info,
        "experiences": experiences,
        "educations": educations,
        "sensitive": sensitive_data,
        "json_file": file_path,
    }

    # 3️⃣ Guardamos en JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)
    linkedin_logger.debug(f"✅ Resultados guardados en {file_path}")

    return Response({"status": "success", **result_data})
