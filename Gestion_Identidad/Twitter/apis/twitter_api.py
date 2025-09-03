import os
import requests
import json
from debug.loggers import twitter_logger
from django.conf import settings


TWITTER_BEARER_TOKEN = getattr(settings, "TWITTER_BEARER_TOKEN", None)


BASE_URL = "https://api.x.com/2"  # Twitter/X API v2


def make_request(endpoint, params=None):
    """Hace una petición a la API de Twitter"""
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    url = f"{BASE_URL}{endpoint}"
    twitter_logger.debug(f"🌐 GET {url} con params={params}")

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        twitter_logger.error(f"❌ Error {response.status_code}: {response.text}")
        return None


def get_user_info(username):
    """Obtiene información de un usuario de Twitter por username"""
    endpoint = f"/users/by/username/{username}"
    params = {"user.fields": "id,name,username,description,created_at,public_metrics"}
    data = make_request(endpoint, params)

    if data:
        twitter_logger.debug(f"✅ Usuario encontrado: {json.dumps(data, indent=2)}")
    return data


def get_user_tweets(user_id, max_results=10):
    """Obtiene los tweets recientes de un usuario"""
    endpoint = f"/users/{user_id}/tweets"
    params = {
        "max_results": max_results,
        "tweet.fields": "id,text,created_at,public_metrics"
    }
    data = make_request(endpoint, params)

    if data:
        twitter_logger.debug(f"✅ Tweets encontrados: {json.dumps(data, indent=2)}")
    return data
