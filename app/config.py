import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY=os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=7)
    JWT_TOKEN_LOCATION=["headers"]
    JWT_HEADER_TYPE="Bearer"
    JWT_BLACKLIST_ENABLED=True