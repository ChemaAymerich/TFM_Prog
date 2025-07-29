from django.urls import path
from Gestion_Identidad.Instagram.views.home_view import home
from Gestion_Identidad.Instagram.views.search_view import search
from Gestion_Identidad.Instagram.views.post_view import extract_posts
from Gestion_Identidad.Instagram.views.instagram_analysis_view import instagram_analysis


urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search, name='search'),
    path('extract_posts/', extract_posts), 
    path('api/instagram_analysis/', instagram_analysis, name='instagram_analysis'), 
]

