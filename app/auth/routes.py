from flask import Blueprint, request
from app.models import User,TokenBlockList
from app import db, bcrypt
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity,create_refresh_token, get_jwt
from app.schema import RegisterSchema, LoginSchema, UserResponseSchema
import logging
from datetime import datetime


auth=Blueprint("auth",__name__,url_prefix="/api/auth")
api=Api(auth)

### not added db.rollback in case of errors like when registration fails we shoudl rollback the db 

class RegistrationResource(Resource):
    def post(self):
        data=request.get_json()
        
        schema=RegisterSchema()
        validated_data=schema.load(data)
        if User.query.filter_by(username=validated_data["username"]).first():
            logging.warning(f"Registration failed - username exists: {validated_data['username']}")
            return {
                "status" : "fail",
                "message" : "Username already exists"
            },400

        if User.query.filter_by(email=validated_data["email"]).first():
            logging.warning(f"Registration failed - email exists: {validated_data['email']}")
            return {
                "status" : "fail",
                "message" : "Email already exists"
            },400

        hashed_password=bcrypt.generate_password_hash(
            validated_data["password"]).decode("utf-8")
        
        validated_data["password"] = hashed_password
        user=User(**validated_data)

        db.session.add(user)
        db.session.commit()

        logging.info(f"New user registered: {validated_data['email']}")
        return {
            "status" : "success",
            "message" : "User registered successfully!"
        },201

class LoginResource(Resource):
    def post(self):
        data=request.get_json()

        schema=LoginSchema()
        validated_data=schema.load(data)

        logging.info(f"Login attempt for {validated_data['email']}")
        user=User.query.filter_by(email=validated_data["email"]).first()
        if not user :
            logging.warning(f"Failed login for {validated_data['email']}")
            return {
                "status":"fail",
                "message":"Invalid credentials!"
            },401
        if not bcrypt.check_password_hash(user.password,validated_data["password"]):
            logging.warning(f"Failed login for {validated_data['email']}")
            return {
                "status":"fail",
                "message" : "Invalid credentials!"
            },401
        
        access_token=create_access_token(identity=str(user.id))
        refresh_token=create_refresh_token(identity=str(user.id))

        return {
            "status" : "success",
            "data" : {
                "access_token" :access_token,
                "refresh_token": refresh_token
            }   
        },200

class MeResource(Resource):
    @jwt_required()
    def get(self):    
        user_id=int(get_jwt_identity())
        #user=User.query.get_or_404(user_id)
        # the above method is depricated in newer sqlalchemy 
        user=db.session.get(User,user_id) 
        schema=UserResponseSchema()

        if not user :
            logging.info(f"No user exist for {user_id} !")
            return {
                "status" : "fail",
                "message" : "No User Found !"
            },404
        
        return {
            "status" : "success",
            "data":schema.dump(user)
        },200

class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id=get_jwt_identity()
        new_access_token=create_access_token(identity=user_id)
        logging.info(f"Access token refreshed for user {user_id} !")

        return {
            "status" : "success",
            "data" : {
                "access_token": new_access_token
            }
        },200
    

class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        jwt_data=get_jwt()
        jti=jwt_data["jti"]
        exp=jwt_data["exp"]
        expires_at=datetime.fromtimestamp(exp)
        db.session.add(TokenBlockList(
            jti=jti,
            token_type="access",
            expires_at=expires_at
        ))
        db.session.commit()
        return {
            "status": "success",
            "message": "Access token revoked"
        }, 200
        
class LogoutRefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jwt_data=get_jwt()
        jti = jwt_data["jti"]
        exp=jwt_data["exp"]
        expires_at=datetime.fromtimestamp(exp)
        db.session.add(TokenBlockList(
            jti=jti,
            token_type="refresh",
            expires_at=expires_at
        ))
        db.session.commit()
        return {
            "status": "success",
            "message": "Refresh token revoked"
        }, 200



api.add_resource(RegistrationResource,"/register")
api.add_resource(LoginResource,"/login")
api.add_resource(MeResource,"/me")
api.add_resource(RefreshResource,"/refresh")
api.add_resource(LogoutResource,"/logout")
api.add_resource(LogoutRefreshResource,"/logout/refresh")