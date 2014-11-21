DATABASES = {
        'default': {
            'ENGINE': 'phidb.db.backends.postgresql_psycopg2',
            'NAME' : 'geodjango_test',
            'USER' : 'megacell',
            'TEST_NAME' : 'geodjango_test2'
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
        'orm',
        )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SECRET_KEY = '8lu*6g0lg)9z!ba+a$ehk)xt)x%rxgb$i1&amp;022shmi1jcgihb*'

POSTGIS_VERSION = (2,1,3)
