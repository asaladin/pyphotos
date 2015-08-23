import boto
from boto.s3.key import Key


class Store(object):
    def __init__(self):
       pass

    def __getitem__(self, key):
       raise NotImplemented

    def __setitem__(self, key, content):
       raise NotImplemented


import os
import os.path

class LocalStore(Store):
    def __init__(self, basedir):
       self.basedir = basedir
    
    def _path(self, key):
        filepath = os.path.join(self.basedir, key)
        path = os.path.realpath(filepath)
        
        assert(".." not in path)
        if not path.startswith(self.basedir):
            raise RuntimeError("Error: file path is not a subpath of basedir")
        return path
    
    def __getitem__(self, key):
       filepath = self._path(key)
       f = open(filepath, 'rb')
       return f.read() 

    def __setitem__(self, key, content): 
       filepath = self._path(key)
       basedir = os.path.split(filepath)[0]
       if not os.path.exists(basedir):
           os.makedirs(basedir)  #recursive
       f = open(filepath, 'wb')
       f.write(content)
       f.close() 

    @staticmethod
    def genkey(album, filename, thumbnail=False):
        if thumbnail:
           key = os.path.join("thumbnail", album, filename)
        else:
           key = os.path.join(album, filename)
        return key
     
    def view_url(self, filekey):
        url="/fullsize/%s"%(filekey)
        return url

class S3Store(Store):
    def __init__(self, bucketname):
        #create amazon S3 connection:
        self.bucketname = bucketname
        self.s3 = boto.connect_s3()
        self.bucket = self.s3.get_bucket(bucketname)
        
    def __getitem__(self, key):
        #get the S3 key:
        s3key = Key(self.bucket)
        s3key.key=key 
        f = s3key.get_contents_as_string()
        return f
    def __setitem__(self, key, content):
        s3key = self.bucket.new_key(key)
        s3key.set_contents_from_string(content)
        
    @staticmethod
    def genkey(album, filename, thumbnail=False):
        if thumbnail:
            key = 'thumbnail/%s/%s'%(album, filename)
        else:
            key = '%s/%s'%(album, filename)
        return key
    
    def view_url(self, filekey):
        url = self.s3.generate_url(3600 , "GET" ,  self.bucketname,filekey )
        return url
        
    def list(self, albumname):
        return self.bucket.list(albumname)
        
def storefactory(settings):
    store_type = settings['store.type']
    if store_type == "local":
        return LocalStore(settings['store.dir'])
    elif store_type == "s3":
        return S3Store(settings['store.bucket'])
    else:
        raise RuntimeError("cannot determine the store type")
    
    