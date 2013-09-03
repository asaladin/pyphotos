from celery import Celery
from celery.signals import worker_init

from sqlalchemy import engine_from_config


import pymongo

import pyphotos.models as M

from .models import (
          DBSession, 
          Base,
          )
          
from storage import store
          
import boto

@worker_init.connect
def bootstrap_pyramid(signal, sender):
        print "signal:", signal
        print "sender:", sender.app
        import os
        from pyramid.paster import bootstrap
        _here = os.path.dirname(__file__)
        filepath = os.path.join(_here, "../development.ini")
        settings = bootstrap(filepath)['registry'].settings
        
        if settings["sqlalchemy.url"]!="testing":
            #set up sqlalchemy:
            engine = engine_from_config(settings, 'sqlalchemy.')
            DBSession.configure(bind=engine)
            Base.metadata.bind = engine
        
        
        
        #conn = pymongo.Connection(settings['db_uri'])
        #db = conn[settings['db_name']]
        #sender.app.db = db
        #M.init_mongo(engine=(settings.get('mongo.url'), settings.get('mongo.database')))
        
        #create amazon S3 connection:
        
        sender.app.mystore = store.storefactory(settings)
        
        #s3 = boto.connect_s3()
        #sender.app.s3 = s3
        #sender.app.bucket = s3.get_bucket(settings['bucket_name'])
        


celery = Celery('tasks', broker='amqp://', backend='amqp://')
