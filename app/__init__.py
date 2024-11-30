#Flask Configuration
from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY']='thisismysecretkeyformusicapp'
app.config['UPLOAD_FOLDER']='static/media'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MusicDataBase.sqlite3'
db = SQLAlchemy()
db.init_app(app)
api = Api(app)
app.app_context().push()

#Login Manager setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'index'
login_manager.init_app(app)

#Importing the routes
from app import views, models, forms

#-------------------------------------------- APIS ------------------------------------------
from flask_restful import Resource, abort, reqparse, fields, marshal_with
from app.models import Albums, Playlists, Songs, Users
from werkzeug.security import generate_password_hash
#User Apis
user_fields = {
    'id': fields.Integer,
    'u_userType': fields.String,
    'u_status': fields.String,
    'u_flag': fields.Integer,
    'u_fName': fields.String,
    'u_lName': fields.String,
    'u_gender': fields.String,
    'u_username': fields.String,
    'u_email': fields.String,
    'u_password': fields.String
}
user_req = reqparse.RequestParser()
user_req.add_argument("u_userType")
user_req.add_argument("u_status")
user_req.add_argument("u_flag")
user_req.add_argument("u_fName")
user_req.add_argument("u_lName")
user_req.add_argument("u_gender")
user_req.add_argument("u_username")
user_req.add_argument("u_email")
user_req.add_argument("u_password")

update_user_req = reqparse.RequestParser()
update_user_req.add_argument("u_userType")
update_user_req.add_argument("u_status")
update_user_req.add_argument("u_flag")
update_user_req.add_argument("u_fName")
update_user_req.add_argument("u_lName")
update_user_req.add_argument("u_gender")
update_user_req.add_argument("u_username")
update_user_req.add_argument("u_email")
update_user_req.add_argument("u_password")

class UserAPI(Resource):
    @marshal_with(user_fields)
    def get(self, id=None):
        if id:
            user=Users.query.get(id)
            if not user:
                abort(404, message="User does not exists.")
            else:
                return user
        else:
            user= Users.query.all()
            return user, 200
    
    @marshal_with(user_fields)
    def post(self, id=None):
        data=user_req.parse_args()
        user=Users(u_userType=data.u_userType, u_status=data.u_status, u_flag=data.u_flag, u_fName=data.u_fName, u_lName=data.u_lName, u_gender=data.u_gender, u_username=data.u_username, u_email=data.u_email, u_password=generate_password_hash(data.u_password, method='scrypt', salt_length=16))
        db.session.add(user)
        db.session.commit()
        return user, 200
    
    @marshal_with(user_fields)
    def put(self, id=None):
        if not id:
            abort(404, message="Invalid user id.")
        else:
            data= update_user_req.parse_args()
            data.u_password=generate_password_hash(data.u_password, method='scrypt', salt_length=16)
            user= Users.query.filter_by(id=id)
            if not user.first():
                abort(404, message="User does not exists.")
            else:
                user.update(data)
                db.session.commit()
                return 200
    
    @marshal_with(user_fields)
    def delete(self, id=None):
        if id:
            user=Users.query.get(id)
            if not user:
                abort(404, message="User does not exists.")
            db.session.delete(user)
            db.session.commit()
            return "User deleted successfully.", 200
        else:
            abort(400, message="Please provide user id")

#Album Apis
album_fields={
    'id': fields.Integer,
    'a_name': fields.String,
    'a_artist': fields.String,
    'a_genres': fields.String,
    'a_date': fields.String,
    'a_rating': fields.Integer,
    'a_totalRaters': fields.Integer,
    'a_flag': fields.Integer,
    'user_id': fields.Integer
}

album_req=reqparse.RequestParser()
album_req.add_argument("a_name")
album_req.add_argument("a_artist")
album_req.add_argument("a_genres")
album_req.add_argument("a_date")
album_req.add_argument("a_rating")
album_req.add_argument("a_totalRaters")
album_req.add_argument("a_flag")
album_req.add_argument("user_id")

update_album_req=reqparse.RequestParser()
update_album_req.add_argument("a_name")
update_album_req.add_argument("a_artist")
update_album_req.add_argument("a_genres")
update_album_req.add_argument("a_date")
update_album_req.add_argument("a_rating")
update_album_req.add_argument("a_totalRaters")
update_album_req.add_argument("a_flag")
update_album_req.add_argument("user_id")

class AlbumAPI(Resource):
    @marshal_with(album_fields)
    def get(self, id=None):
        if id:
            album=Albums.query.get(id)
            if not album:
                abort(404, message="Album does not exists.")
            else:
                return album
        else:
            album=Albums.query.all()
            return album, 200
    
    @marshal_with(album_fields)
    def post(self, id=None):
        data=album_req.parse_args()
        album=Albums(a_name=data.a_name, a_artist=data.a_artist, a_genres=data.a_genres, a_date=data.a_date, a_rating=data.a_rating, a_totalRaters=data.a_totalRaters, a_flag=data.a_flag, user_id=data.user_id)
        db.session.add(album)
        db.session.commit()
        return album, 200
    
    @marshal_with(album_fields)
    def put(self, id=None):
        if not id:
            abort(404, message="Invalid album id.")
        else:
            data= update_album_req.parse_args()
            album= Albums.query.filter_by(id=id)
            if not album.first():
                abort(404, message="Album does not exists.")
            else:
                album.update(data)
                db.session.commit()
                return 200
    
    @marshal_with(album_fields)
    def delete(self, id=None):
        if id:
            album = Albums.query.get(id)
            if not album:
                abort(404, message="Album does not exists.")
            db.session.delete(album)
            db.session.commit()
            return "Album deleted successfully.", 200
        else:
            abort(400, message="Please provide album id")

