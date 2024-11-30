import io
import random
from flask import flash, redirect, render_template, request, send_file, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import and_, or_
from app import app, login_manager, db
from app.forms import AlbumForm, CreatorSignupForm, ForgotPassForm, LoginForm, PlaylistForm, RatingForm, SearchForm, SignupForm, SongForm
from app.models import Albums, Playlists, Songs, Users
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import base64
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

#Provided Login Manager with loaded user
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

#Declaring list of status
Status=["Approved", "Pending", "Others", "Rejected"]

#Declaring flagged status
Flagged=[0,1]

#Declaring allowed extensions
Allowed_Extensions={'mp3'}

#Declaring path for songPath
Parent_path = "../../static/media/"

#Defining allowed song file
def allowed_song_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Allowed_Extensions

#Defining Search
def uni_search(searched):
    searchedList=[]
    likeSearched = "%" + searched + "%"
    songConditions=[Songs.s_name.like(likeSearched), Songs.s_genre.like(likeSearched), Songs.s_artist.like(likeSearched)]
    albumConditions=[Albums.a_name.like(likeSearched), Albums.a_genres.like(likeSearched), Albums.a_artist.like(likeSearched)]
    songs=Songs.query.filter(or_(*songConditions)).all()
    searchedList.append(songs)
    albums=Albums.query.filter(or_(*albumConditions)).all()
    searchedList.append(albums)
    return searchedList

# -------------------------- Start of pre-login routes --------------------------

#Non-Authorized routes: Index
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('accounts/index.html')

#Non-Authorized routes: User Login
@app.route('/userLogin', methods=['GET','POST'])
def userLogin():
    #Declare the LoginFrom
    form = LoginForm()
    if request.method == 'GET':
        return render_template('accounts/userLogin.html', form=form)
    else:
        if form.validate_on_submit():
            #Fetch data from user inputs and assign it to variables
            username=request.form.get('username')
            password=request.form.get('password')
            #Searching the database for user
            user = Users.query.filter_by(u_username=username).first()
            #Validating the user inputs against database
            if not user or not check_password_hash(user.u_password, password):
                flash('Please check your login credentials and try again.')
                return redirect(url_for('userLogin'))
            else:
                #Checking if the user is Listener
                if user.u_userType=='Listener' or user.u_userType=='Listener, Creator':
                    login_user(user)
                    flash('Logged in successfully.')
                    return redirect(url_for('userHome'))
                else:
                    flash('Invalid Login credentials !!')
                    return redirect(url_for('userLogin'))
        else:
            flash('Validation error. Please try again !!')
            return redirect(url_for('userLogin'))

#Non-Authorized routes: Admin Login
@app.route('/adminLogin', methods=['GET','POST'])
def adminLogin():
    #Declare the LoginFrom
    form = LoginForm()
    if request.method == 'GET':
        return render_template('accounts/adminLogin.html', form=form)
    else:
        if form.validate_on_submit():
            #Fetch data from user inputs and assign it to variables
            username=request.form.get('username')
            password=request.form.get('password')
            #Searching the database for user
            user = Users.query.filter_by(u_username=username).first()
            #Validating the user inputs against database
            if not user or not check_password_hash(user.u_password, password):
                flash('Please check your login credentials and try again.')
                return redirect(url_for('adminLogin'))
            else:
                #Checking if the user is admin
                if user.u_userType=='Admin':
                    #Checking if the status is approved
                    if user.u_status.lower()=='approved':
                        login_user(user)
                        flash('Logged in successfully.')
                        return redirect(url_for('adminHome'))
                    else:
                        flash('Approval Pending. Please try again in 3-4 days.')
                        return redirect(url_for('adminLogin'))
                else:
                    flash('Invalid Login credentials !!')
                    return redirect(url_for('adminLogin'))
        else:
            flash('Validation error. Please try again !!')
            return redirect(url_for('adminLogin'))

#Non-Authorized routes: Sign Up
@app.route('/signup/<string:userType>', methods=['GET','POST'])
def signUp(userType):
    #Declare the SignupForm
    form = SignupForm()
    if request.method == 'GET':
        return render_template('accounts/signUp.html', form=form, u=userType)
    else:
        if form.validate_on_submit():
            #Fetching data from user inputs and assign it to variables
            uType=userType
            uFlag=Flagged[0]
            fName=request.form.get('fName')
            lName=request.form.get('lName')
            gender=request.form.get('gender')
            username=request.form.get('username')
            email=request.form.get('email')
            password=request.form.get('password')
            confirmPassword=request.form.get('confirmPassword')
            #Checking if password and confirmPassword matches
            if password != confirmPassword:
                flash('Password & Confirm Password does not match. Try again.')
                return redirect(url_for('signUp',userType=uType))
            #Checking if the user already exists in the database
            user = Users.query.filter_by(u_username=username).first()
            if user:
                flash('User already exists !!')
                return redirect(url_for('signUp',userType=uType))
            #Checking the type of user and thereby assigning appropriate status
            if uType.lower() == 'listener':
                status=Status[2]
            else:
                status=Status[0]     
            #Creating new User object using fetched data
            new_user = Users(u_userType=uType, u_status=status, u_flag=uFlag, u_fName=fName, u_lName=lName, u_gender=gender, u_username=username, u_email=email, u_password=generate_password_hash(password, method='scrypt', salt_length=16))
            #Adding new user to database
            db.session.add(new_user)
            db.session.commit()
            playlistUser = Users.query.filter_by(u_username=username).first()
            if playlistUser.u_userType=="Listener":
                likedPlaylist="Liked Songs"
                dislikedPlaylist="Disliked Songs"
                playlistUserId = playlistUser.id
                newLikedPlaylist = Playlists(p_name=likedPlaylist,p_noOfTracks=0,songIds_list="",user_id=playlistUserId)
                newDislikedPlaylist = Playlists(p_name=dislikedPlaylist,p_noOfTracks=0,songIds_list="",user_id=playlistUserId)
                db.session.add(newLikedPlaylist)
                db.session.add(newDislikedPlaylist)
                db.session.commit()
            flash('User signed up successfully')
            return redirect(url_for('index'))
        else:
            flash('Validation error. Please try again !!')
            return redirect(url_for('signUp',userType=userType))

