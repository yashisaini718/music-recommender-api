from flask import Blueprint, request
from app.songs.services import search_songs, get_recommendation
from flask_restful import Api,Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import LikedSongs
from app import db
from app.schema import LikeSongSchema, SongSchema
import logging

songs=Blueprint("songs",__name__, url_prefix="/api/songs")
api=Api(songs)

class SearchSongResource(Resource):
    def get(self):
        query=request.args.get("q")
        if not query :
            logging.warning(f"missing query parameter")
            return {
                "status" : "fail",
                "message" : " query parameter 'q' is required"
            }, 400
        
        songs=search_songs(query)
        if songs is None :
            return {
                "status" : "fail",
                "message" : "Failed to fetch songs"
            },500
        
        logging.info(f"Search song with query parameter: {query}")
        return {
            "status" : "success",
            "data" : songs
        },200

class LikeSongResource(Resource):
    @jwt_required()
    def post(self):
        user_id=int(get_jwt_identity())
        data=request.get_json()
        schema=LikeSongSchema()
        validated_data=schema.load(data)
        existing=LikedSongs.query.filter_by(
            user_id=user_id,song_id=validated_data["song_id"]
        ).first()
        if existing :
            logging.warning(f"User {user_id} tried to like already liked song {validated_data['song_id']}")
            return {
                "status" :"fail",
                "message" : "Already Liked!"
            },409
        song=LikedSongs(user_id=user_id, **validated_data)
        db.session.add(song)
        db.session.commit()
        logging.info(f"User {user_id} liked song {validated_data['song_id']}")
        return {
            "status" : "success",
            "message" : "Song added to LikedSongs!"
        },201


class GetLikedSongResource(Resource):
    @jwt_required()
    def get(self):
        user_id=get_jwt_identity()
        page=request.args.get("page",type=int, default=1)
        limit=request.args.get("limit", type=int, default=10)
        results_query=LikedSongs.query.filter_by(user_id=user_id)
        results=results_query.paginate(page=page,per_page=limit, error_out=False)
        if not results.items:
            #return {
            #    "status" : "fail",
            #   "message" : "Songs not found!"
            
            #},404
            return {
                "status": "success",
                "data": [],
                "pagination": {
                    "page": page,
                    "total": 0
                }
            },200
        schema=SongSchema(many=True)
        logging.info(f"Fetched liked songs for user {user_id}")
        return {
            "status" : "success",
            "data" : schema.dump(results.items),
            "pagination": {
                "page": page,
                "total": results.total
            }
        },200
    
class DeleteLikedSongResource(Resource):
    @jwt_required()
    def delete(self,song_id):
        user_id=int(get_jwt_identity())
        song=LikedSongs.query.filter_by(song_id=song_id,user_id=user_id).first()
        if not song :
            return {
                "status" : "fail",
                "message" : "Song not found!"
            },404
        db.session.delete(song)
        db.session.commit()
        return {
            "status" : "success",
            "message" : "Song unliked successfully!"
        },200
    
class RecommendationResource(Resource):
    @jwt_required()
    def get(self):
        user_id=int(get_jwt_identity())
        recommendations=get_recommendation(user_id)
        if recommendations is None :
            return {
                "status" : "fail",
                "message" : "Failed to fetch songs"
            },500
        schema=SongSchema(many=True)
        logging.info(f"Fetched recommndations for user {user_id}")
        return {
            "status" : "success",
            "data":schema.dump(recommendations)
        },200
    

api.add_resource(SearchSongResource,"")
api.add_resource(LikeSongResource,"/like-song")
api.add_resource(GetLikedSongResource,"/liked-songs")
api.add_resource(DeleteLikedSongResource,"/liked-songs/<string:song_id>")
api.add_resource(RecommendationResource,"/recommendations")