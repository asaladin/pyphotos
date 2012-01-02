from pyramid.config import Configurator
from pyphotos.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('pyphotos.views.my_view',
                    context='pyphotos:resources.Root',
                    renderer='pyphotos:templates/mytemplate.pt')
    config.add_static_view('static', 'pyphotos:static', cache_max_age=3600)
    return config.make_wsgi_app()
