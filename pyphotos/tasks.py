from pyphotos.mycelery import celery
from pyphotos.models import Photo, User, Album

from io import BytesIO
from boto.s3.key import Key
import Image

@celery.task
def foo():
    albums = celery.db.albums.find()
    for al in albums:
        print al
        
        
@celery.task
def generate_thumbnail(albumname, filename):
    print "generating thumbnail for %s/%s"%(albumname, filename)
    
    #get the S3 key:
    key = Key(celery.bucket)
    imagepath = '%s/%s'%(albumname, filename)
    thumbnailpath = 'thumbnails/'+imagepath
    key.key=imagepath  #I know, boto...
    
    f = key.get_contents_as_string()
    
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
    
    imagefile.seek(0)
    
    key = celery.bucket.new_key("thumbnails/%s/%s"%(albumname,filename))
    key.set_contents_from_file(imagefile)
    
    #update photo url:
    photo = Photo.m.find({'albumname':albumname, 'filename':filename}).one()
    photo.thumbnailpath = thumbnailpath
    photo.m.save()
    
    print "thumbnail generation done for %s/%s"%(albumname, filename)
