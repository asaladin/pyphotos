from  pyramid.security import authenticated_userid
from model import User, Album


def myalbums(request):
    username = authenticated_userid(request)
    albums = Album.m.find({'owner': username})
    albums = list(albums)
    return albums
    
