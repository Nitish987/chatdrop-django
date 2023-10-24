from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from .services import NotificationService
from account.authentication import UserWebAuthentication
from account.throttling import AuthenticatedUserThrottling
from utils.debug import debug_print



# List Notification
@method_decorator(csrf_protect, name='dispatch')
class UserNotificationsV2(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            notifications, has_next = NotificationService.list_notification_v2(auth_user=request.user, page=request.query_params.get('page'))
            
            # sending response
            return Response.success({
                'message': 'notifications',
                'notifications': notifications,
                'has_next': has_next,
            })
        except:
            return Response.something_went_wrong()





# List Notifications
@method_decorator(csrf_protect, name='dispatch')
class ReadNotifications(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request):
        try:
            NotificationService.read_notification(
                auth_user=request.user,
                notification_id=request.data.get('id'),
            )

            # sending response
            return Response.success({
                'message': 'notification read',
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()