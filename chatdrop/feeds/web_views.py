from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.authentication import UserWebAuthentication
from account.throttling import AuthenticatedUserThrottling
from .services import TimeLineService, StoryLineFeedsService, ReelLineService
from utils.debug import debug_print





# Timeline Feeds
@method_decorator(csrf_protect, name='dispatch')
class TimeLineFeedsV3(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            feeds, has_next = TimeLineService.generate_timeline_feeds_v3(
                user=request.user,
                page=request.query_params.get('page'),
            )

            # sending response
            return Response.success({
                'message': 'Timeline Feeds',
                'feeds': feeds,
                'has_next': has_next,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
        




# Story Feeds
@method_decorator(csrf_protect, name='dispatch')
class StoryLineFeeds(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            feeds = StoryLineFeedsService.list_all(request.user)

            # sending response
            return Response.success({
                'message': 'Story Feeds',
                'feeds': feeds
            })
        except:
            return Response.something_went_wrong()




# Reel Feeds
@method_decorator(csrf_protect, name='dispatch')
class ReelLineFeeds(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            feeds, has_next = ReelLineService.list_all(
                auth_user=request.user,
                page=request.query_params.get('page'),
            )

            # sending response
            return Response.success({
                'message': 'Reel Feeds',
                'feeds': feeds,
                'has_next': has_next,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()