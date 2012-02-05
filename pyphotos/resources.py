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
        self.__acl__ = [(Allow, Authenticated, 'create'),]
        
        print request.session
        
        
        db = request.db
        albumname = request.matchdict['albumname']
        
        album = db.albums.find_one({'title': albumname})
        owner = album['owner']
        print "debug: owner ", owner
        self.__acl__.append( (Allow, owner, 'createticket'), )
        self.__acl__.append( (Allow, owner, 'view'), )
        
        if 'tickets' in request.session:
            print "debug: ok il y a des tickets"
            tickets = request.session['tickets']
            try:
                 credential = tickets[albumname]
                 print "debug: ok il y a un credential"
            except KeyError:
                return
                
            #check credential in the ticket database:
            cred = db.tickets.find_one({'token': credential})
            print "debug: cred", cred
            if cred['albumname'] == album['title']:
                 print "cred ok"        
                 self.__acl__.append( (Allow, Everyone, 'view'),)

        
        
        
        
            
        
        
        