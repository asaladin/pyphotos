from pyramid.config import Configurator
from pyphotos.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


import pyramid_beaker


from gridfs import GridFS
import pymongo



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.include(pyramid_beaker)
    
    authentication_policy = AuthTktAuthenticationPolicy('seekrit')
    authorization_policy = ACLAuthorizationPolicy()
    
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    
    
    
    db_uri = settings['db_uri']
    conn = pymongo.Connection(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)
    
    
    config.add_route("index", "/")
    config.add_view('pyphotos.views.my_view',
                    renderer='pyphotos:templates/index.mako', route_name="index")
                    
                    
    config.add_route("listalbum", "/album/{name}/list")
    config.add_view("pyphotos.views.listalbum", route_name="listalbum", renderer="pyphotos:templates/list.mako", permission='view' )
    
    config.add_route("addphotoform", "/album/{name}/addphoto")
    config.add_view("pyphotos.views.addphotoform", route_name="addphotoform", renderer="pyphotos:templates/addphoto.mako")
    
    config.add_route("view_thumbnail", "/thumbnail")
    config.add_view("pyphotos.views.thumbnail", route_name="view_thumbnail")
    
    config.add_route("login", "/login")
    config.add_view("pyphotos.views.login", route_name="login", renderer="pyphotos:templates/login.mako")
    
    config.add_route("velruse_endpoint", "/velruse_endpoint")
    config.add_view("pyphotos.views.endpoint", route_name="velruse_endpoint")
   
    config.add_route("newalbum", "/newalbum")
    config.add_view("pyphotos.views.newalbum", route_name="newalbum", renderer="pyphotos:templates/newalbum.mako") 
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    event.request.fs = GridFS(db)
