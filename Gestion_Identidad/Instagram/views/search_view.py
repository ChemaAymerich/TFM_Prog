from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import os
from collections import defaultdict

from Gestion_Identidad.Instagram.apis.instagram_api import get_user_info, get_user_posts, get_detailed_posts

from Gestion_Identidad.Google.views.google_search_view import find_sensitive, dict_to_list

from Gestion_Identidad.Google.apis.google_api import google_search

from Gestion_Identidad.Twitter.apis.twitter_api import get_user_info as twitter_user_info, get_user_tweets

from Gestion_Identidad.Linkedin.apis.linkedin_api import get_profile_from_url





from debug.loggers import instagram_logger, google_logger, general_logger,twitter_logger,linkedin_logger




@api_view(['POST'])
def search(request):
    try:
        general_logger.debug("─" * 120)
        google_logger.debug("─" * 120)
        twitter_logger.debug("─" * 120)
        linkedin_logger.debug("─" * 120)
        general_logger.debug("🎯 Endpoint /search activado correctamente")
        general_logger.debug(f"📨 Payload recibido: {json.dumps(request.data)}")


        rows = request.data.get('rows', [])
        general_logger.debug(f"📨 Rows recibido: {rows}")


        if not rows or not rows[0].get('text'):
            return Response({'status': 'error', 'message': 'El campo de texto es obligatorio.'})


        all_results_final = []


        for row in rows:
            platform = row.get('selectedOption1')
            text = row.get('text')
            tipo = row.get('selectedOption2')


            general_logger.debug(f"▶️ Procesando fila -> platform={platform}, text={text}, tipo={tipo}")


            # 🚀 Rama Google
            if platform == "Google":
                google_logger.debug(f"▶️ Llamando a Google con texto={text}, tipo={tipo}")


                queries = []
                if tipo == "Nombre/Apellidos":
                    partes = text.split(" ", 1)
                    nombre = partes[0]
                    apellidos = partes[1] if len(partes) > 1 else ""


                    queries = [
                        f"\"{nombre} {apellidos}\"",
                        f"\"{apellidos} {nombre}\"",
                        f"{nombre} {apellidos}",
                        f"\"{nombre}\" \"{apellidos}\""
                    ]


                elif tipo == "Nº Teléfono":
                    telefono = text.strip()
                    if telefono.startswith(("6", "7")):
                        queries.append(f"\"+34{telefono}\"")
                    queries.append(f"\"{telefono}\"")


                elif tipo == "Email":
                    queries = [
                        f"\"{text}\"",
                        f"\"{text.split('@')[0]}\""
                    ]


                elif tipo == "DNI":
                    dni = text.strip().upper()
                    if dni[-1].isalpha():  # Con letra
                        numero = dni[:-1].zfill(8)
                        letra = dni[-1]
                        queries.append(f"\"{numero}{letra}\"")
                        queries.append(f"\"{numero}\"")
                    else:  # Solo números
                        queries.append(f"\"{dni.zfill(8)}\"")


                else:
                    google_logger.warning(f"⚠️ Tipo de búsqueda desconocido: {tipo}")
                    queries = [text]


                all_results = []
                sensitive_data = {
                    'dnis': defaultdict(set),
                    'ibans': defaultdict(set),
                    'cccs': defaultdict(set),
                    'phones': defaultdict(set)
                }

                for q in queries:
                    google_logger.debug(f"🔎 Ejecutando búsqueda: {q}")
                    data = google_search(q, num_results=5)


                    if data and "items" in data:
                        for item in data.get("items", []):  # ✅ usamos get con lista vacía
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


                all_results_final.append({
                    "platform": "Google",
                    "tipo": tipo,
                    "texto": text,
                    "results": all_results,
                    "sensitive": {
                        "dnis": dict_to_list(sensitive_data['dnis']),
                        "ibans": dict_to_list(sensitive_data['ibans']),
                        "cccs": dict_to_list(sensitive_data['cccs']),
                        "phones": dict_to_list(sensitive_data['phones']),
                    }
                })
                google_logger.debug(f"📊 Resultados recopilados Google: {len(all_results)} items")
                safe_sensitive = {
                    "dnis": dict_to_list(sensitive_data['dnis']),
                    "ibans": dict_to_list(sensitive_data['ibans']),
                    "cccs": dict_to_list(sensitive_data['cccs']),
                    "phones": dict_to_list(sensitive_data['phones']),
                }
                google_logger.debug(f"📊 Sensitive extraído: {json.dumps(safe_sensitive, indent=2, ensure_ascii=False)}")


            # 🚀 Rama Instagram
            elif platform == "Instagram":
                general_logger.debug("🌐 Entrando en rama Instagram en search_view.py")
                num_photos_raw = row.get('numPhotos')
                if not num_photos_raw:
                    return Response({'status': 'error', 'message': 'Debes indicar cuántas fotos analizar.'})
                n_fotos = int(num_photos_raw)
                instagram_logger.debug(f"Número de fotos: {n_fotos}")


                username = text
                base_dir = os.path.dirname(os.path.abspath(__file__))
                busquedas_dir = os.path.normpath(os.path.join(base_dir, '..', 'busquedas'))
                user_base_folder = os.path.join(busquedas_dir, username)
                posts_folder = os.path.join(user_base_folder, str(n_fotos))
                os.makedirs(posts_folder, exist_ok=True)


                user_info_path = os.path.join(user_base_folder, 'user_info.json')
                user_posts_save_path = os.path.join(user_base_folder, 'user_posts.json')
                detailed_info_path = os.path.join(posts_folder, f'full_information_{n_fotos}_posts.json')


                if os.path.exists(user_info_path):
                    instagram_logger.debug(f"📂 Archivo user_info.json ya existe: {user_info_path}")
                    with open(user_info_path, 'r', encoding='utf-8') as f:
                        user_info = json.load(f)
                else:
                    instagram_logger.debug("🆕 user_info.json no existe, llamando a API")
                    user_info, user_id, _ = get_user_info(username)
                    with open(user_info_path, 'w', encoding='utf-8') as f:
                        json.dump(user_info, f, indent=4)


                user_data = user_info.get("data", {}).get("user", {})
                user_id = user_data.get("id") or user_data.get("pk")
                if not user_id:
                    return Response({'status': 'error', 'message': f"No se pudo obtener el ID de {username}"})


                instagram_logger.debug(f"✅ Usuario {username} preparado. user_id: {user_id}")


                if os.path.exists(user_posts_save_path):
                    instagram_logger.debug(f"📂 user_posts.json ya existe: {user_posts_save_path}")
                    with open(user_posts_save_path, 'r', encoding='utf-8') as f:
                        user_posts = json.load(f)
                else:
                    instagram_logger.debug("🆕 Llamando a get_user_posts")
                    user_posts = get_user_posts(username, user_id, n_fotos, posts_folder)
                    with open(user_posts_save_path, 'w', encoding='utf-8') as f:
                        json.dump(user_posts, f, indent=4)


                if os.path.exists(detailed_info_path):
                    with open(detailed_info_path, 'r', encoding='utf-8') as f:
                        detailed_posts = json.load(f)
                else:
                    detailed_posts = get_detailed_posts(user_posts, n_fotos, user_id, username, posts_folder)


                instagram_logger.debug(f"📦 search finalizado. Enviando datos de {username} con {n_fotos} fotos.")
                all_results_final.append({
                    'platform': 'Instagram',
                    'username': username,
                    'user_data': user_info,
                    'user_posts': user_posts
                })
            elif platform == "Twitter":
                twitter_logger.debug(f"🐦 Llamando a Twitter con username={text}")

                # 📂 Carpeta de búsquedas
                busquedas_dir = os.path.join(
                    os.path.dirname(__file__), "..", "..", "Twitter","busquedas",
                )
                os.makedirs(busquedas_dir, exist_ok=True)
                file_path = os.path.join(busquedas_dir, f"{text}.json")

                # 1️⃣ Si ya existe, cargar desde JSON
                if os.path.exists(file_path):
                    twitter_logger.debug(f"📂 Archivo ya existe, cargando desde: {file_path}")
                    with open(file_path, "r", encoding="utf-8") as f:
                        result_data = json.load(f)
                    all_results_final.append(result_data)
                    continue
                
                # 2️⃣ Si no existe → llamar a la API
                user_info = twitter_user_info(text)
                if not user_info or "data" not in user_info:
                    all_results_final.append({
                        "platform": "Twitter",
                        "status": "error",
                        "message": f"No se encontró el usuario {text}"
                    })
                    continue
                
                user_id = user_info["data"]["id"]
                tweets = get_user_tweets(user_id, max_results=10)
                sensitive_data = {
                    'dnis': defaultdict(set),
                    'ibans': defaultdict(set),
                    'cccs': defaultdict(set),
                    'phones': defaultdict(set)
                }

                for t in tweets.get("data", []):
                    find_sensitive(
                        t.get("text", ""), 
                        sensitive_data, 
                        f"https://twitter.com/{text}/status/{t.get('id')}"
                    )

                sensitive_summary = {
                    "dnis": dict_to_list(sensitive_data['dnis']),
                    "ibans": dict_to_list(sensitive_data['ibans']),
                    "cccs": dict_to_list(sensitive_data['cccs']),
                    "phones": dict_to_list(sensitive_data['phones']),
                }  
                              
                result_data = {
                    "platform": "Twitter",
                    "status": "success",
                    "username": text,
                    "user": user_info["data"],  
                    "tweets": tweets.get("data", []),
                    "sensitive": sensitive_summary,
                    "json_file": file_path
                }

                # 3️⃣ Guardar en JSON
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result_data, f, indent=4, ensure_ascii=False)
                twitter_logger.debug(f"💾 Resultados guardados en {file_path}")

                all_results_final.append(result_data)

            elif platform == "LinkedIn":
                linkedin_logger.debug(f"💼 [LinkedIn] Iniciando búsqueda para {text} (tipo={tipo})")

                from Gestion_Identidad.Linkedin.apis.linkedin_api import get_profile_from_url

                # 📂 Carpeta de búsquedas para LinkedIn
                busquedas_dir = os.path.join(
                    os.path.dirname(__file__), "..", "..", "Linkedin", "busquedas"
                )
                os.makedirs(busquedas_dir, exist_ok=True)

                # Nombre de archivo seguro (usar username de la URL o del texto)
                username = text.rstrip("/").split("/")[-1]
                filename = username or "linkedin_profile"
                file_path = os.path.join(busquedas_dir, f"{filename}.json")


                # 1️⃣ Si ya existe el archivo → cargarlo
                if os.path.exists(file_path):
                    linkedin_logger.debug(f"📂 [LinkedIn] Archivo ya existe, cargando desde: {file_path}")
                    with open(file_path, "r", encoding="utf-8") as f:
                        result_data = json.load(f)
                    all_results_final.append(result_data)
                    continue

                if tipo == "URL del perfil ó Nombre de usuario":
                    linkedin_logger.debug(f"🌐 [LinkedIn] Llamando a get_profile_from_url con {text}")
                    data = get_profile_from_url(text)
                else:
                    all_results_final.append({
                        "platform": "LinkedIn",
                        "status": "error",
                        "message": f"Tipo de búsqueda '{tipo}' no soportado con la nueva API"
                    })
                    continue
                
                linkedin_logger.debug(f"🔎 [LinkedIn] Respuesta cruda: {json.dumps(data, indent=2, ensure_ascii=False) if data else 'None'}")

                # 🚨 Manejo de errores cuando la API devuelve null
                if not data or not data.get("success") or not data.get("data"):
                    all_results_final.append({
                        "platform": "LinkedIn",
                        "status": "error",
                        "message": f"No se encontró información de {text} o el servicio está suspendido"
                    })
                    continue
                
                # ✅ Si hay datos, procesamos normalmente
                profile = data["data"]

                user_info = {
                    "name": profile.get("basic_info", {}).get("fullname"),
                    "headline": profile.get("basic_info", {}).get("headline"),
                    "location": profile.get("basic_info", {}).get("location", {}).get("full"),
                    "profile_url": f"https://www.linkedin.com/in/{profile.get('basic_info', {}).get('public_identifier', '')}",
                }

                experiences = profile.get("experience", [])
                educations = profile.get("education", [])

                # 🔍 Analizar datos sensibles
                sensitive_data = {
                    "dnis": defaultdict(set),
                    "ibans": defaultdict(set),
                    "cccs": defaultdict(set),
                    "phones": defaultdict(set),
                }

                find_sensitive(user_info.get("headline", ""), sensitive_data, user_info.get("profile_url", ""))

                for exp in experiences:
                    find_sensitive(exp.get("title", ""), sensitive_data, user_info.get("profile_url", ""))
                for edu in educations:
                    find_sensitive(edu.get("school", ""), sensitive_data, user_info.get("profile_url", ""))

                sensitive_summary = {
                    "dnis": dict_to_list(sensitive_data['dnis']),
                    "ibans": dict_to_list(sensitive_data['ibans']),
                    "cccs": dict_to_list(sensitive_data['cccs']),
                    "phones": dict_to_list(sensitive_data['phones']),
                }

                result_data = {
                    "platform": "LinkedIn",
                    "status": "success",
                    "username": filename,
                    "user": user_info,
                    "experiences": experiences,
                    "educations": educations,
                    "sensitive": sensitive_summary,
                    "json_file": file_path,
                }

                # 3️⃣ Guardar resultados en JSON
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result_data, f, indent=4, ensure_ascii=False)
                general_logger.debug(f"💾 [LinkedIn] Resultados guardados en {file_path}")
                linkedin_logger.debug(f"💾 [LinkedIn] Resultados guardados en {file_path}")

                all_results_final.append(result_data)


            else:
                general_logger.warning(f"⚠️ Plataforma no soportada: {platform}")


        # ✅ Compatibilidad: si solo hay 1 fila → devuelve en formato antiguo
        if len(all_results_final) == 1:
            google_logger.debug(f"📊 1-Devolviendo respeusta con {len(all_results_final)} bloques")
            return Response({
                "status": "success",
                **all_results_final[0]
            })

        google_logger.debug(f"📊 2-Devolviendo respeusta con {len(all_results_final)} bloques")
        # Si hay varias filas → devuelve lista
        return Response({
            "status": "success",
            "results": all_results_final
        })


    except Exception as e:
        general_logger.error(f"❌ Error en search: {str(e)}")
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})
