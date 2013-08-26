
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