from pyramid.config import Configurator
from pyphotos.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest, BeforeRender, NewResponse

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from  pyramid.security import authenticated_userid


import pyramid_beaker
import random

from gridfs import GridFS
import pymongo
import hashlib
import lib

import boto


def ingroup(userid, request):
    return [userid]



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.include(pyramid_beaker)

    config.include("velruse.providers.openid")
    config.include('velruse.providers.google_oauth2')
    config.add_openid_login()

    
    authentication_policy = AuthTktAuthenticationPolicy('seekrit', callback=ingroup)
    authorization_policy = ACLAuthorizationPolicy()
    
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    
    
    
    db_uri = settings['db_uri']
    conn = pymongo.Connection(db_uri)
    db = conn[settings['db_name']]
    config.registry.settings['db_conn'] = conn
    
    s3 = boto.connect_s3()
    config.registry.settings['s3'] = s3
    config.registry.settings['bucket'] = s3.get_bucket("asphotos")
    
    
    config.add_subscriber(add_mongo_db, NewRequest)
    config.add_subscriber(before_render, BeforeRender)
    
    #add root account if none present:
    if db.users.find({'admin':True}).count() == 0:
        pwd = hashlib.sha1('%s'%random.randint(1,1e99)).hexdigest()
        
        db.users.insert({'login':'root', 'pwd':pwd, 'admin':True })
        print 'created root account with password ', pwd
    
    
    
    
    config.add_route("index", "/")
    #config.add_view('pyphotos.views.my_view',
                    #renderer='pyphotos:templates/index.mako', route_name="index")
                    
                    
    config.add_route("listalbum", "/album/{albumname}/list", factory="pyphotos.resources.AlbumFactory")
    #config.add_view("pyphotos.views.listalbum", route_name="listalbum", renderer="pyphotos:templates/list.mako", permission='view' )
    
    config.add_route("addphotoform", "/album/{albumname}/addphoto")
    #config.add_view("pyphotos.views.addphotoform", route_name="addphotoform", renderer="pyphotos:templates/addphoto.mako")
    
    config.add_route("view_thumbnail", "/thumbnail")
    #config.add_view("pyphotos.views.thumbnail", route_name="view_thumbnail")
    
    config.add_route("login", "/login")
    #config.add_view("pyphotos.views.login", route_name="login", renderer="pyphotos:templates/login.mako")
    
    config.add_route("logout", "/logout")
    #config.add_view("pyphotos.views.logout", route_name="logout")
    
    
    #config.add_view("pyphotos.views.endpoint", route_name="velruse_endpoint")
   
    config.add_route("newalbum", "/newalbum")
    #config.add_view("pyphotos.views.newalbum", route_name="newalbum", renderer="pyphotos:templates/newalbum.mako", permission="create") 
    
    config.add_route("createticket", "/createticket/{albumname}", factory="pyphotos.resources.AlbumFactory")
    
    config.add_route("allowview", "/allow/{credential}")
    config.add_route('myalbums', '/myalbums')
    config.add_route('fullsize', '/fs/{albumname}/{filename}')
    
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    
    config.scan()
    
    
    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    event.request.fs = GridFS(db)
    
    event.request.s3 = settings['s3']
    event.request.bucket = settings['bucket']
    
    

def before_render(event):
    event["username"] = authenticated_userid(event['request'])
    event["myalbums"] = lib.myalbums(event['request'])
    