#Non-Authorized routes: Forgot Password
@app.route('/forgotPassword', methods=['GET', 'POST'])
def forgot():
    #Declare the ForgotPassForm
    form = ForgotPassForm()
    if request.method == 'GET':
        return render_template('utils/forgotPassword.html', form=form)
    else:
        if form.validate_on_submit():
            email=request.form.get('email')           
            #Searching the database for registered email
            user = Users.query.filter_by(u_email=email).first()
            if not user:
                flash('Invalid Email. No users found.')
                return redirect(url_for('forgot'))
            return render_template('utils/forgotPassword.html', email=email)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('forgot'))

# -------------------------- End of pre-login routes -------------------------

# -------------------------- Start of Admin Home and Analytics Routes --------------------------

#Authorized routes: Admin Home page
@app.route('/adminHome', methods=['GET', 'POST'])
@login_required
def adminHome():
    if request.method == 'GET':
        userCount=Users.query.filter(Users.u_userType.like('%Listener%')).count()
        creatorCount=Users.query.filter(Users.u_userType.like('%Creator%')).count()
        songs=Songs.query.all()
        songCount=len(songs)
        albums=Albums.query.all()
        albumCount=len(albums)
        genreCount=Songs.query.with_entities(Songs.s_genre).distinct().count()
        pendingAdmin=Users.query.filter(and_(Users.u_status=="Pending", Users.u_userType=="Admin")).all()
        pendingCreator=Users.query.filter(and_(Users.u_status=="Pending", Users.u_userType=="Listener")).all()
        return render_template('admin/adminHome.html',aH="active text-primary", sCount=songCount, aCount=albumCount, gCount=genreCount, uCount=userCount, cCount=creatorCount, pendingAReq=pendingAdmin, pendingCReq=pendingCreator)

#Authorized routes: Approve user request
@app.route('/approveRequest/<string:username>', methods=['GET', 'POST'])
@login_required
def approveRequest(username):
    if request.method == 'GET':
        #Searching the database for user's details
        user = Users.query.filter_by(u_username=username).first()
        if user.u_userType == 'Admin':
            user.u_status = Status[0]
            db.session.commit()
            message = "Admin request approved for " + str(username) + "."
            flash(message)
            return redirect(url_for('adminHome'))

#Authorized routes: Reject user request
@app.route('/rejectRequest/<string:username>', methods=['GET','POST'])
@login_required
def rejectRequest(username):
    if request.method == 'GET':
        #Searching database for user's details
        user = Users.query.filter_by(u_username=username).first()
        user.u_status = Status[3]
        db.session.commit()
        message = "Request rejected for " + str(username) + " ."
        flash(message)
        return redirect(url_for('adminHome'))

#Authorized routes: Admin analytics
@app.route('/analytics', methods=['GET','POST'])
@login_required
def analytics():
    if request.method=='GET':
        return render_template('/admin/analytics.html',aAN="active text-warning")

#Authorized routes: Admin Analytics
@app.route('/analyticsChart', methods=['GET','POST'])
@login_required
def Chart():
    topSongList = Songs.query.order_by(Songs.s_rating.desc()).limit(10).all()
    songsNameAndRating = {}
    for s in topSongList:
        songsNameAndRating[s.s_name]=s.s_rating
    keyList=list(songsNameAndRating.keys())
    random.shuffle(keyList)
    valueList=[]
    for i in keyList:
        valueList.append(songsNameAndRating[i])
    fig,ax=plt.subplots(figsize=(20,10))
    ax= sns.set(style='darkgrid')
    sns.barplot(x=valueList,y=keyList)
    plt.ylabel('Songs Name')
    plt.xlabel('Rating')
    canvas = FigureCanvas(fig)
    img=io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img,mimetype='img/png')




# -------------------------- End of Admin Home and Analytics Routes --------------------------

# -------------------------- Start of Admin Track Routes --------------------------

#Authorized routes: Admin all Tracks 
@app.route('/allTracks', methods=['GET','POST'])
@login_required
def allTracks():
    #Defining searchForm
    form = SearchForm()
    songs=Songs.query.filter(Songs.s_flag==Flagged[0]).order_by(Songs.s_rating.desc()).all()
    flaggedSongs=Songs.query.filter(Songs.s_flag==Flagged[1]).all()
    if request.method == 'GET':
        searchedSongsList=[]
        return render_template('admin/allTracks.html', aT="active text-info", form=form, sSL=searchedSongsList, sList=songs, sFList=flaggedSongs)
    else:
        if form.validate_on_submit():
            searched = request.form.get('searchString')
            searchedSongsList = uni_search(searched)
            if not searchedSongsList[0] and not searchedSongsList[1]:
                searchedSongsList.pop()
                searchedSongsList.pop()
                searchedSongsList.append("No Search Results")
            return render_template('admin/allTracks.html', aT="active text-info", form=form, sSL=searchedSongsList, sList=songs, sFList=flaggedSongs)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('allTracks'))

