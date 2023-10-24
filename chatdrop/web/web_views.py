from rest_framework.views import APIView
from utils.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AttachCsrf(APIView):
    def get(self, request):
        return Response.success({'message': 'CSRF Token Attached'})
