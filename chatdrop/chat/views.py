from rest_framework.views import APIView
from utils.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from account.permissions import IsRequestValid
from account.throttling import AuthenticatedUserThrottling, ChatGptThrottling
from .services import SecretChatService, NormalChatService, ChatGptService
from utils.debug import debug_print


# Can Chat
class CanChat(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            # checking whether the friend is available for chat or not
            can_chat = SecretChatService.canChat(auth_user=request.user, friend_uid=request.query_params.get('to'))

            return Response.success({
                'message': 'can chat',
                'can_chat': can_chat
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()


# Chat Message
class SecretChatMessage(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            # sending NEW message signal
            receiver_prekey_bundle = SecretChatService.new_message(
                sender=request.user,
                receiver_uid=request.query_params.get('to'),
                content=request.data.get('content'),
            )

            return Response.success({
                'message': 'message sent',
                'prekey_bundle': receiver_prekey_bundle,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()
    
    def put(self, request):
        try:
            # sending READ message signal
            SecretChatService.read_message(
                sender=request.user,
                receiver_uid=request.query_params.get('to'),
            )

            return Response.success({
                'message': 'message read'
            })
        except:
            return Response.something_went_wrong()
    
    def delete(self, request):
        try:
            # sending DEL message signal
            SecretChatService.del_message(
                sender=request.user,
                receiver_uid=request.query_params.get('to'),
                messageId=request.query_params.get('id'),
            )

            return Response.success({
                'message': 'message deleted'
            })
        except:
            return Response.something_went_wrong()




# Normal chat message
class NormalChatMessage(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            # sending NEW message signal
            receiver_prekey_bundle = NormalChatService.new_message(
                sender=request.user,
                receiver_uid=request.query_params.get('to'),
                message=request.data.get('message'),
            )

            return Response.success({
                'message': 'message sent',
                'prekey_bundle': receiver_prekey_bundle,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# chatGpt message
class ChatGptMessage(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [ChatGptThrottling]

    def post(self, request):
        try:
            message = request.data.get('message')

            # sending New generated message
            reply = ChatGptService.generate_reply(
                auth_user=request.user,
                message=message,
            )

            return Response.success({
                'message': 'message sent',
                'reply': reply,
            })
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()