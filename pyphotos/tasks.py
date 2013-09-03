from pyphotos.mycelery import celery
from pyphotos.models import DBSession, Photo, User, Album

from sqlalchemy import engine_from_config

from io import BytesIO
from boto.s3.key import Key
from PIL import Image
import transaction
import os.path


import logging
log = logging.getLogger(__name__)


@celery.task
def foo():
    albums = celery.db.albums.find()
    for al in albums:
        print al
        
        
@celery.task
def generate_thumbnail(albumname, filename):
    log.debug("generating thumbnail for %s/%s"%(albumname, filename))
    
    #get the Photo object:
    album = DBSession.query(Album).filter(Album.name==albumname).one()
    photo = DBSession.query(Photo).filter(Photo.album==album).filter(Photo.filename==filename).one()
        
    #retrieve the original image:
    f = celery.mystore[photo.filekey]    
    
    #create the thumbnail
    size = 300, 300
    inputfile = BytesIO(f)
    im = Image.open(inputfile)
    im.thumbnail(size, Image.ANTIALIAS)
        
    imagefile = BytesIO()
    def fileno():
        raise AttributeError
    imagefile.fileno = fileno #hack to make PIL and BytesIO work together...
                
    im.save(imagefile, 'JPEG')
    imagefile.seek(0)  # put the file cursor back to the origin
    
    #save the thumbnail into the storage system:
    dirname = os.path.dirname(photo.filekey)
    key = celery.mystore.genkey(dirname, filename, thumbnail=True)
    celery.mystore[key] = imagefile.read()
    
    #update photo url:
    photo.thumbkey = key
    DBSession.add(photo)
    
    transaction.commit()
    log.debug('the key is: %s'%key)
    log.debug("thumbnail generation done for %s/%s"%(albumname, filename))
