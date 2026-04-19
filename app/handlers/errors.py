from flask import Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

error=Blueprint("error",__name__)

@error.app_errorhandler(ValidationError)
def handle_validation_error(err):
    logging.error(f"Validation Error: {str(err)}")
    return {
        "status":"fail",
        "error": str(err)
    },400

@error.app_errorhandler(IntegrityError)
def handle_integrity_error(err):
    logging.error(f"Integrity Error: {str(err)}")

    return {
        "status":"fail",
        "message":"Dupliate or Invalid data!"
    },400

@error.app_errorhandler(SQLAlchemyError)
def handle_db_error(err):
    logging.error(f"DB Error: {str(err)}")

    return{
        "status":"fail",
        "message":"database error"
    },500

@error.app_errorhandler(404)
def handle_not_found(err):
    logging.error(f"NOT FOUND Error: {str(err)}")

    return {
        "status": "fail",
        "message": "Resource not found"
    }, 404

@error.app_errorhandler(500)
def handle_server_error(err):
    logging.error(f"Internal Server Error: {str(err)}")

    return {
        "status": "error",
        "message": "Internal server error"
    }, 500