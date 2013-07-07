from  pyramid.security import authenticated_userid
from model import User, Album


def myalbums(request):
    try:
       username = request.username
       albums = Album.m.find({'owner': username})
       albums = list(albums)
       
    except AttributeError:
        albums = list(Album.m.find({'public': True}))
        
    return albums    
        

def get_user(request):
    return authenticated_userid(request)
    
    
def get_username(request):
    userid = authenticated_userid(request)
    try:
       user = User.m.find({"browserid": userid}).one()
    except:
        return ''
    return user.user_name