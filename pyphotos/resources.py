from pyramid.security import Everyone
from pyramid.security import Allow, Deny

class Root(object):
    def __init__(self, request):
        self.request = request
        self.__acl__ = [(Allow, 'toto', 'view'),]
    
