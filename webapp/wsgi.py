"""
WSGI config for ProjectOllie project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

path = '/var/www/'
if path not in sys.path:
    sys.path.append(path)
    sys.path.append('/var/www/ProjectOllie/')
    sys.path.append('/var/www/ProjectOllie/ProjectOllie/')

sys.path.append('/usr/lib/python2.7/dist-packages/')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
