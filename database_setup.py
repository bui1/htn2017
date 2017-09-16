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
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20))
    birthdate = Column(DateTime)
    gender = Column(Enum('male', 'female', 'other'))
    email = Column(String(100), nullable=False)
    
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
    body = Column(Text, nullable=False)
    attachment = Column(String(500))

# Message users class
class MessageUser(Base):
    __tablename__ = 'msg_user'

    msg_id = Column(Integer, ForeignKey('msg.id'))
    user_to = Column(Integer, ForeignKey('user.id'))
    user_from = Column(Integer, ForeignKey('user.id'))
    __table_args__ = (
        PrimaryKeyConstraint('msg_id', 'user_to', 'user_from'),
        )
    
# Run the database code
if __name__ == '__main__':
    engine = create_engine('sqlite:///langchat.db')
    Base.metadata.create_all(engine)
