from pyphotos.model import session

from ming import Field, schema
from ming.declarative import Document

class Photo(Document):

    class __mongometa__:
        session = session
        name = 'photos'
    
    _id = Field(schema.ObjectId)
    filename = Field(str)
    albumname = Field(str)
    thumbnailid = Field(schema.ObjectId)
    
