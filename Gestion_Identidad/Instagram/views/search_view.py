from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import os
from collections import defaultdict
from datetime import datetime

from Gestion_Identidad.Instagram.apis.instagram_api import get_user_info, get_user_posts, get_detailed_posts
from Gestion_Identidad.Google.views.google_search_view import find_sensitive, dict_to_list
from Gestion_Identidad.Google.apis.google_api import google_search
from Gestion_Identidad.Twitter.apis.twitter_api import get_user_info as twitter_user_info, get_user_tweets
from Gestion_Identidad.Linkedin.apis.linkedin_api import get_profile_from_url

from debug.loggers import instagram_logger, google_logger, general_logger, twitter_logger, linkedin_logger


@api_view(['POST'])
def search(request):
    try:
        # Separadores de logs
        general_logger.debug("─" * 120)
        google_logger.debug("─" * 120)
        twitter_logger.debug("─" * 120)
        linkedin_logger.debug("─" * 120)
        instagram_logger.debug("─" * 120)

        general_logger.debug("🎯 Endpoint /search activado correctamente")
        general_logger.debug(f"📨 Payload recibido: {json.dumps(request.data)}")

        mode = request.data.get("mode", "development") 
        rows = request.data.get("rows", [])
        general_logger.debug(f" Modo: {mode}")

        if not rows or not rows[0].get('text'):
            return Response({'status': 'error', 'message': 'El campo de texto es obligatorio.'})

        all_results_final = []

        for row in rows:
            platform = row.get('selectedOption1')
            text = row.get('text')
            tipo = row.get('selectedOption2')

            general_logger.debug(f"▶️ Procesando fila -> platform={platform}, text={text}, tipo={tipo}")

            # 🚀 GOOGLE
            if platform == "Google":
                google_logger.debug(f"[Google] Iniciando búsqueda con texto={text}, tipo={tipo}")
            
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
                    tel = text.strip()
                    if tel.startswith(("6", "7")):
                        queries.append(f"\"+34{tel}\"")
                    queries.append(f"\"{tel}\"")
                elif tipo == "Email":
                    queries = [f"\"{text}\"", f"\"{text.split('@')[0]}\""]
                elif tipo == "DNI":
                    dni = text.strip().upper()
                    if dni[-1].isalpha():
                        numero, letra = dni[:-1].zfill(8), dni[-1]
                        queries += [f"\"{numero}{letra}\"", f"\"{numero}\""]
                    else:
                        queries.append(f"\"{dni.zfill(8)}\"")
                else:
                    queries = [text]
            
                google_logger.debug(f"[Google] Queries generadas: {queries}")
            
                resultados = []
                sensitive_data = {
                    'dnis': defaultdict(set),
                    'ibans': defaultdict(set),
                    'cccs': defaultdict(set),
                    'phones': defaultdict(set)
                }
            
                for q in queries:
                    google_logger.debug(f"[Google] Ejecutando búsqueda con query: {q}")
                    data = google_search(q, num_results=5)
            
                    if data and "items" in data:
                        google_logger.debug(f"[Google] {len(data['items'])} resultados devueltos")
                        for idx, item in enumerate(data.get("items", [])):
                            snippet = item.get("snippet", "")
                            google_logger.debug(f"[Google] Resultado {idx+1}: {item.get('title')} -> {item.get('link')}")
                            google_logger.debug(f"[Google] Snippet analizado: {snippet[:120]}...")
            
                            resultados.append({
                                "query": q,
                                "title": item.get("title"),
                                "link": item.get("link"),
                                "snippet": snippet
                            })
                            find_sensitive(snippet, sensitive_data, item.get("link"))
                    else:
                        google_logger.warning(f"[Google] ⚠️ Sin resultados para query: {q}")
            
                google_logger.debug(f"[Google] Sensibles encontrados: DNI={len(sensitive_data['dnis'])}, "
                                    f"IBAN={len(sensitive_data['ibans'])}, "
                                    f"CCC={len(sensitive_data['cccs'])}, "
                                    f"Phones={len(sensitive_data['phones'])}")
            
                all_results_final.append({
                    "platform": "Google",
                    "status": "success",
                    "texto": text,
                    "tipo": tipo,
                    "results": resultados,
                    "sensitive": {
                        "dnis": dict_to_list(sensitive_data['dnis']),
                        "ibans": dict_to_list(sensitive_data['ibans']),
                        "cccs": dict_to_list(sensitive_data['cccs']),
                        "phones": dict_to_list(sensitive_data['phones']),
                    }
                })
            # 🚀 INSTAGRAM
            elif platform == "Instagram":
                instagram_logger.debug(f"[Instagram] Iniciando búsqueda para usuario={text}")
            
                username = text
                n_fotos = int(row.get("numPhotos", 3))
            
                base_dir = os.path.dirname(os.path.abspath(__file__))
                busquedas_dir = os.path.normpath(os.path.join(base_dir, '..', 'busquedas'))
                user_base_folder = os.path.join(busquedas_dir, username)
                posts_folder = os.path.join(user_base_folder, str(n_fotos))
            
                # 📁 Solo en development creamos carpetas y archivos
                if mode == "development":
                    os.makedirs(posts_folder, exist_ok=True)
            
                user_info_path = os.path.join(user_base_folder, 'user_info.json')
                user_posts_path = os.path.join(user_base_folder, 'user_posts.json')
            
                # 📌 USER INFO
                if mode == "development" and os.path.exists(user_info_path):
                    instagram_logger.debug(f"[Instagram][DEV] Leyendo user_info desde cache: {user_info_path}")
                    with open(user_info_path, 'r', encoding='utf-8') as f:
                        user_info = json.load(f)
                    user_id = user_info.get("data", {}).get("user", {}).get("id") or \
                              user_info.get("data", {}).get("user", {}).get("pk")
                else:
                    instagram_logger.debug(f"[Instagram][{mode.upper()}] Forzando API get_user_info() para {username}")
                    result = get_user_info(username, mode=mode)

                    # Normalizar retorno
                    if isinstance(result, tuple):
                        user_info, user_id, _ = result
                    else:
                        user_info = result
                        user_id = None

                    # Si es string, intentar parsear
                    if isinstance(user_info, str):
                        try:
                            user_info = json.loads(user_info)
                            instagram_logger.debug("[Instagram] user_info convertido desde string a JSON")
                        except Exception as e:
                            instagram_logger.error(f"[Instagram] ❌ user_info no es JSON válido: {e}")
                            return Response({'status': 'error', 'message': f"Respuesta inesperada de get_user_info para {username}"})

                    if not user_id:
                        user_id = user_info.get("data", {}).get("user", {}).get("id") or \
                                  user_info.get("data", {}).get("user", {}).get("pk")

                    if mode == "development":
                        with open(user_info_path, 'w', encoding='utf-8') as f:
                            json.dump(user_info, f, indent=4)
            
                user_data = user_info.get("data", {}).get("user", {})
                if not user_id:
                    return Response({'status': 'error', 'message': f"No se pudo obtener el ID de {username}"})
            
                # 📌 USER POSTS
                if mode == "development" and os.path.exists(user_posts_path):
                    with open(user_posts_path, 'r', encoding='utf-8') as f:
                        user_posts = json.load(f)
                else:
                    instagram_logger.debug(f"[Instagram][{mode.upper()}] Forzando API get_user_posts() para {username}")
                    user_posts = get_user_posts(username, user_id, n_fotos, posts_folder, mode=mode)
            
                    if isinstance(user_posts, str):
                        try:
                            user_posts = json.loads(user_posts)
                            instagram_logger.debug("[Instagram] user_posts convertido desde string a JSON")
                        except Exception as e:
                            instagram_logger.error(f"[Instagram] ❌ user_posts no es JSON válido: {e}")
                            return Response({'status': 'error', 'message': f"Respuesta inesperada de get_user_posts para {username}"})
            
                    if mode == "development":
                        with open(user_posts_path, 'w', encoding='utf-8') as f:
                            json.dump(user_posts, f, indent=4)
            
                # 📌 DETAILED POSTS
                try:
                    detailed_posts = get_detailed_posts(user_posts, n_fotos, user_id, username, posts_folder, mode=mode)
            
                    if isinstance(detailed_posts, str):
                        try:
                            detailed_posts = json.loads(detailed_posts)
                            instagram_logger.debug("[Instagram] detailed_posts convertido desde string a JSON")
                        except Exception as e:
                            instagram_logger.error(f"[Instagram] ❌ detailed_posts no es JSON válido: {e}")
                            detailed_posts = []
                except Exception as e:
                    instagram_logger.error(f"[Instagram] ❌ Error en get_detailed_posts: {e}")
                    detailed_posts = []
            
                # 📌 EXTRAER INFORMACIÓN COMPROMETIDA
                sensitive_data = {
                    'dnis': defaultdict(set),
                    'ibans': defaultdict(set),
                    'cccs': defaultdict(set),
                    'phones': defaultdict(set)
                }
            
                # Bio
                bio = user_data.get("biography", "")
                find_sensitive(bio, sensitive_data, f"https://instagram.com/{username}")
            
                # Captions de posts
                for dp in detailed_posts:
                    caption = dp.get("data", {}).get("shortcode_media", {}) \
                                .get("edge_media_to_caption", {}).get("edges", [])
                    if caption:
                        text_caption = caption[0].get("node", {}).get("text", "")
                        find_sensitive(text_caption, sensitive_data, f"https://instagram.com/p/{dp.get('shortcode','')}")
            
                instagram_logger.debug(f"mode: {mode}")
                # SOLO EN DEVELOPMENT -> buscar sensibles en comentarios con JSON
                if mode == "development":
                    instagram_logger.debug("[Instagram][DEV] Analizando comentarios desde JSON")
                    try:
                        from Gestion_Identidad.Instagram.views.instagram_analysis_view import find_sensitive_data_in_comments
                        full_info_path = os.path.join(posts_folder, f'full_information_{n_fotos}_posts.json')
                        if os.path.exists(full_info_path):
                            with open(full_info_path, 'r', encoding='utf-8') as f:
                                full_posts = json.load(f)
                            extra_sensitive = find_sensitive_data_in_comments(full_posts)
                            for key in ['dnis', 'ibans', 'cccs', 'phones']:
                                for item in extra_sensitive[key]:
                                    sensitive_data[key][item['value']].update(item['users'])
                    except Exception as e:
                        instagram_logger.error(f"[Instagram][DEV] ❌ Error analizando comentarios: {e}")
                else:
                    instagram_logger.debug("[Instagram][PROD] 🚫 Saltamos análisis de comentarios (solo bio y captions)")
            
                # 📌 EXTRAER UBICACIONES
                locations = []
                for dp in detailed_posts:
                    sc_media = dp.get('data', {}).get('shortcode_media', {})
                    if sc_media.get('location') and sc_media['location'].get('name'):
                        loc_name = sc_media['location']['name']
                        timestamp = sc_media.get('taken_at_timestamp')
                        if timestamp:
                            date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                            locations.append({'location': loc_name, 'date': date_str})
            
                all_results_final.append({
                    "platform": "Instagram",
                    "status": "success",
                    "username": username,
                    "texto": username,
                    "user_data": user_info,
                    "user_posts": user_posts,
                    "detailed_posts": detailed_posts,
                    "locations": locations,
                    "sensitive": {
                        "dnis": dict_to_list(sensitive_data['dnis']),
                        "ibans": dict_to_list(sensitive_data['ibans']),
                        "cccs": dict_to_list(sensitive_data['cccs']),
                        "phones": dict_to_list(sensitive_data['phones']),
                    }
                })
            
            # 🚀 TWITTER
            elif platform == "Twitter":
                twitter_logger.debug(f"[Twitter] Iniciando búsqueda para usuario={text}")

                busquedas_dir = os.path.join(os.path.dirname(__file__), "..", "..", "Twitter", "busquedas")
                os.makedirs(busquedas_dir, exist_ok=True)
                file_path = os.path.join(busquedas_dir, f"{text}.json")

                # 📂 Si existe cache, lo cargamos y reanalizamos
                if mode == "development" and os.path.exists(file_path):
                    twitter_logger.debug(f"[Twitter] Usando cache en {file_path}")
                    with open(file_path, "r", encoding="utf-8") as f:
                        result_data = json.load(f)

                    sensitive_data = {'dnis': defaultdict(set), 'ibans': defaultdict(set),
                                      'cccs': defaultdict(set), 'phones': defaultdict(set)}

                    for t in result_data.get("tweets", []):
                        tweet_text = t.get("text", "")
                        tweet_url = f"https://twitter.com/{text}/status/{t.get('id')}"
                        find_sensitive(tweet_text, sensitive_data, tweet_url)

                    result_data["sensitive"] = {
                        "dnis": dict_to_list(sensitive_data['dnis']),
                        "ibans": dict_to_list(sensitive_data['ibans']),
                        "cccs": dict_to_list(sensitive_data['cccs']),
                        "phones": dict_to_list(sensitive_data['phones']),
                    }

                    twitter_logger.debug(f"[Twitter] Reanalizados {len(result_data.get('tweets', []))} tweets")
                    all_results_final.append(result_data)
                    continue

                # 🚀 Si no hay cache
                twitter_logger.debug(f"[Twitter] Consultando API para {text}")
                user_info = twitter_user_info(text)

                if not user_info or "data" not in user_info:
                    twitter_logger.warning(f"[Twitter] No se encontró el usuario {text}")
                    all_results_final.append({
                        "platform": "Twitter",
                        "status": "error",
                        "message": f"No se encontró el usuario {text}"
                    })
                    continue

                user_id = user_info["data"]["id"]
                twitter_logger.debug(f"[Twitter] ID de usuario obtenido: {user_id}")

                tweets = get_user_tweets(user_id, max_results=10)
                twitter_logger.debug(f"[Twitter] Tweets obtenidos: {len(tweets.get('data', []))}")

                sensitive_data = {'dnis': defaultdict(set), 'ibans': defaultdict(set),
                                  'cccs': defaultdict(set), 'phones': defaultdict(set)}

                for t in tweets.get("data", []):
                    find_sensitive(t.get("text", ""), sensitive_data,
                                   f"https://twitter.com/{text}/status/{t.get('id')}")

                twitter_logger.debug(f"[Twitter] Sensibles detectados -> "
                                     f"DNI={len(sensitive_data['dnis'])}, "
                                     f"IBAN={len(sensitive_data['ibans'])}, "
                                     f"CCC={len(sensitive_data['cccs'])}, "
                                     f"Phones={len(sensitive_data['phones'])}")

                result_data = {
                    "platform": "Twitter",
                    "status": "success",
                    "username": text,
                    "user": user_info["data"],
                    "tweets": tweets.get("data", []),
                    "sensitive": {
                        "dnis": dict_to_list(sensitive_data['dnis']),
                        "ibans": dict_to_list(sensitive_data['ibans']),
                        "cccs": dict_to_list(sensitive_data['cccs']),
                        "phones": dict_to_list(sensitive_data['phones']),
                    },
                }

                if mode == "development":
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(result_data, f, indent=4, ensure_ascii=False)

                all_results_final.append(result_data)

            # 🚀 LINKEDIN
            elif platform == "LinkedIn":
                linkedin_logger.debug(f"[LinkedIn] Iniciando búsqueda para URL={text}")

                username = text.rstrip("/").split("/")[-1]
                filename = username or "linkedin_profile"
                busquedas_dir = os.path.join(os.path.dirname(__file__), "..", "..", "Linkedin", "busquedas")
                os.makedirs(busquedas_dir, exist_ok=True)
                file_path = os.path.join(busquedas_dir, f"{filename}.json")

                if mode == "development" and os.path.exists(file_path):
                    linkedin_logger.debug(f"[LinkedIn] Usando cache en {file_path}")
                    with open(file_path, "r", encoding="utf-8") as f:
                        result_data = json.load(f)
                    all_results_final.append(result_data)
                    continue

                data = get_profile_from_url(text)
                if not data or not data.get("success") or not data.get("data"):
                    linkedin_logger.warning(f"[LinkedIn] No se encontró información para {text}")
                    all_results_final.append({
                        "platform": "LinkedIn",
                        "status": "error",
                        "message": f"No se encontró información de {text}"
                    })
                    continue

                profile = data["data"]
                linkedin_logger.debug(f"[LinkedIn] Perfil obtenido: {profile.get('basic_info', {}).get('fullname')}")

                result_data = {
                    "platform": "LinkedIn",
                    "status": "success",
                    "username": filename,
                    "user": {
                        "name": profile.get("basic_info", {}).get("fullname"),
                        "headline": profile.get("basic_info", {}).get("headline"),
                        "location": profile.get("basic_info", {}).get("location", {}).get("full"),
                        "profile_url": f"https://www.linkedin.com/in/{profile.get('basic_info', {}).get('public_identifier', '')}"
                    },
                    "experiences": profile.get("experience", []),
                    "educations": profile.get("education", []),
                }

                if mode == "development":
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(result_data, f, indent=4, ensure_ascii=False)

                all_results_final.append(result_data)

        # 🔹 Devolver respuesta
        if len(all_results_final) == 1:
            return Response({"status": "success", **all_results_final[0]})
        return Response({"status": "success", "results": all_results_final})

    except Exception as e:
        general_logger.error(f"❌ Error en search: {e}")
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})
