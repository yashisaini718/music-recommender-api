import random
import requests
import logging
from sqlalchemy import or_
from app.models import LikedSongs

ITUNES_URL= "https://itunes.apple.com/search"

#song searching logic
def search_songs(query):
    params={
        "term" : query,
        "entity" : "song",
        "limit" : 10
    }
    try :
        response=requests.get(ITUNES_URL,params=params)
        response.raise_for_status()
    except requests.RequestException as e :
        logging.error(f"Song Api Error: {str(e)}")
        return None
    data=response.json()
    songs=[]
    for item in data.get("results",[]):
        songs.append({
            "song_id" : item.get("trackId"),
            "title" : item.get("trackName"),
            "artist" : item.get("artistName"),
            "album" : item.get("collectionName"),
            "preview" : item.get("previewUrl"),
            "image" : item.get("artworkUrl60")
        })
    return songs


#recommendation logic
def get_recommendation(user_id):
    liked_songs=LikedSongs.query.filter_by(user_id=user_id).all()
    if not liked_songs :
        return []
    artists=[song.artist for song in liked_songs]
    albums=[song.album for song in liked_songs]
    liked_ids={song.song_id for song in liked_songs}
    songs=LikedSongs.query.filter(
        or_(LikedSongs.artist.in_(artists),
            LikedSongs.album.in_(albums)
            )
        ).all()
    unique={}
    for song in songs :
        if song.song_id not in liked_ids:
            unique[song.song_id]=song
    result=list(unique.values())
    random.shuffle(result)
    #used list for artists since we just want a collection of items 
    #used a set for liked_ids since we are checking membership and TC for this operation in sets is O(1) while in list it would be O(n)
    #used dictionary for unique since we want unique songs only secondly we can easily acces the values while constructing the result
    return result[:10]
