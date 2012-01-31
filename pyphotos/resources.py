from pyramid.security import Everyone
from pyramid.security import Allow, Deny

class Root(object):
    __acl__ = [(Deny, Everyone, 'view'),]
    def __init__(self, request):
        self.request = request
    
