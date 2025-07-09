import http.client
import json
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from debug.loggers import instagram_logger
from pathlib import Path

# Ruta del archivo de cuentas (persistente)
ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'accounts.json')

# Cargar cuentas desde archivo JSON
def load_accounts():
    with open(ACCOUNTS_FILE, 'r') as file:
        return json.load(file)

# Guardar cuentas en archivo JSON
def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as file:
        json.dump(accounts, file, indent=4)

# Lógica para cambiar de cuenta y actualizar estado
def switch_account():
    accounts = load_accounts()
    current_time = time.time()

    for account in accounts:
        if (current_time - account['last_request_time']) > 60:
            account['requests'] = 0

        if account['saldo'] > 0 and account['requests'] < 3:
            account['requests'] += 1
            account['saldo'] -= 1
            account['last_request_time'] = current_time
            save_accounts(accounts)

            instagram_logger.debug(f"Usando cuenta: {account['name']} - Saldo restante: {account['saldo']} - Requests: {account['requests']}")

            headers = {
                'x-rapidapi-host': "instagram28.p.rapidapi.com",
                'x-rapidapi-key': account['key']
            }
            return headers

    raise Exception("🚫 No hay cuentas disponibles para hacer solicitudes.")

BUSQUEDAS_DIR = r"C:\Users\jm_ay\Documents\0-TFM_Programacion\Proyecto_TFM\Gestion_Identidad\Instagram\busquedas"

def get_user_info(username):
    instagram_logger.debug(f"🔍 Buscando info del usuario: {username}")

    user_folder = os.path.join(BUSQUEDAS_DIR, username)
    json_path = os.path.join(user_folder, "user_info.json")
    Path(user_folder).mkdir(parents=True, exist_ok=True)

    if os.path.exists(json_path):
        instagram_logger.debug(f"📂 Cargando user_info desde: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            user_info = json.load(f)
    else:
        headers = switch_account()
        conn = http.client.HTTPSConnection("instagram28.p.rapidapi.com")
        conn.request("GET", f"/user_info?user_name={username}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        user_info = json.loads(data.decode("utf-8"))

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(user_info, f, indent=4, ensure_ascii=False)
            instagram_logger.debug(f"💾 user_info guardado en {json_path}")

    user_data = user_info.get("data", {}).get("user", {})
    user_id = user_data.get("id") or user_data.get("pk", "N/A")
    is_private = user_data.get("is_private", False)

    return user_info, user_id, is_private

# Obtener publicaciones del usuario
def get_user_posts(username, user_id, n_fotos, posts_folder):
    instagram_logger.debug(f"📸 Extrayendo {n_fotos} fotos para usuario {username} (user_id: {user_id})")
    instagram_logger.debug(f"📁 Carpeta destino: {posts_folder}")
    
    #Path(posts_folder).mkdir(parents=True, exist_ok=True)
    json_path = os.path.join(posts_folder, "user_posts.json")

    if os.path.exists(json_path):
        instagram_logger.debug(f"📂 user_posts.json ya existe en: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            posts_info = json.load(f)
    else:
        headers = switch_account()
        conn = http.client.HTTPSConnection("instagram28.p.rapidapi.com")
        conn.request("GET", f"/medias?user_id={user_id}&batch_size={n_fotos}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        posts_info = json.loads(data.decode("utf-8"))

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(posts_info, f, indent=4, ensure_ascii=False)
        instagram_logger.debug(f"💾 user_posts.json guardado en: {json_path}")

    return posts_info

def get_detailed_posts(user_posts_data, n_fotos, user_id, username, destination_folder):
    """
    Recorre los n primeros posts del usuario, y para cada uno llama a otra API
    para obtener datos completos del post (comentarios, likes, media, etc.)
    """
    instagram_logger.debug(f"💾 Entrando en get_detailed_posts")
    detailed_posts = []
    instagram_logger.debug(f"Antes Enumerate.")
    edges = user_posts_data.get("data", {}) \
                       .get("user", {}) \
                       .get("edge_owner_to_timeline_media", {}) \
                       .get("edges", [])
    for i, edge in enumerate(edges):
        if i >= n_fotos:
            break
        post = edge.get("node", {})
        shortcode = post.get("shortcode")
        if not shortcode:
            continue
        instagram_logger.debug(f"Post {i} shortcode: {shortcode}")
        headers = switch_account()
        conn = http.client.HTTPSConnection("instagram28.p.rapidapi.com")
        conn.request("GET", f"/media_info?short_code={shortcode}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        detailed_post = json.loads(data.decode("utf-8"))

        detailed_posts.append(detailed_post)

        instagram_logger.debug(f"📥 Post {i+1}/{n_fotos} detallado para shortcode {shortcode}")

    # Guardar resultado completo
    output_path = os.path.join(destination_folder, f"full_information_{n_fotos}_posts.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(detailed_posts, f, indent=4, ensure_ascii=False)
    instagram_logger.debug(f"💾 Detalles completos guardados en: {output_path}")

    return detailed_posts


# Generar reporte de estado de cuentas
def generate_account_saldos():
    accounts = load_accounts()
    instagram_logger.debug("Generando reporte de cuentas:")
    saldos = []
    for account in accounts:
        instagram_logger.debug(f"Cuenta: {account['name']} | Saldo: {account['saldo']} | Requests: {account['requests']}")
        saldos.append({
            "name": account["name"],
            "saldo": account["saldo"],
            "requests": account["requests"]
        })
    return saldos
