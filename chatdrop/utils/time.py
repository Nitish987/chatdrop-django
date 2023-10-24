from django.utils import timezone, timesince

def caltime_string(posted_on, depth=1):
    # calculating ago time
    time_ago = timesince.timesince(d=posted_on, now=timezone.now(), depth=depth)

    if time_ago.startswith('0'):
        return 'just now'

    return f'{time_ago} ago'