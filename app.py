from flask import Flask, session, render_template, request, redirect,jsonify, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import *
from form import LoginForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkeyforhtn2017'
app.config['UPLOAD_FOLDER']  = '/imgs/avatars'
app.config['DEBUG'] = True
app.config['THREADED'] = True
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

@app.route('/how-it-works')
def showHow():
    return render_template('how-it-works.html')

# show about us
@app.route('/about-us')
def showAbout():
    return(render_template('about-us.html'))

#### PROFILE ####

# View profile
@app.route('/user/<int:user_id>/', methods = ['GET', 'POST'])
@login_required
def user_view(user_id):
    # search db for user by user id
    user = db_session.query(User).filter_by(id = user_id).one()

    female = True if user.gender == 'female' else False 
    
    # render the html page
    # return render_template('profile.html', user)
    return(render_template('profile-page.html', user=user, female=female))

# Edit profile
@app.route('/user/<int:user_id>/edit/', methods = ['GET', 'POST'])
@login_required
def user_edit(user_id):
    # search db for user by user id
    user = db_session.query(User).filter_by(id = user_id).one()

    female = True if user.gender == 'female' else False
    
    #user submits form
    if request.method == 'POST':
        # go through each field in the form
        for key, value in request.form:
            # 
            if getattr(user, key) != value:
                print("yo")

    # render the html page
    return redirect(url_for('user_view', user=user.id, female=female))

### LOGIN ####
@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=user_id).first()

@app.route("/logout/")
@login_required
def logout():
    user = db_session.query(User).filter_by(id=session.get('user_id')).one()

    user.active = 0

    db_session.commit()
    
    logout_user()
    return redirect(url_for('showHomepage'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = db_session.query(User).filter_by(username = request.form['username']).first()

        user.active = 1

        db_session.commit()
        
        login_user(user)

        flash('Logged in successfully.')

        session['user_id'] = user.id
        
        return redirect(url_for('dashboard_view', user_id=user))
    else:
        flash('Username or password incorrect', 'error')
        
    return render_template('login.html', form=form)

# New profile
@app.route('/user/new', methods = ['GET', 'POST'])
def user_new():
    
    # user submits form
    if request.method == 'POST':
        print(request.form)

        birthday = "19" + request.form['birthyear'] + "-" + request.form['birthmonth'] + "-" + request.form['birthday']
        
        user = User(
            username = request.form['username'],
            email = request.form['email'],
            birthdate = datetime.datetime.strptime(birthday, "%Y-%m-%d"),
            gender = request.form['gender'],
            password = request.form['password'],
            active = 0,
            lang = request.form['lang']
        )

        print(user)
        try:
            # add user
            db_session.add(user)

            # flush
            db_session.flush()
            
            # commit database
            db_session.commit()

            return(redirect(url_for('login')))
            
        except Exception as e:
            print(e)
            return(render_template('profile-page.html', user=None, female=None))
            
    # user sees form
    else:
        return(render_template('profile-page.html', user=None, female=None))

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
    user = db_session.query(User).filter_by(id=session.get('user_id')).one();
    
    return(render_template ('dashboard.html', user=user)) 

#### CHAT ####

@app.route('/chat/<int:lang>', methods = ['GET', 'POST'])
@login_required
def chat_view(lang):
    user_id = session.get('user_id')
    room = session.get('msg_id')
    session['lang'] = lang
    
    chat_lang = str(lang)

    user = db_session.query(User).filter_by(id=user_id).one()

    posts = db_session.query(Message,User).filter_by(thread=lang).filter(Message.user_from==User.id).order_by(Message.timestamp).limit(30).all()

    for post in posts:
        print(post[0])
        print(post[1])
        print(post[0].user_from)
    print(posts)
    
    return render_template('chat.html', user=user, posts=posts, lang=lang, room=lang)

@app.route('/chat-send/<int:lang>', methods = ['POST'])
def send_msg(lang):
    lang = session.get('lang')
    print(request.form)
    message = request.form.to_dict()
    
    msg = Message(
        body = message['data'],
        user_from = session.get('user_id')
    )

    db_session.add(msg)

    db_session.flush()

    db_session.commit()

    return redirect(url_for('chat_view', lang=lang))

if __name__ == '__main__':
    socketio.run(app)
