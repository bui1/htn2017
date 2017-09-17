from sqlalchemy import Column, PrimaryKeyConstraint, DateTime, Text, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
 
Base = declarative_base()

# User class
class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    birthdate = Column(DateTime)
    gender = Column(Enum('male', 'female', 'other'))
    email = Column(String(100), nullable=False)
    password = Column(String(200))

    active = Column(Integer)
    lang = Column(Enum('0', '1')) 
    authenticated = False
    anon = False
    
    def is_authenticated():
        return self.authenticated

    def is_active(self):
        return active == 1

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
    
# Language class
class Lang(Base):
    __tablename__ = 'lang'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))

# Language to learn relationship
class LangLearn(Base):
    __tablename__ = 'lang_learn'

    lang_id = Column(Integer, ForeignKey('lang.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    __table_args__ = (
        PrimaryKeyConstraint('lang_id', 'user_id'),
        )    
# Language to teach  relationship
class LangTeach(Base):
    __tablename__ = 'lang_teach'

    lang_id = Column(Integer, ForeignKey('lang.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    __table_args__ = (
        PrimaryKeyConstraint('lang_id', 'user_id'),
        )
    
# Message class
class Message(Base):
    __tablename__ = 'msg'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    thread = Column(Integer)
    body = Column(Text, nullable=False)
    attachment = Column(String(500))
    user_from = Column(Integer)
    
# Run the database code
if __name__ == '__main__':
    engine = create_engine('sqlite:///langchat.db')
    Base.metadata.create_all(engine)
