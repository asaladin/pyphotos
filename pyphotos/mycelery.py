from celery import Celery
from celery.signals import worker_init

import pymongo

@worker_init.connect
def bootstrap_pyramid(signal, sender):
        print "signal:", signal
        print "sender:", sender.app
        import os
        from pyramid.paster import bootstrap
        settings = bootstrap('/home/adrien/Src/web/Pyramid/pyphotos.orig/development.ini')['registry'].settings
        conn = pymongo.Connection(settings['db_uri'])
        db = conn[settings['db_name']]
        sender.app.db = db


celery = Celery('tasks', broker='amqp://', backend='amqp://')
