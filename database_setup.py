from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

# User class
class User(Base):
    __tablename__ = 'user'
   
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20))
    birthdate = Column(Date)
    gender = Column(Enum('male', 'female', 'other'))

# Language class
class Language(Base):
    __tablename__ = 'lang'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))

# Language to learn relationship
class LanguageLearn(Base):
    __tablename__ = 'lang_learn'

    lang_id = Column(Integer, ForeignKey(lang.id))
    user_id = Column(Integer, ForeignKey(user.id))

# Language to teach  relationship
class LanguageTeach(Base):
    __tablename__ = 'lang_teach'

    lang_id = Column(Integer, ForeignKey(lang.id))
    user_id = Column(Integer, ForeignKey(user.id))

# Message class
class Message(Base):
    __tablename__ = 'msg'

    id = Column(Integer, primary_key=True)
    timestamp = Column(Date)
    body = Column(Longtext, nullable=False)
    attachment = Column(String(500))

# Message users class
class MessageUser(Base):
    __tablename__ = 'msg_user'

    msg_id = Column(Integer, ForeignKey(msg.id))
    user_to = Column(Integer, ForeignKey(user.id))
    user_from = Column(Interger, ForeignKey(user.id))
    
# Run the database code
if __name__ = '__main__':
    engine = create_engine('sqlite:///langchat.db')
    Base.metadata.create_all(engine)
