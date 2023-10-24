from django.conf import settings
from django.core.mail import EmailMessage
from .debug import debug_print

class Mailer:
    @staticmethod
    def sendEmail(email, data):
        '''sends email'''

        if settings.DEBUG:
            # printing data only for Development
            debug_print(data)
        else:
            try:
                debug_print(email)
                email = EmailMessage(
                    subject='chatdrop app', 
                    body=str(data), 
                    from_email=str(settings.EMAIL_HOST_USER), 
                    to=[email,], 
                    reply_to=['support@example.in']
                )
                email.send(fail_silently=False)
            except Exception as e:
                debug_print(e)
            