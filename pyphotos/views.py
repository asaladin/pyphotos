
# encoding:  utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid

from pyramid.view import view_config

from pyphotos.model import User


import time
import Image

import hashlib
import random
import lib

from io import BytesIO

@view_config(renderer='pyphotos:templates/index.mako', route_name="index")
def my_view(request):
    albums = request.db.albums.find({'visible': True})
    print dir(User)
    print type(User)

    print list(User.m.find())


    return {'project':'pyphotos', 'albums': albums, 'myalbums': lib.myalbums(request) }


@view_config(route_name='listalbum', renderer="pyphotos:templates/list.mako", permission='view')
def listalbum(request):
    session = request.session
    
    username = authenticated_userid(request)
   
    
    albumname = request.matchdict['albumname']
    photos = request.db.photos.find({'album': albumname})
    
    
    
    photos=list(photos)
    
    for p in photos:
        p['url'] = request.s3.generate_url(3600 , "GET" ,'asphotos','%s/%s'%(albumname,p['filename']) )

    
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
    
    albumname = request.matchdict['albumname']
    
    if request.method == "POST":
        filename = request.POST['jpg'].filename
        inputfile = request.POST['jpg'].file
        
        print filename

        key = request.bucket.new_key("%s/%s"%(albumname,filename))
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
    
    return {}
    

#simply logout
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.flash("You have logged out")
    return HTTPFound(location='/', headers=headers)



#velruse authentication endpoint
@view_config(
    context='velruse.AuthenticationComplete',
    renderer='pyphotos:templates/login_result.mako',
)
def login_complete_view(request):
    context = request.context
    result = {
        'provider_type': context.provider_type,
        'provider_name': context.provider_name,
        'profile': context.profile,
        'credentials': context.credentials,
    }

    username = context.profile['accounts'][0]['username']
    print "username:", username

    headers = remember(request, username)
    return HTTPFound(location="/", headers=headers)
   
    return {
        'result': json.dumps(result, indent=4),
    }



    
@view_config(route_name="createticket", renderer='pyphotos:templates/displayticket.mako', permission='createticket')
def createticket(request):
    username = authenticated_userid(request)
    albumname = request.matchdict['albumname']
    token = hashlib.sha1( "%s"%random.randint(1,1e99)).hexdigest()
    
    request.db.tickets.insert({'owner':username, 'albumname': albumname, 'token': token } )
    
    
    return {'token': token}

@view_config(route_name="allowview")
def allowview(request):
    credential = request.matchdict['credential']
    
    try:
        ticket = request.db.tickets.find_one({'token': credential})
        albumname = ticket['albumname']
    except KeyError:    
        return Response('ce ticket ne vaut rien!')
        
    if 'tickets' in request.session:
        request.session['tickets'][ albumname ] = credential
    else:    
        request.session['tickets'] = { albumname: credential }
        
    request.session.flash(u"album %s ajouté!"%albumname )
        
        
    return HTTPFound(location='/')
    
@view_config(route_name='fullsize', renderer='pyphotos:templates/fullsize.mako')
def fullsize_view(request):
    albumname = request.matchdict['albumname']
    filename = request.matchdict['filename']
    url = request.s3.generate_url(3600 , "GET" ,'asphotos','%s/%s'%(albumname,filename) )
    return {'url': url}
    
