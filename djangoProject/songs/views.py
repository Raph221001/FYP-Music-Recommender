from __future__ import unicode_literals
from time import localtime, strftime
from django.shortcuts import render, redirect
from .models import Song, Album, Artist, SongReview, AlbumReview, ArtistReview
from django.db.models import Avg
import unicodedata
import spotipy
import spotipy.util as util
import spotipy.oauth2 as oauth2
import requests
#import googleapis
from isodate import parse_duration
from django.conf import settings

credentials = oauth2.SpotifyClientCredentials(
    client_id='CLIENT_KEY',
    client_secret='CLIENT_SECRET')


def search(request):
    token = settings.OAUTH_KEY
    sp = spotipy.Spotify(auth=token)
    musicData = 'there is an error'
    if request.GET:
        search = request.GET.get('q')
        if 'r' in request.GET:
            Song.objects.all().delete()
            Album.objects.all().delete()
            Artist.objects.all().delete()
            try:
                searchresults = sp.search(q=search, limit=20, type='track')
                for i, t in enumerate(searchresults['tracks']['items']):
                    Title = t['name']
                    theAlbum = t['album']['name']
                    albumId = t['album']['id']
                    theId = t['id']
                    Type = t['type']
                    Preview = t['preview_url']
                    External = t['external_urls']['spotify']
                    URI = t['uri']
                    MainArtist = t['artists'][0]['name']
                    somelist = [x['name'] for x in t['artists']]
                    Artists = ', '.join(somelist)
                    Popularity = float(t['popularity'])
                    artistId = t['artists'][0]['id']
                    if not t['album']['images']:
                        theImage = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
                    else:
                        theImage = t['album']['images'][0]['url']
                    theSong = Song.objects.create(title=Title, theType=Type, query=search, albumId=albumId,
                                                  album=theAlbum, songId=theId, preview=Preview,
                                                  external=External, uri=URI, duration='none',
                                                  mainArtist=MainArtist, artists=Artists,
                                                  popularity=Popularity, image=theImage, artistId=artistId)
                    musicData = Song.objects.filter(query=search)
            except:
                musicData = "there is a song error"

        if 'p' in request.GET:
            Song.objects.all().delete()
            Album.objects.all().delete()
            Artist.objects.all().delete()
            try:
                searchresults = sp.search(q=search, limit=10, type='album')
                for i, t in enumerate(searchresults['albums']['items']):
                    Title = t['name']
                    print(t['name'])
                    if not t['images']:
                        theImage = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
                    else:
                        theImage = t['images'][0]['url']
                    theId = t['id']
                    someting = sp.album(theId)
                    releaseDate = someting['release_date']
                    popularity = float(someting['popularity'])
                    Type = someting['album_type']
                    External = t['external_urls']['spotify']
                    URI = t['uri']
                    MainArtist = t['artists'][0]['name']
                    somelist = [x['name'] for x in t['artists']]
                    Artists = ', '.join(somelist)
                    thatList = [str(x) for x in t['available_markets']]
                    theMarkets = ', '.join(thatList)
                    stringDate = unicodedata.normalize('NFKD', releaseDate).encode('ascii', 'ignore')
                    Year = stringDate[:4]
                    theAlbum = Album.objects.create(year=Year, title=Title, theType=Type,
                                                    popularity=popularity, releaseDate=releaseDate, query=search,
                                                    image=theImage, albumId=theId, external=External, uri=URI,
                                                    mainArtist=MainArtist, artists=Artists, artistId='no')
                    musicData = Album.objects.filter(query=search)
            except:
                musicData = "there is a album error"

        if 'n' in request.GET:
            Song.objects.all().delete()
            Album.objects.all().delete()
            Artist.objects.all().delete()
            try:
                searchresults = sp.search(q=search, limit=50, type='artist')
                for i, t in enumerate(searchresults['artists']['items']):
                    name = t['name']
                    artistId = t['id']
                    genres = [x for x in t['genres']]
                    Genres = ', '.join(genres)
                    external = t['external_urls']['spotify']
                    uri = t['uri']
                    if not t['images']:
                        image = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
                    else:
                        image = t['images'][0]['url']
                    popularity = float(t['popularity'])
                    numOfFollowers = t['followers']
                    theArtist = Artist.objects.create(name=name, query=search, artistId=artistId, genres=Genres,
                                                      external=external, uri=uri, image=image, popularity=popularity,
                                                      numOfFollowers=numOfFollowers, songId="None", albumId="None")
                    musicData = Artist.objects.filter(query=search)
            except:
                musicData = "there is a artist error"
        return render(request=request, template_name='search.html', context={'musicData': musicData, 'search': True})
    else:
        return render(request, 'search.html')


