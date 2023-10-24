from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling
from .services import FollowService
from utils.debug import debug_print


# Send Follow Request
class SendFollowRequest(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            FollowService.send_follow_request(
                auth_user=request.user,
                receiver_uid=request.query_params.get('to'),
            )
            
            # sending response
            return Response.success({
                'message': 'Follow Request Sent.',
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()


# Follow
class AcceptFollowRequest(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, request_id):
        try:
            FollowService.accept_follow_request(
                auth_user=request.user,
                request_id=request_id,
            )

            return Response.success({
                'message': 'Followed'
            })
        except:
            return Response.something_went_wrong()


# Unfollow
class Unfollow(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request):
        try:
            FollowService.unfollow(
                auth_user=request.user,
                following_uid=request.query_params['to'],
            )

            return Response.success({
                'message': 'Unfollowed'
            })
        except:
            return Response.something_went_wrong()


# Force Unfollow
class ForceUnfollow(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request):
        try:
            FollowService.force_unfollow(
                auth_user=request.user,
                follower_uid=request.query_params['to'],
            ) 

            return Response.success({
                'message': 'Force unfollowed'
            })
        except:
            return Response.something_went_wrong()


# List Followers
class ListFollowers(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            followers, has_next = FollowService.list_followers(
                auth_user=request.user,
                uid=request.query_params['of'],
                page=request.query_params['page'],
            )
            
            return Response.success({
                'message': 'All Followers.',
                'followers': followers,
                'has_next': has_next
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()


# List Followings
class ListFollowings(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            followings, has_next = FollowService.list_followings(
                auth_user=request.user,
                uid=request.query_params['of'],
                page=request.query_params['page'],
            )
            
            return Response.success({
                'message': 'All Followings.',
                'followings': followings,
                'has_next': has_next
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()