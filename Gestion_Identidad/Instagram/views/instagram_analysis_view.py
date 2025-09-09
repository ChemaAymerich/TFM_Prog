from rest_framework.response import Response
from rest_framework.decorators import api_view
from debug.loggers import instagram_logger
from datetime import datetime
from collections import defaultdict, Counter
import json
import os
import re

from Gestion_Identidad.Instagram.apis.instagram_api import get_user_info, get_user_posts, get_detailed_posts


BUSQUEDAS_DIR = r"C:\Users\jm_ay\Documents\0-TFM_Programacion\Proyecto_TFM\Gestion_Identidad\Instagram\busquedas"

def find_sensitive_data_in_comments(full_posts):
    dnis, ibans, cccs, phones = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set)
    dni_regex = r'\b\d{8}[A-Za-z]\b'
    iban_regex = r'([A-Z]{2}\d{2}(?:\s?\d{4}){4,7})'
    ccc_regex = r'\b\d{20}\b'
    phone_regex = r'(?:(?:\+34|0034)?\s*([6-9]\d{2})\s*\d{3}\s*\d{3})'

    def process_text(text, owner):
        for match in re.findall(dni_regex, text, re.I):
            dnis[match.upper()].add(owner)
        for match in re.findall(iban_regex, text, re.I):
            normalized = match.replace(" ", "").upper()
            if len(normalized) >= 24:
                ibans[normalized].add(owner)
        for match in re.findall(ccc_regex, text.replace(" ", ""), re.I):
            cccs[match].add(owner)
        for match in re.findall(phone_regex, text, re.I):
            number = match.replace(" ", "")
            if len(number) >= 9:
                phones[number].add(owner)

    for post in full_posts:
        edges = post.get('data', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
        for edge in edges:
            comment = edge.get('node', {})
            owner = comment.get('owner', {}).get('username', 'Desconocido')
            text = comment.get('text', '')
            process_text(text, owner)
            for subedge in comment.get('edge_threaded_comments', {}).get('edges', []):
                sub_node = subedge.get('node', {})
                sub_owner = sub_node.get('owner', {}).get('username', 'Desconocido')
                sub_text = sub_node.get('text', '')
                process_text(sub_text, sub_owner)

    def dict_to_list(d):
        return [{'value': k, 'users': list(v)} for k, v in d.items()] if d else []

    return {
        'dnis': dict_to_list(dnis),
        'ibans': dict_to_list(ibans),
        'cccs': dict_to_list(cccs),
        'phones': dict_to_list(phones),
    }


@api_view(['POST'])
def instagram_analysis(request):
    username = request.data.get('username')
    num_posts = int(request.data.get('num_posts', 3))
    mode = request.data.get('mode', 'development')  # 👈 nuevo
    instagram_logger.debug(f"Analizando usuario={username}, posts={num_posts}, mode={mode}")

    if not username:
        return Response({'status': 'error', 'message': 'Falta username'})

    if mode == "development":
        # 📂 Leer de archivos
        user_info_path = os.path.join(BUSQUEDAS_DIR, username, 'user_info.json')
        full_info_path = os.path.join(BUSQUEDAS_DIR, username, str(num_posts), f'full_information_{num_posts}_posts.json')

        if not os.path.exists(user_info_path):
            return Response({'status': 'error', 'message': 'No existe user_info.json'})
        with open(user_info_path, encoding='utf-8') as f:
            user_info = json.load(f)

        if not os.path.exists(full_info_path):
            return Response({'status': 'error', 'message': 'No existe full_information_x_posts.json'})
        with open(full_info_path, encoding='utf-8') as f:
            full_posts = json.load(f)

    else:
        # 🌐 Producción → usar APIs
        result = get_user_info(username, mode="production")
        if isinstance(result, tuple):
            user_info, user_id, _ = result
        else:
            user_info, user_id = result, None

        if isinstance(user_info, str):
            user_info = json.loads(user_info)

        if not user_id:
            user_id = user_info.get("data", {}).get("user", {}).get("id")

        user_posts = get_user_posts(username, user_id, num_posts, posts_folder="", mode="production")
        if isinstance(user_posts, str):
            user_posts = json.loads(user_posts)

        full_posts = get_detailed_posts(user_posts, num_posts, user_id, username, posts_folder="", mode="production")
        if isinstance(full_posts, str):
            full_posts = json.loads(full_posts)

    # 📌 Extraer bio y nombre
    user = user_info.get('data', {}).get('user', {})
    bio = user.get('biography', '')
    full_name = user.get('full_name', '')

    # 📌 Top comentaristas
    comment_counter = Counter()
    for post in full_posts:
        edges = post.get('data', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
        for edge in edges:
            comment = edge.get('node', {})
            owner = comment.get('owner', {}).get('username')
            if owner:
                comment_counter[owner] += 1
            for subedge in comment.get('edge_threaded_comments', {}).get('edges', []):
                sub_owner = subedge.get('node', {}).get('owner', {}).get('username')
                if sub_owner:
                    comment_counter[sub_owner] += 1
    top_commenters = comment_counter.most_common(10)

    # 📌 Ubicaciones
    locations = []
    for post in full_posts:
        sc_media = post.get('data', {}).get('shortcode_media', {})
        if sc_media.get('location') and sc_media['location'].get('name'):
            loc_name = sc_media['location']['name']
            timestamp = sc_media.get('taken_at_timestamp')
            if timestamp:
                date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                locations.append({'location': loc_name, 'date': date_str})

    # 📌 Info sensible
    sensitive = find_sensitive_data_in_comments(full_posts)

    return Response({
        'status': 'success',
        'bio': bio,
        'full_name': full_name,
        'top_commenters': [{'username': u, 'count': c} for u, c in top_commenters],
        'locations': locations,
        'sensitive': sensitive
    })
