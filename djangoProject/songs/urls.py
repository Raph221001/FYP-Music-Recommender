from django.urls import include, path, re_path
from django.contrib import admin
from songs import views
from . import views
from .views import search, song_page, album_page, artist_page, reviews, recommendations, new_releases, video
from .models import Song

urlpatterns = [
	re_path(r'^search/', search),
	re_path(r'^song/(?P<song_id>\w+)/$', song_page),
	re_path(r'^album/(?P<album_id>\w+)/$', album_page),
	re_path(r'^artist/(?P<artist_id>\w+)/$', artist_page),
	re_path(r'^reviews/', reviews),
	re_path(r'^recommendations/', recommendations),
	re_path(r'^new_releases/', new_releases),
	re_path(r'^video/', video),

]