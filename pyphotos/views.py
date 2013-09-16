# encoding:  utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPBadRequest

from pyramid.response import Response
from pyramid.security import remember, forget, authenticated_userid

from pyramid.view import view_config

from pyphotos.models import User, Album
from pyphotos.models import Photo


import time, datetime
from PIL import Image

import hashlib
import random
import lib

import transaction

from io import BytesIO

import tasks
import os
import os.path

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


@view_config(context=NewUser, renderer="pyphotos:templates/newuser.mako")
def new_user_exception(request):
    if request.method == "POST":
        user = User()
        username = request.POST['username']
        user.username = username
        user.email = authenticated_userid(request)
        
        DBSession.add(user)
        log.debug("added new user %s"%user.username)
        transaction.commit()

        return HTTPFound(request.url)
    return {}    
    
        

# main page
@view_config(renderer='pyphotos:templates/index.mako', route_name="index")
def my_view(request):
    albums = DBSession.query(Album).filter(Album.public == True).all()
    
    for a in albums:
        if a.coverimage is not None:
            photo = DBSession.query(Photo).filter(Photo.id == a.coverimage).one()
            
        else:
            if len(a.photos) > 0:
                photo = a.photos[0] #take the album first picture
            else:
                photo = None  #there is no photo here
                
        if photo is not None:
            if '/generate/' in photo.thumbkey:
                photo.thumbnailpath = request.route_path('generate_thumbnail', albumname=a.name, filename=photo.filename)
            else:
                photo.thumbnailpath = request.mystore.view_url(photo.thumbkey)
        else:
            #the album is empty
            photo = Photo()
            photo.thumbnailpath = request.static_path('pyphotos:static/notgenerated.png')
        
        
        a.cover = photo
    
    return {'project':'pyphotos', 'albums': albums}


#this is the album main view
#shows all photos from an album
@view_config(route_name='listalbum', renderer="pyphotos:templates/list.mako", permission='view')
def listalbum(request):
    
    username = authenticated_userid(request)
    albumname = request.matchdict['albumname']
    album = DBSession.query(Album).filter(Album.name == albumname).one()
    owner = album.owner

    photos = album.photos

    
    for p in photos:
        p.url = "/not/found/yet"
        if '/generate/' in p.thumbkey:
            p.thumbnailpath = request.route_path('generate_thumbnail', albumname=albumname, filename=p.filename)
        else:
            p.thumbnailpath = request.mystore.view_url(p.thumbkey)
        p.fullsizeurl = request.mystore.view_url(p.filekey)
        
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
        album.owner = request.user
        album.public = visible
        DBSession.add(album)
        transaction.commit()

        return HTTPFound(location="/")

    
    return {} 




@view_config(route_name="render_image")
def render_image(request):
    albumname = request.matchdict['albumname']
    filename = request.matchdict['filename']
    thumbkey = request.mystore.genkey(albumname, filename, thumbnail = True)
    return Response(request.mystore[thumbkey], content_type="image/jpeg")


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

        
        #put the photo in the store
        key = request.mystore.genkey(albumname, filename)
        request.mystore[key] = inputfile.read()
        
        
        #create the thumbnail
        inputfile.seek(0)
        size = 300, 300
        im = Image.open(inputfile)
        im.thumbnail(size, Image.ANTIALIAS)
        
        #create a file-like object for storing the thumbnail
        imagefile = BytesIO()
        def fileno():
            raise AttributeError
        imagefile.fileno = fileno #hack to make PIL and BytesIO work together...
                
        im.save(imagefile, 'JPEG')  #save thumbnail in jpeg format into imagefile
        
        imagefile.seek(0)
        
        thumbkey = request.mystore.genkey(albumname, filename, thumbnail = True)
        request.mystore[thumbkey] = imagefile.read()

        #store the new photo in the database
        album = DBSession.query(Album).filter(Album.name==albumname).one()
        
        photo = Photo()
        photo.album = album
        photo.filekey = key
        photo.thumbkey = thumbkey
        photo.filename = filename
        DBSession.add(photo)
                
        return HTTPFound(request.route_path("addphotoform",albumname=albumname))
        
    return {}

    
@view_config(route_name="createticket", renderer='pyphotos:templates/displayticket.mako', permission='createticket')
def createticket(request):
    username = authenticated_userid(request)
    albumname = request.matchdict['albumname']
    token = hashlib.sha1( "%s"%random.randint(1,1e99)).hexdigest()
    
    album = DBSession.query(Album).filter(Album.name==albumname).one()

    ticket = Ticket()
    ticket.token = token
    ticket.creationdate = datetime.datetime.utcnow() 
    ticket.creatorid = request.user.id
    ticket.albumid = album.id    

    DBSession.add(ticket)    

    return {'token': token}

@view_config(route_name="allowview")
def allowview(request):
    credential = request.matchdict['credential']
    
    try:
        ticket = DBSession.query(Ticket).filter(Ticket.tocken==credential).one()
        album = DBSession.query(Album).filter(Album.id==ticket.albumid).one()
        albumname = album.name
    except KeyError:    
        return Response('ce ticket ne vaut rien!')
        
    if 'tickets' in request.session:
        request.session['tickets'][ albumname ] = credential
    else:    
        request.session['tickets'] = { albumname: credential }
        
    request.session.flash(u"album %s added!"%albumname )
        
        
    return HTTPFound(location='/')
    
@view_config(route_name='fullsize', renderer='pyphotos:templates/fullsize.mako', permission='view')
def fullsize_view(request):
    albumname = request.matchdict['albumname']
    filename = request.matchdict['filename']
    
    album = DBSession.query(Album).filter(Album.name==albumname).one()
    photo = DBSession.query(Photo).filter(Photo.album==album).filter(Photo.filename==filename).one()

    url = request.mystore.view_url(photo.filekey)
    return {'url': url}

    
@view_config(route_name="import_s3", permission="create")
def import_s3(request):
    if request.method == "POST":
        if 'dirname' in request.POST:
            dirname = request.POST['dirname']
            albumname = request.POST['albumname']
             
            album = Album()
            album.name = albumname
            album.owner = request.user
            visible = False
            if 'visible' in request.POST:
                visible = True
            album.public = visible
            
            DBSession.add(album)
            
            listdir = request.mystore.list(dirname)
            for f in listdir:
                photo = Photo()
                filename = os.path.basename(f.name)
                
                photo.filename = filename
                photo.albumname = albumname
                photo.album = album
                photo.filekey = request.mystore.genkey(dirname, filename)
                log.debug('************* filekey: ' + photo.filekey)
                
                photo.thumbkey="/thumbnail/generate/"+ f.name
                log.debug("thumbnail path: %s"%photo.thumbkey)
                DBSession.add(photo)
            
            
    return Response("not imported yet")
    
    
@view_config(route_name='admin', renderer='pyphotos:templates/admin.mako', permission='admin')
def admin(request):
    return {}
    
    
    
    
    
    
    
#def forbidden_view(request):
    #if request.user is None:
        #return Response("You must <a href='/login'>log in</a>")
    #return Response("<html><body>You are not allowed to view this ressource. <a href='/'>back home</a></body></html>")
 

def debug_login(request):
    email = request.matchdict["email"]
    headers = remember(request, email)
    return HTTPFound(location="/", headers=headers)    
