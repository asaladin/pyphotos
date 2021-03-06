import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
            'pyramid', 
            'pyramid_debugtoolbar', 
            'pyramid_persona',
            'boto',
            'pastedeploy', 
            'paste',
            'pastescript',
            'ming',
            'pyramid_beaker',
            'pyramid_tm',
            'velruse', 
            'pillow',
            'py-bcrypt', 
            'waitress',
            'pybrowserid',
            'celery',
            'sqlalchemy',
            'pyramid_tm',
            'zope.sqlalchemy',
            'transaction',
            'SQLAlchemy',
            'webtest',
           ]

setup(name='pyphotos',
      version='0.1',
      description='pyphotos',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pyphotos",
      entry_points = """\
      [paste.app_factory]
      main = pyphotos:main
      [console_scripts]
      initialize_pyphotos_db = pyphotos.scripts.initializedb:main
      """,
      paster_plugins=['pyramid'],
      )

