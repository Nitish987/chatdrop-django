from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from account.authentication import UserWebAuthentication
from account.throttling import AuthenticatedUserThrottling
from utils.response import Response
from utils.debug import debug_print
from .services import LinkPreviewService
from . import serializers


# Link Preview
@method_decorator(csrf_protect, name='dispatch')
class LinkPreview(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.LinkPreviewSerializer(data=request.data)

            if serializer.is_valid():
                preview = LinkPreviewService.generate_link_preview(serializer.validated_data.get('url'))
                return Response.success({
                    'message': 'link preview',
                    'preview': preview
                })
            
            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
