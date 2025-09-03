from rest_framework.decorators import api_view
from rest_framework.response import Response
from Gestion_Identidad.Twitter.apis.twitter_api import get_user_info, get_user_tweets
from debug.loggers import twitter_logger
import os, json
from datetime import datetime

@api_view(['POST'])
def twitter_search_view(request):
    username = request.data.get("username")
    if not username:
        return Response({"status": "error", "message": "Debe indicar un nombre de usuario."})

    twitter_logger.debug(f"▶️ Buscando en Twitter: @{username}")

    # 1️⃣ Info de usuario
    user_info = get_user_info(username)
    if not user_info or "data" not in user_info:
        twitter_logger.warning(f"⚠️ No se encontró el usuario {username}")
        return Response({"status": "error", "message": f"No se encontró el usuario {username}"})

    user_data = user_info["data"]
    user_id = user_data["id"]

    # 2️⃣ Tweets del usuario
    tweets_data = get_user_tweets(user_id, max_results=10)
    tweets = tweets_data.get("data", []) if tweets_data else []

    # 3️⃣ Guardar resultados en JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    busquedas_dir = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "Twitter", "busquedas"))
    os.makedirs(busquedas_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_path = os.path.join(busquedas_dir, f"{username}_{ts}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({
            "platform": "Twitter",
            "username": username,
            "user": user_data,
            "tweets": tweets
        }, f, indent=4, ensure_ascii=False)

    twitter_logger.debug(f"✅ Resultados guardados en {file_path}")

    return Response({
        "status": "success",
        "platform": "Twitter",
        "username": username,
        "user": user_data,
        "tweets": tweets,
        "json_file": file_path
    })