#Authorized routes: Admin flag song
@app.route('/flagSong/<int:sid>', methods=['GET','POST'])
@login_required
def flagSong(sid):
    if request.method=='GET':
        cSong = Songs.query.get(sid)
        cSong.s_flag=Flagged[1]
        db.session.commit()
        flash('Successfully flagged the song.')
        return redirect(url_for('allTracks'))

#Authorized routes: Admin unFlag song
@app.route('/unFlagSong/<int:sid>', methods=['GET','POST'])
@login_required
def unFlagSong(sid):
    if request.method=='GET':
        cSong = Songs.query.get(sid)
        cSong.s_flag=Flagged[0]
        db.session.commit()
        flash('Successfully unflagged the song.')
        return redirect(url_for('allTracks'))

# -------------------------- End of Admin Track Routes --------------------------

# -------------------------- Start of Admin Album Routes --------------------------

#Authorized routes: Admin all albums
@app.route('/allAlbums', methods=['GET','POST'])
@login_required
def allAlbums():
    #Defining searchForm
    form = SearchForm()
    albums=Albums.query.filter(Albums.a_flag==Flagged[0]).order_by(Albums.a_rating.desc()).all()
    flaggedAlbums=Albums.query.filter(Albums.a_flag==Flagged[1]).all()
    if request.method == 'GET':
        searchedSongsList=[]
        return render_template('admin/allAlbums.html', aA="active text-success", form=form, sSL=searchedSongsList, aList=albums, aFList=flaggedAlbums)
    else:
        if form.validate_on_submit():
            searched = request.form.get('searchString')
            searchedSongsList = uni_search(searched)
            if not searchedSongsList[0] and not searchedSongsList[1]:
                searchedSongsList.pop()
                searchedSongsList.pop()
                searchedSongsList.append("No Search Results")
            return render_template('admin/allAlbums.html', aA="active text-success", form=form, sSL=searchedSongsList, aList=albums, aFList=flaggedAlbums)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('allTracks'))

#Authorized routes: Admin flag album
@app.route('/flagAlbum/<int:aid>', methods=['GET','POST'])
@login_required
def flagAlbum(aid):
    if request.method=='GET':
        cAlbum = Albums.query.get(aid)
        cAlbum.a_flag=Flagged[1]
        songs = Songs.query.filter_by(album_id=aid).all()
        for s in songs:
            s.s_flag=Flagged[1]
        db.session.commit()
        flash('Successfully flagged the album and its songs.')
        return redirect(url_for('allAlbums'))

#Authorized routes: Admin unFlag song
@app.route('/unFlagAlbum/<int:aid>', methods=['GET','POST'])
@login_required
def unFlagAlbum(aid):
    if request.method=='GET':
        cAlbum = Albums.query.get(aid)
        cAlbum.a_flag=Flagged[0]
        songs = Songs.query.filter_by(album_id=aid).all()
        for s in songs:
            s.s_flag=Flagged[0]
        db.session.commit()
        flash('Successfully unflagged the album and its songs.')
        return redirect(url_for('allAlbums'))

# -------------------------- End of Admin Album Routes --------------------------

# -------------------------- Start of Admin User Routes --------------------------

#Authorized routes: Admin all users
@app.route('/allUsers', methods=['GET','POST'])
@login_required
def allUsers():
    users=Users.query.filter(and_(Users.u_userType.like("%Creator%"),Users.u_flag==Flagged[0])).all()
    flaggedUsers=Users.query.filter(and_(Users.u_userType.like("%Creator%"),Users.u_flag==Flagged[1])).all()
    if request.method=='GET':
        return render_template('/admin/allUsers.html', aU="active text-primary", uList=users, uFList=flaggedUsers)

#Authorized routes: Admin flag user
@app.route('/flagUser/<int:uid>', methods=['GET','POST'])
@login_required
def flagUser(uid):
    if request.method=='GET':
        cUser = Users.query.get(uid)
        cUser.u_flag=Flagged[1]
        albums = Albums.query.filter_by(user_id=uid).all()
        for a in albums:
            a.a_flag=Flagged[1]
            songs = Songs.query.filter_by(album_id=a.id).all()
            for s in songs:
                s.s_flag=Flagged[1]
        db.session.commit()
        flash('Successfully flagged the user and his albums and songs.')
        return redirect(url_for('allUsers'))

#Authorized routes: Admin unFlag user
@app.route('/unFlagUser/<int:uid>', methods=['GET','POST'])
@login_required
def unFlagUser(uid):
    if request.method=='GET':
        cUser = Users.query.get(uid)
        cUser.u_flag=Flagged[0]
        albums = Albums.query.filter_by(user_id=uid).all()
        for a in albums:
            a.a_flag=Flagged[0]
            songs = Songs.query.filter_by(album_id=a.id).all()
            for s in songs:
                s.s_flag=Flagged[0]
        db.session.commit()
        flash('Successfully unflagged the user and his albums and songs.')
        return redirect(url_for('allUsers'))

