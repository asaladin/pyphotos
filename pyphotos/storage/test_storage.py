from unittest import TestCase

from . import store
import tempfile

import shutil
import os

class TestLocalStorage(TestCase):
    def setUp(self):
        self.tempdir=tempfile.mkdtemp()
        self.localstore = store.LocalStore(self.tempdir)
    def tearDown(self):
        shutil.rmtree(self.tempdir)
    
    def testCreateFile(self):
        "create a simple file"
        self.localstore['testfile'] = "testcontent"
        lst=os.listdir(self.tempdir)
        self.assertIn("testfile", lst)
        
    def testCreateFile_cannot_escape_directory(self):
        "one should not be able to move outside the base directory of localstore"
        self.assertRaises(Exception, self.localstore.__setitem__, '../testfile',  "testcontent")
        