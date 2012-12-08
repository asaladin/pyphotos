from pyphotos.mycelery import celery

@celery.task
def foo():
    albums = celery.db.albums.find()
    for al in albums:
        print al