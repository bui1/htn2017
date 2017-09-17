from flask import Flask, session, render_template, request, redirect,jsonify, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import *
from form import LoginForm
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
db_session = DBSession()

# Start login
login_manager = LoginManager()
login_manager.init_app(app)

# Show homepage
@app.route('/')
def showHomepage():
    return render_template('front.html')

# show about us
@app.route('/about-us')
def showAbout():
    return(render_template('aboutus.html'))

#### PROFILE ####

# View profile
@app.route('/user/<int:user_id>/', methods = ['GET'])
@login_required
def user_view(user_id):
    # search db for user by user id
    user = db_session.query(User).filter_by(id = user_id).one()

    # render the html page
    # return render_template('profile.html', user)
    return("Profile")

# Edit profile
@app.route('/user/<int:user_id>/edit/', methods = ['GET', 'POST'])
@login_required
def user_edit(user_id):
    # search db for user by user id
    user = db_session.query(User).filter_by(id = user_id).one()

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
    return db_session.query(User).filter_by(id=user_id).first()

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('showHomepage'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    db_session.flush()
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(username = request.form['username']).first()

        login_user(user)

        flash('Logged in successfully.')

        session['user_id'] = user.id
        
        return redirect(url_for('dashboard_view', user_id=user.id))
    else:
        flash('Username or password incorrect', 'error')
        
    return render_template('login.html', form=form)

# New profile
@app.route('/user/new', methods = ['GET', 'POST'])
def user_new():
    db_session.flush()
    
    # user submits form
    if request.method == 'POST':
        print(request.form)

        user = User(
            username = request.form['username'],
            email = request.form['email'],
            birthdate = datetime.datetime.strptime(request.form['birthdate'], "%Y-%m-%d"),
            gender = request.form['gender'],
            password = request.form['password']
        )
        
        try:
            # add user
            db_session.add(user)

            # flush
            db_session.flush()
            
            # commit database
            db_session.commit()
            
        except Exception as e:
            print(e)
            
    # user sees form
    else:
        return(render_template('user_edit.html'))

# get the id of a list of languages
def get_lang_ids(langs):
    lang_array = []

    for lang in langs:
        lang_id = db_session.query(Lang).filter_by(name=lang).all()
        lang_array.append(lang_id)
    
    return(lang_array)
    
#### DASHBOARD #####
@app.route('/dashboard/', methods = ['GET', 'POST'])
@login_required
def dashboard_view():
    user = session.get('user_id');
    
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

@app.route('/chat', methods = ['GET', 'POST'])
@login_required
def chat_view():
    user = session.get('user_id')
    room = session.get('msg_id')
    return render_template('chat.html', user=user, room=room)

@app.route('/chat-recv', methods = ['GET'])
def recv_msg():
    user = session.get('user_id')
    room = session.get('msg_id')

    msgs = session.query(Message).filter_by(timestamp )
    return

@app.route('/chat-send', methods = ['POST'])
def send_msg():
    message = request.form.to_dict()
    print(message)
    for key in message:
        msg = key
    
    msg = Message(
        body = msg
        )

    db_session.add(msg)

    db_session.flush()

    db_session.commit()

    user_id= db_session.query(User).filter_by(id=session.get('user_id')).one()

    #TODO
    user_to_id = session.get('to_user');
    
    msg_user = MessageUser(
        msg_id = msg.id,
        user_to = user_to_id,
        user_from = user_id.id
    )

    db_session.add(msg_user)

    db_session.flush()

    db_session.commit()

    return redirect(url_for('chat_view'))

if __name__ == '__main__':
    socketio.run(app)
