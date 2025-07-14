from rest_framework.response import Response
from rest_framework.decorators import api_view
from collections import Counter
import json
import os
from Gestion_Identidad.Instagram.apis.instagram_api import get_user_info, get_user_posts
from debug.loggers import instagram_logger
from pathlib import Path

BUSQUEDAS_DIR = r"C:\Users\jm_ay\Documents\0-TFM_Programacion\Proyecto_TFM\Gestion_Identidad\Instagram\busquedas"

@api_view(['POST'])
def extract_posts(request):
    try:
        instagram_logger.debug("📥 extract_posts activado")

        username = request.data.get('username')
        num_posts = int(request.data.get('num_posts'))
        reexecute = request.data.get('reexecute', False)

        if not username or not num_posts:
            return Response({'status': 'error', 'message': 'Faltan parámetros username o num_posts'})

        user_folder = os.path.join(BUSQUEDAS_DIR, username)
        posts_folder = os.path.join(user_folder, str(num_posts))
        Path(posts_folder).mkdir(parents=True, exist_ok=True)

        user_info_path = os.path.join(user_folder, 'user_info.json')
        posts_json_path = os.path.join(posts_folder, 'user_posts.json')

        # Obtener o cargar user_info.json
        if os.path.exists(user_info_path):
            instagram_logger.debug(f"📂 user_info.json encontrado en: {user_info_path}")
            with open(user_info_path, 'r', encoding='utf-8') as f:
                user_info = json.load(f)
        else:
            user_info, user_id, _ = get_user_info(username)
            with open(user_info_path, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, indent=4, ensure_ascii=False)
            instagram_logger.debug(f"💾 user_info.json creado")

        user_data = user_info.get("data", {}).get("user", {})
        user_id = user_data.get("id") or user_data.get("pk")
        if not user_id:
            return Response({'status': 'error', 'message': f"No se pudo obtener el ID de {username} ❌"})

        # Posts
        if os.path.exists(posts_json_path) and not reexecute:
            instagram_logger.debug(f"✅ user_posts.json ya existe y no se reejecuta: {posts_json_path}")
            return Response({
                'status': 'skipped',
                'message': f"user_posts.json ya existe para {username} con {num_posts} fotos.",
                'path': posts_json_path
            })

        instagram_logger.debug(f"📸 Extrayendo {num_posts} fotos para usuario {username} (user_id: {user_id})")
        instagram_logger.debug(f"📁 Carpeta destino: {posts_folder}")
        posts_data = get_user_posts(username, user_id, num_posts, posts_folder)

        with open(posts_json_path, "w", encoding="utf-8") as f:
            json.dump(posts_data, f, indent=4, ensure_ascii=False)
        instagram_logger.debug(f"💾 extracted_posts.json guardado en: {posts_json_path}")

        return Response({
            'status': 'success',
            'message': f"Publicaciones extraídas y guardadas correctamente.",
            'path': posts_json_path
        })

    except Exception as e:
        instagram_logger.error(f"❌ Error en extract_posts: {e}")
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})

@api_view(['GET'])
def instagram_analysis(request):
    username = request.query_params.get('username')
    if not username:
        return Response({"status": "error", "message": "Falta el parámetro username"}, status=400)

    user_folder = os.path.join(BUSQUEDAS_DIR, username)

    # leer biografía
    user_info_path = os.path.join(user_folder, "user_info.json")
    if not os.path.exists(user_info_path):
        return Response({"status": "error", "message": f"user_info.json no encontrado para {username}"}, status=404)

    with open(user_info_path, encoding="utf-8") as f:
        user_info = json.load(f)

    bio = user_info.get("biography") or user_info.get("data", {}).get("user", {}).get("biography", "")

    # detectar full_information_X_posts.json
    full_info_path = None
    for dirpath, dirnames, filenames in os.walk(user_folder):
        for filename in filenames:
            if filename.startswith("full_information") and filename.endswith(".json"):
                full_info_path = os.path.join(dirpath, filename)
                break
        if full_info_path:
            break

    if not full_info_path:
        return Response({"status": "error", "message": f"full_information_*.json no encontrado para {username}"}, status=404)

    with open(full_info_path, encoding="utf-8") as f:
        posts_data = json.load(f)

    counter = Counter()
    for post in posts_data:
        edges = (
            post.get("data", {})
            .get("shortcode_media", {})
            .get("edge_media_to_parent_comment", {})
            .get("edges", [])
        )
        for edge in edges:
            username_c = edge["node"]["owner"]["username"]
            counter[username_c] += 1

    comments = [{"username": u, "count": c} for u, c in counter.most_common()]

    return Response({
        "status": "success",
        "bio": bio,
        "comments": comments
    })

@api_view(['GET'])
def instagram_analysis(request):
    username = request.query_params.get('username')
    if not username:
        return Response({"status": "error", "message": "Falta el parámetro username"}, status=400)

    user_folder = os.path.join(BUSQUEDAS_DIR, username)

    # leer biografía
    user_info_path = os.path.join(user_folder, "user_info.json")
    if not os.path.exists(user_info_path):
        return Response({"status": "error", "message": f"user_info.json no encontrado para {username}"}, status=404)

    with open(user_info_path, encoding="utf-8") as f:
        user_info = json.load(f)

    bio = user_info.get("biography") or user_info.get("data", {}).get("user", {}).get("biography", "")

    # detectar full_information_X_posts.json
    full_info_path = None
    for dirpath, dirnames, filenames in os.walk(user_folder):
        for filename in filenames:
            if filename.startswith("full_information") and filename.endswith(".json"):
                full_info_path = os.path.join(dirpath, filename)
                break
        if full_info_path:
            break

    if not full_info_path:
        return Response({"status": "error", "message": f"full_information_*.json no encontrado para {username}"}, status=404)

    with open(full_info_path, encoding="utf-8") as f:
        posts_data = json.load(f)

    counter = Counter()
    for post in posts_data:
        edges = (
            post.get("data", {})
            .get("shortcode_media", {})
            .get("edge_media_to_parent_comment", {})
            .get("edges", [])
        )
        for edge in edges:
            username_c = edge["node"]["owner"]["username"]
            counter[username_c] += 1

    comments = [{"username": u, "count": c} for u, c in counter.most_common()]

    return Response({
        "status": "success",
        "bio": bio,
        "comments": comments
    })
