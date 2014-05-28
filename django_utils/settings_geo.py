DATABASES = {
        'default': {
            'ENGINE': 'phidb.db.backends.postgresql_psycopg2',
            'NAME' : 'geodjango',
            'USER' : 'megacell'
            }
        }

SOUTH_DATABASE_ADAPTERS = { 'default' : 'south.db.postgresql_psycopg2' }

INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',
        'django.contrib.gis',
        'phidb',
        'south',
        'orm'
        )

SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'
