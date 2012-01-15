from pyramid.config import Configurator
from pyphotos.resources import Root
from pyramid.events import subscriber
from pyramid.events import NewRequest


from gridfs import GridFS
import pymongo



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    
    db_uri = settings['db_uri']
    conn = pymongo.Connection(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_mongo_db, NewRequest)
    
    
    config.add_route("index", "/")
    config.add_view('pyphotos.views.my_view',
                    renderer='pyphotos:templates/index.mako', route_name="index")
                    
                    
    config.add_route("listalbum", "/album/{name}/list")
    config.add_view("pyphotos.views.listalbum", route_name="listalbum", renderer="pyphotos:templates/list.mako")
    
    config.add_route("addphotoform", "/album/{name}/addphoto")
    config.add_view("pyphotos.views.addphotoform", route_name="addphotoform", renderer="pyphotos:templates/addphoto.mako")
    
    config.add_route("view_thumbnail", "/thumbnail")
    config.add_view("pyphotos.views.thumbnail", route_name="view_thumbnail")
    
    
                    
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    return config.make_wsgi_app()

def add_mongo_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db
    event.request.fs = GridFS(db)