def song_page(request, song_id):
    token = settings.OAUTH_KEY
    sp = spotipy.Spotify(auth=token)
    theUser = request.user
    allReviews = SongReview.objects.filter(songId=song_id).order_by('-time')
    average = allReviews.aggregate(Avg('rating'))
    theTrack = sp.track(song_id)
    songArtistLists = [x['name'] for x in theTrack['artists']]
    songArtists = ", ".join(songArtistLists)
    if Song.objects.filter(songId=song_id).exists():
        song_pg = Song.objects.get(songId=song_id)
    else:
        theSong = Song.objects.create(title=theTrack['name'], theType=theTrack['type'], query='nothing',
                                      album=theTrack['album']['name'], songId=theTrack['id'],
                                      preview=theTrack['preview_url'], external=theTrack['external_urls']['spotify'],
                                      uri=theTrack['uri'], duration='none', mainArtist=theTrack['artists'][0]['name'],
                                      artists='nope', popularity=theTrack['popularity'],
                                      image=theTrack['album']['images'][0]['url'],
                                      artistId=theTrack['artists'][0]['id'])
        song_pg = Song.objects.get(songId=song_id)
    Artist.objects.all().delete()
    track = sp.track(song_id)
    album = sp.album(track['album']['id'])
    stringDate = unicodedata.normalize('NFKD', album['release_date']).encode('ascii', 'ignore')
    theYear = stringDate[:4]
    albumId = album['id']
    for r in track['artists']:
        l = sp.artist(r['id'])
        genres = [x for x in l['genres']]
        theGenres = ', '.join(genres)
        if not l['images']:
            image = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        else:
            image = l['images'][0]['url']
        if Artist.objects.filter(artistId=l['id']).exists():
            artistData = Artist.objects.filter(songId=song_id)
        else:
            theArtist = Artist.objects.create(name=l['name'], query='nothing', artistId=l['id'], genres=theGenres,
                                              external=l['external_urls']['spotify'], uri=l['uri'], image=image,
                                              popularity=l['popularity'], numOfFollowers=l['followers'], songId=song_id,
                                              albumId="None")
            artistData = Artist.objects.filter(songId=song_id)
    somelist = [x['name'] for x in album['artists']]
    theArtists = ', '.join(somelist)
    if Album.objects.filter(albumId=albumId).exists():
        album_pg = Album.objects.get(albumId=albumId)
    else:
        theAlbum = Album.objects.create(year=theYear, title=album['name'], theType=album['album_type'],
                                        popularity=float(album['popularity']), releaseDate=album['release_date'],
                                        query='nothin', image=album['images'][0]['url'], albumId=album['id'],
                                        external=album['external_urls']['spotify'], uri=album['uri'],
                                        mainArtist=album['artists'][0]['name'], artists=theArtists, artistId='no')
        album_pg = Album.objects.get(albumId=albumId)
    if not allReviews:
        allReviews = 'nope'
    if request.GET:
        theComment = request.GET.get('review')
        theRating = request.GET.get('number')
        if 'reviewed' in request.GET:
            showtime = strftime("%d-%m-%Y %H:%M:%S", localtime())
            theReview = SongReview.objects.create(songId=song_id, albumId=theTrack['album']['id'],
                                                  albumTitle=theTrack['album']['name'],
                                                  image=theTrack['album']['images'][0]['url'], time=showtime,
                                                  songTitle=theTrack['name'], songArtists=songArtists, user=theUser,
                                                  comment=theComment, rating=theRating)
            allReviews = SongReview.objects.filter(songId=song_id).order_by('-time')
            average = allReviews.aggregate(Avg('rating'))
            return render(request, 'song.html',
                                      {'song_pg': song_pg,  'theUser': theUser,
                                       'average': average, "allReviews": allReviews, 'album_pg': album_pg,
                                       'artist_pg': artistData})
    else:
        return render(request, 'song.html', {'song_pg': song_pg,  'theUser': theUser,
                                                'average': average, "allReviews": allReviews, 'album_pg': album_pg,
                                                'artist_pg': artistData})


