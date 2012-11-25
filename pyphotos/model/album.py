from pyphotos.model import session

from ming import Field, schema
from ming.declarative import Document

class Album(Document):

    class __mongometa__:
        session = session
        name = 'albums'

    _id = Field(schema.ObjectId)
    title = Field(str)
    owner = Field(str)
    public = Field(bool)

