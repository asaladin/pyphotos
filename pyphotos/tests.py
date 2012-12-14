import unittest

from pyramid import testing

import pyphotos.model as model

from pyphotos import views

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        model.init_mongo(engine=("mongodb://localhost/", "pyphotos_tests"))
        
        model.User.m.remove()
        model.Photo.m.remove()
        model.Album.m.remove()
        
        album = model.Album()
        album.title="holidays"
        album.owner="me@localhost"
        album.public=True
        album.m.save()
        
        private_album=model.Album()
        private_album.title="privatealbum"
        private_album.owner="other@localhost"
        private_album.public=False
        private_album.m.save()
        

    def tearDown(self):
        testing.tearDown()

    def test_my_view_anonymous(self):
        
        request = testing.DummyRequest()
        request.username = None
        resp = views.my_view(request)
        self.assertEqual(resp['project'], 'pyphotos')
        titles = [a.title for a in resp['albums']]
        
        self.assertIn('holidays', titles )
        self.assertNotIn('privatealbum', titles)
        
        self.assertEqual(resp['myalbums'], [])

        
    def test_my_view_logged(self):
        request = testing.DummyRequest()
        request.username = "other@localhost"
        
        resp = views.my_view(request)
        
        mytitles = [a.title for a in resp['myalbums']]
        self.assertIn('privatealbum', mytitles)
        