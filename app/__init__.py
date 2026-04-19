from flask import Flask
from app.config import Config
from app.extensions import db, bcrypt, jwt, migrate
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# define application factory 
def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app,db)

    from app.auth.routes import auth
    from app.songs.routes import songs
    from app.playlist.routes import playlist
    from app.handlers.errors import error
    from app.handlers import jwt_handlers

   # with app.app_context():
   #     db.create_all()

    with app.app_context():
        from app.utils import cleanup_expired_tokens
        try:
            cleanup_expired_tokens()
            app.logger.info(f"Deleted expired tokens")
        except Exception as e:
            app.logger.warning(f"Token cleanup failed: {e}")

    app.register_blueprint(auth)
    app.register_blueprint(songs)
    app.register_blueprint(playlist)
    app.register_blueprint(error)
    
    return app