from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    ForeignKey,
    DateTime
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Album(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique = True)
    public = Column(Boolean, default = False)
    ownerid = Column(Integer, ForeignKey('users.id') )
    creationdate = Column(DateTime)    

    photos = relationship("Photo")
    

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    creationdate = Column(DateTime)

    albums = relationship("Album", backref="owner")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key = True)
    


class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key = True)
    idalbum = Column(Integer, ForeignKey('albums.id'))
    filekey = Column(Text) #S3 key, file path, ...
    storagetype = Column(Text) #type of storage (S3, file system, ...)
    annotation = Column(Text)  #caption
    comments = relationship("PhotoComment")


class Ticket(Base):
    __tablename__ = 'tickets'
    token = Column(Text, primary_key=True)
    idalbum = Column(Integer, ForeignKey('albums.id'), nullable=False)
    creationDate = Column(DateTime)
    expirationDate = Column(DateTime)
    creatorid = Column(Integer, ForeignKey('users.id'))
    authorized_email = Column(Text) #e-mail of the person allowed to view an album


class PhotoComment(Base):
    __tablename__ = "photocomments"
    id = Column(Integer, primary_key=True)
    idauthor = Column(Integer, ForeignKey("users.id"))
    idphoto = Column(Integer, ForeignKey("photos.id")) 
    content = Column(Text)
    