#Authorized routes: Admin delete user
@app.route('/deleteUser/<int:uid>', methods=['GET','POST'])
@login_required
def deleteUser(uid):
    if request.method=='GET':
        cUser = Users.query.get(uid)
        cPlaylists = Playlists.query.filter_by(user_id=cUser.id).all()
        if cPlaylists:
            for p in cPlaylists:
                db.session.delete(p)
        cSongs = Songs.query.filter_by(user_id=cUser.id).all()
        if cSongs:
            for s in cSongs:
                db.session.delete(s)
        cAlbums = Albums.query.filter_by(user_id=cUser.id).all()
        if cAlbums:
            for a in cAlbums:
                db.session.delete(a)
        db.session.delete(cUser)
        db.session.commit()
        flash('User deleted successfully')
        return redirect(url_for('allUsers'))

# -------------------------- End of Admin User Routes --------------------------

# -------------------------- Start of Listener Home and Explore Routes --------------------------

#Authorized routes: Listener Home page
@app.route('/userHome', methods=['GET', 'POST'])
@login_required
def userHome():
    #Declare the searchForm
    form = SearchForm()
    playlists=Playlists.query.filter_by(user_id=current_user.id).limit(5).all()
    songs=Songs.query.order_by(Songs.s_plays.desc()).limit(5).all()
    currentPath=None
    lyrics=None
    relatedList=None
    searchedSongsList=[]
    currentSong = "Song Name"
    currentArtist = "Artist Name"
    if request.method == 'GET':
        return render_template('user/userHome.html', uH="active text-primary", form=form,cSId=0, p=playlists, s=songs, cPath=currentPath, songL=lyrics,related=relatedList,sSL=searchedSongsList, song=currentSong, artist=currentArtist)
    else:
        if form.validate_on_submit():
            searched = request.form.get('searchString')
            searchedSongsList = uni_search(searched)
            if not searchedSongsList[0] and not searchedSongsList[1]:
                searchedSongsList.pop()
                searchedSongsList.pop()
                searchedSongsList.append("No Search Results")
            return render_template('user/userHome.html', uH="active text-primary", form=form,cSId=0, p=playlists, s=songs, cPath=currentPath, songL=lyrics,related=relatedList,sSL=searchedSongsList, song=currentSong, artist=currentArtist)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('userHome'))

#Authorized routes: user play music
@app.route('/userHome/playSong/<int:sid>', methods=['GET','POST'])
@login_required
def playSong(sid):
    #Declare the searchForm
    form = SearchForm()
    if request.method == 'GET':
        playlists=Playlists.query.filter_by(user_id=current_user.id).limit(5).all()
        songs=Songs.query.limit(5).all()
        cSong = Songs.query.filter_by(id=sid).first()
        relatedList=[]
        sameArtistSongs=Songs.query.filter_by(user_id=cSong.user_id).limit(3).all()
        for s in sameArtistSongs:
            relatedList.append(s)
        sameGenreSongs=Songs.query.filter(Songs.s_genre.like("%" + cSong.s_genre + "%")).limit(3).all()
        for s in sameGenreSongs:
            if s not in relatedList:
                relatedList.append(s)
        topSongList = Songs.query.order_by(Songs.s_rating.desc()).limit(2).all()
        for s in topSongList:
            if s not in relatedList:
                relatedList.append(s)
        searchedSongsList=[]
        currentPath = cSong.s_filePath
        currentLyrics = cSong.s_lyrics
        currentSong = cSong.s_name
        currentArtist = cSong.s_artist
        cSong.s_plays +=1
        db.session.commit()
        return render_template('user/userHome.html',uH="active text-primary", form=form,sSL=searchedSongsList, cSId=cSong.id, p=playlists, s=songs, cPath=currentPath, song=currentSong, artist=currentArtist, songL = currentLyrics, related=relatedList)

#Authorized routes: Listener Explore page
@app.route('/explore', methods=['GET', 'POST'])
@login_required
def exploreMusic():
    #Declare the searchForm
    form = SearchForm()
    songsList = Songs.query.all()
    albumList = Albums.query.all()  
    if request.method == 'GET':
        searchedSongsList=[]
        return render_template('/user/explore.html', uE="active text-info", form=form, sSL=searchedSongsList, sList=songsList, aList=albumList)
    else:
        if form.validate_on_submit():
            searched = request.form.get('searchString')
            searchedSongsList = uni_search(searched)
            if not searchedSongsList[0] and not searchedSongsList[1]:
                searchedSongsList.pop()
                searchedSongsList.pop()
                searchedSongsList.append("No Search Results")
            return render_template('/user/explore.html', uE="active text-info", form=form, sSL=searchedSongsList, sList=songsList, aList=albumList)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('exploreMusic'))

# -------------------------- End of Listener Home and Explore Routes --------------------------

# -------------------------- Start of Listener's Album and Song Management Routes --------------------------

#Authorized routes: Listener Album Details page
@app.route('/albumDetails/<int:aid>', methods=['GET','POST'])
@login_required
def albumDetails(aid):
    #Declare the RatingForm
    form = RatingForm()
    album = Albums.query.get(aid)
    if request.method == 'GET':
        songList = Songs.query.filter_by(album_id=aid).all()
        return render_template('/user/albumDetails.html', form=form, a=album, songsData = songList)
    else:
        if form.validate_on_submit():
            newRating = request.form.get('currentRating')
            overallRating =int(album.a_rating)
            totalRater = int(album.a_totalRaters)
            finalOverallRating = ((overallRating * totalRater) + int(newRating)) / (totalRater + 1)
            album.a_rating = finalOverallRating
            album.a_totalRaters+=1
            db.session.commit()
            return redirect(url_for('albumDetails', aid=album.id))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('albumDetails',aid=aid))

