from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling
from .services import TimeLineService, StoryLineFeedsService, ReelLineService
from utils.debug import debug_print


# Timeline Feeds

# deprecated
class TimeLineFeedsV2(APIView):
    '''This API is deprecated, must use v3.'''
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            feeds, has_next = TimeLineService.generate_timeline_feeds_v2(
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


class TimeLineFeedsV3(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class StoryLineFeeds(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ReelLineFeeds(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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