from pyramid.httpexceptions import HTTPFound

import boto
import time
import Image
from io import BytesIO

def my_view(request):
    albums = request.db.albums.find({'visible': True})
    return {'project':'pyphotos', 'albums': albums}

def listalbum(request):
    albumname = request.matchdict['name']
    
    photos = request.db.photos.find({'album': albumname})
    
    return {'albumname': albumname, 'photos': photos}



    
def addphotoform(request):
    
    albumname = request.matchdict['name']
    
    if request.method == "POST":
        filename = request.POST['jpg'].filename
        inputfile = request.POST['jpg'].file
        
        print filename
        
        s3 = boto.connect_s3()
        bucket = s3.get_bucket("asphotos")
        key = bucket.new_key("%s/%s"%(albumname,filename))
        key.set_contents_from_file(inputfile)
        
        inputfile.seek(0)
        size = 128, 128
        im = Image.open(inputfile)
        im.thumbnail(size, Image.ANTIALIAS)
        
        imagefile = BytesIO()
        def fileno():
            raise AttributeError
        imagefile.fileno = fileno #hack to make PIL and BytesIO work together...
                
        im.save(imagefile, 'JPEG')
        
        imagefile.seek(0)
        file_id = request.fs.put(imagefile, filename=filename)
        request.db.photos.insert({'album': albumname, 'filename': filename, 'thumbnailid': file_id})
        
                
        return HTTPFound("/album/%s/addphoto"%albumname)
        
    return {}
    
    