#Authorized routes: Listener Song Details page
@app.route('/songDetails/<int:sid>', methods=['GET','POST'])
@login_required
def songDetails(sid):
    #Declare the RatingForm
    form = RatingForm()
    song = Songs.query.get(sid)
    if request.method == 'GET':
        l="No"
        d="No"
        if current_user.u_userType == "Admin":
            return render_template('/user/songDetails.html', form=form, s=song, liked=l, disliked=d)
        else:
            likePlaylist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Liked Songs")).first()
            dislikePlaylist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Disliked Songs")).first()
            if str(sid) in likePlaylist.songIds_list:
                l="Yes"
            if str(sid) in dislikePlaylist.songIds_list:
                d="Yes"
            return render_template('/user/songDetails.html', form=form, s=song, liked=l, disliked=d)
    else:
        if form.validate_on_submit():
            newRating = request.form.get('currentRating')
            overallRating =int(song.s_rating)
            totalRater = int(song.s_totalRaters)
            finalOverallRating = ((overallRating * totalRater) + int(newRating)) / (totalRater + 1)
            song.s_rating = finalOverallRating
            song.s_totalRaters+=1
            db.session.commit()
            return redirect(url_for('songDetails', sid=song.id))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('songDetails',sid=sid))

#Authorized routes: Listener like song
@app.route('/likeSong/<int:sid>', methods=['GET','POST'])
@login_required
def likeSong(sid):
    c_playlist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Liked Songs")).first()
    if request.method == 'GET':
        if not c_playlist.songIds_list:
                c_playlist.songIds_list=str(sid)
                c_playlist.p_noOfTracks+=1
        else:
            tempString = "," + str(sid)
            c_playlist.songIds_list+=tempString
            c_playlist.p_noOfTracks+=1
        db.session.commit()
        return redirect(url_for('songDetails',sid=sid))

#Authorized routes: Listener unlike Song
@app.route('/unlikeSong/<int:sid>', methods=['GET','POST'])
@login_required
def unlikeSong(sid):
    c_playlist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Liked Songs")).first()
    if request.method == 'GET':
        if len(c_playlist.songIds_list) == 1:
            c_playlist.songIds_list=""
            c_playlist.p_noOfTracks-=1
        else:
            if c_playlist.songIds_list[0] == str(sid):
                tempString=str(str(sid)+",")
            else:    
                tempString=str(","+str(sid))
            c_playlist.songIds_list = c_playlist.songIds_list.replace(tempString,'')
            c_playlist.p_noOfTracks-=1
        db.session.commit()
        return redirect(url_for('songDetails',sid=sid))

#Authorized routes: Listener dislike song
@app.route('/dislikeSong/<int:sid>', methods=['GET','POST'])
@login_required
def dislikeSong(sid):
    c_playlist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Disliked Songs")).first()
    if request.method == 'GET':
        if not c_playlist.songIds_list:
                c_playlist.songIds_list=str(sid)
                c_playlist.p_noOfTracks+=1
        else:
            tempString = "," + str(sid)
            c_playlist.songIds_list+=tempString
            c_playlist.p_noOfTracks+=1
        db.session.commit()
        return redirect(url_for('songDetails',sid=sid))

#Authorized routes: Listener unDislike Song
@app.route('/unDislikeSong/<int:sid>', methods=['GET','POST'])
@login_required
def unDislikeSong(sid):
    c_playlist = Playlists.query.filter(and_(Playlists.user_id==current_user.id,Playlists.p_name=="Disliked Songs")).first()
    if request.method == 'GET':
        if len(c_playlist.songIds_list) == 1:
            c_playlist.songIds_list=""
            c_playlist.p_noOfTracks-=1
        else:
            if c_playlist.songIds_list[0] == str(sid):
                tempString=str(str(sid)+",")
            else:    
                tempString=str(","+str(sid))
            c_playlist.songIds_list = c_playlist.songIds_list.replace(tempString,'')
            c_playlist.p_noOfTracks-=1
        db.session.commit()
        return redirect(url_for('songDetails',sid=sid))

# -------------------------- End of Listener's Album and Song Management Routes --------------------------

# -------------------------- Start of Listener's Playlist Management Routes --------------------------

#Authorized routes: Listener Playlist page
@app.route('/playlists', methods=['GET','POST'])
@login_required
def playlists():
    #Declare the playListForm
    form = PlaylistForm()
    if request.method == 'GET':
        allPlaylists = Playlists.query.filter_by(user_id=current_user.id).all()
        return render_template('/user/playlists.html',uP="active text-warning", form=form, p_list=allPlaylists)
    else:
        if form.validate_on_submit():
            pName = request.form.get('pName')
            addedSongsList = ""
            playlist = Playlists.query.filter(and_(Playlists.p_name==pName, Playlists.user_id==current_user.id)).first()
            if playlist:
                flash('Playlist already exists.')
                return redirect(url_for('playlists'))
            else:
                new_playlist = Playlists(p_name=pName, p_noOfTracks=0, songIds_list=addedSongsList, user_id=current_user.id)
                db.session.add(new_playlist)
                db.session.commit()
                flash('Playlist created successfully.')
                return redirect(url_for('playlists'))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('playlists'))

