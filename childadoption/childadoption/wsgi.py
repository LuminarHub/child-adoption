"""
WSGI config for childadoption project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'childadoption.settings')

application = get_wsgi_application()


# this is google credentials

# '576119890722-5f6oop7mqmkgv9mbnl850ug872gt8pah.apps.googleusercontent.com'
# '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'