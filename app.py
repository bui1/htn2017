from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import *
import loginform
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkeyforhtn2017'
app.config['UPLOAD_FOLDER']  = '/imgs/avatars'
app.config['DEBUG'] = True
socketio = SocketIO(app)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import *

#Connect to Database and create database session
engine = create_engine('sqlite:///langchat.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Start login
login_manager = LoginManager()
login_manager.init_app(app)

# Show homepage
@app.route('/')
def showHomepage():
    return render_template('index.html')

#### PROFILE ####

# View profile
@app.route('/user/<int:user_id>/', methods = ['GET'])
@login_required
def user_view(user_id):
    # search db for user by user id
    user = session.query(User).filter_by(id = user_id).one()

    # render the html page
    # return render_template('profile.html', user)
    return("Profile")

# Edit profile
@app.route('/user/<int:user_id>/edit/', methods = ['GET', 'POST'])
@login_required
def user_edit(user_id):
    # search db for user by user id
    user = session.query(User).filter_by(id = user_id).one()

    #user submits form
    if request.method == 'POST':
        # go through each field in the form
        for key, value in request.form:
            # 
            if getattr(user, key) != value:
                print("yo")

    # render the html page
    return render_template('profile_edit.html', user_id)
    # return("Profile edit")

### LOGIN ####
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('showHomepage')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = session.query(User).filter(username = request.form['username']).first()

        login_user(user)

        flask.flash('Logged in successfully.')

        
        return redirect(url_for('showHomepage'))
    else:
        flask.flash('Username or password incorrect', 'error')
        
    return flask.render_template('login.html', form=form)

# New profile
@app.route('/user/new', methods = ['GET', 'POST'])
def user_new():
    # user submits form
    if request.method == 'POST':
        print(request.form)

        user = User(
            username = request.form['username'],
            email = request.form['email'],
            first_name = request.form['first_name'],
            last_name = request.form['last_name'],
            birthdate = datetime.datetime.strptime(request.form['birthdate'], "%Y-%m-%d"),
            gender = request.form['gender']
        )
        
        try:
            # add user
            session.add(user)

            # flush
            session.flush()
            
            # commit database
            session.commit()
            
        except Exception as e:
            print(e)
            
        user_id = user.id
        
        # lang to learn
        langs_learn = request.form['lang_learn']

        # get language ids
        lang_learn_ids = get_lang_ids(langs_learn)

        for id in lang_learn_ids:
            lang_rel = LangLearn(
                lang_id = id,
                user_id = user_id
            )

            try:
                session.add(lang_rel)

                session.flush()

                session.commit()
            except Exception as e:
                print(e)
        # lang to teach
        langs_teach = request.form['lang_teach']

        # get language ids
        lang_teach_ids = get_lang_ids(langs_teach)

        for id in lang_teach_ids:
            lang_rel = LangTeach(
                lang_id = id,
                user_id = user_id
            )

            try:
                session.add(lang_rel)

                session.flush()

                session.commit()
        
            except Exception as e:
                print(e)
    
        return redirect(url_for('user_view', user_id=user_id))

    # user sees form
    else:
        return(render_template('user_edit.html'))

# get the id of a list of languages
def get_lang_ids(langs):
    lang_array = []

    for lang in langs:
        lang_id = session.query(Lang).filter_by(name=lang).all()
        lang_array.append(lang_id)
    
    return(lang_array)
    
#### DASHBOARD #####
@app.route('/dashboard/', methods = ['GET', 'POST'])
@login_required
def dashboard_view(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    
    return(render_template ('dashboard.html', user=user))

#### UPLOAD ####
def allowed(filename):
    allowed = set(['jpg','png','jpeg','gif'])
    
    if '.' in filename and filename.split('.',1)[1].lower() in allowed:
        return true
    return false

@app.route('/upload/', methods = ['GET', 'POST'])
@login_required
def upload(user_id):
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == "":
            flash('No file selected')

        if file and allowed(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['upload_folder'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('upload.html')
    

#### CHAT ####

@app.route('/chat/', methods = ['GET', 'POST'])
@login_required
def chat_view():
    return("hello")

@socketio.on('get message', namespace='/chat')
def handle_my_custom_namespace_event(json):
    print('Received json: ' + str(json))
    
@socketio.on('send message')
def handle_my_custom_namespace_event(json):
    emit('my response', json, namespace='/chat')

@socketio.on('join')
def on_join(data):
    username = data
    room = data['room']
    join_room(room)
    send(username + 'has entered the chat')

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the chat')
    
if __name__ == '__main__':
    socketio.run(app)
