from pyphotos.model import session, DBSession

from ming import Field, schema
from ming.declarative import Document


class User(Document):

    class __mongometa__:
        session = session
        name = 'users'

    _id = Field(schema.ObjectId)
    first_name = Field(str)
    public = Field(bool)


