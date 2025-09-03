from django.urls import path
from Gestion_Identidad.Instagram.views.home_view import home
from Gestion_Identidad.Instagram.views.search_view import search
from Gestion_Identidad.Instagram.views.post_view import extract_posts
from Gestion_Identidad.Instagram.views.instagram_analysis_view import instagram_analysis
from Gestion_Identidad.Google.views.google_search_view import google_search_view
from Gestion_Identidad.Linkedin.views.linkedin_view import linkedin_search_view



urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search, name='search'),
    path('extract_posts/', extract_posts), 
    path('api/instagram_analysis/', instagram_analysis, name='instagram_analysis'),
    path("api/google-search/", google_search_view, name="google_search_view"),
    path("api/linkedin-search/", linkedin_search_view, name="linkedin_search_view"),
]

