from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyphotos.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest, BeforeRender, NewResponse

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from  pyramid.security import authenticated_userid

from pyramid.httpexceptions import HTTPFound

import pyramid_beaker
import random

from gridfs import GridFS
import hashlib
import lib
import transaction

import logging
log = logging.getLogger(__name__)


import boto

from pyphotos.views import forbidden_view
from pyphotos.storage import store 

def ingroup(userid, request):
    return [userid]


from .models import (
    DBSession,
    Base,
    User,
    )



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #set up sqlalchemy:
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    #pyramid configurator (sessions, routes, ...)
    config = Configurator(root_factory=Root, settings=settings)
    config.include("pyramid_persona") 
    
    mystore = store.S3Store("asphotos")
    config.registry.settings['mystore'] = mystore 
    
    config.add_subscriber(add_store, NewRequest)
    config.add_subscriber(check_for_new_user, NewRequest)
    
    #add root account if none present:
    #if db.users.find({'admin':True}).count() == 0:
    #    pwd = hashlib.sha1('%s'%random.randint(1,1e99)).hexdigest()
    #    
    #    db.users.insert({'login':'root', 'pwd':pwd, 'admin':True })
    #    print 'created root account with password ', pwd
    
    
    config.add_route("index", "/")
    config.add_route("listalbum", "/album/{albumname}/list", factory="pyphotos.resources.AlbumFactory")
    config.add_route("addphotoform", "/album/{albumname}/addphoto", factory="pyphotos.resources.AlbumFactory")
    config.add_route("view_thumbnail", "/thumbnail/{albumname}/{filename}", factory="pyphotos.resources.AlbumFactory")
    #config.add_route("login", "/login")
    #config.add_route("browserid_login", "/login/browserid")
    #config.add_route("logout", "/logout")
    config.add_route("newalbum", "/newalbum")
    config.add_route("createticket", "/createticket/{albumname}", factory="pyphotos.resources.AlbumFactory")
    config.add_route("allowview", "/allow/{credential}")
    config.add_route('myalbums', '/myalbums')
    config.add_route('fullsize', '/fullsize/{albumname}/{filename}', factory="pyphotos.resources.AlbumFactory")
    #config.add_route('new_user', "/newuser")
    config.add_route('import_s3', '/import/s3')
    config.add_route('generate_thumbnail', '/thumbnail/generate/{albumname}/{filename}')
    config.add_route('admin', '/admin')
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    
    config.add_forbidden_view(forbidden_view)
    

    config.add_request_method('pyphotos.lib.get_user', name='user', property=True, reify=True)
    
    config.scan()
    
      
    if config.registry.settings['pyphotos_debug_mode']:
        #add a local user:
        nuser = DBSession.query(User).filter(User.email=="root@localhost").count()
        if nuser==0:
            user = User()
            user.email = "root@localhost"
            user.username = "root"
            DBSession.add(user)
            transaction.commit()
  
 
        from .views import debug_login
        config.add_route('debug_login', '/login/debug')
        config.add_view(debug_login, route_name='debug_login')
 
 
    return config.make_wsgi_app()

from views import NewUser  
    
def add_store(event):
    settings = event.request.registry.settings

    event.request.mystore = settings['mystore']


def check_for_new_user(event):
    userid = authenticated_userid(event.request)
    if userid is None: return

    users = DBSession.query(User).filter(User.email==userid)
    log.debug("number of users with this email: %i"%users.count())
    if users.count() == 0:  #only redirect to new_user if the user is not in the database
        #don't reraise the NewUser exception if the new_user view is going to be visited
        #if event.request.url != event.request.route_url('new_user'):
            raise NewUser()
    