def album_page(request, album_id):
    token = settings.OAUTH_KEY
    sp = spotipy.Spotify(auth=token)
    Song.objects.all().delete()
    Artist.objects.all().delete()
    theUser = request.user
    allReviews = AlbumReview.objects.filter(albumId=album_id)
    average = allReviews.aggregate(Avg('rating'))
    album = sp.album(album_id)
    stringDate = unicodedata.normalize('NFKD', album['release_date']).encode('ascii', 'ignore')
    theYear = stringDate[:4]
    somelist = [x['name'] for x in album['artists']]
    theAlbumArtists = ', '.join(somelist)
    if Album.objects.filter(albumId=album_id).exists():
        album_pg = Album.objects.get (albumId=album_id)
    else:
        theAlbum = Album.objects.create(year=theYear, title=album['name'], theType=album['album_type'],
                                        popularity=float(album['popularity']), releaseDate=album['release_date'],
                                        query='nothin', image=album['images'][0]['url'], albumId=album['id'],
                                        external=album['external_urls']['spotify'], uri=album['uri'],
                                        mainArtist=album['artists'][0]['name'], artists=theAlbumArtists, artistId='no')
        album_pg = Album.objects.get(albumId=album_id)
    j = sp.album_tracks(album_id, limit=50, offset=0)
    albumName = album['name']
    for i in album['artists']:
        y = sp.artist(i['id'])
        genres = [x for x in y['genres']]
        theGenres = ', '.join(genres)
        if not y['images']:
            image = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        else:
            image = y['images'][0]['url']
        if Artist.objects.filter(artistId=y['id']).exists():
            artistData = Artist.objects.filter(albumId=album_id)
        else:
            theArtist = Artist.objects.create(name=y['name'], query='nothing', artistId=y['id'], genres=theGenres,
                                              external=y['external_urls']['spotify'], uri=y['uri'], image=image,
                                              popularity=y['popularity'], numOfFollowers=y['followers'], songId="None",
                                              albumId=album_id)
            artistData = Artist.objects.filter(albumId=album_id)
    for r in j['items']:
        track = sp.track(r['id'])
        popularity = track['popularity']
        if not track['album']['images']:
            image = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
        else:
            image = track['album']['images'][0]['url']
        somelist = [x['name'] for x in track['artists']]
        theArtists = ', '.join(somelist)
        if Song.objects.filter(songId=r['id']).exists():
            musicData = Song.objects.filter(albumId=album_id)
        else:
            theSong = Song.objects.create(title=r['name'], theType=r['type'], albumId=album_id, query='nothin',
                                          album=albumName, songId=r['id'], preview=r['preview_url'],
                                          external=r['external_urls']['spotify'], uri=r['uri'], duration='none',
                                          mainArtist=r['artists'][0]['name'], artists=theArtists, popularity=popularity,
                                          image=image, artistId=r['artists'][0]['id'])
            musicData = Song.objects.filter(albumId=album_id)
    if not allReviews:
        allReviews = 'nope'
    if request.GET:
        theComment = request.GET.get('review')
        theRating = request.GET.get('number')
        if 'reviewed' in request.GET:
            showtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
            theReview = AlbumReview.objects.create(albumId=album_id, image=album['images'][0]['url'], time=showtime,
                                                   albumTitle=album['name'], albumArtists=theAlbumArtists, user=theUser,
                                                   comment=theComment, rating=theRating)
            allReviews = AlbumReview.objects.filter(albumId=album_id)
            average = allReviews.aggregate(Avg('rating'))
            return render(request, 'album.html', {'album_pg': album_pg, 'theUser': theUser, 'average': average,
                                                     'allReviews': allReviews, 'musicData': musicData,
                                                     'artist_pg': artistData})
    else:
        return render(request, 'album.html', {'album_pg': album_pg, 'theUser': theUser, 'average': average,
                                                 'allReviews': allReviews, 'musicData': musicData,
                                                 'artist_pg': artistData})


