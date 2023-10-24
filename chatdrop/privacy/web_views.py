from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.authentication import UserWebAuthentication
from account.throttling import AuthenticatedUserThrottling
from .services import BlockedUserService, ReportUserService
from utils.debug import debug_print




# Block User
@method_decorator(csrf_protect, name='dispatch')
class BlockUser(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    # blocks the paritcular user
    def post(self, request):
        try:
            BlockedUserService.block_user(
                auth_user=request.user,
                uid=request.query_params.get('to'),
            )
            
            return Response.success({
                'message': 'User blocked',
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
    
    # returns blocked user list
    def get(self, request):
        try:
            blocked_users = BlockedUserService.list_all(request.user)
            
            return Response.success({
                'message': 'Blocked users list',
                'blocked_users': blocked_users,
            })
        except:
            return Response.something_went_wrong()
    
    # removes the blocked user
    def delete(self, request):
        try:
            BlockedUserService.unblock(
                auth_user=request.user,
                uid=request.query_params.get('to'),
            )

            return Response.success({
                'message': 'User Unblocked',
            })
        except:
            return Response.something_went_wrong()


# Report User
@method_decorator(csrf_protect, name='dispatch')
class ReportUser(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    # report the paritcular user
    def post(self, request):
        try:
            ReportUserService.make_report(
                auth_user=request.user,
                uid=request.query_params.get('to'),
                message=request.data.get('message'),
            )
            
            return Response.success({
                'message': 'User Reported',
            })
        except:
            return Response.something_went_wrong()
    