#Authorized routes: Listener playlist view/edit
@app.route('/viewEditPlaylist/<int:vEId>', methods=['GET','POST'])
@login_required
def viewEditPlaylist(vEId):
    if request.method == 'GET':
        allSongs=[]
        allSongsList = Songs.query.all()
        songList=[]
        c_playlist = Playlists.query.get(vEId)
        if not c_playlist.songIds_list:
            songList=[]
        else:
            tempList = c_playlist.songIds_list.split(',')
            for t in tempList:
                song = Songs.query.get(int(t))
                if song:
                    songList.append(song)
                else:
                    if len(tempList) == 1:
                        c_playlist.songIds_list=""
                        c_playlist.p_noOfTracks-=1
                    else:
                        if tempList[0] == str(t):
                            tempString=str(str(t)+",")
                        else:    
                            tempString=str(","+str(t))
                        c_playlist.songIds_list = c_playlist.songIds_list.replace(tempString,'')
                        c_playlist.p_noOfTracks-=1
                        db.session.commit()
        for s in allSongsList:
            if s not in songList:
                allSongs.append(s)
        return render_template('/user/viewEditPlaylist.html', c_p=c_playlist, songsData=songList, allSongsData=allSongs)

#Authorized routes: Listener playlist add songs
@app.route('/addSongToPlaylist/<int:pid>/<int:sid>', methods=['GET','POST'])
@login_required
def addSongToPlaylist(pid,sid):
    if request.method == 'GET':
        c_playlist = Playlists.query.get(pid)
        if not c_playlist.songIds_list:
            c_playlist.songIds_list=str(sid)
            c_playlist.p_noOfTracks+=1
        else:
            tempString = "," + str(sid)
            c_playlist.songIds_list+=tempString
            c_playlist.p_noOfTracks+=1
        db.session.commit()
        flash('Song added to playlist successfully.')
        return redirect(url_for('viewEditPlaylist',vEId=pid))

#Authorized routes: Listener playlist remove song
@app.route('/removeFromPlaylist/<int:pid>/<int:sid>')
@login_required
def removeFromPlaylist(pid,sid):
    if request.method == 'GET':
        c_playlist = Playlists.query.get(pid)
        if len(c_playlist.songIds_list) == 1:
            c_playlist.songIds_list=""
            c_playlist.p_noOfTracks-=1
        else:
            if c_playlist.songIds_list[0] == str(sid):
                tempString=str(str(sid)+",")
            else:    
                tempString=str(","+str(sid))
            c_playlist.songIds_list = c_playlist.songIds_list.replace(tempString,'')
            c_playlist.p_noOfTracks-=1
        db.session.commit()
        flash('Song successfully removed from playlist.')
        return redirect(url_for('viewEditPlaylist',vEId=pid))

#Authorized routes: Listener delete playlist
@app.route('/deletePlaylist/<int:pid>', methods=['GET','POST'])
@login_required
def deletePlaylist(pid):
    if request.method == 'GET':
        c_playlist = Playlists.query.get(pid)
        db.session.delete(c_playlist)
        db.session.commit()
        flash('Playlist deleted successfully.')
        return redirect(url_for('playlists'))

# -------------------------- End of Listener's Album and Song Management Routes --------------------------

# -------------------------- Start of Creator's Home and Uploads Routes --------------------------

#Authorized routes: Creator Home page
@app.route('/creatorHome', methods=['GET', 'POST'])
@login_required
def creatorHome():
    #Declare the creatorSignupForm
    form = CreatorSignupForm()
    if request.method == 'GET':
        if current_user.u_flag == Flagged[1]:
            flash('You have been flagged. Please reach out to admin.')
            return redirect(url_for('userHome'))
        else:
            topSongList = Songs.query.filter_by(user_id=current_user.id).order_by(Songs.s_rating.desc()).limit(5).all()
            albumCount = Albums.query.filter_by(user_id=current_user.id).count()
            songsList = Songs.query.filter_by(user_id=current_user.id).all()
            songCount = len(songsList)
            sum=0
            for s in songsList:
                sum+=s.s_rating
            if songCount==0:
                avgRating="NA"
            else:
                avgRating = sum/songCount
            return render_template('creator/creatorHome.html', cH="active text-success", form=form, aCount=albumCount, sCount=songCount, avg=avgRating, tSongs=topSongList)
    else:
        if form.validate_on_submit():
            response = request.form.get('register')
            password = request.form.get('confirmPassword')
            #Searching database for current user's details
            user = Users.query.filter_by(id=current_user.id).first()
            if response.lower()=="no":
                flash('Still want to register ? Please select "Yes" as a response.')
                return redirect(url_for('creatorHome'))
            else:
                if check_password_hash(user.u_password, password):
                    user.u_status = Status[0]
                    user.u_userType += str(", Creator")
                    db.session.commit()
                    flash('Creator sign up successful.')
                    return redirect(url_for('creatorHome'))
                else:
                    flash('Please check your password and try again !!')
                    return redirect(url_for('creatorHome'))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('creatorHome'))

