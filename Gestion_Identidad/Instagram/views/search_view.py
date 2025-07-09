from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
import os
from Gestion_Identidad.Instagram.apis.instagram_api import get_user_info, get_user_posts,get_detailed_posts
from debug.loggers import instagram_logger

@api_view(['POST'])
def search(request):
    try:
        instagram_logger.debug("─" * 120)
        instagram_logger.debug("🎯 Endpoint /search activado correctamente")
        instagram_logger.debug(f"📨 Payload recibido: {json.dumps(request.data)}")

        rows = request.data.get('rows', [])
        if not rows or not rows[0].get('text'):
            return Response({'status': 'error', 'message': 'El campo de texto es obligatorio.'})

        username = rows[0]['text']
        platform = rows[0]['selectedOption1']
        num_photos_raw = rows[0].get('numPhotos')
        if not num_photos_raw:
            return Response({'status': 'error', 'message': 'Debes indicar cuántas fotos analizar.'})
        n_fotos = int(num_photos_raw)
        instagram_logger.debug(f"Número de fotos: {n_fotos}")

        if platform != "Instagram":
            return Response({'status': 'error', 'message': 'Solo se admite Instagram.'})

        base_dir = os.path.dirname(os.path.abspath(__file__))
        busquedas_dir = os.path.normpath(os.path.join(base_dir, '..', 'busquedas'))
        user_base_folder = os.path.join(busquedas_dir, username)
        posts_folder = os.path.join(user_base_folder, str(n_fotos))
        os.makedirs(posts_folder, exist_ok=True)

        user_info_path = os.path.join(user_base_folder, 'user_info.json')
        user_posts_path = os.path.join(posts_folder, 'user_posts.json')

        # Info del usuario
        if os.path.exists(user_info_path):
            instagram_logger.debug(f"📂 Archivo user_info.json ya existe, cargando desde disco: {user_info_path}")
            with open(user_info_path, 'r', encoding='utf-8') as f:
                user_info = json.load(f)
        else:
            instagram_logger.debug("🆕 user_info.json no existe, extrayendo de API")
            user_info, user_id, _ = get_user_info(username)
            with open(user_info_path, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, indent=4)
            instagram_logger.debug(f"💾 user_info.json guardado en disco: {user_info_path}")

        user_data = user_info.get("data", {}).get("user", {})
        user_id = user_data.get("id") or user_data.get("pk")
        if not user_id:
            return Response({'status': 'error', 'message': f"No se pudo obtener el ID de {username}"})
        instagram_logger.debug(f"✅ Usuario {username} preparado. user_id: {user_id}")

        # Posts
        user_posts_save_path = os.path.join(user_base_folder, 'user_posts.json')
        if os.path.exists(user_posts_save_path):
            instagram_logger.debug(f"📂 Archivo user_posts.json ya existe: {user_posts_save_path}, cargando.")
            with open(user_posts_save_path, 'r', encoding='utf-8') as f:
                user_posts = json.load(f)
        else:
            instagram_logger.debug("🆕 user_posts.json no existe, llamando a get_user_posts")
            instagram_logger.debug(f"📁 Carpeta esperada para posts: {posts_folder}")
            user_posts = get_user_posts(username, user_id, n_fotos, posts_folder)
            with open(user_posts_save_path, 'w', encoding='utf-8') as f:
                json.dump(user_posts, f, indent=4)
            instagram_logger.debug(f"💾 user_posts.json guardado en disco: {user_posts_save_path}")
        
        # Obtener detalles completos y guardar
        detailed_info_path = os.path.join(posts_folder, f'full_information_{n_fotos}_posts.json')
        if os.path.exists(detailed_info_path):
            instagram_logger.debug(f"📂 full_information ya existe: {detailed_info_path}, no se regenera.")
            with open(detailed_info_path, 'r', encoding='utf-8') as f:
                detailed_posts = json.load(f)
        else:
            instagram_logger.debug(f"user_posts type: {type(user_posts)} keys: {list(user_posts.keys())}")
            instagram_logger.debug("🔍 Generando información detallada de publicaciones...")
            detailed_posts = get_detailed_posts(user_posts, n_fotos, user_id, username, posts_folder)



        instagram_logger.debug(f"📦 search finalizado. Enviando datos de {username} con {n_fotos} fotos.")
        return Response({
            'status': 'success',
            'message': f"Datos de {username} con {n_fotos} fotos extraídos.",
            'user_data': user_info,
            'user_posts': user_posts
        })
    

    except Exception as e:
        instagram_logger.error(f"❌ Error en search: {str(e)}")
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})