#Songs Apis
song_fields={
    'id': fields.Integer,
    's_name': fields.String,
    's_artist': fields.String,
    's_album': fields.String,
    's_genre': fields.String,
    's_duration': fields.String,
    's_date': fields.String,
    's_filePath': fields.String,
    's_lyrics': fields.String,
    's_rating': fields.Integer,
    's_totalRaters': fields.Integer,
    's_flag': fields.Integer,
    's_plays': fields.Integer,
    'album_id': fields.Integer,
    'user_id': fields.Integer
}

song_req=reqparse.RequestParser()
song_req.add_argument("s_name")
song_req.add_argument("s_artist")
song_req.add_argument("s_album")
song_req.add_argument("s_genre")
song_req.add_argument("s_duration")
song_req.add_argument("s_date")
song_req.add_argument("s_filePath")
song_req.add_argument("s_lyrics")
song_req.add_argument("s_rating")
song_req.add_argument("s_totalRaters")
song_req.add_argument("s_flag")
song_req.add_argument("s_plays")
song_req.add_argument("album_id")
song_req.add_argument("user_id")

update_song_req=reqparse.RequestParser()
update_song_req.add_argument("s_name")
update_song_req.add_argument("s_artist")
update_song_req.add_argument("s_album")
update_song_req.add_argument("s_genre")
update_song_req.add_argument("s_duration")
update_song_req.add_argument("s_date")
update_song_req.add_argument("s_filePath")
update_song_req.add_argument("s_lyrics")
update_song_req.add_argument("s_rating")
update_song_req.add_argument("s_totalRaters")
update_song_req.add_argument("s_flag")
update_song_req.add_argument("s_plays")
update_song_req.add_argument("album_id")
update_song_req.add_argument("user_id")

class SongAPI(Resource):
    @marshal_with(song_fields)
    def get(self, id=None):
        if id:
            song=Songs.query.get(id)
            if not song:
                abort(404, message="Song does not exists.")
            else:
                return song
        else:
            song=Songs.query.all()
            return song, 200
    
    @marshal_with(song_fields)
    def post(self, id=None):
        data=song_req.parse_args()
        song=Songs(s_name=data.s_name, s_artist=data.s_artist, s_album=data.s_album, s_genre=data.s_genre,s_duration=data.s_duration, s_date=data.s_date,s_filepath=data.s_filePath,s_lyrics=data.s_lyrics, s_rating=data.s_rating, s_totalRaters=data.s_totalRaters, s_flag=data.s_flag,s_plays=data.s_plays, album_id=data.album_id, user_id=data.user_id)
        db.session.add(song)
        db.session.commit()
        return song, 200
    
    @marshal_with(song_fields)
    def put(self, id=None):
        if not id:
            abort(404, message="Invalid song id.")
        else:
            data= update_song_req.parse_args()
            song= Songs.query.filter_by(id=id)
            if not song.first():
                abort(404, message="Song does not exists.")
            else:
                song.update(data)
                db.session.commit()
                return 200
    
    @marshal_with(song_fields)
    def delete(self, id=None):
        if id:
            song = Songs.query.get(id)
            if not song:
                abort(404, message="Song does not exists.")
            db.session.delete(song)
            db.session.commit()
            return "Song deleted successfully.", 200
        else:
            abort(400, message="Please provide song id")

playlist_fields={
    'id': fields.Integer,
    'p_name': fields.String,
    'p_noOfTracks': fields.Integer,
    'songIds_list': fields.String,
    'user_id': fields.Integer
}

playlist_req=reqparse.RequestParser()
playlist_req.add_argument("p_name")
playlist_req.add_argument("p_noOfTracks")
playlist_req.add_argument("songIds_list")
playlist_req.add_argument("user_id")

update_playlist_req=reqparse.RequestParser()
update_playlist_req.add_argument("p_name")
update_playlist_req.add_argument("p_noOfTracks")
update_playlist_req.add_argument("songIds_list")
update_playlist_req.add_argument("user_id")

class PlaylistAPI(Resource):
    @marshal_with(playlist_fields)
    def get(self, id=None):
        if id:
            playlist=Playlists.query.get(id)
            if not playlist:
                abort(404, message="Playlist does not exists.")
            else:
                return playlist
        else:
            playlist=Playlists.query.all()
            return playlist, 200
    
    @marshal_with(playlist_fields)
    def post(self, id=None):
        data=playlist_req.parse_args()
        playlist=Playlists(p_name=data.p_name, p_noOfTracks=data.p_noOfTracks, songIds_list=data.songIds_list, user_id=data.user_id)
        db.session.add(playlist)
        db.session.commit()
        return playlist, 200
    
    @marshal_with(playlist_fields)
    def put(self, id=None):
        if not id:
            abort(404, message="Invalid playlist id.")
        else:
            data= update_playlist_req.parse_args()
            playlist= Playlists.query.filter_by(id=id)
            if not playlist.first():
                abort(404, message="Playlist does not exists.")
            else:
                playlist.update(data)
                db.session.commit()
                return 200
    
    @marshal_with(playlist_fields)
    def delete(self, id=None):
        if id:
            playlist = Playlists.query.get(id)
            if not playlist:
                abort(404, message="Playlist does not exists.")
            db.session.delete(playlist)
            db.session.commit()
            return "Playlist deleted successfully.", 200
        else:
            abort(400, message="Please provide playlist id")

api.add_resource(UserAPI, '/api/users', '/api/users/<int:id>')
api.add_resource(AlbumAPI, '/api/albums', '/api/albums/<int:id>')
api.add_resource(SongAPI, '/api/songs', '/api/songs/<int:id>')
api.add_resource(PlaylistAPI, '/api/playlists', '/api/playlists/<int:id>')