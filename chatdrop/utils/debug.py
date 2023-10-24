from django.conf import settings

def debug_print(object):
    if settings.DEBUG:
        print(f'LOGS : {object}')