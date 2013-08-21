# encoding:  utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest

from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid

from pyramid.view import view_config

from pyphotos.models import User, Album
from pyphotos.models import Photo


import time
import Image

import hashlib
import random
import lib

from io import BytesIO

import tasks
import os

import logging
log = logging.getLogger(__name__)


from .models import (
    DBSession,
    User,
    Album,
    )


class NewUser(Exception): pass 

def getBucketName(request):
    return request.registry.settings['bucket_name']


@view_config(context=NewUser)
def new_user_exception(request):
    return HTTPFound(request.route_path('new_user'))
    
@view_config(route_name="new_user", renderer="pyphotos:templates/newuser.mako")
def new_user(request):
    
    if request.method == "POST":
        user = User()
        username = request.POST['username']
        
        user.username = username
        
        user.email = request.user
        DBSession.add(user)

        return HTTPFound(request.route_path('index'))
    return {}    
        

# main page
@view_config(renderer='pyphotos:templates/index.mako', route_name="index")
def my_view(request):
    albums = DBSession.query(Album).filter(Album.public == True).all()
    return {'project':'pyphotos', 'albums': albums, 'myalbums': lib.myalbums(request)}


#this is the album main view
#shows all photos from an album
@view_config(route_name='listalbum', renderer="pyphotos:templates/list.mako", permission='view')
def listalbum(request):
    
    username = authenticated_userid(request)
    albumname = request.matchdict['albumname']
    album = DBSession.query(Album).filter(Album.name == albumname).one()
    owner = album.owner

    photos = album.photos

    def url_for_thumbnail(url):
        if "/thumbnail/generate/" in url:
            return url
        else:
            return request.s3.generate_url(3600 , "GET" ,getBucketName(request), url )

    
    for p in photos:
        p.url = request.s3.generate_url(3600 , "GET" ,getBucketName(request),'%s/%s'%(albumname,p.filename) )
        p.thumbnailpath = url_for_thumbnail(p.thumbnailpath)
    
    return {'albumname': albumname, 'photos': photos, 'username': username, 'owner':owner}

@view_config(route_name="newalbum", renderer="pyphotos:templates/newalbum.mako", permission="create")
def newalbum(request):
    if 'albumname' in request.POST:
        albumname = request.POST['albumname']
        visible = False
        if 'visible' in request.POST:
            visible = True
        album = Album()
        album.name = albumname
        album.owner = request.username       
        album.public = visible
        DBSession.add(album)

        return HTTPFound(location="/")

    
    return {} 




@view_config(route_name="view_thumbnail")
def thumbnail(request):
    fid = request.GET['filename']
    fid2 = request.db.fs.files.find_one({'filename':fid})['_id']
    fich = request.fs.get(fid2)
    return Response(fich.read(),content_type="image/jpeg")


@view_config(route_name='generate_thumbnail')
def generate_thumbnail(request):
    albumname = request.matchdict['albumname']
    filename = request.matchdict['filename']
    
    tasks.generate_thumbnail.delay(albumname, filename)
    
    _here = os.path.dirname(__file__)
    response = Response(content_type='image/jpeg')
    response.app_iter = open(os.path.join(_here, 'static','notgenerated.png'), 'rb')
    
    return response
    
    
    
@view_config(route_name="addphotoform", renderer="pyphotos:templates/addphoto.mako", permission='append')
def addphotoform(request):
    
    albumname = request.matchdict['albumname']
    
    if request.method == "POST":
        filename = request.POST['jpg'].filename
        inputfile = request.POST['jpg'].file

        #store the photo in S3
        key = request.bucket.new_key("%s/%s"%(albumname,filename))
        key.set_contents_from_file(inputfile)
        
        #create the thumbnail
        inputfile.seek(0)
        size = 300, 300
        im = Image.open(inputfile)
        im.thumbnail(size, Image.ANTIALIAS)
        
        imagefile = BytesIO()
        def fileno():
            raise AttributeError
        imagefile.fileno = fileno #hack to make PIL and BytesIO work together...
                
        im.save(imagefile, 'JPEG')
        
        #store the thumbnail into S3:
        imagefile.seek(0)
        key = request.bucket.new_key("/thumbnails/%s/%s"%(albumname,filename))
        key.set_contents_from_file(imagefile)

        #store the new photo in the database
        photo = Photo()
        photo.albumname = albumname
        photo.filename = filename
        photo.thumbnailpath = "/thumbnails/%s/%s"%(albumname,filename)
        photo.m.save()
                
        return HTTPFound("/album/%s/addphoto"%albumname)
        
    return {}


#page showing login options
@view_config(route_name="login", renderer="pyphotos:templates/login.mako")
def login(request):
    userid = authenticated_userid(request)
    #browserid reloads the current page, so simply go back to home if the user has logged in
    if userid is not None:
        try:
            user = User.m.find({'browserid':userid}).one()
            print user
        except:
            return HTTPFound(location='/newuser')
        
        return HTTPFound(location="/")
    
    return {}
    

#simply logout
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.flash("You have logged out")
    return HTTPFound(location='/', headers=headers)

#browserid login:
@view_config(route_name="browserid_login")
def bid_login(request):
    assertion = request.POST['assertion']
    print "assertion:", assertion
    import browserid
    import browserid.errors
    try:
        data = browserid.verify(assertion, request.registry.settings['persona.siteid'])
    except (ValueError, browserid.errors.TrustError):
        raise HTTPBadRequest('invalid assertion')

    headers = remember(request, data['email'])
    return HTTPFound(location="/", headers=headers)    


    
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
    
@view_config(route_name='fullsize', renderer='pyphotos:templates/fullsize.mako', permission='view')
def fullsize_view(request):
    albumname = request.matchdict['albumname']
    filename = request.matchdict['filename']
    url = request.s3.generate_url(3600 , "GET" ,getBucketName(request),'%s/%s'%(albumname,filename) )
    return {'url': url}

    
@view_config(route_name="import_s3", permission="create")
def import_s3(request):
    if request.method == "POST":
        if 'dirname' in request.POST:
            dirname = request.POST['dirname']
            albumname = request.POST['albumname']
            albumpublic = request
            
            album = Album()
            album.title = albumname
            album.owner = authenticated_userid(request)
            visible = False
            if 'visible' in request.POST:
                visible = True
            album.public = visible
            
            album.m.save()
            
            listdir = request.bucket.list(dirname)
            for f in listdir:
                photo = Photo()
                filename = f.name.strip(albumname+'/')
                
                photo.filename = filename
                photo.albumname = albumname
                
                photo.thumbnailpath="/thumbnail/generate/"+ f.name
                log.debug("thumbnail path:", photo.thumbnailpath)
                photo.m.save()
            
            
    return Response("not imported yet")
    
    
@view_config(route_name='admin', renderer='pyphotos:templates/admin.mako', permission='admin')
def admin(request):
    return {}
    
    
    
    
    
    
    
def forbidden_view(request):
    if request.user is None:
        return Response("You must <a href='/login'>log in</a>")
    return Response("You are not allowed to view this ressource. <a href='/'>back home</a>")
 


def debug_login(request):
    headers = remember(request, 'root@localhost')
    return HTTPFound(location="/", headers=headers)    
