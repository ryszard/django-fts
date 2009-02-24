from django.conf import settings

FTS_BACKEND = getattr(settings, 'FTS_BACKEND', 'simple://')
