from pyphotos.model import session, DBSession

from ming import Field, schema
from ming.declarative import Document
import bcrypt

class User(Document):

    class __mongometa__:
        session = session
        name = 'users'

    _id = Field(schema.ObjectId)
    user_name = Field(str)
    browserid = Field(str)
    hashed_password = Field(str, if_missing='')

    def set_password(self, clear_password):
        self.hashed_password = bcrypt.hashpw(clear_password, bcrypt.gensalt())
    
    def check_password(self, password):
        hashed = bcrypt.hashpw(password, self.hashed_password)
        return hashed == self.hashed_password
