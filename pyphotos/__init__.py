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

import pyphotos.model as M
from pyphotos.model import user

def ingroup(userid, request):
    return [userid]


def get_user(request):
    username = authenticated_userid(request)
    return username


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.include(pyramid_beaker)

    config.include("velruse.providers.openid")
    config.include('velruse.providers.google_oauth2')
    config.add_openid_login()

    config.scan("pyphotos.model")
    M.init_mongo(engine=(settings.get('mongo.url'), settings.get('mongo.database')))

    #config.include("pyramid_persona")


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
    config.add_route("listalbum", "/album/{albumname}/list", factory="pyphotos.resources.AlbumFactory")
    config.add_route("addphotoform", "/album/{albumname}/addphoto")
    config.add_route("view_thumbnail", "/thumbnail")
    config.add_route("login", "/login")
    config.add_route("browserid_login", "/login/browserid")
    config.add_route("logout", "/logout")
    config.add_route("newalbum", "/newalbum")
    config.add_route("createticket", "/createticket/{albumname}", factory="pyphotos.resources.AlbumFactory")
    config.add_route("allowview", "/allow/{credential}")
    config.add_route('myalbums', '/myalbums')
    config.add_route('fullsize', '/fs/{albumname}/{filename}')
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)

    config.add_request_method(get_user, name='user', property=True, reify=True)
    
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
    