#Authorized routes: Your uploads
@app.route('/yourUploads', methods=['GET','POST'])
@login_required
def creatorUploads():
    #Declare searchForm
    form = SearchForm()
    albums = Albums.query.filter_by(user_id=current_user.id).all()
    songs = Songs.query.filter_by(user_id=current_user.id).all()
    searchedSongsList=[]
    if request.method == 'GET':
        return render_template('creator/yourUploads.html', cYU="active text-primary", form=form,sSL=searchedSongsList, albumsData=albums, songsData=songs)
    else:
        if form.validate_on_submit():
            searched = request.form.get('searchString')
            searchedSongsList = uni_search(searched)
            tempS,tempA=[],[]
            for s in searchedSongsList[0]:
                if s.user_id == current_user.id:
                    tempS.append(s)
            for a in searchedSongsList[1]:
                if a.user_id == current_user.id:
                    tempA.append(a)
            searchedSongsList.clear()
            searchedSongsList.append(tempS)
            searchedSongsList.append(tempA)
            if not searchedSongsList[0] and not searchedSongsList[1]:
                searchedSongsList.pop()
                searchedSongsList.pop()
                searchedSongsList.append("No Search Results")
            return render_template('creator/yourUploads.html', cYU="active text-primary", form=form,sSL=searchedSongsList, albumsData=albums, songsData=songs)
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('creatorUploads'))

# -------------------------- End of Creator's Home and Uploads Routes --------------------------

# -------------------------- Start of Creator's Album Management Routes --------------------------

#Authorized routes: upload album
@app.route('/uploadAlbum', methods=['GET','POST'])
@login_required
def uploadAlbum():
    #Declare the AlbumForm
    form = AlbumForm()
    artistName = current_user.u_fName + ' ' + current_user.u_lName
    if request.method == 'GET':
        return render_template('creator/uploadAlbum.html', cUA="active text-success", form=form, artist=artistName)
    else:
        if form.validate_on_submit():
            albumName = request.form.get('aName')
            albumGenres = request.form.get('aGenres')
            dateCreated = request.form.get('aDate')
            new_album = Albums(a_name=albumName, a_artist=artistName, a_genres=albumGenres, a_date=dateCreated, user_id=current_user.id, a_rating=0, a_totalRaters=0, a_flag=Flagged[0])
            db.session.add(new_album)
            db.session.commit()
            flash('Album created successfully.')
            return redirect(url_for('creatorHome'))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('uploadAlbum'))

#Authorized routes: View Album
@app.route('/viewAlbum/<int:aid>', methods=['GET','POST'])
@login_required
def viewUpdateAlbum(aid):
    #Declare AlbumForm
    form = AlbumForm()
    if request.method == 'GET':
        songsList = Songs.query.filter_by(album_id=aid).all()
        album = Albums.query.get(aid)
        return render_template('creator/updateAlbum.html', form=form, s=True, songsData=songsList, a=album)

#Authorized routes: Update Album
@app.route('/updateAlbum/<int:aid>', methods=['GET','POST'])
@login_required
def updateAlbum(aid):
    #Declare AlbumForm
    form = AlbumForm()
    album = Albums.query.get(aid)
    if request.method == 'GET':
        songsList = Songs.query.filter_by(album_id=aid).all()
        return render_template('creator/updateAlbum.html', form=form, s=False, songsData=songsList, a=album)
    else:
        if form.validate_on_submit():
            albumName = request.form.get('aName')
            albumGenres = request.form.get('aGenres')
            dateCreated = request.form.get('aDate')
            #Updating the fields in database
            album.a_name = albumName
            album.a_genres = albumGenres
            album.a_date = dateCreated
            db.session.commit()
            flash('Album Updated successfully.')
            return redirect(url_for('viewUpdateAlbum', aid=aid))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('updateAlbum',aid=aid))

#Authorized routes: Delete Album
@app.route('/deleteAlbum/<int:aid>', methods=['GET','POST'])
@login_required
def deleteAlbum(aid):
    if request.method == 'GET':
        album = Albums.query.get(aid)
        db.session.delete(album)
        db.session.commit()
        flash('Album delete successfully')
        if current_user.u_userType=='Admin':
            return redirect(url_for('allAlbums'))
        else:
            return redirect(url_for('creatorHome'))

# -------------------------- End of Creator's Album Management Routes --------------------------

# -------------------------- Start of Creator's Song Management Routes --------------------------

#Authorized routes: upload song
@app.route('/uploadSong', methods=['GET','POST'])
@login_required
def uploadSong():
    #Declare SongForm
    form = SongForm()
    artistName = current_user.u_fName + ' ' + current_user.u_lName
    albums = Albums.query.filter_by(user_id=current_user.id).all()
    album_list=[(i.a_name,i.a_name) for i in albums]
    form.sAlbum.choices = album_list
    if request.method == 'GET':
        return render_template('creator/uploadSong.html', cUS="active text-info", form=form, artist=artistName)
    else:
        if form.validate_on_submit():
            songName = request.form.get('sName')
            songArtist = artistName
            songAlbum = request.form.get('sAlbum')
            songGenre = request.form.get('sGenre')
            songDuration = request.form.get('sDuration')
            songDate = request.form.get('sDate')
            songRating = 0
            songPlays = 0
            user_id = current_user.id
            #Searching the albums database with songAlbum name to get it's id
            album = Albums.query.filter_by(a_name=songAlbum).first()
            album_id = album.id
            songFile = request.files['sFile']
            name = current_user.u_fName[0] + current_user.u_lName[0] + '_' + songName + '.mp3'
            name = name.replace(' ', '_')
            if songFile and allowed_song_file(songFile.filename):
                songFile.filename = name
                filename = secure_filename(songFile.filename)
                songFile.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            songLyrics = request.form.get('sLyrics')
            songFilePath = Parent_path + name
            new_song=Songs(s_name=songName, s_artist=songArtist, s_album=songAlbum, s_genre=songGenre, s_duration=songDuration, s_date=songDate, s_filepath=songFilePath, s_lyrics=songLyrics, s_rating=songRating, s_totalRaters=0, s_flag=Flagged[0], s_plays=songPlays, user_id=user_id, album_id=album_id)
            db.session.add(new_song)
            db.session.commit()
            flash("Song uploaded successfully.")
            return redirect(url_for('creatorHome'))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('uploadSong'))

