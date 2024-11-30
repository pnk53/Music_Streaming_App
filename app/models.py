from app import db
from flask_login import UserMixin

#User table
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    u_userType = db.Column(db.String(50), nullable=False)
    u_status = db.Column(db.String(50), nullable=False)
    u_flag = db.Column(db.Integer(), nullable=False)
    u_fName = db.Column(db.String(100), nullable=False)
    u_lName = db.Column(db.String(100))
    u_gender = db.Column(db.String(50), nullable=False)
    u_username = db.Column(db.String(100), nullable=False, unique=True)
    u_email = db.Column(db.String(200), nullable=False)
    u_password = db.Column(db.String(1000), nullable=False)
    albums = db.relationship('Albums', backref='users')
    songs = db.relationship('Songs', backref='users')
    playlists = db.relationship('Playlists', backref='users')
    
    def __init__(self, u_userType, u_status, u_flag, u_fName, u_lName, u_gender, u_username, u_email, u_password):
        self.u_userType = u_userType
        self.u_status = u_status
        self.u_flag = u_flag
        self.u_fName = u_fName
        self.u_lName = u_lName
        self.u_gender = u_gender
        self.u_username = u_username
        self.u_email = u_email
        self.u_password = u_password

#Album table
class Albums(UserMixin, db.Model):
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    a_name = db.Column(db.String(100), nullable=False)
    a_artist = db.Column(db.String(50), nullable=False)
    a_genres = db.Column(db.String(50), nullable=False)
    a_date = db.Column(db.String(50), nullable=False)
    a_rating = db.Column(db.Integer())
    a_totalRaters = db.Column(db.Integer())
    a_flag = db.Column(db.Integer(), nullable=False)
    user_id = db.Column(db.Integer(),db.ForeignKey('users.id'),nullable=False)
    songs = db.relationship('Songs', backref='albums')
    
    def __init__(self, a_name, a_artist,a_genres, a_date, a_rating, a_totalRaters, a_flag, user_id):
        self.a_name = a_name
        self.a_artist = a_artist
        self.a_genres = a_genres
        self.a_date = a_date
        self.a_rating = a_rating
        self.a_totalRaters = a_totalRaters
        self.a_flag = a_flag
        self.user_id = user_id

#Song table
class Songs(UserMixin, db.Model):
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    s_name = db.Column(db.String(100), nullable=False)
    s_artist = db.Column(db.String(50), nullable=False)
    s_album = db.Column(db.String(100), nullable=False)
    s_genre = db.Column(db.String(50), nullable=False)
    s_duration = db.Column(db.String(50), nullable=False)
    s_date = db.Column(db.String(50), nullable=False)
    s_filePath = db.Column(db.String(100), nullable=False)
    s_lyrics = db.Column(db.Text(), nullable=False)
    s_rating = db.Column(db.Integer())
    s_totalRaters = db.Column(db.Integer())
    s_flag = db.Column(db.Integer(), nullable=False)
    s_plays = db.Column(db.Integer())
    album_id = db.Column(db.Integer(), db.ForeignKey('albums.id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),nullable=False)
    
    def __init__(self, s_name, s_artist, s_album, s_genre, s_duration, s_date, s_filepath, s_lyrics, s_rating, s_totalRaters, s_flag, s_plays, album_id, user_id):
        self.s_name = s_name
        self.s_artist = s_artist
        self.s_album = s_album
        self.s_genre = s_genre
        self.s_duration = s_duration
        self.s_date = s_date
        self.s_filePath = s_filepath
        self.s_lyrics = s_lyrics
        self.s_rating = s_rating
        self.s_totalRaters = s_totalRaters
        self.s_flag = s_flag
        self.s_plays = s_plays
        self.album_id = album_id
        self.user_id = user_id

#Playlist table
class Playlists(UserMixin, db.Model):
    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    p_name = db.Column(db.String(100), nullable=False)
    p_noOfTracks = db.Column(db.Integer(), nullable=False)
    songIds_list = db.Column(db.String(250))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),nullable=False)

    def __init__(self, p_name, p_noOfTracks, songIds_list, user_id):
        self.p_name = p_name
        self.p_noOfTracks = p_noOfTracks
        self.songIds_list = songIds_list
        self.user_id = user_id