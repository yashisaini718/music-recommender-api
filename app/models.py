from app import db
from datetime import datetime, timezone

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120),unique=True, nullable=False)
    password=db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self.password}>"
    
class LikedSongs(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    song_id=db.Column(db.String(100))
    title=db.Column(db.String(200))
    artist=db.Column(db.String(200))
    album=db.Column(db.String(200))
    image=db.Column(db.String(300))
    preview=db.Column(db.String(300))
    user=db.relationship('User',backref="liked_songs")

class Playlist(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

class PlaylistSong(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    playlist_id=db.Column(db.Integer(),db.ForeignKey('playlist.id'))
    song_id=db.Column(db.String(100))
    title=db.Column(db.String(200))
    artist=db.Column(db.String(200))
    album=db.Column(db.String(200))
    image=db.Column(db.String(300))
    preview=db.Column(db.String(300))
    __table_args__ = (
        db.UniqueConstraint(
            'playlist_id', 'song_id', 
            name='unique_song_per_playlist'
        ),
    )

class TokenBlockList(db.Model):
    __tablename__="token_blocklist"
    id=db.Column(db.Integer(),primary_key=True)
    jti=db.Column(db.String(36),nullable=False,index=True)
    token_type=db.Column(db.String(30))
    created_at=db.Column(db.DateTime(timezone=True), default= lambda: datetime.now(timezone.utc))
    expires_at=db.Column(db.DateTime(),nullable=False)