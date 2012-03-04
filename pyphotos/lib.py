from  pyramid.security import authenticated_userid


def myalbums(request):
    username = authenticated_userid(request)
    albums = request.db.albums.find({'owner':username})
    
    return list(albums)
    
