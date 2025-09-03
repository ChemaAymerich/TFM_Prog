from django.urls import path, include
from .views import home
from Gestion_Identidad.Instagram.views.search_view import search
from Gestion_Identidad.Instagram.views.post_view import extract_posts
from Gestion_Identidad.Instagram.views.instagram_analysis_view import instagram_analysis
from Gestion_Identidad.Twitter.views.twitter_view import twitter_search_view
from Gestion_Identidad.Linkedin.views.linkedin_view import linkedin_search_view

urlpatterns = [
    path('', home, name='home'),
    path('api/search/', search, name='search'), 
    path('extract_posts/', extract_posts, name='extract_posts'),
    path("api/instagram-analysis/", instagram_analysis, name="instagram_analysis"),
    path("api/twitter-search/", twitter_search_view, name="twitter_search"),
    path("api/linkedin-search/", linkedin_search_view, name="linkedin_search"),
]

