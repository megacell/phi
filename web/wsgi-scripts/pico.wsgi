import pico.server
import sys
sys.stdout = sys.stderr # sys.stdout access restricted by mod_wsgi
path = '/srv/http/pico' # the modules you want to be usable by Pico
if path not in sys.path:
    sys.path.insert(0, path)
print sys.path

RELOAD = True

# Set the WSGI application handler
application = pico.server.wsgi_app
