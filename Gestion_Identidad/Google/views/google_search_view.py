from rest_framework.decorators import api_view
from rest_framework.response import Response
from debug.loggers import google_logger
from Gestion_Identidad.Google.apis.google_api import google_search
import os, json, re
from collections import defaultdict
from datetime import datetime


BUSQUEDAS_DIR = os.path.join(os.path.dirname(__file__), "..", "busquedas", "google")
os.makedirs(BUSQUEDAS_DIR, exist_ok=True)


# Regex patrones sensibles
DNI_REGEX = r'\b\d{8}[A-Za-z]\b'
IBAN_REGEX = r'\b[A-Z]{2}\d{2}(?:\s?\d{4}){3,7}\b'
CCC_REGEX = r'\b\d{20}\b'
PHONE_REGEX = r'(?:(?:\+34|0034)?\s*([6-9]\d{2})\s*\d{3}\s*\d{3})'


def find_sensitive(text, sensitive_data, source):
    text = str(text or "")
    try:
        for m in re.findall(DNI_REGEX, text, re.I):
            sensitive_data['dnis'].setdefault(m, set()).add(source)
        for m in re.findall(IBAN_REGEX, text.replace(" ", ""), re.I):
            sensitive_data['ibans'].setdefault(m, set()).add(source)
        for m in re.findall(CCC_REGEX, text, re.I):
            sensitive_data['cccs'].setdefault(m, set()).add(source)
        for m in re.findall(PHONE_REGEX, text, re.I):
            sensitive_data['phones'].setdefault(m, set()).add(source)
    except Exception as e:
        google_logger.error(f"❌ Error en find_sensitive: {e}")



def dict_to_list(d):
    return [{'value': k, 'sources': list(v)} for k, v in d.items()] if d else []


def build_queries(tipo, texto):
    queries = []

    if tipo == "Nombre/Apellidos":
        partes = texto.split(" ", 1)
        nombre = partes[0]
        apellidos = partes[1] if len(partes) > 1 else ""
        base = f"{nombre} {apellidos}".strip()

        queries = [
            f"\"{nombre} {apellidos}\"",
            f"\"{apellidos} {nombre}\"",
            f"{nombre} {apellidos}",
            f"\"{nombre}\" \"{apellidos}\"",
            f"\"{nombre} {apellidos}\" site:linkedin.com",
            f"\"{nombre} {apellidos}\" site:twitter.com",
            f"\"{nombre} {apellidos}\" site:facebook.com",
            f"\"{nombre} {apellidos}\" filetype:pdf"
        ]
    elif tipo == "Nº Teléfono":
        telefono = texto.strip().replace(" ", "").replace("-", "")
        queries = []
        if telefono.startswith("+34"):
            queries.append(f"\"{telefono}\"")
            queries.append(f"\"{telefono[3:]}\"")
        elif telefono.startswith(("6", "7")) and len(telefono) == 9:
            queries.append(f"\"{telefono}\"")
            queries.append(f"\"+34{telefono}\"")
        else:
            queries.append(f"\"{telefono}\"")

        # Dorks
        queries = [
            f"\"{telefono}\"",
            f"\"{tel_int}\"",
            f"\"{telefono}\" site:pastebin.com",
            f"\"{telefono}\" filetype:pdf",
            f"\"{telefono}\" site:facebook.com"
        ]


    elif tipo == "Email":
        user, domain = texto.split("@") if "@" in texto else (texto, "")

        queries = [
            f"\"{texto}\"",
            f"\"{texto.split('@')[0]}\"",
            f"\"{texto}\" site:pastebin.com",
            f"\"{texto}\" site:github.com",
            f"\"{texto}\" site:facebook.com",
            f"\"{texto}\" filetype:txt",
            f"\"{texto}\" filetype:pdf"
        ]

    elif tipo == "DNI":
        dni = texto.upper().replace(" ", "")
        base = dni[:-1] if dni[-1].isalpha() else dni
        letra = dni[-1] if dni[-1].isalpha() else ""
        base = base.zfill(8)

        variantes = [base]
        if letra:
            variantes.append(base + letra)

        # Dorks
        queries = [
            f"\"{base}{letra}\"",
            f"\"{base}\"",
            f"\"{base}{letra}\" site:pastebin.com",
            f"\"{base}\" filetype:pdf",
            f"\"{base}\" site:docs.google.com"
        ]

    elif tipo == "Nombre de usuario":
        username = texto.strip()
        queries = [
            f"\"{username}\"",
            f"@{username} site:twitter.com",
            f"{username} site:twitter.com",
            f"{username} site:instagram.com",
            f"{username} site:github.com",
            f"{username} site:linkedin.com",
            f"{username} site:facebook.com",
            f"{username} site:tiktok.com",
            f"{username} site:pinterest.com",
            f"{username} site:reddit.com",
            f"{username} site:youtube.com",
            f"{username} inurl:profile",
            f"{username} intitle:profile",
            f"{username} \"user\"",
        ]

    else:
        queries = [texto, f"\"{texto}\""]

    return queries



@api_view(['POST'])
def google_search_view(request):
    google_logger.debug("🎯 Endpoint /google_search activado correctamente")
    google_logger.debug(f"📨 Payload recibido: {json.dumps(request.data)}")



    rows = request.data.get("rows", [])
    if not rows:
        return Response({"status": "error", "message": "No hay datos para buscar."})


    all_results = []
    sensitive_data = {
        'dnis': defaultdict(set),
        'ibans': defaultdict(set),
        'cccs': defaultdict(set),
        'phones': defaultdict(set)
    }


    for row in rows:
        texto = row.get("text", "").strip()
        tipo = row.get("selectedOption2", "General")
        num_results = int(row.get("num_results", 5))


        google_logger.debug(f"🔎 Generando queries para tipo={tipo}, texto={texto}")
        queries = build_queries(tipo, texto)


        for q in queries:
            google_logger.debug(f"▶️ Ejecutando búsqueda: {q}")
            data = google_search(q, num_results=num_results)
            if data and "items" in data:
                for item in data["items"]:
                    result = {
                        "query": q,
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "snippet": item.get("snippet")
                    }
                    all_results.append(result)
                    find_sensitive(item.get("snippet", ""), sensitive_data, item.get("link"))
            else:
                google_logger.warning(f"⚠️ Sin resultados para query: {q}")


    # Nombre archivo por timestamp
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_path = os.path.join(BUSQUEDAS_DIR, f"{ts}_Google.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    google_logger.debug(f"✅ Archivo guardado en {file_path}")

    google_logger.debug(f"[GoogleView] Payload recibido: {request.data}")
    google_logger.debug(f"[GoogleView] Procesando fila: texto={texto}, tipo={tipo}")
    google_logger.debug(f"[GoogleView] Guardando archivo en {file_path}")
    return Response({
        "status": "success",
        "results": all_results,
        "sensitive": {
            "dnis": dict_to_list(sensitive_data['dnis']),
            "ibans": dict_to_list(sensitive_data['ibans']),
            "cccs": dict_to_list(sensitive_data['cccs']),
            "phones": dict_to_list(sensitive_data['phones']),
        },
        "json_file": file_path
    })