def artist_page(request, artist_id):
    token = settings.OAUTH_KEY
    sp = spotipy.Spotify(auth=token)
    Song.objects.all().delete()
    Album.objects.all().delete()
    theUser = request.user
    ta = sp.artist(artist_id)
    allReviews = ArtistReview.objects.filter(artistId=artist_id)
    average = allReviews.aggregate(Avg('rating'))
    if not ta['images']:
        image = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
    else:
        image = ta['images'][0]['url']
    if Artist.objects.filter(artistId=artist_id).exists():
        artist_pg = Artist.objects.get(artistId=artist_id)
    else:
        genres = [x for x in ta['genres']]
        theGenres = ', '.join(genres)
        artistData = Artist.objects.create(name=ta['name'], query='nothin', artistId=ta['id'], genres=theGenres,
                                           external=ta['external_urls']['spotify'], uri=ta['uri'], image=image,
                                           popularity=ta['popularity'], numOfFollowers=ta['followers'], songId="None",
                                           albumId="none")
        artist_pg = Artist.objects.get(artistId=artist_id)
    top = sp.artist_top_tracks(artist_id, country='US')
    if not top['tracks']:
        songData = 'nothin'
    else:
        for i in top['tracks'][:10]:
            somelist = [x['name'] for x in i['artists']]
            theArtists = ', '.join(somelist)
            if Song.objects.filter(songId=i['id']).exists():
                songData = Song.objects.filter(artistId=artist_id)
            else:
                theSong = Song.objects.create(title=i['name'], theType=i['type'], albumId=i['album']['id'], query='nah',
                                              album=i['album']['name'], songId=i['id'], preview=i['preview_url'],
                                              external=i['external_urls']['spotify'], uri=i['uri'], duration='none',
                                              mainArtist=i['artists'][0]['name'], artists=theArtists,
                                              popularity=i['popularity'], image=i['album']['images'][0]['url'],
                                              artistId=artist_id)
                songData = Song.objects.filter(artistId=artist_id)
    albums = sp.artist_albums(artist_id, country='US', album_type='album', limit=50)
    # print albums
    if not albums['items']:
        albumData = 'nothin'
    else:
        for album in albums['items']:
            # print album['id']
            if Album.objects.filter(albumId=album['id']).exists():
                album_pg = Album.objects.filter(artistId=artist_id)
            else:
                someAlbum = sp.album(album['id'])
                somelist = [x['name'] for x in album['artists']]
                theArtists = ', '.join(somelist)
                stringDate = unicodedata.normalize('NFKD', someAlbum['release_date']).encode('ascii', 'ignore')
                theYear = stringDate[:4]
                if not album['images']:
                    theImage = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
                else:
                    theImage = album['images'][0]['url']
                # print album['name']
                # print theArtists
                theAlbum = Album.objects.create(year=theYear, title=album['name'], theType=album['album_type'],
                                                popularity=float(someAlbum['popularity']),
                                                releaseDate=someAlbum['release_date'], query='nothin', image=theImage,
                                                albumId=album['id'], external=album['external_urls']['spotify'],
                                                uri=album['uri'], mainArtist=album['artists'][0]['name'],
                                                artists=theArtists, artistId=artist_id)
                albumData = Album.objects.filter(artistId=artist_id)
    if not allReviews:
        allReviews = 'nope'
    if request.GET:
        theComment = request.GET.get('review')
        theRating = request.GET.get('number')
        if 'reviewed' in request.GET:
            showtime = strftime("%Y-%m-%d %H:%M:%S", localtime())
            theReview = ArtistReview.objects.create(artistId=artist_id, image=image, user=theUser, comment=theComment,
                                                    rating=theRating, artistName=ta['name'], time=showtime)
            allReviews = ArtistReview.objects.filter(artistId=artist_id)
            average = allReviews.aggregate(Avg('rating'))
            return render(request, 'artist.html', {'artist_pg': artist_pg, 'average': average, 'theUser': theUser,
                                                      'allReviews': allReviews, 'songData': songData,
                                                      'albumData': albumData})
    else:
        return render(request, 'artist.html', {'artist_pg': artist_pg, 'average': average, 'theUser': theUser,
                                                  'allReviews': allReviews, 'songData': songData,
                                                  'albumData': albumData})


