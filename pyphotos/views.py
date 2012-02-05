from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid


from velruse.store.mongodb_store import MongoDBStore
from pyramid.view import view_config

import boto
import time
import Image


from io import BytesIO

@view_config(renderer='pyphotos:templates/index.mako', route_name="index")
def my_view(request):
    albums = request.db.albums.find({'visible': True})
    return {'project':'pyphotos', 'albums': albums}


@view_config(route_name='listalbum', renderer="pyphotos:templates/list.mako", permission='view')
def listalbum(request):
    session = request.session
    
    try:
       username = request.session["username"]
    except: 
       username = "anonymous"
       session['username'] = username
    
    
    albumname = request.matchdict['name']
    photos = request.db.photos.find({'album': albumname})
    
    s3 = boto.connect_s3()
    bucket=s3.get_bucket("asphotos")
    
    photos=list(photos)
    
    for p in photos:
        p['url'] = s3.generate_url(3600 , "GET" ,'asphotos','%s/%s'%(albumname,p['filename']) )

    
    return {'albumname': albumname, 'photos': photos, 'username': username}

@view_config(route_name="newalbum", renderer="pyphotos:templates/newalbum.mako", permission="create")
def newalbum(request):
    if 'albumname' in request.POST:
        albumname = request.POST['albumname']
        visible = False
        if 'visible' in request.POST:
            visible = True
        request.db.albums.insert({'title': albumname, 'visible':visible, 'owner': authenticated_userid(request)})
        return HTTPFound(location="/")

    
    return {} 




@view_config(route_name="view_thumbnail")
def thumbnail(request):
    fid = request.GET['filename']
    fid2 = request.db.fs.files.find_one({'filename':fid})['_id']
    fich = request.fs.get(fid2)
    return Response(fich.read(),content_type="image/jpeg")


@view_config(route_name="addphotoform", renderer="pyphotos:templates/addphoto.mako")
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


#page showing login options
@view_config(route_name="login", renderer="pyphotos:templates/login.mako")
def login(request):
    if 'login' in request.POST:
        login = request.POST["login"]
        password = request.POST["password"]
        
        #TODO: real security check...
        real_passwd = request.db.users.find_one({'login': login})['pwd']
        if real_passwd == password:
            headers = remember(request, login)
            return HTTPFound(location='/', headers=headers)
        
        
    termination = request.route_url("velruse_endpoint")
    
    return {"termination":termination}
    

#simply logout
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.flash("You have logged out")
    return HTTPFound(location='/', headers=headers)


#page called after velruse authentication
@view_config(route_name="velruse_endpoint")
def endpoint(request):
    
    if 'token' in request.params:
        token = request.params['token']
    
        store = MongoDBStore(db="pyphotos")
        values = store.retrieve(token)
        
        if values['status'] == 'ok':
            print values
            identifier = values['profile']['identifier']
            print identifier
            
            try:
                username = request.db.identifiers.find_one({'id': identifier })['username']
            except TypeError:
                 if authenticated_userid(request) is not None:
                      request.db.identifiers.insert({'id': identifier, 'username': authenticated_userid(request)  })
                      request.session.flash('welcome back %s'%authenticated_userid(request))
                      return HTTPFound(location='/')
                 else:
                     #no local account, try to create a new one
                     if request.registry.settings['allownewaccount'] == 'True':
                         request.session['identifier'] = identifier
                         return HTTPFound(location='/newaccount')
                         
                
            
            headers = remember(request, username)
            request.session.flash("welcome %s"%username)
            
            return HTTPFound(location='/', headers=headers)
            
        
        print values
    
    return Response("hello")
    
@view_config(route_name="createticket", permission='createticket')
def createticket(request):
    return Response("allowed to create tickets!")
