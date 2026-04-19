from flask import Blueprint, request
from flask_restful import Api,Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Playlist, PlaylistSong
from app import db
from app.schema import PlaylistCreateSchema, PlaylistResponseSchema, PlaylistSongCreateSchema, PlaylistSongResponseSchema
import logging

playlist=Blueprint("playlist",__name__, url_prefix="/api")
api=Api(playlist)

class CreatePlaylistResource(Resource):
    @jwt_required()
    def post(self):
        user_id=int(get_jwt_identity())
        data=request.get_json()
        schema=PlaylistCreateSchema()
        validated_data=schema.load(data)
        existing=Playlist.query.filter_by(user_id=user_id,name=validated_data["name"]).first()
        if existing :
            logging.info(f"Playlist {validated_data['name']} already exist for {user_id}")
            return {
                "status":"fail",
                "message":"Playlist already exists!"
            },409
        playlist=Playlist(user_id=user_id,**validated_data)
        db.session.add(playlist)
        db.session.commit()
        return {
            "status":"success",
            "message" : "Playlist Created successfully!"
        },201
    
class ViewPlaylistResource(Resource):
    @jwt_required()
    def get(self):
        #checking ownership {use query filter with userid to filter the playlists}
        user_id=int(get_jwt_identity())
        playlists=Playlist.query.filter_by(user_id=user_id).all()
        if not playlists :
            logging.info(f"No playlist found for user {user_id} !")
            return {
                "status" : "fail",
                "message" : "No existing playlist!"
            },404
        schema=PlaylistResponseSchema(many=True)
        return {
            "status" : "success",
            "data" : schema.dump(playlists)
        },200

class DeletePlaylistResource(Resource):
    @jwt_required()
    def delete(self,playlist_id):
        user_id=int(get_jwt_identity())
        playlist=Playlist.query.filter_by(user_id=user_id,id=playlist_id).first()
        if not playlist:
            logging.info(f"User {user_id} tried deleting unauthorized playlist {playlist_id}")
            return {
                "status" : "fail",
                "message" : "Playlist not found or unauthorised!"
            },404
        db.sesion.delete(playlist)
        db.session.commit()
        logging.info(f"Playlist {playlist_id} deleted by user {user_id}")
        return {
            "status" : "success",
            "message" : "playlist deleted successfully!"
        },200
    

class AddPlaylistSongResource(Resource):
    @jwt_required()
    def post(self,playlist_id):
        #step1 check ownership (the user access its own playlist only)
        user_id=int(get_jwt_identity())
        playlist=Playlist.query.filter_by(id=playlist_id,user_id=user_id).first()
        if not playlist:
            return{
                "status":"fail",
                "message":"Playlist not found or unauthorized!"
            },404
        #step2 validate data
        data=request.get_json()
        schema=PlaylistSongCreateSchema()
        validated_data=schema.load(data)
        #step3 check for duplicates
        existing=PlaylistSong.query.filter_by(playlist_id=playlist_id,song_id=validated_data["song_id"]).first()
        if existing:
            logging.info(f"Song {validated_data['song_id']} already exist in playlist {playlist_id}")
            return {
                "status" : "fail",
                "message" : "Song already added to playlist!"
            },409
        #step 4 add song to db
        song = PlaylistSong(playlist_id=playlist_id, **validated_data)
        db.session.add(song)
        db.session.commit()
        logging.info(f"Song {validated_data['song_id']} added to playlist {playlist_id} for user {user_id} !")
        return{
            "status":"success",
            "message":"song added to playlist!"
        },201

class ViewPlaylistSongResource(Resource):
    @jwt_required()
    def get(self,playlist_id):
        user_id=int(get_jwt_identity())
        playlist=Playlist.query.filter_by(id=playlist_id,user_id=user_id).first()
        if not playlist:
            return {
                "status" : "fail",
                "message":"Playlist not found or unauthorized!"
            },404
        page=request.args.get("page", type=int , default=1)
        limit=request.args.get("limit", type=int, default=10)
        songs_query=PlaylistSong.query.filter_by(playlist_id=playlist_id)
        songs=songs_query.paginate(page=page, per_page=limit, error_out=False)
        if not songs.items:
            return {
                "status": "success",
                "data": [],
                "pagination": {
                    "page": page,
                    "total": 0
                }
            },200
        schema=PlaylistSongResponseSchema(many=True)
        return {
            "status" : "success",
            "data" : schema.dump(songs.items),
            "pagination": {
                "page": page,
                "total": songs.total
            }
        },200

class RemovePlaylistSongResource(Resource):
    @jwt_required()
    def delete(self,playlist_id,song_id):
        user_id=int(get_jwt_identity())
        playlist=Playlist.query.filter_by(id=playlist_id,user_id=user_id).first()
        if not playlist:
            logging.info(f"User {user_id} tried deleting song from unauthorized playlist {playlist_id}")
            return {
                "status" : "fail",
                "message" : "Playlist not found or unauthorized!"
            },404
        song=PlaylistSong.query.filter_by(playlist_id=playlist_id,song_id=song_id).first()
        if not song:
            logging.info(f"User {user_id} tried deleting unauthorized song {song_id}")
            return {
                "status" : "fail",
                "message" : "Song not found or unauthorized!"
            },404
        db.session.delete(song)
        db.session.commit()
        logging.info(f"song {song_id} removed from playlist {playlist_id} by user {user_id}")
        return{
            "status" : "success",
            "message" : "song removed successfully!"
        },200


api.add_resource(CreatePlaylistResource,"/playlists")
api.add_resource(ViewPlaylistResource,"/playlists")
api.add_resource(DeletePlaylistResource,"/playlists/<int:playlist_id>")

api.add_resource(AddPlaylistSongResource,"/playlists/<int:playlist_id>/songs")
api.add_resource(ViewPlaylistSongResource,"/playlists/<int:playlist_id>/songs")
api.add_resource(RemovePlaylistSongResource,"/playlists/<int:playlist_id>/songs/<string:song_id>")