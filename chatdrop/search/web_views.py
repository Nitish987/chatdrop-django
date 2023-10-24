from utils.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.authentication import UserWebAuthentication
from account.throttling import AuthenticatedUserThrottling
from .services import SearchService
from utils.debug import debug_print


# Search Profiles
@method_decorator(csrf_protect, name='dispatch')
class SearchProfiles(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            if request.query_params.get('q') == None:
                return Response.error('No search query given.')
            else:
                result = SearchService.query_profiles(request.user, request.query_params.get('q'), request.query_params.get('page'))
            
            # sending response
            return Response.success({
                'message': 'Search result.',
                'result': result
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Search Audios
@method_decorator(csrf_protect, name='dispatch')
class SearchAudios(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            if request.query_params.get('q') == None:
                return Response.error('No search query given.')
            else:
                result = SearchService.query_audios(request.user, request.query_params.get('q'), request.query_params.get('page'))
            
            # sending response
            return Response.success({
                'message': 'Search result.',
                'result': result
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()