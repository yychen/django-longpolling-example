#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer

from django.core.management import setup_environ
import example.settings
import sys
setup_environ(example.settings)

from django.core.handlers.wsgi import WSGIHandler as DjangoWSGIApp
application = DjangoWSGIApp()

host = 'localhost'
port = 80
if len(sys.argv) > 1:
    url = sys.argv[1]

    if ':' in url:
        (host, port) = url.split(':')
    else:
        host = url

server = WSGIServer((host, int(port)), application)
print "Starting server on http://%s:%s" % (host, port)
server.serve_forever()
