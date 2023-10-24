from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling
from .services import FriendService, FriendRequestService
from utils.debug import debug_print




# Send Friend Request
class SendFriendRequest(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            FriendRequestService.send_friend_request(
                auth_user=request.user,
                receiver_uid=request.query_params.get('to'),
            )
            
            # sending response
            return Response.success({
                'message': 'Friend Request Sent.',
            })
        except:
            return Response.something_went_wrong()
        




# Accept Friend Request
class AcceptFriendRequest(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request, request_id):
        try:
            FriendRequestService.accept_friend_request(
                auth_user=request.user,
                request_id=request_id,
            )
            
            # sending response
            return Response.success({
                'message': 'Friend Request Accepted.',
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Remove Friend Request
class UnFriend(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def delete(self, request):
        try:
            FriendService.unfriend(
                auth_user=request.user,
                friend_uid=request.query_params.get('to'),
            )

            # sending response
            return Response.success({
                'message': 'Friend Removed',
            })
        except:
            return Response.something_went_wrong()





# Check whether the user is friend or not
class IsFriend(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            is_friend = FriendService.has_friendship(
                auth_user=request.user,
                friend_uid=request.query_params.get('of')
            )
            
            return Response.success({
                'message': 'Friends List.',
                'is_friend': is_friend
            })
        except:
            return Response.something_went_wrong()
        




# List Friend
class ListFriend(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            friends = FriendService.list_all(
                auth_user=request.user,
                uid=request.query_params.get('of'),
                page=request.query_params.get('page'),
            )
            
            return Response.success({
                'message': 'Friends List.',
                'friends': friends
            })
        except:
            return Response.something_went_wrong()





# List Friend Request
class ListFriendRequest(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            friend_requests = FriendRequestService.list_all(
                user=request.user,
                page=request.query_params.get('page'),
            )
            
            return Response.success({
                'message': 'Friend Requests List.',
                'requests': friend_requests
            })
        except:
            return Response.something_went_wrong()