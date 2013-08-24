import unittest

from pyramid import testing

import pyphotos.models as model

from pyphotos import views
import transaction

from sqlalchemy import create_engine


import logging
log = logging.getLogger(__name__)


from .models import (
    User,
    Album,
    Photo,
    )

    
import models    

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

    
    

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        
        engine = create_engine('sqlite://')
        models.Base.metadata.create_all(engine)
        models.DBSession.configure(bind=engine)
        
        with transaction.manager:        
            album = Album()
            album.name="holidays"
        
            rootuser = User()
            rootuser.username = "root"
            rootuser.email = "root@localhost"
            models.DBSession.add(rootuser)
            transaction.commit()
            
            otheruser = User()
            otheruser.username ="other"
            otheruser.email = "other@localhost"
            models.DBSession.add(otheruser)
            transaction.commit()
            
            album.owner=rootuser
            album.public=True
            models.DBSession.add(album)
            
            album = Album()
            album.name = "privatealbum"
            album.owner = otheruser
            album.public = False
            models.DBSession.add(album)
            
       
        
        self.request = testing.DummyRequest()
        self.request.user = otheruser

        

    def tearDown(self):
        model.DBSession.remove()
        testing.tearDown()
    

    def test_my_view_anonymous(self):
        
        self.request.user = None
        resp = views.my_view(self.request)
        self.assertEqual(resp['project'], 'pyphotos')
        titles = [a.name for a in resp['albums']]
        
        self.assertIn('holidays', titles )
        self.assertNotIn('privatealbum', titles)
        
        self.assertEqual(resp['myalbums'], [])

        
    def test_my_view_logged(self):
        
        self.request.user = models.DBSession.query(User).filter(User.email == "other@localhost").one()
        resp = views.my_view(self.request)
        mytitles = [a.name for a in resp['myalbums']]
        self.assertIn('privatealbum', mytitles)


    
    def test_newalbum(self):
        self.request.username = "other@localhost"
        
        self.request.POST['albumname'] = 'myawesomealbum'
        self.request.POST['visible'] = 'True'
        
        response = views.newalbum(self.request)
        
        from pyramid.httpexceptions import HTTPFound
        self.assertTrue(isinstance(response, HTTPFound))
        
        #albums = model.Album.m.find({"title": "myawesomealbum"}).all()
        albums = model.DBSession.query(Album).filter(Album.name=="myawesomealbum")
        self.assertEqual(albums.count(), 1)
        
        
        
    