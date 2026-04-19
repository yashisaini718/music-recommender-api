from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    id=fields.Int(dump_only=True)
    username=fields.Str(required=True, validate=validate.Length(min=3,max=20))
    email=fields.Email(required=True)
    password=fields.Str(required=True, load_only=True)
        
class LoginSchema(Schema):
    email=fields.Email(required=True)
    password=fields.Str(required=True, load_only=True)

class UserResponseSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()

class LikeSongSchema(Schema):
    id=fields.Int(dump_only=True)
    song_id=fields.Str(required=True)
    title=fields.Str(required=True)
    artist=fields.Str(required=True)
    album=fields.Str()
    image=fields.Str()
    preview=fields.Str()

class SongSchema(Schema):
    id=fields.Int()
    song_id = fields.Str()
    title=fields.Str()
    artist=fields.Str()
    album=fields.Str()
    image=fields.Str()
    preview=fields.Str()

class PlaylistCreateSchema(Schema):
    id=fields.Int(dump_only=True)
    name=fields.Str(required=True)

class PlaylistResponseSchema(Schema):
    id=fields.Int()
    name=fields.Str()

class PlaylistSongCreateSchema(Schema):
    id=fields.Int(dump_only=True)
    song_id = fields.Str(required=True)
    title=fields.Str()
    artist=fields.Str()
    album=fields.Str()
    image=fields.Str()
    preview=fields.Str()

class PlaylistSongResponseSchema(Schema):
    id=fields.Int()
    song_id = fields.Str()
    title=fields.Str()
    artist=fields.Str()
    image=fields.Str()
    preview=fields.Str()