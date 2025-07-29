from rest_framework.response import Response
from rest_framework.decorators import api_view
from debug.loggers import instagram_logger
from datetime import datetime
from collections import defaultdict
import json
import os
import re


BUSQUEDAS_DIR = r"C:\Users\jm_ay\Documents\0-TFM_Programacion\Proyecto_TFM\Gestion_Identidad\Instagram\busquedas"
def find_sensitive_data_in_comments(full_posts):
    from collections import defaultdict
    import re


    dnis = defaultdict(set)
    ibans = defaultdict(set)
    cccs = defaultdict(set)
    phones = defaultdict(set)
    dni_regex = r'\b\d{8}[A-Za-z]\b'
    # Captura IBANs juntos o con espacios
    iban_regex = r'([A-Z]{2}\d{2}(?:\s?\d{4}){4,7})'
    ccc_regex = r'\b\d{20}\b'
    phone_regex = r'(?:(?:\+34|0034)?\s*([6-9]\d{2})\s*\d{3}\s*\d{3})'


    def process_text(text, owner):
        # DNI
        for match in re.findall(dni_regex, text, re.I):
            dnis[match.upper()].add(owner)
        # IBAN (normalize, remove spaces, only valid if length >= 24)
        for match in re.findall(iban_regex, text, re.I):
            normalized = match.replace(" ", "").upper()
            if len(normalized) >= 24:  # ES IBAN length is 24
                ibans[normalized].add(owner)
        # CCC
        for match in re.findall(ccc_regex, text.replace(" ", ""), re.I):
            cccs[match].add(owner)
        # Phones
        for match in re.findall(phone_regex, text, re.I):
            number = match.replace(" ", "")
            if len(number) >= 9:
                phones[number].add(owner)


    # Extraer de todos los comentarios y subcomentarios
    for post in full_posts:
        edges = post.get('data', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
        for edge in edges:
            comment = edge.get('node', {})
            owner = comment.get('owner', {}).get('username', 'Desconocido')
            text = comment.get('text', '')
            process_text(text, owner)
            # Subcomentarios
            subedges = comment.get('edge_threaded_comments', {}).get('edges', [])
            for subedge in subedges:
                sub_node = subedge.get('node', {})
                sub_owner = sub_node.get('owner', {}).get('username', 'Desconocido')
                sub_text = sub_node.get('text', '')
                process_text(sub_text, sub_owner)


    # Convertir a lista para JSON
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
    instagram_logger.debug(f"Probando numero_fotos:{num_posts}")
    if not username:
        return Response({'status': 'error', 'message': 'Falta username'})
    
    # Paths
    user_info_path = os.path.join(BUSQUEDAS_DIR, username, 'user_info.json')
    full_info_path = os.path.join(BUSQUEDAS_DIR, username, str(num_posts), f'full_information_{num_posts}_posts.json')
    
    # Load user info
    if not os.path.exists(user_info_path):
        return Response({'status': 'error', 'message': 'No existe user_info.json'})
    with open(user_info_path, encoding='utf-8') as f:
        user_info = json.load(f)
    
    # Load full info
    if not os.path.exists(full_info_path):
        return Response({'status': 'error', 'message': 'No existe full_information_x_posts.json'})
    with open(full_info_path, encoding='utf-8') as f:
        full_posts = json.load(f)
    
    # Bio y avatar
    user = user_info.get('data', {}).get('user', {})
    bio = user.get('biography', '')
    avatar = user.get('profile_pic_url', '')
    full_name = user.get('full_name', '')
    
    # Top comentaristas (comentarios y subcomentarios)
    from collections import Counter
    comment_counter = Counter()
    for post in full_posts:
        edges = post.get('data', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
        for edge in edges:
            comment = edge.get('node', {})
            owner = comment.get('owner', {}).get('username', None)
            if owner:
                comment_counter[owner] += 1
            # subcomentarios
            subedges = comment.get('edge_threaded_comments', {}).get('edges', [])
            for subedge in subedges:
                sub_owner = subedge.get('node', {}).get('owner', {}).get('username', None)
                if sub_owner:
                    comment_counter[sub_owner] += 1
    top_commenters = comment_counter.most_common(10)
    locations = []
    for post in full_posts:
        sc_media = post.get('data', {}).get('shortcode_media', {})
        location_name = None
        if 'location' in sc_media and sc_media['location'] and sc_media['location'].get('name'):
            location_name = sc_media['location']['name']
        timestamp = sc_media.get('taken_at_timestamp')
        if location_name and timestamp:
            date_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
            locations.append({
                'location': location_name,
                'date': date_str
            })
    sensitive = find_sensitive_data_in_comments(full_posts)
    return Response({
        'status': 'success',
        'bio': bio,
        'avatar': avatar,
        'full_name': full_name,
        'top_commenters': [{'username': u, 'count': c} for u, c in top_commenters],
        'locations': locations,
        'dnis': sensitive['dnis'],
        'ibans': sensitive['ibans'],
        'cccs': sensitive['cccs'],
        'phones': sensitive['phones'],
    })


