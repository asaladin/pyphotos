from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique = True)
    public = Column(Boolean, default = False)
    owner = Column(Text)
    
    def __init__(self, name):
       self.name = name

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    email = Column(Text, unique=True)


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key = True)
    


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value
