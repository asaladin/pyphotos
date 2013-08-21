from  pyramid.security import authenticated_userid
from .models import DBSession, User, Album


def myalbums(request):
    try:
       username = request.username
       albums = DBSession.query(Album).filter(Album.owner == username).all()
       
    except AttributeError:
        albums = []
        
    return albums    
        

def get_user(request):
    email = authenticated_userid(request)
    user = DBSession.query(User).filter(User.email==email).one()
    return user
    
    
def get_username(request):
    userid = authenticated_userid(request)
    try:
       user = User.m.find({"browserid": userid}).one()
    except:
        return ''
    return user.user_name
