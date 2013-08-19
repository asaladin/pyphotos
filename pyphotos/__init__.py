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
import pymongo
import hashlib
import lib

import boto

import pyphotos.model as M
from pyphotos.model import user

from pyphotos.views import forbidden_view

from pyphotos.storage import store 


def ingroup(userid, request):
    return [userid]





def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.include(pyramid_beaker)

    config.scan("pyphotos.model")
    M.init_mongo(engine=(settings.get('mongo.url'), settings.get('mongo.database')))

    authentication_policy = AuthTktAuthenticationPolicy('seekrit', callback=ingroup, hashalg='sha512')
    authorization_policy = ACLAuthorizationPolicy()
    
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    
    #create mongodb connection:
    db_uri = settings['db_uri']
    conn = pymongo.Connection(db_uri)
    db = conn[settings['db_name']]
    config.registry.settings['db_conn'] = conn
    
    #create amazon S3 connection:
    #s3 = boto.connect_s3()
    #config.registry.settings['s3'] = s3
    #config.registry.settings['bucket'] = s3.get_bucket(settings['bucket_name'])

    mystore = store.LocalStore("/tmp/photos")
    config.registry.settings['mystore'] = mystore 
    
    config.add_subscriber(add_mongo_db, NewRequest)
    config.add_subscriber(before_render, BeforeRender)
    config.add_subscriber(check_for_new_user, NewRequest)
    
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
    config.add_route('fullsize', '/fullsize/{albumname}/{filename}', factory="pyphotos.resources.AlbumFactory")
    config.add_route('new_user', "/newuser")
    config.add_route('import_s3', '/import/s3')
    config.add_route('generate_thumbnail', '/thumbnail/generate/{albumname}/{filename}')
    config.add_route('admin', '/admin')
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    
    config.add_forbidden_view(forbidden_view)
    

    config.add_request_method('pyphotos.lib.get_user', name='user', property=True, reify=True)
    
    config.scan()
    
    
    return config.make_wsgi_app()

from views import NewUser  
    
def add_mongo_db(event):
        
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    event.request.fs = GridFS(db)

    event.request.mystore = settings['mystore']

from pyphotos.model import User    

def check_for_new_user(event):
    userid = authenticated_userid(event.request)
    if userid is None: return
    users = User.m.find({"browserid": userid})
    if len(users) == 0:  #only redirect to new_user if the user is not in the database
        #don't reraise the NewUser exception if the new_user view is going to be visited
        if event.request.url != event.request.route_url('new_user'):
            raise NewUser()
    else:
        user = users.first()
        event.request.username = user.username
    

def before_render(event):
    event["myalbums"] = lib.myalbums(event['request'])
    
    
