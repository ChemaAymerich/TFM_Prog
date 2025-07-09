from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SearchSerializer
import json
import os
import logging

logging.basicConfig(
    filename='debug.log',           # Nombre del archivo donde se guardarán los logs
    level=logging.DEBUG,            # Nivel de logging (DEBUG muestra todo)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Formato de cada línea de log
)

try:
    from .apis.instagram_api import get_user_info, get_user_posts,generate_account_saldos
    print("Módulo cargado correctamente")
except ImportError as e:
    print("Error al cargar el módulo:", e)

# Vista para servir la página principal
def home(request):
    return render(request, 'home.html')  # Asegúrate de tener un archivo home.html en tu directorio de plantillas

# Endpoint para manejar las búsquedas
@api_view(['POST'])
def search(request):
    try:
        logging.debug("🎯 Endpoint /search activado correctamente")
        rows = request.data.get('rows', [])
        if not rows or not rows[0].get('text'):
            return Response({'status': 'error', 'message': 'El campo de texto (nombre de usuario) es obligatorio.'})

        username = rows[0]['text']
        platform = rows[0]['selectedOption1']
        n_fotos = int(rows[0]['numPhotos'])

        if platform != "Instagram":
            return Response({'status': 'error', 'message': 'Actualmente, solo se admite la plataforma Instagram.'})

        # Ruta al directorio de búsqueda
        base_dir = os.path.dirname(os.path.abspath(__file__))
        busquedas_dir = os.path.join(base_dir, '..', 'busquedas')
        user_folder = os.path.join(busquedas_dir, f"{username}_{n_fotos}")

        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

            # Hacer las peticiones reales
            user_info, user_id = get_user_info(username)
            if user_id == "N/A":
                return Response({'status': 'error', 'message': f"No se encontró información para el usuario: {username}"})

            user_posts = get_user_posts(user_id)

            # Guardar archivos
            with open(os.path.join(user_folder, 'user_info.json'), 'w') as f:
                json.dump(user_info, f, indent=4)
            with open(os.path.join(user_folder, 'user_posts.json'), 'w') as f:
                json.dump(user_posts, f, indent=4)

        else:
            # Leer los archivos ya guardados
            with open(os.path.join(user_folder, 'user_info.json'), 'r') as f:
                user_info = json.load(f)
            with open(os.path.join(user_folder, 'user_posts.json'), 'r') as f:
                user_posts = json.load(f)

        return Response({
            'status': 'success',
            'message': f"Datos obtenidos para el usuario {username} con {n_fotos} fotos.",
            'user_data': user_info,
            'user_posts': user_posts
        })

    except Exception as e:
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})
    

@api_view(['POST'])
def extract_posts(request):
    try:
        logging.debug("📥 Extract_posts activado")

        username = request.data.get('username')
        num_posts = int(request.data.get('num_posts'))

        logging.debug(f"📌 Parámetros recibidos: username={username}, num_posts={num_posts}")

        if not username or not num_posts:
            return Response({'status': 'error', 'message': 'Faltan parámetros username o num_posts'})

        search_folder = os.path.join(os.path.dirname(__file__), 'busquedas', f"{username}_{num_posts}")
        if not os.path.exists(search_folder):
            os.makedirs(search_folder)
            logging.debug(f"📁 Carpeta creada: {search_folder}")

            user_data, user_id, is_private  = get_user_info(username)
            logging.debug(f"👤 Datos del usuario: {user_data}")
            logging.debug(f"🆔 ID del usuario: {user_id}")

            if user_id == "N/A":
                return Response({'status': 'error', 'message': f"No se pudo obtener el ID del usuario {username}"})

            posts_data = get_user_posts(user_id)
            logging.debug(f"📸 Posts obtenidos: {len(posts_data.get('data', {}).get('user', {}).get('edge_owner_to_timeline_media', {}).get('edges', []))} elementos")

            posts_path = os.path.join(search_folder, "posts.json")
            with open(posts_path, "w", encoding="utf-8") as f:
                json.dump(posts_data, f, indent=4)

            return Response({'status': 'success', 'message': f"Datos guardados en {search_folder}"})
        else:
            return Response({'status': 'skipped', 'message': f"La carpeta {search_folder} ya existe. No se hizo la petición."})

    except Exception as e:
        logging.error(f"❌ Error en extract_posts: {e}")
        return Response({'status': 'error', 'message': f"Error interno: {str(e)}"})