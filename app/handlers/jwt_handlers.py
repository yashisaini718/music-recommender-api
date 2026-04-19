from app import jwt
from app.models import TokenBlockList
from app.extensions import db

@jwt.unauthorized_loader
def missing_token(err):
    return {
        "status": "fail",
        "message": "Authorization token is missing"
    }, 401

@jwt.invalid_token_loader
def invalid_token(err):
    return {
        "status": "fail",
        "message": "Invalid token!"
    }, 401

@jwt.expired_token_loader
def expired_token(jwt_header,jwt_payload):
    return {
        "status": "fail",
        "message": "Expired token!"
    }, 401

@jwt.revoked_token_loader
def revoked_token(jwt_header,jwt_payload):
    return {
        "status": "fail",
        "message": "Token has been revoked!"
    }, 401


@jwt.needs_fresh_token_loader
def fresh_token_required(jwt_header,jwt_payload):
    return {
        "status": "fail",
        "message": "Fresh token required!"
    }, 401

@jwt.token_in_blocklist_loader
def check_if_Token_revoked(jwt_header,jwt_payload):
    jti=jwt_payload["jti"]
    return db.session.query(TokenBlockList.id).filter_by(jti=jti).scalar() is not None