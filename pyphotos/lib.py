from  pyramid.security import authenticated_userid
from model import User, Album


def myalbums(request):
    username = authenticated_userid(request)
    albums = Album.m.find({'owner': username})
    albums = list(albums)
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