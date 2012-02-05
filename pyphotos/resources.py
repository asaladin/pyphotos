from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow, Deny
from pyramid.security import authenticated_userid


class Root(object):
    def __init__(self, request):
        self.request = request
        self.__acl__ = [
                         (Allow, Authenticated, 'create'),
                         (Allow, 'toto', 'view'),
                       ]
    
class AlbumFactory(object):
    def __init__(self, request):
        self.request = request
        self.__acl__ = []
        
        db = request.db
        albumname = request.matchdict['albumname']
        
        album = db.albums.find_one({'title': albumname})
        owner = album['owner']
        print "debug: owner ", owner
        self.__acl__.append( (Allow, owner, 'createticket'), )
        
        
            
        
        
        