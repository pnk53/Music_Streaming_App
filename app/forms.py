from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, SelectField, DateField, TextAreaField, TimeField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, Email, Length, InputRequired, EqualTo, NumberRange

#User SignUp form
class SignupForm(FlaskForm):
    fName = StringField("First Name: ", validators=[DataRequired(), InputRequired()])
    lName = StringField("Last Name: ")
    gender = SelectField("Gender: ", choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], default='', validators=[DataRequired(), InputRequired()])
    username = StringField("Username: ", validators=[DataRequired(), InputRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Email(), InputRequired()])
    password = PasswordField("Password: ", validators=[DataRequired(), InputRequired(), Length(min=8, max=15)])
    confirmPassword = PasswordField("Confirm Password: ", validators=[DataRequired(), InputRequired(), Length(min=8, max=15), EqualTo('password', message="Password does not match. Please check  again!")])
    signUp = SubmitField("Sign Up")

#Creator SignUp form
class CreatorSignupForm(FlaskForm):
    register = SelectField("Register as Creator ?", choices=[('','--- Select ---'), ('Yes','Yes'), ('No','No')], default='', validators=[DataRequired(), InputRequired()])
    confirmPassword = PasswordField("Confirm Your Passowrd", validators=[DataRequired(), Length(min=8, max=15)])
    signUp = SubmitField("Sign Up")
#user Login form
class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired(), InputRequired()])
    password = PasswordField("Password: ", validators=[DataRequired(), Length(min=8, max=15), InputRequired()])
    logIn = SubmitField("Log In")
    
#Forgot Password form
class ForgotPassForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email(), InputRequired()])
    submit = SubmitField("Submit")

#Search form
class SearchForm(FlaskForm):
    searchString = StringField("Search String", validators=[DataRequired()])
    search = SubmitField("Search")

#Create Album form
class AlbumForm(FlaskForm):
    aName = StringField("Album Name: ", validators=[DataRequired(), InputRequired()])
    aGenres = StringField("Genres: ", validators=[DataRequired(), InputRequired()])
    aDate = DateField("Date Created: ", validators=[DataRequired(), InputRequired()])
    create = SubmitField("Create Album")

#Upload Song form
class SongForm(FlaskForm):
    sName = StringField("Song Name: ", validators=[DataRequired(), InputRequired()])
    sGenre = StringField("Song Genre: ", validators=[DataRequired(), InputRequired()])
    sDuration = TimeField("Song Duration: ", validators=[DataRequired(), InputRequired()])
    sDate = DateField("Date Created: ", validators=[DataRequired(), InputRequired()])
    sAlbum = SelectField("Select Album: ", validators=[DataRequired(), InputRequired()])
    sFile = FileField("Upload song ", validators=[FileRequired(), FileAllowed(['mp3'], '.MP3 FILES ONLY')])
    sLyrics = TextAreaField("Upload Lyrics", validators=[DataRequired(), InputRequired()])
    upload = SubmitField("Upload Song")

#Create Playlist form
class PlaylistForm(FlaskForm):
    pName = StringField("Playlist Name: ", validators=[DataRequired()])
    create = SubmitField("Create Playlist")

#Rating form
class RatingForm(FlaskForm):
    currentRating = IntegerField("Rate: ", validators=[DataRequired(),InputRequired(), NumberRange(min=1,max=10,message="Invalid input")])
    rate = SubmitField("Rate")