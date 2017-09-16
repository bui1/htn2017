from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import *

#Connect to Database and create database session
engine = create_engine('sqlite:///langchat.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Show homepage
@app.route('/')
def showHomepage():
    return render_template('index.html')

#### PROFILE ####

# View profile
@app.route('/user/<int:user_id>/', methods = ['GET'])
def user_view(user_id):
    # search db for user by user id
    user = session.query(User).filter_by(id = user_id).one()

    # render the html page
    # return render_template('profile.html', user)
    return("Profile")

# Edit profile
@app.route('/user/<int:user_id>/edit/', methods = ['GET', 'POST'])
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
    # return render_template('profile_edit.html', user_id)
    return("Profile edit")

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

        print(user.id)
            
        return redirect(url_for('user_view', user_id=user.id))

    # user sees form
    else:
        return(render_template('user_edit.html'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