#Authorized routes: Add song to specific album
@app.route('/uploadSong/album/<int:aid>', methods=['GET','POST'])
@login_required
def addSongAlbum(aid):
    #Declare SongForm
    form = SongForm()
    artistName = current_user.u_fName + ' ' + current_user.u_lName
    albums = Albums.query.get(aid)
    album_list=[(albums.a_name,albums.a_name)]
    form.sAlbum.choices = album_list
    if request.method == 'GET':
        return render_template('creator/uploadSong.html', cUS="active text-info", form=form, artist=artistName)
    else:
        if form.validate_on_submit():
            songName = request.form.get('sName')
            songArtist = artistName
            songAlbum = request.form.get('sAlbum')
            songGenre = request.form.get('sGenre')
            songDuration = request.form.get('sDuration')
            songDate = request.form.get('sDate')
            songRating = 0
            songPlays = 0
            user_id = current_user.id
            album_id = aid
            songFile = request.files['sFile']
            name = current_user.u_fName[0] + current_user.u_lName[0] + '_' + songName + '.mp3'
            name = name.replace(' ', '_')
            if songFile and allowed_song_file(songFile.filename):
                songFile.filename = name
                filename = secure_filename(songFile.filename)
                songFile.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename))
            songLyrics = request.form.get('sLyrics')
            songFilePath = Parent_path + name
            new_song=Songs(s_name=songName, s_artist=songArtist, s_album=songAlbum, s_genre=songGenre, s_duration=songDuration, s_date=songDate, s_filepath=songFilePath, s_lyrics=songLyrics, s_rating=songRating, s_totalRaters=0, s_flag=Flagged[0], s_plays=songPlays, user_id=user_id, album_id=album_id)
            db.session.add(new_song)
            db.session.commit()
            flash("Song uploaded successfully.")
            return redirect(url_for('creatorHome'))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('uploadSong'))

#Authorized routes: View Song
@app.route('/viewSong/<int:sid>', methods=['GET','POST'])
@login_required
def viewUpdateSong(sid):
    #Declare AlbumForm
    form = SongForm()
    song = Songs.query.get(sid)
    album_list=[(song.s_album,song.s_album)]
    form.sAlbum.choices = album_list
    form.sLyrics.data = song.s_lyrics
    if request.method == 'GET':
        return render_template('creator/updateSong.html', form=form, s=True, sData=song)

#Authorized routes: Update Song
@app.route('/updateSong/<int:sid>', methods=['GET','POST'])
@login_required
def updateSong(sid):
    #Declare AlbumForm
    form = SongForm()
    song = Songs.query.get(sid)
    albums = Albums.query.filter_by(user_id=current_user.id).all()
    album_list=[(i.a_name,i.a_name) for i in albums]
    form.sAlbum.choices = album_list
    form.sLyrics.data = song.s_lyrics
    form.sFile.validators=()
    if request.method == 'GET':
        return render_template('creator/updateSong.html', form=form, s=False, sData=song)
    else:
        if form.validate_on_submit():
            songName = request.form.get('sName')
            songAlbum = request.form.get('sAlbum')
            songGenre = request.form.get('sGenre')
            songDuration = request.form.get('sDuration')
            songDate = request.form.get('sDate')
            songLyrics = request.form.get('sLyrics')
            song.s_name = songName
            song.s_album = songAlbum
            song.s_genre = songGenre
            song.s_duration = songDuration
            song.s_date = songDate
            song.s_lyrics = songLyrics
            db.session.commit()
            flash('Song update successfully.')
            return redirect(url_for('viewUpdateSong', sid=sid))
        else:
            flash('Validation error. Try again !!')
            return redirect(url_for('updateSong',sid=sid))

#Authorized routes: Delete Song
@app.route('/deleteSong/<int:sid>', methods=['GET','POST'])
@login_required
def deleteSong(sid):
    if request.method == 'GET':
        song = Songs.query.get(sid)
        filename= song.s_filePath.split('/')[-1]
        path=os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(path):
            os.remove(path)
        else:
            flash('File does not exists')
            if current_user.u_userType=="Admin":
                return redirect(url_for('allTracks'))
            else:
                return redirect(url_for('creatorHome'))
        db.session.delete(song)
        db.session.commit()
        flash('Song delete successfully')
        if current_user.u_userType=="Admin":
            return redirect(url_for('allTracks'))
        else:
            return redirect(url_for('creatorHome'))

# -------------------------- End of Creator's Song Management Routes --------------------------

# -------------------------- Start of Logout Route --------------------------

#Authorized routes: Logout route
@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    flash('Logged Out Successfully')
    return redirect(url_for('index'))

# -------------------------- End of Logout Route --------------------------