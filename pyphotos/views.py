from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from velruse.store.mongodb_store import MongoDBStore


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
    
    s3 = boto.connect_s3()
    bucket=s3.get_bucket("asphotos")
    
    photos=list(photos)
    
    for p in photos:
        p['url'] = s3.generate_url(3600 , "GET" ,'asphotos','%s/%s'%(albumname,p['filename']) )

    
    return {'albumname': albumname, 'photos': photos}


def newalbum(request):
    if 'albumname' in request.POST:
        albumname = request.POST['albumname']
        visible = False
        if 'visible' in request.POST:
            visible = True
        request.db.albums.insert({'title': albumname, 'visible':visible})
        return HTTPFound(location="/")

    
    return {} 





def thumbnail(request):
    fid = request.GET['filename']
    fid2 = request.db.fs.files.find_one({'filename':fid})['_id']
    fich = request.fs.get(fid2)
    return Response(fich.read(),content_type="image/jpeg")

    
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
        size = 300, 300
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


def login(request):
    termination = request.route_url("velruse_endpoint")
    
    return {"termination":termination}

def endpoint(request):
    
    if 'token' in request.params:
        token = request.params['token']
    
        store = MongoDBStore(db="pyphotos")
        values = store.retrieve(token)
        print values
    
    return Response("hello")
    
