from pyramid.security import Everyone, Authenticated
from pyramid.security import Allow, Deny, ALL_PERMISSIONS
from pyramid.security import authenticated_userid


class Root(object):
    def __init__(self, request):
        self.request = request
        self.__acl__ = [
                         (Allow, 'group:admin', ALL_PERMISSIONS),
                         (Allow, request.registry.settings['admin_email'], ALL_PERMISSIONS),
                         (Allow, Authenticated, 'create'),
                       ]
    
class AlbumFactory(object):
    def __init__(self, request):
        self.request = request
        self.__acl__ = [
                         (Allow, 'group:admin', ALL_PERMISSIONS) ,
                         (Allow, Authenticated, 'create'),
                       ]

        db = request.db
        albumname = request.matchdict['albumname']
        
        album = db.albums.find_one({'title': albumname})
        owner = album['owner']
        self.__acl__.append( (Allow, owner, 'createticket'), )
        self.__acl__.append( (Allow, owner, 'view'), )
        self.__acl__.append( (Allow, owner, 'append'), ) #add new photo
        if album['public'] is True:
            self.__acl__.append( (Allow, Everyone, 'view') )
        
        if 'tickets' in request.session:
            tickets = request.session['tickets']
            try:
                 credential = tickets[albumname]
                 print "debug: ok il y a un credential"
            except KeyError:
                return
                
            #check credential in the ticket database:
            cred = db.tickets.find_one({'token': credential})
            if cred['albumname'] == album['title']:
                 print "cred ok"        
                 self.__acl__.append( (Allow, Everyone, 'view'),)

        
        
        
        
            
        
        
        
