from ming import Session
from ming.datastore import DataStore
from ming import create_datastore
from ming.odm import ThreadLocalORMSession

import logging
log = logging.getLogger(__name__)

session = Session()
DBSession = ThreadLocalORMSession(doc_session=session)
 
def init_mongo(engine):
    global session
    server, database = engine
    log.debug("%s%s"%(server, database))
    session.bind = create_datastore("%s%s"%(server, database))


from .user import User
from .album import Album
from .photo import Photo
