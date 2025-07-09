from django.urls import path
from Gestion_Identidad.Instagram.views.home_view import home
from Gestion_Identidad.Instagram.views.search_view import search
from Gestion_Identidad.Instagram.views.post_view import extract_posts

urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search, name='search'),
    path('extract_posts/', extract_posts), 
]