def reviews(request):
    theUser = request.user
    songReview_pg = SongReview.objects.filter(user=theUser).order_by('-time')
    albumReview_pg = AlbumReview.objects.filter(user=theUser).order_by('-time')
    artistReview_pg = ArtistReview.objects.filter(user=theUser).order_by('-time')
    if not songReview_pg:
        songReview_pg = 'nope'
    if not albumReview_pg:
        albumReview_pg = 'nope'
    if not artistReview_pg:
        artistReview_pg = 'nope'
    return render(request, 'reviews.html', {'songReview_pg': songReview_pg, 'albumReview_pg': albumReview_pg,
                                                    'artistReview_pg': artistReview_pg})


def recommendations(request):
    token = settings.OAUTH_KEY
    sp = spotipy.Spotify(auth=token)
    Song.objects.all().delete()
    theRecommendedSongs = {}
    songs = []
    idList = []
    theUser = request.user
    songReviews = SongReview.objects.filter(user=theUser)
    if not songReviews:
        theRecommendedSongs = 'nonexistent'
    for r in songReviews:
        if r.rating > 5:
            songs.append(r.songId)
    if not songs:
        theRecommendedSongs = 'nonexistent'
    else:
        recommendedSongs = sp.recommendations(seed_artists=None, seed_genres=None, seed_tracks=songs, limit=12,
                                              country='US')
        for i in recommendedSongs['tracks']:
            idList.append(i['id'])
        for y in songReviews:
            if y.songId in idList:
                idList.remove(y.songId)
        recSongs = list(set(idList))
        for n in recSongs:
            theTrack = sp.track(n)
            songArtistLists = [x['name'] for x in theTrack['artists']]
            songArtists = ", ".join(songArtistLists)
            if not theTrack['album']['images']:
                theImage = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
            else:
                theImage = theTrack['album']['images'][0]['url']
            theSong = Song.objects.create(title=theTrack['name'], theType=theTrack['type'],
                                          albumId=theTrack['album']['id'], query='recs',
                                          album=theTrack['album']['name'], songId=theTrack['id'],
                                          preview=theTrack['preview_url'],
                                          external=theTrack['external_urls']['spotify'], uri=theTrack['uri'],
                                          duration='none', mainArtist=theTrack['artists'][0]['name'],
                                          artists=songArtists, popularity=theTrack['popularity'], image=theImage,
                                          artistId=theTrack['artists'][0]['id'])
            theRecommendedSongs = Song.objects.filter(query='recs')
    return render(request, 'recommendations.html', {'theRecommendedSongs': theRecommendedSongs})



def new_releases(request):
	token = settings.OAUTH_KEY
	sp = spotipy.Spotify(auth=token)
	Album.objects.all().delete()
	theNewStuff = sp.new_releases(country='US',limit=20)
	for i in theNewStuff['albums']['items']:
		theAlbum = sp.album(i['id'])
		featuresList = [x['name'] for x in theAlbum['artists']]
		features = ", ".join(featuresList)
		stringDate = unicodedata.normalize('NFKD', theAlbum['release_date']).encode('ascii','ignore')
		theYear = stringDate[:4]
		if not theAlbum['images']:
			theImage = 'https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg'
		else:
			theImage = theAlbum['images'][0]['url']
		theAlbum = Album.objects.create(year=theYear,title=theAlbum['name'],theType=theAlbum['album_type'],popularity=float(theAlbum['popularity']),releaseDate=theAlbum['release_date'],query='reca',image=theAlbum['images'][0]['url'],albumId=theAlbum['id'],external=theAlbum['external_urls']['spotify'],uri=theAlbum['uri'],mainArtist=theAlbum['artists'][0]['name'],artists=features,artistId='nah')
		newAlbums = Album.objects.filter(query='reca')
	return render(request, 'new_releases.html',{'newAlbums': newAlbums})


def video(request):
    videos = []

    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': request.POST['search'],
            'key': settings.YOUTUBE_KEY,
            'maxResults': 3,
            'type': 'video'
        }

        r = requests.get(search_url, params=search_params)

        results = r.json()['items']

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])


        video_params = {
            'key': settings.YOUTUBE_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(video_ids),
            'maxResults': 3
        }

        r = requests.get(video_url, params=video_params)

        results = r.json()['items']

        for result in results:
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail': result['snippet']['thumbnails']['high']['url']
            }

            videos.append(video_data)

    context = {
        'videos': videos
    }

    return render(request, 'video.html', context)