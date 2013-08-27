import boto
from boto.s3.key import Key


class Store(object):
    def __init__(self):
       pass

    def __getitem__(self, key):
       raise NotImplemented

    def __setitem__(self, key, content):
       raise NotImplemented


import os.path

class LocalStore(Store):
    def __init__(self, basedir):
       self.basedir = basedir
    
    def __getitem__(self, key):
       filepath = os.path.join(self.basedir, key)
       f = open(filepath, 'rb')
       return f.read() 

    def __setitem__(self, key, content): 
       filepath = os.path.join(self.basedir, key)
       f = open(filepath, 'wb')
       f.write(content)
       f.close() 

    @staticmethod
    def genkey(album, filename, thumbnail=False):
        if thumbnail:
           key = os.path.join(album, "thumbnail",  filename)
        else:
           key = os.path.join(album, filename)
        return key

class S3Store(Store):
    def __init__(self, bucketname):
        #create amazon S3 connection:
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
            key = '%s/thumbnail/%s'%(album, filename)
        else:
            key = '%s/%s'%(album, filename)
        return key
    